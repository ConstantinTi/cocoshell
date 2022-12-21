import requests, ast, time, os
from .log import Log
from .agent import Agent

logger = Log(True)

def print_agents(url):
    logger.print_agents(get_agents(url))

def get_agents(url):
    response = requests.get(f"{url}/agents")
    logger.debug(response.content.decode())
    return ast.literal_eval(response.content.decode())

def get_agent(url, uuid):
    response = requests.get(f"{url}/agents/{uuid}")
    agent = ast.literal_eval(response.content.decode())
    return Agent(agent[0], agent[1], agent[2])

def delete_agent(url, uuid):
    response = requests.delete(f"{url}/agents/{uuid}")
    return response.content.decode()

def interact(url, uuid):
    for agent in get_agents(url):
        if uuid == agent[0]:
            logger.info(f"Interacting with agent {uuid}")
            return get_agent(url, uuid)
    logger.failed(f"Cannot interact with that agent. Does it exist?")
    logger.info("Use the command 'agents' to print all available agents")
    return False

def execute_command(url, uuid, command):
    response = requests.post(f"{url}/cmd/{uuid}", command)
    logger.debug(response.content.decode())
    if response.content.decode() == 'True':
        while True:
            time.sleep(1.0)
            result = requests.get(f"{url}/cmd/{uuid}")
            text = result.content.decode()
            if text != 'None':
                text = text.replace('%NL%', os.linesep)
                return text
            else:
                continue
    else:
        logger.failed("Sending the command failed for some reason")
    pass