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
                self.__restrictAccess = data["restrictAccess"]
        except Exception as ex:
            logger.error(ex)

    def get_auth_for_catalog(self, catalog_name):
        for auth in self.__restrictAccess:
            if auth["catalog"] == catalog_name:
                return auth
        return None
