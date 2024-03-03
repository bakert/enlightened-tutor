from configparser import ConfigParser

CONFIG = ConfigParser()
CONFIG.read("config.ini")


def get(section: str, key: str) -> str:
    return CONFIG[section][key]
