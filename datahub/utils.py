from datetime import datetime
import logging
import logging.config
import os
import requests


def datetime_to_string(date_obj):
    return date_obj.strftime("%Y-%m-%dT%H:%M:%SZ")


def string_to_datetime(str_date):
    return datetime.strptime(str_date, "%Y-%m-%dT%H:%M:%SZ")


def get_logger(name):
    config_ini = f"{os.path.dirname(__file__)}/logging.ini"
    logging.config.fileConfig(config_ini)
    logger = logging.getLogger(name)
    return logger


def download_file(url, local_filename, auth):
    # local_filename = url.split('/')[-1]
    # NOTE the stream=True parameter below
    with requests.get(url, stream=True, auth=auth) as r:
        r.raise_for_status()
        with open(local_filename, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                # If you have chunk encoded response uncomment if
                # and set chunk_size parameter to None.
                # if chunk:
                f.write(chunk)
    return local_filename
