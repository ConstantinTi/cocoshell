import sqlite3, datetime
from os.path import exists
#import log

class Db:
    con = None
    logger = None

    def __init__(self, dbname, verbose=False):
        db_exists = exists(dbname)
        if not db_exists:
            self.create_db(self, dbname)
        #self.logger = Log(verbose)

        self.con = sqlite3.connect(dbname, check_same_thread=False)
        cur = self.get_cursor()
        cur.execute("UPDATE commands SET hasBeenRun = 1")
        self.con.commit()

    def __del__(self):
        self.con.close()

    def create_db(self, dbname):
        cur = self.get_cursor()
        cur.execute("CREATE TABLE commands (id integer primary key autoincrement, cmd text, result text, hasBeenRun integer)")
        cur.execute("CREATE TABLE pwd (id integer, pwd text)")
        cur.execute("CREATE TABLE pulse (id integer primary key autoincrement, beat timestamp)")
        cur.execute("INSERT INTO commands (cmd, result, hasBeenRun) VALUES (null, null, 1)")
        cur.execute("INSERT INTO pwd (id, pwd) VALUES (1, 'NULL')")
        cur.execute("INSERT INTO pulse (beat) VALUES (null)")
        self.con.commit()

    def get_cursor(self):
        return self.con.cursor()

    def close_cursor(self, cursor):
        cursor.close()

    def close_connection(self):
        self.con.close()

    def get_last_result(self):
        cur = self.get_cursor()
        cur.execute("SELECT * FROM commands ORDER BY id DESC LIMIT 1")
        result = cur.fetchone()
        self.close_cursor(cur)
        return result

    def is_active(self, timeout_agent):
        cur = self.get_cursor()
        cur.execute("SELECT beat FROM pulse ORDER BY id DESC LIMIT 1")
        timestamp_str = cur.fetchone()[0]
        timestamp = datetime.datetime.strptime(timestamp_str, "%H:%M:%S %m/%d/%Y")
        difference = datetime.datetime.now() - timestamp
        active = True if difference.total_seconds() > timeout_agent else False
        self.close_cursor(cur)
        return active

    def get_heartbeat(self):
        cur = self.get_cursor()
        cur.execute("SELECT beat FROM pulse ORDER BY id DESC LIMIT 1")
        result = cur.fetchone()[0]
        self.close_cursor(cur)
        return result

    def set_heartbeat(self):
        now = datetime.datetime.now()
        timestamp = now.strftime("%H:%M:%S %m/%d/%Y")
        cur = self.con.cursor()
        cur.execute("INSERT INTO pulse (beat) VALUES ('" + timestamp + "')")
        self.close_cursor(cur)
        self.con.commit()
        return timestamp

    def reset_agent(self):
        cur = self.get_cursor()
        cur.execute("UPDATE commands SET hasBeenRun = 1")
        cur.execute("UPDATE pwd SET pwd = 'NULL'")
        self.con.commit()
        self.close_cursor(cur)
        return ['NULL', False]

    def is_command_available(self):
        cur = self.get_cursor()
        cur.execute("SELECT * FROM commands ORDER BY id DESC LIMIT 1")
        result = cur.fetchone()
        self.close_cursor(cur)
        return result

    def set_result(self, result):
        cur = self.get_cursor()
        cur.execute("UPDATE commands SET result = '" + result + "' WHERE hasBeenRun = 0")
        cur.execute("UPDATE commands SET hasBeenRun = 1")
        self.con.commit()
        self.close_cursor(cur)
        return True

    def set_pwd(self, pwd):
        cur = self.get_cursor()
        cur.execute(f"UPDATE pwd SET pwd = '{pwd}' WHERE id = 1")
        self.con.commit()
        self.close_cursor(cur)
        return True

    def get_pwd(self):
        cur = self.con.cursor()
        cur.execute("SELECT pwd FROM pwd LIMIT 1")
        result = cur.fetchone()[0]
        self.close_cursor(cur)
        return result

    def new_command(self, cmd):
        if self.get_last_result()[3] == 1:
            cur = self.con.cursor()
            cur.execute("INSERT INTO commands (cmd, result, hasBeenRun) VALUES ('" + cmd + "', null, 0)")
            self.con.commit()
        return True