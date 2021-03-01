import unittest
import xarray
from datahub.products import Products
from datahub.catalog import Catalog
from datahub import utils


class TestCatalog(unittest.TestCase):
    def setUp(self):
        self.id = 198
        self.product = Products().get(198)
        self.start = utils.string_to_datetime("2020-11-24T00:00:00Z")
        self.end = utils.string_to_datetime("2020-12-24T12:00:00Z")
        self.dates = {"start": self.start, "end": self.end}
        self.coordinates_point = {"lat": 43.456, "lon": -2.883}
        self.coordinates_area = {
            "north": 43.456,
            "east": -2.883,
            "south": 43,
            "west": -3,
        }

    def test_get_datasets(self):
        c = Catalog(self.product)
        n = len(c.datasets)
        self.assertEqual(n, 4)

    def test_data_latest(self):
        c = Catalog(self.product)
        variables = self.product.variables
        points = c.latest.data(self.coordinates_point, self.dates, variables)
        n = len(points)
        self.assertEqual(n, 81)

    # def test_data_protected(self):
    #     coordinates = {"lat": 0.2, "lon": 0.2}
    #     dates = None
    #     c = Catalog(self.product_protected)
    #     points = c.data(coordinates, dates, self.variables_test)
    #     n = len(points)
    #     self.assertEqual(n, 1)

    # def test_data_protected_auth_parameter(self):
    #     coordinates = {"lat": 0.2, "lon": 0.2}
    #     dates = None
    #     auth = ("test", "test99%")
    #     c = Catalog(self.product_protected, auth=auth)
    #     points = c.data(coordinates, dates, self.variables_test)
    #     n = len(points)
    #     self.assertEqual(n, 1)

    def test_download_extent_latest(self):
        filename = "/tmp/test.nc"
        c = Catalog(self.product)
        variables = self.product.variables
        filenames = c.latest.download(
            filename, variables, coordinates=self.coordinates_area, dates=self.dates
        )
        dataset = xarray.open_dataset(filename)
        self.assertIsNotNone(dataset)
        dataset.close()
        self.assertIn(filename, filenames)

    def test_open_with_xarray(self):
        catalog = Catalog(self.product)
        ds = catalog.open_xarray_conn()
        self.assertIsNotNone(ds)
        ds.close()

    def test_download_point(self):
        filename = "/tmp/test-point.nc"
        c = Catalog(self.product)
        variables = self.product.variables
        filenames = c.latest.download(
            filename,
            variables,
            coordinates=self.coordinates_point,
            dates=self.dates,
        )

        dataset = xarray.open_dataset(filename)
        self.assertIsNotNone(dataset)
        dataset.close()
        self.assertIn(filename, filenames)

    def test_download_csv_point_latest(self):
        filename = "/tmp/test.csv"
        c = Catalog(self.product)
        variables = self.product.variables
        filenames = c.latest.download(
            filename,
            variables,
            coordinates=self.coordinates_point,
            dates=self.dates,
            formato="csv",
        )
        self.assertIn(filename, filenames)

    def test_download_raw(self):
        local_path = "/tmp/test.nc"
        catalog = Catalog(Products().get(8))
        dataset = catalog.latest
        path = dataset.download_raw(local_path)
        self.assertEqual(local_path, path)

    def test_get_extent_dataset(self):
        c = Catalog(self.product)
        datasets = c.datasets
        extent = datasets[0].extent
        self.assertIsNotNone(extent["north"])

    def test_accept_list(self):
        c = Catalog(self.product)
        datasets = c.datasets
        accept_list = datasets[0].accept_list
        self.assertIn("grid", accept_list)
        self.assertIn("xml", accept_list["grid"])

    # def test_is_protected(self):
    #     c = Catalog(self.product_protected)
    #     protected = c.is_protected
    #     self.assertTrue(protected)


if __name__ == "__main__":
    unittest.main()
