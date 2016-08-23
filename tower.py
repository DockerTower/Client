from cement.core.foundation import CementApp
from src.controller.agent_controller import AgentController
from src.controller.app_controller import AppController
from tower_controller import TowerController


class Tower(CementApp):
    class Meta:
        label = 'tower'
        handlers = [
            TowerController,
            AgentController,
            AppController
        ]


def main():
    with Tower() as app:
        app.run()


if __name__ == '__main__':
    main()
