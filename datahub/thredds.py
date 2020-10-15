from bs4 import BeautifulSoup
import csv
from datetime import datetime, timedelta
from io import StringIO
import json
import math
import os
import requests
import urllib.request
import xarray

from xml.etree import ElementTree

from datahub.config import Config
from datahub import utils

logger = utils.get_logger(__name__)


class Catalog(object):
    def __init__(self, product):
        self.urlBase = product["urlBase"]
        self.urlXmlLatest = product["urlXmlLatest"]
        self.urlCatalog = product["urlCatalog"]

        configuration = Config()
        self.auth = ()
        auth_json = configuration.get_auth_for_catalog(product["name"])

        if auth_json:
            from requests.auth import HTTPBasicAuth

            self.auth = HTTPBasicAuth(auth_json["user"], auth_json["password"])
            logger.debug("Using auth")

    @property
    def url(self):
        url = f"{self.urlBase}{self.urlCatalog}"
        logger.debug(f"url={url}")
        return url

    @property
    def datasets(self):
        productLatest = requests.get(self.url, auth=self.auth)
        bxml = productLatest.content

        soup = BeautifulSoup(bxml, "xml")
        services = soup.find_all("service")
        ncssPath = ""
        httpserver = ""
        for service in services:
            if service.attrs["name"] == "ncss":
                ncssPath = service.attrs["base"]
            if service.attrs["name"] == "http":
                httpserver = service.attrs["base"]
        logger.debug(f"ncssPath={ncssPath}")
        datasets_xml = soup.find_all("dataset")
        datasets = []
        for dataset_xml in datasets_xml:
            if (
                dataset_xml.has_attr("urlPath")
                and dataset_xml.attrs["urlPath"] != "latest.xml"
            ):
                urlPath = "{dns}{ncss}{dataset}".format(
                    dns=self.urlBase,
                    ncss=ncssPath,
                    dataset=dataset_xml.attrs["urlPath"],
                )
                url_httpserver = "{dns}{httpserver}{dataset}".format(
                    dns=self.urlBase,
                    httpserver=httpserver,
                    dataset=dataset_xml.attrs["urlPath"],
                )
                name = dataset_xml.attrs["name"]
                id = dataset_xml.attrs["ID"]
                dataset = Dataset(name, id, urlPath, url_httpserver, self.auth)
                datasets.append(dataset)
        logger.info(f"{len(datasets)} datasets found")
        return datasets

    def data(self, coordinates, dates, variables):
        datasets_for_download = self._get_datasets_with_data(dates)
        points = []

        for dataset in datasets_for_download:
            points.extend(dataset.data(coordinates, dates, variables))
        logger.info(f"{len(points)} points found")
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
        if formato == "netcdf" and len(coordinates.keys()) == 2:
            self._fix_netcdf(filename, variables, dates)
        logger.info("downloaded completed in {names}".format(names=",".join(filenames)))
        return filenames

    def _fix_netcdf(self, filename, variables, dates):
        """
        Thredds doesn't write offset, scale factor and time when we request data for a point.
        """
        logger.debug(f"fix netcdf variables: {filename}")
        dataset = xarray.open_dataset(filename)
        for variable in variables:
            logger.debug(
                "Variable {name}: add_offset={offset}, scale_factor={scaleFactor}, date start={start}".format(
                    name=variable["nameShort"],
                    offset=variable["offset"],
                    scaleFactor=variable["scaleFactor"],
                    start=dates["start"],
                )
            )
            dataset.variables[variable["nameShort"]].attrs["units"] = variable["offset"]
            dataset.variables[variable["nameShort"]].attrs["add_offset"] = variable[
                "offset"
            ]
            dataset.variables[variable["nameShort"]].attrs["scale_factor"] = variable[
                "scaleFactor"
            ]
            dataset.variables["time"].encoding[
                "units"
            ] = f"hours since {dates['start']}"
        dataset.swap_dims({"obs": "time"})
        dataset.to_netcdf(f"{filename}-new.nc")
        dataset.close()
        os.remove(filename)
        os.rename(f"{filename}-new.nc", filename)
        logger.debug("netcdf is fixed")

    def _get_datasets_with_data(self, dates):
        dataset_ok = []
        for dataset in self.datasets:
            try:
                if not dates:
                    dataset_ok.append(dataset)
                elif not dates["start"] and dates["end"] > dataset.dates["start"]:
                    dataset_ok.append(dataset)
                elif not dates["end"] and dates["start"] < dataset.dates["end"]:
                    dataset_ok.append(dataset)
                elif (
                    dates["start"]
                    and dates["end"]
                    and dates["start"] < dataset.dates["end"]
                    and dates["end"] > dataset.dates["start"]
                ):
                    dataset_ok.append(dataset)
            except TypeError:
                raise Exception("Dataset doesn't contain date period")
        return dataset_ok

    def _coordinates_to_string(self, coordinates):
        text = ""
        if "lat" in coordinates:
            text = f"&longitude={coordinates['lon']}&latitude={coordinates['lat']}"
        else:
            text = f"&north={coordinates['north']}&east={coordinates['east']}&south={coordinates['south']}&west={coordinates['west']}"
        logger.debug(f"coordinates={coordinates}")
        return text


class Dataset(object):
    def __init__(self, name, id, url, url_httpserver, auth):
        self.name = name
        self.id = id
        # self.restrictAccess = restrictAccess
        self.ncss_url = url
        self.http_url = url_httpserver
        self.auth = auth

    """
    -32767 is the most common value for _fillValue. However some variable can have another value. 
    It's hardcode because the data is not available in datahub yet.
    TODO: When the value is in datahub, use that.
    """

    @property
    def _fillValue(self):
        return -32767

    @property
    def dates(self):
        datasetDetailsGet = requests.get(f"{self.ncss_url}/dataset.xml", auth=self.auth)
        soup = BeautifulSoup(datasetDetailsGet.content, "lxml")
        try:
            begin = soup.find("timespan").find("begin").text
        except AttributeError:
            begin = None
        try:
            end = soup.find("timespan").find("end").text
        except AttributeError:
            end = None
        dates = {"start": begin, "end": end}
        logger.debug(f"dates={dates}")
        return dates

    @property
    def extent(self):
        datasetDetailsGet = requests.get(f"{self.ncss_url}/dataset.xml", auth=self.auth)
        soup = BeautifulSoup(datasetDetailsGet.content, "lxml")
        west = soup.find("latlonbox").find("west").text
        east = soup.find("latlonbox").find("east").text
        north = soup.find("latlonbox").find("north").text
        south = soup.find("latlonbox").find("south").text
        bound = {"east": east, "north": north, "south": south, "west": west}
        logger.debug(f"boud={bound}")
        return bound

    @property
    def accept_list(self):
        datasetDetailsGet = requests.get(f"{self.ncss_url}/dataset.xml", auth=self.auth)
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
        logger.debug(f"accept_list={accept_list}")
        return accept_list

    def __create_time_string_ncss(self, dates):
        time_start = ""
        time_end = ""
        if dates and dates["start"]:
            time_start = "&time_start={start}".format(start=dates["start"])
        if dates and dates["end"]:
            time_end = "&time_end={end}".format(end=dates["end"])
        return time_start, time_end

    def data(self, coordinates, dates, variables):
        ncss_coordinates = self._coordinates_to_string(coordinates)
        points = []
        name_variables = self._get_name_variables(variables)

        time_start, time_end = self.__create_time_string_ncss(dates)

        ncssUrl = "{url}?var={vars}{coordinates}{time_start}{time_end}&accept={format}".format(
            url=self.ncss_url,
            vars=name_variables,
            coordinates=ncss_coordinates,
            time_start=time_start,
            time_end=time_end,
            format="xml",
        )
        response = requests.get(ncssUrl, auth=self.auth)
        soup = BeautifulSoup(response.content, "xml")
        points_xml = soup.find_all("point")
        for point_xml in points_xml:
            point = {}
            data_tags_xml = point_xml.find_all("data")
            for data_xml in data_tags_xml:
                real_value = self._real_value(
                    data_xml.attrs["name"], data_xml.text, variables
                )
                point.update({data_xml.attrs["name"]: real_value})
            points.append(point)
        return points

    def _real_value(self, name, value, variables):
        for variable in variables:
            if variable["nameShort"] == name:
                if float(value) == self._fillValue:
                    value = None
                else:
                    if "scaleFactor" in variable:
                        value = float(value) * variable["scaleFactor"]
                    if "offset" in variable:
                        value = float(value) + variable["offset"]
        return value

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
        logger.debug(f"ncssUrl={ncssUrl}")
        urllib.request.urlretrieve(ncssUrl, filename)
        logger.debug(f"dataset downloaded completed in {filename}")
        return filename

    def download_raw(self, local_path):
        utils.download_file(self.http_url, local_path, self.auth)
        logger.debug(f"dataset downloaded in {local_path}")

        return local_path

    def _get_name_variables(self, variables):
        nameShort = []
        for variable in variables:
            nameShort.append(variable["nameShort"])
        complete_name_short = ",".join(nameShort)
        logger.debug(f"name short={complete_name_short}")
        return complete_name_short

    def _coordinates_to_string(self, coordinates):
        text = ""
        if "lat" in coordinates:
            text = f"&longitude={coordinates['lon']}&latitude={coordinates['lat']}"
        else:
            text = f"&north={coordinates['north']}&east={coordinates['east']}&south={coordinates['south']}&west={coordinates['west']}"
        logger.debug(f"coordinates={text}")
        return text
