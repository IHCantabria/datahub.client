import unittest
from datahub.products import Products
from datahub.product import Product


class TestProduct(unittest.TestCase):
    def setUp(self):
        self.id = 7

    def test_get_product(self):

        p = Products()
        obj_json = p.get(self.id)
        product = Product(obj_json)
        self.assertEqual(self.id, product.id)

    def test_get_product_by_name(self):
        name = "GLOBAL_REANALYSIS_PHY_001_030"
        p = Products()
        product = Product(p.get_by_name_alias(name))
        self.assertIsNotNone(product)

    def test_get_product_by_alias(self):
        alias = "GLOBAL REANALYSIS PHY 001 030"
        p = Products()
        product = Product(p.get_by_name_alias(alias))
        self.assertIsNotNone(product)

    def test_get_all(self):
        expected_result = 172
        p = Products()
        all_products = p.get_all()
        product_all = []
        for product_json in all_products:
            product = Product(product_json)
            product_all.append(product)
        n = len(product_all)

        self.assertEqual(n, expected_result)

    def test_latest_ncss(self):
        url_expected = "http://193.144.208.177:8080/thredds/ncss/grid/copernicus/CMEMS/GLOBAL_REANALYSIS_PHY_001_030/GLOBAL_REANALYSIS_PHY_001_030.nc"

        p = Products()
        obj_json = p.get(self.id)
        product = Product(obj_json)
        url = product._getLatestNcssUrl()
        self.assertEqual(url_expected, url)

    def test_dates_latest(self) :
        p = Products()
        obj_json = p.get(self.id)
        product = Product(obj_json)
        url = product._getLatestNcssUrl()
        dates = product._get_dates(url)
        self.assertIsNotNone(dates["start"])
        self.assertIsNotNone(dates["end"])
if __name__ == "__main__":
    unittest.main()

