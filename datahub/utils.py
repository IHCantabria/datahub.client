from datetime import datetime
import logging
import logging.config
import os


def datetime_to_string(date_obj):
    return date_obj.strftime("%Y-%m-%dT%H:%M:%SZ")


def string_to_datetime(str_date):
    return datetime.strptime(str_date, "%Y-%m-%dT%H:%M:%SZ")


def get_logger(name):
    config_ini = f"{os.path.dirname(__file__)}/logging.ini"
    logging.config.fileConfig(config_ini)
    logger = logging.getLogger(name)
    return logger
