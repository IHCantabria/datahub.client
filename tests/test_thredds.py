import unittest
from datahub.thredds import Catalog


class TestCatalog(unittest.TestCase):
    def setUp(self):
        self.id = 7
        self.product = {
            "urlBase": "https://ihthredds.ihcantabria.com",
            "urlXmlLatest": "/thredds/catalog/copernicus/CMEMS/GLOBAL_REANALYSIS_WAV_001_032/latest.xml",
            "urlCatalog": "/thredds/catalog/copernicus/CMEMS/GLOBAL_REANALYSIS_WAV_001_032/catalog.xml",
        }
        self.variables = [
            {
                "id": 317,
                "nameShort": "VTPK",
                "nameLong": "Wave period at spectral peak / peak period (Tp)",
                "alias": "Wave period at spectral peak / peak period (Tp)",
                "units": "s",
                "idVariableTypes": 1,
                "scaleFactor": 0.01,
                "offset": 0.0,
                "productVariable": [],
            },
            {
                "id": 316,
                "nameShort": "VMDR",
                "nameLong": "Mean wave direction from (Mdir)",
                "alias": "Mean wave direction from (Mdir)",
                "units": "\u00ba",
                "idVariableTypes": 1,
                "scaleFactor": 0.01,
                "offset": 180.0,
                "productVariable": [],
            },
        ]

    def test_get_datasets(self):
        c = Catalog(self.product)
        n = len(c.datasets)
        self.assertEqual(n, 1)

    def test_data(self):
        coordinates = {"lat": 43.456, "lon": -2.883}
        dates = {"start": "2018-12-24T00:00:00", "end": "2018-12-24T12:00:00"}
        c = Catalog(self.product)
        points = c.data(coordinates, dates, self.variables)
        n = len(points)
        self.assertEqual(n, 5)

    def test_download_extent(self):
        coordinates = {"north": 43.456, "east": -2.883, "south": 43, "west": -3}
        dates = {"start": "2018-12-24T00:00:00", "end": "2018-12-24T12:00:00"}
        filename = "/tmp/test.nc"
        c = Catalog(self.product)
        filenames = c.download(coordinates, dates, self.variables, filename)
        self.assertIn(filename, filenames)
    
    def test_download_csv_point(self):
        coordinates = {"lon": 43.456, "lat": -2.883}
        dates = {"start": "2018-12-24T00:00:00", "end": "2018-12-24T12:00:00"}
        filename = "/tmp/test.csv"
        c = Catalog(self.product)
        filenames = c.download(coordinates, dates, self.variables, filename, "csv")
        self.assertIn(filename, filenames)

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


if __name__ == "__main__":
    unittest.main()
