import json
import requests

from datahub.config import Config


class Products(object):
    def __init__(self):
        configuration = Config()
        self.url = configuration.URLs["products"]

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
        else:
            raise response.raise_for_status()
        return data

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
