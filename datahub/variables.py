import json
import requests

from datahub.config import Config


class Variables(object):
    url_variables = None
    url_product_variables = None

    def __init__(self):
        configuration = Config()
        self.url_variables = configuration.URLs["variables"]
        self.url_product_variables = configuration.URLs["product_variables"]

    def get_all(self):
        response = requests.get(self.url_variables)
        if response.ok:
            data = json.loads(response.content)
        else:
            raise response.raise_for_status()
        return data

    def get_all_by_product(self, id_product):
        url_variables = (self.url_product_variables).format(id_product=id_product)

        response = requests.get(url_variables)
        if response.ok:
            data = json.loads(response.content)
        else:
            raise response.raise_for_status()
        return data

    def get(self, id_variable):
        url = f"{self.url_variables}/{id_variable}"

        response = requests.get(url)
        if response.ok:
            data = json.loads(response.content)
        else:
            raise response.raise_for_status()
        try:
            variable_json = data[0]
            return variable_json
        except IndexError:
            return None
