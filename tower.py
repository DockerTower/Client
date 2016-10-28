import signal

from cement.core.exc import CaughtSignal
from cement.core.foundation import CementApp

from src.controller.app_controller import AppController
from src.controller.server_controller import ServerController
from src.controller.tower_controller import TowerController


class Tower(CementApp):
    class Meta:
        label = 'tower'
        handlers = [
            TowerController,
            ServerController,
            AppController
        ]


def main():
    with Tower() as app:
        try:
            app.run()
        except CaughtSignal as e:
            if e.signum == signal.SIGINT:
                print("Stoping...")


if __name__ == '__main__':
    main()
