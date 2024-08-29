import configparser
from typing import List


"""
    Config utility functions
    
    Config utility is a collection of useful methods for interacting 
    with .ini configuration files.

    Note: this file was originally written by Dylan Dutton (@astrodyl on Github)
"""


def read(path: str) -> configparser.ConfigParser:
    """ Reads the telescope config file.

    :param path: path to the config file
    :return: configparser.ConfigParser object
    """
    config = configparser.ConfigParser()
    config.read(path)
    return config


def get(config: configparser.ConfigParser, section: str, option: str) -> str | None:
    """ Retrieves the key from the provided config file and section.
    Returns None if the key is not found.

    :param config: configparser.ConfigParser object
    :param section: section of the config file
    :param option: option for the section
    :return: the value of the key or None
    """
    try:
        return config.get(section, option)
    except configparser.NoSectionError:
        return None
    except configparser.NoOptionError:
        return None


def expected_type(value: str) -> str | float | bool | List | None:
    """ Converts the parsed config value into the expected type.

    :param value: parsed config value
    :return: the parsed config value in its expected type
    """
    if value is None:
        return

    try:  # Return a number
        if (number := float(value)) % 1.0 == 0.0:
            return int(number)
        return float(number)

    except ValueError:  # Return a boolean
        if value.lower() == 'true':
            return True
        if value.lower() == 'false':
            return False

        if ',' in value:  # Return a list
            return [expected_type(v.strip()) for v in value.split(',')]

        return value  # Return a string
