from bs4 import BeautifulSoup
import csv
from datetime import datetime, timedelta
from io import StringIO
import json
import requests
import urllib.request

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

        for dataset in datasets_for_download:
            points.extend(dataset.data(coordinates, dates, variables))
        return points

    def download(self, coordinates, dates, variables, filename, formato="netcdf"):
        datasets_for_download = self._get_datasets_with_data(dates)
        filenames = []
        if len(datasets_for_download) > 1:
            for i, dataset in enumerate(datasets_for_download):
                name = dataset.download(
                    coordinates, dates, variables, f"{filename}{i}", formato
                )
                filenames.append(name)
        elif len(datasets_for_download) > 0:
            dataset = datasets_for_download[0]
            name = dataset.download(coordinates, dates, variables, filename, formato)
            filenames.append(name)
        return filenames

    def _get_datasets_with_data(self, dates):
        dataset_ok = []
        for dataset in self.datasets:
            if (
                dates["start"] < dataset.dates["end"]
                and dates["end"] > dataset.dates["start"]
            ):
                dataset_ok.append(dataset)
        return dataset_ok

    def _coordinates_to_string(self, coordinates):
        text = ""
        if "lat" in coordinates:
            text = f"&longitude={coordinates['lon']}&latitude={coordinates['lat']}"
        else:
            text = f"&north={coordinates['north']}&east={coordinates['east']}&south={coordinates['south']}&west={coordinates['west']}"
        return text


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

    @property
    def extent(self):
        datasetDetailsGet = requests.get(f"{self.ncss_url}/dataset.xml")
        soup = BeautifulSoup(datasetDetailsGet.content, "lxml")
        west = soup.find("latlonbox").find("west").text
        east = soup.find("latlonbox").find("east").text
        north = soup.find("latlonbox").find("north").text
        south = soup.find("latlonbox").find("south").text
        bound = {"east": east, "north": north, "south": south, "west": west}
        return bound

    @property
    def accept_list(self):
        datasetDetailsGet = requests.get(f"{self.ncss_url}/dataset.xml")
        soup = BeautifulSoup(datasetDetailsGet.content, "lxml")
        grid_as_point = soup.find("acceptlist").find("gridaspoint").find_all("accept")
        grid = soup.find("acceptlist").find("gridaspoint").find_all("accept")

        dict_as_point = []
        dict_grid = []

        for accept in grid_as_point:
            dict_as_point.append(accept.text)
        for accept in grid:
            dict_grid.append(accept.text)

        accept_list = {"grid_as_point": dict_as_point, "grid": dict_grid}
        return accept_list

    def data(self, coordinates, dates, variables):
        ncss_coordinates = self._coordinates_to_string(coordinates)
        points = []
        name_variables = self._get_name_variables(variables)
        ncssUrl = "{url}?var={vars}{coordinates}&time_start={start}&time_end={end}&accept={format}".format(
            url=self.ncss_url,
            vars=name_variables,
            coordinates=ncss_coordinates,
            start=dates["start"],
            end=dates["end"],
            format="xml",
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

    def download(self, coordinates, dates, variables, filename, formato="netcdf"):

        ncss_coordinates = self._coordinates_to_string(coordinates)
        name_variables = self._get_name_variables(variables)

        ncssUrl = "{url}?var={vars}{coordinates}&time_start={start}&time_end={end}&accept={format}".format(
            url=self.ncss_url,
            vars=name_variables,
            coordinates=ncss_coordinates,
            start=dates["start"],
            end=dates["end"],
            format=formato,
        )
        urllib.request.urlretrieve(ncssUrl, filename)
        return filename

    def _get_name_variables(self, variables):
        nameShort = []
        for variable in variables:
            nameShort.append(variable["nameShort"])
        return ",".join(nameShort)

    def _coordinates_to_string(self, coordinates):
        text = ""
        if "lat" in coordinates:
            text = f"&longitude={coordinates['lon']}&latitude={coordinates['lat']}"
        else:
            text = f"&north={coordinates['north']}&east={coordinates['east']}&south={coordinates['south']}&west={coordinates['west']}"
        return text
