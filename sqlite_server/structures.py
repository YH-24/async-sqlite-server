from yaml import parse, load
from yaml.loader import UnsafeLoader


class DatabaseRow:
    pass


class DatabaseTable:
    pass


class DatabaseFile:
    pass


class DatabaseManager:
    config: dict

    def __init__(self):
        pass

    def config_from_yaml(self, config_dir: str = '../config/'):
        with open(f'{config_dir}/meta.yaml', 'r') as meta_raw:
            parsed = load(meta_raw.read(), UnsafeLoader)

            print(parsed)
        pass

    pass
