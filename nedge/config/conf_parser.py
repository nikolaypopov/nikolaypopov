import os
import json
from collections import namedtuple


def dict2namedtuple(dictionary):
    """
    Creates a named tuple from a dictionary to clearer presentation
    of data.

    e.g. {'a': 1, 'b': 2} can be accessible as
    d.a and d.b instead of d['a'] and d['b']

    :param dictionary: a dict to convert to a named tuple
    :return: namedtuple

    """

    for key, value in dictionary.items():
        if isinstance(value, dict):
            dictionary[key] = dict2namedtuple(value)
    return namedtuple('GenericDict', dictionary.keys())(**dictionary)


with open(os.path.dirname(os.path.abspath(__file__))
                  + '/config.json', 'r') as f:
    config_dict = json.load(f)
    config = dict2namedtuple(config_dict)

with open(os.path.dirname(os.path.abspath(__file__))
                  + '/test_list.json', 'r') as f:
    test_list = json.load(f)
