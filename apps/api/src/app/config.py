import os
import logging
from dotenv import load_dotenv
from dataclasses import dataclass


# set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PULLSAR_API")


@dataclass
class DBConfig:
    """A dataclass to hold database connection details."""

    dbname: str
    user: str
    password: str
    host: str
    port: int


class BaseConfig(object):
    """
    Class that represents config variables. Database configuration can be loaded
    from '.env' file. For example, see '.env.example' file.
    """

    load_dotenv()

    # PostgreSQL configuration
    DB_CONFIG = DBConfig(
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        host=os.environ["DB_HOST"],
        port=int(os.getenv("DB_PORT", 5432)),
    )
