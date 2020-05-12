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
        self.assertIsNotNone(variable)

    def test_get_ko(self):
        variables = Variables()
        variable = variables.get(-1)
        self.assertIsNone(variable)


if __name__ == "__main__":
    unittest.main()
