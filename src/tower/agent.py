import json
import docker
from termcolor import colored


class Agent(object):

    def __init__(self, config, application, environment_name):
        self.config = config
        self.environment_name = environment_name
        self.application = application
        self.client = docker.Client(base_url=self.config.get("url", False), version='auto', timeout=180)

    def deploy(self, services):
        agent = self.client.create_container(
            image='tower:latest',
            detach=True,
            command="agent deploy",
            stdin_open=True,
            tty=True,
            environment={
                'APPLICATION': json.dumps(self.application),
                'APPLICATION_ENVIRONMENT': self.environment_name,
                'SERVICES': json.dumps(services),
            },
            volumes=[
                '/var/run/docker.sock',
            ],
            host_config=self.client.create_host_config(
                binds=[
                    '/var/run/docker.sock:/var/run/docker.sock',
                    'tower:/etc/nginx/conf.d',
                ],
            )
        )
        agent_id = agent.get('Id')

        self.client.start(container=agent_id)
        response = self.client.attach(container=agent_id, stream=True)
        response = print_stream(response)
        response = json.loads(response)

        if response.get("success", False):
            pass
            # self.client.remove_container(container=agent_id)

        return response

    def down(self):
        agent = self.client.create_container(
            image='tower:latest',
            detach=True,
            command="agent down",
            stdin_open=True,
            tty=True,
            environment={
                'APPLICATION': json.dumps(self.application),
                'APPLICATION_ENVIRONMENT': self.environment_name,
            },
            volumes=['/var/run/docker.sock'],
            host_config=self.client.create_host_config(binds=[
                '/var/run/docker.sock:/var/run/docker.sock',
                'tower:/etc/nginx/conf.d',
            ])
        )
        agent_id = agent.get('Id')

        self.client.start(container=agent_id)
        response = self.client.attach(container=agent_id, stream=True)
        response = print_stream(response)
        response = json.loads(response)

        if response.get("success", False):
            pass
            # self.client.remove_container(container=agent_id)

        return response


def print_stream(message, color="cyan"):
    line = ""
    for s in message:
        s = s.decode("utf-8")

        if line == '===> \r\n':
            line = ""

        if line.startswith('===>') and line.endswith('\r\n') and line != '===> \r\n':
            print(colored("{message}".format(message=line), color), end="")
            line = ""

        line += s
    return line
