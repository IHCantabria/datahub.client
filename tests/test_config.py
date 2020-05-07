import unittest
from datahub.config import Config


class TestConfig(unittest.TestCase):
    def test_load(self):
        configuration = Config()

        self.assertGreater(len(configuration.URLs), 0)


if __name__ == "__main__":
    unittest.main()
