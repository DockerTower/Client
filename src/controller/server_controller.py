from cement.core.controller import CementBaseController, expose
import zmq
import uuid
import getpass
import socket as host
from termcolor import colored


class ServerController(CementBaseController):
    class Meta:
        label = 'agent'
        stacked_on = 'base'
        stacked_type = 'nested'
        description = "Agents"

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.DEALER)
        self.socket.identity = str(uuid.uuid1()).encode('ascii')
        self.socket.connect('tcp://localhost:5570')

    @expose(hide=True)
    def default(self):
        self.app.args.print_help()

    @expose(help="Register agent")
    def register(self):
        self.socket.send_json({
            "command": "agent.register",
            "client": {
                "user": getpass.getuser(),
                "hostname": host.gethostname(),
            }
        })

        poll = zmq.Poller()
        poll.register(self.socket, zmq.POLLIN)

        for i in range(100):
            sockets = dict(poll.poll(1000))
            if self.socket in sockets:
                msg = self.socket.recv_string()
                self.print(msg)

        self.socket.close()
        self.context.term()

    def print(self, message, color="green", end="\n"):
        print(colored("===> {message}".format(message=message), color), end=end)