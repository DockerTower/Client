import json
import docker
from termcolor import colored


class Builder(object):
    def __init__(self, config, application, environment_name):
        self.config = config
        self.environment_name = environment_name
        self.application = application
        self.client = docker.Client(base_url=self.config.get("url", False), version='auto', timeout=180)

    def build(self):
        builder = self.client.create_container(
            image='tower:latest',
            detach=True,
            command="builder build",
            stdin_open=True,
            tty=True,
            environment={
                'APPLICATION': json.dumps(self.application),
                'APPLICATION_ENVIRONMENT': self.environment_name
            },
            volumes=['/var/run/docker.sock'],
            host_config=self.client.create_host_config(binds=[
                '/var/run/docker.sock:/var/run/docker.sock',
                '/home/veeenex/.ssh/:/.ssh_host/',
            ])
        )
        builder_id = builder.get('Id')
        self.client.start(container=builder_id)
        response = self.client.attach(container=builder_id, stream=True)
        response = self.print_stream(response)
        response = json.loads(response)

        if response.get("success", False):
            self.client.remove_container(container=builder_id)

        return response

    @staticmethod
    def print_stream(message, color="green"):
        line = ""
        for s in message:
            s = s.decode("utf-8")

            if line.startswith('===>') and line.endswith('\r\n'):
                print(colored("{message}".format(message=line), color), end="")
                line = ""

            line += s
        return line
