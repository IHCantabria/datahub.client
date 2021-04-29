import json
import os

from dotenv import dotenv_values

from datahub import utils

logger = utils.get_logger(__name__)


class Config(object):
    def __init__(self):
        try:
            with open(
                f"{os.path.dirname(__file__)}/config.{dotenv_values('.env')['ENV']}.json"
            ) as f:
                data = json.load(f)
                self.URLs = data["URLs"]
                self.__restrictAccess = data["restrictAccess"]
        except Exception as ex:
            logger.error(ex)

    def get_auth_for_catalog(self, catalog_id):
        for auth in self.__restrictAccess:
            if auth["catalog"] == catalog_id:
                return auth
        return None

    @classmethod
    def get_auth_for_opendap(self, url, auth):
        # ToDo: Test
        if "http://" in url:
            return url.replace("http://", f"http://{auth.username}:{auth.password}@")
        elif "https://" in url:
            return url.replace("https://", f"https://{auth.username}:{auth.password}@")
