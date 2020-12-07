import unittest
from datahub.variables import Variables


class TestVariables(unittest.TestCase):
    def setUp(self):
        self.id_variable = 17

    def test_get_all_by_product(self):
        expected_result = 5
        id_product = 7
        v = Variables()
        all_variables = v.get_all_by_product(id_product)
        n = len(all_variables)

        self.assertEqual(n, expected_result)

    def test_get(self):
        variables = Variables()
        variable = variables.get(self.id_variable)
        self.assertEqual(variable.id, self.id_variable)

    def test_get_ko(self):
        variables = Variables()
        variable = variables.get(-1)
        self.assertIsNone(variable)

    def test_get_by_product_filtered_by_name(self):
        names = ["thetao", "so"]
        product = {"id": 7}
        variables = Variables()
        filtered_variables = variables.get_by_product_filtered_by_name(product, names)
        n = len(filtered_variables)
        self.assertEqual(n, len(names))


if __name__ == "__main__":
    unittest.main()
