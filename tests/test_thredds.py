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


if __name__ == "__main__":
    unittest.main()
