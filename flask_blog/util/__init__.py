import os
import json

def load_json(path):
    if os.path.isfile(path):
        with open(path) as infile:
            return json.load(infile)
    return None
