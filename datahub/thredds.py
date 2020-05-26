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

        datasets_xml = soup.find_all("dataset")
        datasets = []
        for dataset_xml in datasets_xml:
            if (
                dataset_xml.has_attr("urlPath")
                and dataset_xml.attrs["urlPath"] != "latest.xml"
            ):
                dataset = Dataset(
                    "{dns}{ncss}{dataset}".format(
                        dns=self.urlBase,
                        ncss=ncssPath,
                        dataset=dataset_xml.attrs["urlPath"],
                    )
                )
                datasets.append(dataset)

        return datasets

    def data(self, coordinates, dates, variables):
        datasets_for_download = self._get_datasets_with_data(dates)

        points = []
        name_variables = self._get_name_variables(variables)
        for dataset in datasets_for_download:

            ncssUrl = "{url}?var={vars}&longitude={lon}&latitude={lat}&time_start={start}&time_end={end}&accept={format}".format(
                url=dataset.ncss_url,
                vars=name_variables,
                lon=coordinates["lon"],
                lat=coordinates["lat"],
                start=dates["start"],
                end=dates["end"],
                format="xml"
            )
            response = requests.get(ncssUrl)

            soup = BeautifulSoup(response.content, "xml")
            points_xml = soup.find_all("point")

            for point_xml in points_xml:
                point = {}
                data_tags_xml = point_xml.find_all("data")
                for data_xml in data_tags_xml:
                    point.update({data_xml.attrs["name"]: data_xml.text})
                points.append(point)
        return points

    def _get_datasets_with_data(self, dates):
        dataset_ok = []
        for dataset in self.datasets:
            if (
                dates["start"] < dataset.dates["end"]
                and dates["end"] > dataset.dates["start"]
            ):
                dataset_ok.append(dataset)
        return dataset_ok

    def _get_name_variables(self, variables):
        nameShort = []
        for variable in variables:
            nameShort.append(variable["nameShort"])
        return ",".join(nameShort)


class Dataset(object):
    def __init__(self, url):
        self.ncss_url = url

    @property
    def dates(self):
        datasetDetailsGet = requests.get(f"{self.ncss_url}/dataset.xml")
        soup = BeautifulSoup(datasetDetailsGet.content, "lxml")
        begin = soup.find("timespan").find("begin").text
        end = soup.find("timespan").find("end").text
        dates = {"start": begin, "end": end}
        return dates
