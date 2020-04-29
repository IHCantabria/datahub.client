import unittest
from datahub.products import Products

class TestProducts(unittest.TestCase):
    def test_get_all(self):
        expected_result = 172
        p = Products()
        all_products = p.get_all()
        n = len(all_products)

        self.assertEqual(n, expected_result)


if __name__ == "__main__":
    unittest.main()
