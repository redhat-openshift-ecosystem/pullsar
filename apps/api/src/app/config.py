import os
import logging
from dotenv import load_dotenv
from dataclasses import dataclass
from typing import Optional


# set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PULLSAR_API")


@dataclass
class DBConfig:
    """A dataclass to hold database connection details."""

    dbname: Optional[str] = None
    user: Optional[str] = None
    password: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None


class BaseConfig(object):
    """
    Class that represents config variables. Database configuration can be loaded
    from '.env' file. For example, see '.env.example' file.
    """

    load_dotenv()

    # PostgreSQL configuration
    DB_CONFIG = DBConfig(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", 5432)),
    )
