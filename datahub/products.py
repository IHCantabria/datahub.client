import json
import requests


class Products(object):
    url = "https://datahub.ihcantabria.com/v1/public/Products"

    def get_all(self):
        response = requests.get(self.url)
        if response.ok:
            data = json.loads(response.content)
        else:
            raise response.raise_for_status()
        return data
