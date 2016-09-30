from cement.core.controller import CementBaseController, expose
from termcolor import colored
import zmq
import yaml
import getpass
import uuid
import socket as host
import json

VERSION = '0.0.1'
BANNER = """
Tower v%s
Copyright (c) 2016 VeeeneX
""" % VERSION


class TowerController(CementBaseController):
    class Meta:
        label = 'base'
        description = "Tower orchestrated docker"
        arguments = [
            (['-v', '--version'], dict(action='version', version=BANNER)),
            (['-f', '--file'], dict(dest='file')),
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.DEALER)
        self.socket.identity = str(uuid.uuid1()).encode('ascii')
        self.socket.connect('tcp://185.8.164.31:5570')


    @expose(hide=True)
    def default(self):
        self.app.args.print_help()

    @expose(help="Start application")
    def up(self):

        if self.app.pargs.file:

            config = []
            with open(self.app.pargs.file, 'r') as stream:
                try:
                    config = yaml.load(stream)
                except yaml.YAMLError as exc:
                    print(exc)

            self.socket.send_json({
                "command": "up",
                "client": {
                    "user": getpass.getuser(),
                    "hostname": host.gethostname(),
                },
                "data": config
            })

            poll = zmq.Poller()
            poll.register(self.socket, zmq.POLLIN)

            success = False
            while not success:
                sockets = dict(poll.poll(1000))
                if self.socket in sockets:
                    msg = self.socket.recv_string()

                    try:
                        message = json.loads(msg)
                        print(message)
                        if "success" in message:
                            success = message["success"]
                    except ValueError as e:
                        self.print(msg)
                    else:
                        pass  # valid json

            self.socket.close()
            self.context.term()

    def print(self, message, color="green", end="\n"):
        print(colored("===> {message}".format(message=message), color), end=end)