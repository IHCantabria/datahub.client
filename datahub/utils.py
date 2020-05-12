from datetime import datetime


def datetime_to_string(date_obj):
    return date_obj.strftime("%Y-%m-%dT%H:%M:%SZ")


def string_to_datetime(str_date):
    return datetime.strptime(str_date, "%Y-%m-%dT%H:%M:%SZ")
