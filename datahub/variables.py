import json
import requests

from datahub.config import Config
from datahub.variable import Variable
from datahub import utils

logger = utils.get_logger(__name__)


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
            variables = [Variable(variable_json) for variable_json in data]
        else:
            logger.error(response.raise_for_status())
            raise response.raise_for_status()
        logger.info(f"{len(variables)} variables found")
        return variables

    def get_all_by_product(self, id_product):
        url_variables = (self.url_product_variables).format(id_product=id_product)

        response = requests.get(url_variables)
        if response.ok:
            data = json.loads(response.content)
            variables = [Variable(variable_json) for variable_json in data]
        else:
            response.raise_for_status()
            raise response.raise_for_status()
        logger.info(f"{len(data)} variables found")
        return variables

    def get(self, id_variable):
        url = "{url}/{id}".format(url=self.url_variables, id=id_variable)

        response = requests.get(url)
        if response.ok:
            data = json.loads(response.content)
        else:
            response.raise_for_status()
            raise response.raise_for_status()
        try:
            variable_json = data[0]
            logger.info(f"Variable found, id={variable_json['id']}")
            variable_obj = Variable(variable_json)
            return variable_obj
        except IndexError as ie:
            logger.error(ie)
            return None

    def get_by_product_filtered_by_name(self, product, names):
        url_variables = (self.url_product_variables).format(id_product=product.id)

        response = requests.get(url_variables)
        if response.ok:
            variables_json = json.loads(response.content)
        else:
            response.raise_for_status()
            raise response.raise_for_status()
        filtered_variables = []
        for variable_json in variables_json:
            variable_obj = Variable(variable_json)
            for name in names:
                if variable_obj.nameShort == name:
                    filtered_variables.append(variable_obj)
                elif variable_obj.nameLong == name:
                    filtered_variables.append(variable_obj)
        logger.info(f"{len(filtered_variables)} variables found")
        return filtered_variables
