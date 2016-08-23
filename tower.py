from cement.core.foundation import CementApp
from controller.tower_controller import TowerController
from controller.app_controller import AppController
from controller.agent_controller import AgentController


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
