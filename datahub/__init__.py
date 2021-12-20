""" Datahub client"""
__version__ = "0.9.3b1"


# load environ

import os
from dotenv import load_dotenv

if not os.environ.get("ENV"):
    env_path = f"{os.getcwd()}/.env"
    load_dotenv(env_path)
