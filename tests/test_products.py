import unittest
from datahub.products import Products


class TestProducts(unittest.TestCase):
    def test_get_product(self):
        id = 7
        p = Products()
        product = p.get(id)
        self.assertEqual(id, product["id"])

    def test_get_product_invalid_id(self):
        id = -5
        p = Products()
        product = p.get(id)
        self.assertIsNone(product)

    def test_get_all(self):
        expected_result = 172
        p = Products()
        all_products = p.get_all()
        n = len(all_products)

        self.assertEqual(n, expected_result)

    def test_get_all_filter(self):
        expected_result = 121
        p = Products()
        all_products = p.get_all(lon_min=-10, lon_max=0, lat_min=40, lat_max=50)
        n = len(all_products)

        self.assertEqual(n, expected_result)

    def test_get_all_filter_partial(self):
        p = Products()
        with self.assertRaises(Exception):
            p.get_all(lon_min=-10, lon_max=0, lat_max=50)

    def test_get_variables(self):
        id = 7
        p = Products()
        variables = p.get_variables(id)
        n = len(variables)
        self.assertEqual(n, 5)

    def test_get_variables_no_product(self):
        id = -5
        p = Products()
        variables = p.get_variables(id)
        n = len(variables)
        self.assertEqual(n, 0)


if __name__ == "__main__":
    unittest.main()
