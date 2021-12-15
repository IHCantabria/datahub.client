import json
import os

from dotenv import dotenv_values

from datahub import utils

logger = utils.get_logger(__name__)


class Config(object):
    def __init__(self):
        try:

            self.URLs = {
                "products": "{url}/v1/public/Products".format(
                    url=dotenv_values(".env")["DATAHUB_API_URL"]
                ),
                "product_variables": dotenv_values(".env")["DATAHUB_API_URL"]
                + "/v1/public/Products/{id_product}/Variables",
                "variables": "{url}/v1/public/Variables".format(
                    url=dotenv_values(".env")["DATAHUB_API_URL"]
                ),
            }
            try:
                self.__restrictAccess = json.loads(
                    dotenv_values(".env")["DATAHUB_SECRET_AUTH"]
                )
            except:
                self.__restrictAccess = []
        except Exception as ex:
            logger.error(ex)
            raise

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
