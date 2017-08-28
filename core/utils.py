import os
import json


def load_json(path):
    path = os.path.normpath(path)
    with open(path, 'rb') as stream:
        return json.load(stream)
