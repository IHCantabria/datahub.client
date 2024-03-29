from bs4 import BeautifulSoup
import logging
import numpy as np
import requests
import xarray

from datahub import utils

logger = utils.get_logger(__name__)


class Dataset(object):
    def __init__(self, name, id, protocols, auth):
        self.name = name
        self.id = id
        # self.restrictAccess = restrictAccess
        self.ncss_url = protocols["ncss"]
        self.http_url = protocols["httpserver"]
        self.opendap_url = protocols["opendap"]
        self.auth = auth

    """
    -32767 is the most common value for _fillValue. However some variable can have another value. 
    It's hardcode because the data is not available in datahub yet.
    TODO: When the value is in datahub, use that.
    """

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    @property
    def _fillValue(self):
        return -32767

    @property
    def dates(self):
        datasetDetailsGet = requests.get(f"{self.ncss_url}/dataset.xml", auth=self.auth)
        soup = BeautifulSoup(datasetDetailsGet.content, "lxml")
        try:
            begin = soup.find("timespan").find("begin").text
            begin_datetime = utils.string_to_datetime(begin)
        except AttributeError:
            begin = None
        try:
            end = soup.find("timespan").find("end").text
            end_datetime = utils.string_to_datetime(end)
        except AttributeError:
            end = None
        dates = {"start": begin_datetime, "end": end_datetime}
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

        # time_start, time_end = self.__create_time_string_ncss(dates)
        period = self._get_time_start_end(dates)

        ncssUrl = "{url}?{vars}{coordinates}{period}&accept={format}".format(
            url=self.ncss_url,
            vars=name_variables,
            coordinates=ncss_coordinates,
            period=period,
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
            if variable.nameShort == name:
                if float(value) == self._fillValue:
                    value = None
                else:
                    value = float(value) * variable.scaleFactor
                    value = float(value) + variable.offset
        return value

    def download(
        self, filename, variables, coordinates=None, dates=None, formato="netCDF4"
    ):
        ncss_coordinates = self._coordinates_to_string(coordinates)
        name_variables = self._get_name_variables(variables)
        period = self._get_time_start_end(dates)
        ncssUrl = "{url}?{vars}{coordinates}{period}&accept={format}".format(
            url=self.ncss_url,
            vars=name_variables,
            coordinates=ncss_coordinates,
            period=period,
            format=formato,
        )
        logger.debug(f"ncssUrl={ncssUrl}")
        response = requests.get(ncssUrl, auth=self.auth)
        open(filename, "wb").write(response.content)
        logger.debug(f"dataset downloaded completed in {filename}")
        return filename

    def download_raw(self, local_path):
        utils.download_file(self.http_url, local_path, self.auth)
        logger.debug(f"dataset downloaded in {local_path}")

        return local_path

    def _get_time_start_end(self, dates):
        start = ""
        end = ""
        if not dates:
            return f"&time_start={utils.datetime_to_string(self.dates['start'])}&time_end={utils.datetime_to_string(self.dates['end'])}"
        if dates["start"]:
            start = f"&time_start={utils.datetime_to_string(dates['start'])}"
        else:
            start = f"&time_start={utils.datetime_to_string(self.dates['start'])}"
        if dates["end"]:
            end = f"&time_end={utils.datetime_to_string(dates['end'])}"
        else:
            end = f"&time_end={utils.datetime_to_string(self.dates['end'])}"
        return f"{start}{end}"

    def _get_name_variables(self, variables):
        nameShort = []
        for variable in variables:
            nameShort.append(variable.nameShort)
        complete_name_short = ",".join(nameShort)
        logger.debug(f"name short={complete_name_short}")
        return f"var={complete_name_short}"

    def _coordinates_to_string(self, coordinates):
        text = ""
        if not coordinates:
            coordinates = self.extent
        if "lat" in coordinates:
            text = f"&longitude={coordinates['lon']}&latitude={coordinates['lat']}"
        else:
            text = f"&north={coordinates['north']}&east={coordinates['east']}&south={coordinates['south']}&west={coordinates['west']}"
        logger.debug(f"coordinates={text}")
        return text

    def open_xarray_conn(self, dates=None, extent=None, method=None):
        if method and method == "outside" and not extent:
            raise Exception(f"Outside method requires an extent")
        logger.debug(f"opening {self.opendap_url}")
        ds = xarray.open_dataset(self.opendap_url)
        if dates:
            start = dates["start"] if "start" in dates else None
            end = dates["end"] if "end" in dates else None
            if "time" in ds.dims:
                if method == "outside" and start:
                    start = (
                        start
                        - np.diff(ds["time"].values)
                        .max()
                        .astype("timedelta64[s]")
                        .item()
                    )
                    end = (
                        end
                        + np.diff(ds["time"].values)
                        .max()
                        .astype("timedelta64[s]")
                        .item()
                    )
                ds = ds.sel(time=slice(start, end))
            elif "t" in ds.dims:
                if method == "outside" and start:
                    start = (
                        start
                        - np.diff(ds["t"].values).max().astype("timedelta64[s]").item()
                    )
                    end = (
                        end
                        + np.diff(ds["t"].values).max().astype("timedelta64[s]").item()
                    )
                ds = ds.sel(t=slice(start, end))
        if extent:
            if "longitude" in ds.dims:
                if method == "outside":
                    extent["west"] = (
                        extent["west"] - np.diff(ds["longitude"].values).max()
                    )
                    extent["east"] = (
                        extent["east"] - np.diff(ds["longitude"].values).max()
                    )
                    extent["south"] = (
                        extent["south"] - np.diff(ds["latitude"].values).max()
                    )
                    extent["north"] = (
                        extent["north"] - np.diff(ds["latitude"].values).max()
                    )
                ds = ds.sel(
                    longitude=slice(extent["west"], extent["east"]),
                    latitude=slice(extent["south"], extent["north"]),
                )
            elif "lon" in ds.dims:
                if method == "outside":
                    extent["west"] = extent["west"] - np.diff(ds["lon"].values).max()
                    extent["east"] = extent["east"] - np.diff(ds["lon"].values).max()
                    extent["south"] = extent["south"] - np.diff(ds["lat"].values).max()
                    extent["north"] = extent["north"] - np.diff(ds["lat"].values).max()

                ds = ds.sel(
                    lon=slice(extent["west"], extent["east"]),
                    lat=slice(extent["south"], extent["north"]),
                )
        return ds
