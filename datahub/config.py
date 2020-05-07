import json


class Config(object):
    def __init__(self):
        with open("config.json") as f:
            data = json.load(f)
            self.URLs = data["URLs"]
