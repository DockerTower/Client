import os
import yaml


class Config(object):
    def __init__(self, file):
        self.file = file

    def save(self, config):
        if os.path.isfile(self.file):
            with open(self.file, 'w') as f:
                return yaml.dump(config, f, default_flow_style=False)

    def open(self):
        if os.path.isfile(self.file):
            with open(self.file, 'r') as f:
                return yaml.load(f) or {}
