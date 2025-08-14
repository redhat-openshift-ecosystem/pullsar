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


def _load_db_conf() -> DBConfig:
    """
    Loads PostgreSQL database configuration from '.env' file.
    For example, see '.env.example' file.
    """
    load_dotenv()
    return DBConfig(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", 5432)),
    )


DB_CONFIG = _load_db_conf()
