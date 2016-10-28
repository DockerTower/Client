from cement.core.controller import CementBaseController, expose
import yaml
import os.path
import os
from termcolor import colored
from ..config.config import Config
from haikunator import Haikunator
import click
from docker import Client
import requests
import json


class ServerController(CementBaseController):
    class Meta:
        label = 'server'
        stacked_on = 'base'
        stacked_type = 'nested'
        description = "Servers"

    def __init__(self, *args, **kw):
        self.config = Config(os.environ['HOME'] + '/tower.yml')
        self.haikunator = Haikunator()
        self.roles = ['agent', 'builder']
        super().__init__(*args, **kw)

    @expose(hide=True)
    def default(self):
        self.app.args.print_help()

    @expose(help="Register docker server")
    def register(self):
        config = self.config.open()
        random_name = self.haikunator.haikunate(token_chars='TOWEROCKS')

        name = click.prompt('Server name', type=str, default=random_name)
        url = click.prompt('Server url', type=str, default='unix://var/run/docker.sock')
        provisioned = click.confirm('Is your server already provisioned?')

        if click.confirm('Do you test connection to server?'):
            self.print('Client will test connection to server')

            client = self.create_connection(url)
            if self.test_connection(client):
                self.print('Success! connected to server', color='green')
            else:
                self.print('Unable to connect to the server', color='red')

        server = {
            'name': name,
            'url': url,
            'provisioned': provisioned,
        }

        config['servers'][server['name']] = server

        if provisioned:
            self.print('Great! Now you can provision your server!', color='green')
        else:
            self.print('Great! Server is now registered!', color='green')

        self.config.save(config)

    @expose(help="List servers")
    def list(self):
        config = self.config.open()
        print(config['servers'])

    @expose(help="Provision")
    def provision(self):
        config = self.config.open()
        servers = config.get("servers", {})

        self.print('Please select sever:', color='green')
        for server in servers:
            self.print('* {server}'.format(server=server), color='yellow')

        server = click.prompt('Server name', type=str)

        if server in servers:
            server = config['servers'][server]
        else:
            self.print('Invalid server name', color='red')
            exit(1)

        self.print('Checking connection')

        client = self.create_connection(server['url'])
        if self.test_connection(client):
            self.print('Success! connected to server', color='green')
        else:
            self.print('Unable to connect to the server', color='red')
            exit(1)

        role = click.prompt('Server role', type=str, default='agent')

        if role not in self.roles:
            self.print('Invalid server role', color='red')

        self.print('Starting provision')

        tower_volume = False
        for volume in client.volumes().get("Volumes", {}):
            name = client.inspect_volume(volume.get("Name"))
            if name is 'tower':
                tower_volume = True

        if tower_volume is False:
            client.create_volume(
                name='tower',
                driver='local'
            )

        containers = client.containers(filters={'name': 'tower-nginx'}, all=True)
        if 0 == len(containers):

            for line in client.pull('nginx:alpine', stream=True):
                print(json.loads(line.decode('utf-8')).get("status", ''))

            tower_nginx = client.create_container(
                image='nginx:alpine',
                detach=True,
                name='tower-nginx',
                ports=['80', '443'],
                host_config=client.create_host_config(
                    port_bindings={
                        80: ('127.0.0.1', 80),
                        443: ('127.0.0.1', 443)
                    })
            )
            client.start(container=tower_nginx.get('Id'))

        containers = client.containers(filters={'name': 'tower-builder'}, all=True)
        if 0 == len(containers):

            for line in client.pull('veeenex/tower-builder', stream=True):
                print(json.loads(line.decode('utf-8')).get("status", ''))

            tower_builder = client.create_container(
                image='veeenex/tower-builder',
                detach=True,
                command='',
                name='tower-builder'
            )
            client.start(container=tower_builder.get('Id'))

    def test_connection(self, client):
        try:
            client.containers()
            return True
        except requests.exceptions.RequestException as e:
            return False

    def create_connection(self, url):
        return Client(base_url=url)

    def print(self, message, color="blue", end="\n"):
        print(colored("===> {message}".format(message=message), color), end=end)
