import uuid, datetime, json

class Agent:
    id = None
    hostname = None
    cwd = None
    connected = None
    last_checkin = None
    command = ''
    result = 'None'
    has_run = False
    pulses = []

    def __init__(self, uuid, hostname, cwd):
        self.id = uuid
        self.hostname = hostname
        self.cwd = cwd
        self.connected = datetime.datetime.now()
        self.last_checkin = datetime.datetime.now()

    def new_command(self, command):
        self.command = command
        self.result = 'None'
        has_run = False

    def set_result(self, result):
        self.result = result
        self.has_run = True

    def get_result(self):
        self.has_run = False
        return self.result
        

    

