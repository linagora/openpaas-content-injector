#!/usr/bin/env python3
import configparser

config = configparser.ConfigParser()

def reinitialize_parser():
    '''Initialize or reinitialize parser to parse a new file'''
    global config
    config = configparser.ConfigParser()

def parse_a_file(path: str):
    'Parse the given file'
    config.read(path)


def get_sections_list():
    'Returns the current sections'
    return config.sections()


def get_section(section: str):
    'Returns a section as a dictionnary'
    return dict(config[section])


def get_item(section: str, key: str):
    'Returns the value attached to key and section'
    return config[section][key]
