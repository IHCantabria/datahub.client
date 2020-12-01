import json
import requests

from datahub.config import Config
from datahub.product import Product
from datahub import utils

logger = utils.get_logger(__name__)


class Products(object):
    url = None

    def __init__(self):
        configuration = Config()
        self.url = configuration.URLs["products"]

    def get(self, id_product):
        url_products = "{url}/{id}".format(url=self.url, id=id_product)

        response = requests.get(url_products)
        if response.ok:
            data = json.loads(response.content)
        else:
            logger.error(response.raise_for_status())
            raise response.raise_for_status()
        try:
            product = Product(data[0])
            logger.info(f"Product found, {product}")
            return product
        except IndexError as ie:
            logger.error(ie)
            return None

    def filter(self, name=None, alias=None):
        products = self.get_all()
        products_match = []
        for product in products:

            if name and name.upper() in product.name.upper():
                logger.info(f"Product found, id={product}")
                products_match.append(product)
            elif alias and alias.upper() in product.alias.upper():
                logger.info(f"Product found, id={product}")
                products_match.append(product)
        return products_match

    def get_all(self, lon_min=None, lat_min=None, lon_max=None, lat_max=None):
        params = self._set_filters(lon_min, lat_min, lon_max, lat_max)

        if not self._check_there_are_all_coors(params):
            raise Exception(
                "lon_min, lon_max, lat_min and lat_max are required for filter"
            )
        url_products = f"{self.url}?{'&'.join(params)}"

        response = requests.get(url_products)
        if response.ok:
            data = json.loads(response.content)
            products = [Product(product_json) for product_json in data]
        else:
            logger.error(response.raise_for_status())
            raise response.raise_for_status()

        logger.info(f"{len(products)} products found")
        return products

    def get_variables(self, product, var_names=None):
        url_products = "{url}/{id}/Variables".format(url=self.url, id=str(product.id))

        response = requests.get(url_products)
        if response.ok:
            result = json.loads(response.content)
            if var_names:
                data = self._filter_variables(result, var_names)
            else:
                data = result
        else:
            logger.error(response.raise_for_status())
            raise response.raise_for_status()
        logger.info(f"{len(data)} variables found")
        return data

    def _filter_variables(self, variables, var_names):
        variables_ok = []
        for variable in variables:
            if variable.nameShort in var_names:
                variables_ok.append(variable)
        return variables_ok

    def _set_filters(self, lon_min, lat_min, lon_max, lat_max):
        params = []
        if lon_min is not None:
            params.append(f"xMin={lon_min}")
        if lat_min is not None:
            params.append(f"yMin={lat_min}")
        if lon_max is not None:
            params.append(f"xMax={lon_max}")
        if lat_max is not None:
            params.append(f"yMax={lat_max}")
        return params

    def _check_there_are_all_coors(self, params):

        n = len(params)
        if n > 0 and n != 4:
            return False
        return True
