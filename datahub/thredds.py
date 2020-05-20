from bs4 import BeautifulSoup
import csv
from datetime import datetime, timedelta
from io import StringIO
import json
import requests

from xml.etree import ElementTree


class Catalog(object):
    def __init__(self, product):
        self.urlBase = product["urlBase"]
        self.urlXmlLatest = product["urlXmlLatest"]
        self.urlCatalog = product["urlCatalog"]

    @property
    def url(self):
        return f"{self.urlBase}{self.urlCatalog}"

    @property
    def datasets(self):
        productLatest = requests.get(self.url)
        bxml = productLatest.content

        soup = BeautifulSoup(bxml, "xml")
        services = soup.find_all("service")
        ncssPath = ""
        for service in services:
            if service.attrs["name"] == "ncss":
                ncssPath = service.attrs["base"]
                break

        datasets_xml = soup.find_all('dataset')
        datasets = []
        for dataset_xml in datasets_xml:
            try:
                if dataset_xml.attrs["urlPath"] != "latest.xml":
                    dataset = Dataset(
                        "{dns}{ncss}{dataset}".format(
                            dns=self.urlBase, ncss=ncssPath, dataset=dataset_xml.attrs["urlPath"]
                        )
                    )
                    datasets.append(dataset)

            except KeyError:
                pass       
        
        return datasets

    def download(self, coordinates, dates, variables):
        datasets_for_download = self._get_datasets_with_data(dates)

        outputs = []

        for dataset in datasets_for_download:
            
            ncssUrl = "{0}?var=VMDR&longitude={1}&latitude={2}&time_start={3}&time_end={4}&accept={5}&vertCoord=0.49402499198913574".format(
                dataset.ncss_url,
                coordinates["lon"],
                coordinates["lat"],
                dates["start"],
                dates["end"],
                "xml",
            )
            response = requests.get(ncssUrl)
            csv_text = StringIO(response.text)
            outputs.append(csv)
            if not "Lat/Lon" in response.text:
                csv_reader = csv.reader(csv_text, delimiter=",")
                next(csv_reader)
                with open("output.csv", mode="w", newline="") as output:
                    spamwriter = csv.writer(
                        output, delimiter=";", quoting=csv.QUOTE_MINIMAL
                    )
                    for row in csv_reader:
                        spamwriter.writerow(
                            [
                                row[0],
                                row[1],
                                row[2],
                                float(row[3])
                            ]
                        )
            else:
                print(response.text)
        return "output.csv"

    def _get_datasets_with_data(self, dates):
        dataset_ok = []
        for dataset in self.datasets:
            if (
                dates["start"] < dataset.dates["end"]
                and dates["end"] > dataset.dates["start"]
            ):
                dataset_ok.append(dataset)
        return dataset_ok


class Dataset(object):
    def __init__(self, url):
        self.ncss_url = url

    @property
    def dates(self):
        datasetDetailsGet = requests.get(f"{self.ncss_url}/dataset.xml")
        soup = BeautifulSoup(datasetDetailsGet.content)
        begin = soup.find("TimeSpan").find("begin").text
        end = soup.find("TimeSpan").find("end").text
        dates = {"start": begin, "end": end}
        return dates
