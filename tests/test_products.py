import unittest
from datahub.products import Products


class TestProducts(unittest.TestCase):
    def setUp(self):
        self.id = 198

    def test_get_product(self):
        product = Products().get(self.id)
        self.assertIsNotNone(product)

    def test_get_product_invalid_id(self):
        id = -5
        p = Products()
        product = p.get(id)
        self.assertIsNone(product)

    def test_get_all(self):
        p = Products()
        all_products = p.get_all()
        n = len(all_products)
        self.assertGreater(n, 1)

    def test_get_all_filter(self):
        p = Products()
        all_products = p.get_all(lon_min=-10, lon_max=0, lat_min=40, lat_max=50)
        n = len(all_products)
        self.assertGreater(n, 1)

    def test_get_all_filter_partial(self):
        p = Products()
        with self.assertRaises(Exception):
            p.get_all(lon_min=-10, lon_max=0, lat_max=50)

    def test_get_variables(self):
        p = Products()
        product = p.get(self.id)
        variables = p.get_variables(product)
        n = len(variables)
        self.assertEqual(n, 3)

    def test_get_variables_no_product(self):
        invalid_product = {}
        p = Products()
        with self.assertRaises(Exception):
            p.get_variables(invalid_product)

    def test_filter_name(self):
        match = Products().filter(name="datahubTests")
        self.assertEqual(match[0].id, self.id)

    def test_filter_name_partial(self):
        match = Products().filter(name="datahub")
        self.assertEqual(match[0].id, self.id)

    def test_filter_name_ko(self):
        match = Products().filter(name="datahub_ko")
        self.assertEqual(len(match), 0)

    def test_filter_alias(self):
        match = Products().filter(alias="Cantabrico")
        self.assertGreaterEqual(len(match), 1)

    def test_filter_alias_partial(self):
        match = Products().filter(alias="Cantab")
        self.assertGreaterEqual(len(match), 1)

    def test_filter_alias_ko(self):
        match = Products().filter(alias="test_ko")
        self.assertEqual(len(match), 0)


if __name__ == "__main__":
    unittest.main()
