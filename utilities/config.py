import yaml


class ConfigReader():
    def __init__(self, mode, source):
        if mode == 'local':
            self.config = yaml.load(open(source))

    def get_config(self, key_path):
        return reduce(lambda d, k: d[k], key_path, self.config)
