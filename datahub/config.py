import json
import os

from datahub import utils

logger = utils.get_logger(__name__)


class Config(object):
    def __init__(self):
        try:
            with open(f"{os.path.dirname(__file__)}/config.json") as f:
                data = json.load(f)
                self.URLs = data["URLs"]
        except Exception as ex:
            logger.error(ex)
