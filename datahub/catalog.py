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

from requests.auth import HTTPBasicAuth
from xml.etree import ElementTree

from datahub.config import Config
from datahub.dataset import Dataset
from datahub.variable import Variable
from datahub import utils

logger = utils.get_logger(__name__)


class Catalog(object):
    def __init__(self, product, auth=None):
        self.urlBase = product.urlBase
        self.urlXmlLatest = product.urlXmlLatest
        self.urlCatalog = product.urlCatalog

        configuration = Config()

        self.auth = ()
        if auth:
            self.auth = HTTPBasicAuth(auth[0], auth[1])
            logger.debug("Using auth")
        else:
            auth_json = configuration.get_auth_for_catalog(product.id)
            if auth_json:
                self.auth = HTTPBasicAuth(auth_json["user"], auth_json["password"])
                logger.debug("Using auth")

    @property
    def url(self):
        url = f"{self.urlBase}{self.urlCatalog}"
        logger.debug(f"url={url}")
        return url

    @property
    def latest(self):
        productLatest = requests.get(
            self.url.replace("catalog.xml", "latest.xml"), auth=self.auth
        )
        bxml = productLatest.content

        soup = BeautifulSoup(bxml, "xml")
        services = soup.find_all("service")
        ncssPath = ""
        httpserver = ""
        opendap_protocol = ""
        for service in services:
            if service.attrs["name"] == "ncss":
                ncssPath = service.attrs["base"]
            if service.attrs["name"] == "http":
                httpserver = service.attrs["base"]
            if service.attrs["name"] == "odap":
                opendap_protocol = service.attrs["base"]
        logger.debug(
            f"ncssPath={ncssPath}, httpserver={httpserver}, opendap={opendap_protocol}"
        )
        datasets_xml = soup.find_all("dataset")
        dataset_latest = None
        for dataset_xml in datasets_xml:

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
            url_opendap = "{dns}{protocol}{dataset}".format(
                dns=self.urlBase,
                protocol=opendap_protocol,
                dataset=dataset_xml.attrs["urlPath"],
            )
            if self.auth:
                url_opendap = Config.get_auth_for_opendap(url_opendap, self.auth)
            protocols = {
                "ncss": urlPath,
                "httpserver": url_httpserver,
                "opendap": url_opendap,
            }

            name = dataset_xml.attrs["name"]
            id = dataset_xml.attrs["ID"]
            dataset = Dataset(name, id, protocols, self.auth)
            dataset_latest = dataset
            logger.info(f"latest dataset found")
            return dataset_latest

        logger.info(f"latest not dataset found")
        return dataset_latest

    @property
    def datasets(self):
        productLatest = requests.get(self.url, auth=self.auth)
        bxml = productLatest.content

        soup = BeautifulSoup(bxml, "xml")
        services = soup.find_all("service")
        ncssPath = ""
        httpserver = ""
        opendap_protocol = ""
        for service in services:
            if service.attrs["name"] == "ncss":
                ncssPath = service.attrs["base"]
            if service.attrs["name"] == "http":
                httpserver = service.attrs["base"]
            if service.attrs["name"] == "odap":
                opendap_protocol = service.attrs["base"]
        logger.debug(
            f"ncssPath={ncssPath}, httpserver={httpserver}, opendap={opendap_protocol}"
        )
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
                url_opendap = "{dns}{protocol}{dataset}".format(
                    dns=self.urlBase,
                    protocol=opendap_protocol,
                    dataset=dataset_xml.attrs["urlPath"],
                )
                if self.auth:
                    url_opendap = Config.get_auth_for_opendap(url_opendap, self.auth)
                protocols = {
                    "ncss": urlPath,
                    "httpserver": url_httpserver,
                    "opendap": url_opendap,
                }

                name = dataset_xml.attrs["name"]
                id = dataset_xml.attrs["ID"]
                dataset = Dataset(name, id, protocols, self.auth)
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

    def _join_datasets(self, filenames):
        ds_files = []
        for filename in filenames:
            ds = xarray.open_dataset(filename)
            ds_files.append(ds)

        ds_result = ds_files[0]

        time_var = "t" if "t" in ds_result else "time"
        for ds in ds_files[1:]:
            end = ds_result[time_var][0] - 1
            ds_cut = ds.sel(time=slice(None, end))
            ds_result = xarray.concat([ds_cut, ds_result], dim=time_var)
        return ds_result

    def download(
        self, filename, variables, coordinates=None, dates=None, formato="netCDF4"
    ):
        datasets_for_download = self._get_datasets_with_data(dates)
        filenames = []
        if len(datasets_for_download) > 1:

            for i, dataset in enumerate(datasets_for_download):
                name = dataset.download(
                    f"{filename}{i}.nc", variables, coordinates, dates, formato
                )
                filenames.append(name)
            ds = self._join_datasets(filenames)
            self._to_netcdf(ds, filename)
            ds.close()
            for name in filenames:
                os.remove(name)
            filenames = [filename]

        elif len(datasets_for_download) > 0:
            dataset = datasets_for_download[0]
            name = dataset.download(
                filename,
                variables,
                coordinates=coordinates,
                dates=dates,
                formato=formato,
            )
            filenames.append(name)
        if formato == "netcdf" and coordinates and len(coordinates.keys()) == 2:
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
            dataset.variables[variable["nameShort"]].attrs["add_offset"] = variable[
                "offset"
            ]
            dataset.variables[variable["nameShort"]].attrs["scale_factor"] = variable[
                "scaleFactor"
            ]
            dataset.variables["time"].encoding[
                "units"
            ] = f"hours since {dates['start']}"

        renamed = dataset.swap_dims({"obs": "time"})
        self.to_netcdf(renamed, f"{filename}-new.nc")

        os.remove(filename)
        os.rename(f"{filename}-new.nc", filename)
        logger.debug("netcdf is fixed")

    def _to_netcdf(self, ds, filename):
        comp = dict(zlib=True, complevel=4)
        encoding = {var: comp for var in ds.data_vars}

        ds.to_netcdf(filename, mode="w", format="NETCDF4", encoding=encoding)

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

    def open_xarray_conn(self, dates=None, extent=None):

        list_conn = [dataset.opendap_url for dataset in self.datasets]
        logger.debug(f"opening: {','.join(list_conn)}")

        ds = self._join_datasets(list_conn)
        # ds = self._join_datasets(list_conn)
        if dates:
            start = dates["start"] if "start" in dates else None
            end = dates["end"] if "end" in dates else None
            if "time" in ds.dims:
                ds = ds.sel(time=slice(start, end))
            elif "t" in ds.dims:
                ds = ds.sel(t=slice(start, end))
        if extent:
            if "longitud" in ds.dims:
                ds = ds.sel(
                    longitude=slice(extent["west"], extent["east"]),
                    latitude=slice(extent["south"], extent["north"]),
                )
            elif "lon" in ds.dims:
                ds = ds.sel(
                    lon=slice(extent["west"], extent["east"]),
                    lat=slice(extent["south"], extent["north"]),
                )
        return ds
