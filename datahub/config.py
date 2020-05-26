import json
import os


class Config(object):
    def __init__(self):
        with open(f"{os.path.dirname(__file__)}/config.json") as f:
            data = json.load(f)
            self.URLs = data["URLs"]
