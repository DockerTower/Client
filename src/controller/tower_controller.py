from cement.core.controller import CementBaseController, expose
from termcolor import colored
import yaml
import dockerpty
import os
from src.config.config import Config
from src.tower.builder import Builder
from src.tower.agent import Agent
from src.tower.nginx import Nginx

VERSION = '0.0.1'
BANNER = """
Client v%s
Copyright (c) 2016 VeeeneX
""" % VERSION


class TowerController(CementBaseController):
    class Meta:
        label = 'base'
        description = "Client orchestrated docker"
        arguments = [
            (['-v', '--version'], dict(action='version', version=BANNER)),
            (['-f', '--file'], dict(dest='file')),
        ]

    application_config = {}

    def __init__(self, *args, **kwargs):
        self.config = Config(os.environ['HOME'] + '/tower.yml')
        super().__init__(*args, **kwargs)

    @expose(hide=True)
    def default(self):
        self.app.args.print_help()

    def load_configuration(self):
        if self.app.pargs.file:
            file = self.app.pargs.file
        elif os.path.isfile(os.getcwd() + '/Towerfile'):
            file = os.getcwd() + '/Towerfile'
        else:
            raise ValueError('Please specify file!')

        with open(file, 'r') as stream:
            try:
                self.application_config = yaml.load(stream)
            except yaml.YAMLError as e:
                raise ValueError(e)

    @expose(help="Start application")
    def up(self):
        self.load_configuration()
        for environment_name, environment in self.application_config.get('environments', {}).items():

            agent_name = environment.get('agent', '')
            builder_name = environment.get('builder', '')

            if agent_name == '' and builder_name == '':
                agent_name = builder_name = environment.get('server', '')

            tower_config = self.config.open()
            servers = tower_config.get('servers', {})

            agent_config = servers.get(agent_name, False)
            builder_config = servers.get(builder_name, False)

            builder = Builder(builder_config, self.application_config, environment_name)
            agent = Agent(agent_config, self.application_config, environment_name)
            nginx = Nginx(agent_config, self.application_config, environment_name)

            if builder_config:

                try:
                    response = builder.build()
                    if response.get("success", False):
                        self.print("Images has been built!")

                        services = response.get("data", {})
                        agent.deploy(services)
                        nginx.start()

                except ValueError:
                    self.print("Failed to build!")

    @expose(help="Stop application")
    def down(self):
        self.load_configuration()
        for environment_name, environment in self.application_config.get('environments', {}).items():

            agent_name = environment.get('agent', '')

            if agent_name == '' and builder_name == '':
                agent_name = builder_name = environment.get('server', '')

            tower_config = self.config.open()
            servers = tower_config.get('servers', {})

            agent_config = servers.get(agent_name, False)
            agent = Agent(agent_config, self.application_config, environment_name)

            agent.down()

    @staticmethod
    def print(message, color="green", end="\n"):
        print(colored("===> {message}".format(message=message), color), end=end)