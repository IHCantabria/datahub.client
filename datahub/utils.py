from datetime import datetime
from dotenv import dotenv_values
import logging
import logging.config
import os
import requests


def datetime_to_string(date_obj, format="%Y-%m-%dT%H:%M:%SZ"):
    return date_obj.strftime(format)


def string_to_datetime(str_date, format="%Y-%m-%dT%H:%M:%SZ"):
    return datetime.strptime(str_date, format)


def get_logger(name):
    try:
        config_ini = f"{os.path.dirname(__file__)}/logging.{os.environ.get('ENV')}.ini"
        logging.config.fileConfig(
            config_ini, defaults={"logfilename": os.environ.get("DATAHUB_LOG")}
        )
    except Exception as e:
        pass
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
