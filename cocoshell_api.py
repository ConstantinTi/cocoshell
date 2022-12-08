import random
import string
from multiprocessing import Process
from flask import Flask, session, request

letters = string.ascii_lowercase
#route = '/' + ''.join(random.choice(letters) for i in range(3))

api = Flask(__name__)
api.config["SECRET_KEY"] = ''.join(random.choice(letters) for i in range(32))

@api.route('/test', methods=['GET', 'POST'])
def get_command():
    if request.method == 'GET':
        if 'command' in session:
            return session['command']
        return ''
    if request.method == 'POST':
        return 'not implemented yet'

@api.route('/cmd', methods=['PUT'])
def set_command():
    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
        content = request.get_json()
        session['command'] = content['cmd']
        return session['command']

@api.route('/session', methods=['DELETE'])
def delete_session():
    session.clear()
    return ''

#def get_command_from_file():

#def write_command_to_file():


if __name__ == '__main__':
    try:
        api.run()
    except KeyboardInterrupt:
        exit