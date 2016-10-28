import json
import docker
from termcolor import colored


class Nginx(object):

    def __init__(self, config, application, environment_name):
        self.config = config
        self.environment_name = environment_name
        self.application = application
        self.client = docker.Client(base_url=self.config.get("url", False), version='auto')

    def start(self):

        containers = self.client.containers(filters={
            "name": 'tower-nginx'
        }, all=True)

        if not containers:
            nginx = self.client.create_container(
                name='tower-nginx',
                image='tower:latest',
                detach=True,
                command="nginx start",
                stdin_open=True,
                tty=True,
                volumes=['/var/run/docker.sock'],
                ports=[80, 443],
                environment={
                    'APPLICATION': json.dumps(self.application),
                    'APPLICATION_ENVIRONMENT': self.environment_name
                },
                host_config=self.client.create_host_config(
                    port_bindings={
                        80: 80,
                        443: 443
                    },
                    binds=[
                        '/var/run/docker.sock:/var/run/docker.sock',
                        'tower:/etc/nginx/conf.d',
                    ],
                )
            )
            nginx_id = nginx.get('Id')
            self.client.start(container=nginx_id)
        else:
            container = containers[0]
            status = container.get("Status")
            container_id = container.get("Id")

            if status == 'Created' or status.startswith("Exited"):
                self.client.start(container=container_id)
            elif status.startswith("Up"):
                self.print("Reloading nginx")
                exec_id = self.client.exec_create(
                    container=container_id,
                    cmd="./tower nginx reload"
                )
                response = self.client.exec_start(
                    exec_id=exec_id,
                    stream=True,
                    detach=False
                )
                self.print_stream(response)

        return True

    @staticmethod
    def print_stream(message, color="cyan"):
        line = ""
        for s in message:
            s = s.decode("utf-8")

            if line.startswith('===>') and line.endswith('\r\n'):
                print(colored("{message}".format(message=line), color), end="")
                line = ""

            line += s
        return line

    @staticmethod
    def print(message, color="green", end="\n"):
        print(colored("===> {message}".format(message=message), color), end=end)
