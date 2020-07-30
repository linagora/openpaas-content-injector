import configparser


config = configparser.ConfigParser()

def reinitialize_parser():
    global config
    config = configparser.ConfigParser()

def parse_a_file(path:str):
    config.read(path)


def get_sections_list():
    return config.sections()


def get_section(section:str):
    return dict(config[section])


def get_item(section:str, key:str):
    return config[section][key]