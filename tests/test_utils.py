import unittest
from datetime import datetime
from datahub import utils


class TestUtils(unittest.TestCase):
    def test_datetime_to_str(self):
        dt = datetime(2000, 1, 1, 13, 0, 0)
        dt_str = utils.datetime_to_string(dt)
        self.assertEqual("2000-01-01T13:00:00Z", dt_str)

    def test_datetime_to_str_format(self):
        dt = datetime(2000, 1, 1, 13, 0, 0)
        dt_str = utils.datetime_to_string(dt, format="%Y")
        self.assertEqual("2000", dt_str)

    def test_str_to_datetime(self):
        dt_str = "2000-01-01T13:00:00Z"
        dt = utils.string_to_datetime(dt_str)
        self.assertEqual(datetime(2000, 1, 1, 13, 0, 0), dt)

    def test_str_to_datetime_format(self):
        dt_str = "2000-01-01"
        dt = utils.string_to_datetime(dt_str, format="%Y-%m-%d")
        self.assertEqual(datetime(2000, 1, 1), dt)


if __name__ == "__main__":
    unittest.main()
