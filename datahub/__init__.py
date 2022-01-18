""" Datahub client"""
__version__ = "0.9.4"

import os


try:
    from dotenv import load_dotenv

    dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
    load_dotenv(dotenv_path)
except Exception:
    pass
