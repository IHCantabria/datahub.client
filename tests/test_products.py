import unittest
from datahub.products import Products


class TestProducts(unittest.TestCase):
    def setUp(self):
        url = "https://datahub.ihcantabria.com/v1/public/Products"

    def test_get_all(self):
        expected_result = 172
        p = Products("https://datahub.ihcantabria.com/v1/public/Products")
        all_products = p.get_all()
        n = len(all_products)

        self.assertEqual(n, expected_result)

    def test_get_all_filter(self):
        expected_result = 121
        p = Products("https://datahub.ihcantabria.com/v1/public/Products")
        all_products = p.get_all(lon_min=-10, lon_max=0, lat_min=40, lat_max=50)
        n = len(all_products)

        self.assertEqual(n, expected_result)

    def test_get_all_filter_partial(self):
        p = Products("https://datahub.ihcantabria.com/v1/public/Products")
        with self.assertRaises(Exception):
            p.get_all(lon_min=-10, lon_max=0, lat_max=50)


if __name__ == "__main__":
    unittest.main()
