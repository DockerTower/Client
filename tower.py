from cement.core.foundation import CementApp
from src.controller.agent_controller import AgentController
from src.controller.app_controller import AppController
from src.controller.tower_controller import TowerController
from src.controller.server_controller import ServerController


class Tower(CementApp):
    class Meta:
        label = 'tower'
        handlers = [
            TowerController,
            AgentController,
            ServerController,
            AppController
        ]


def main():
    with Tower() as app:
        app.run()


if __name__ == '__main__':
    main()
