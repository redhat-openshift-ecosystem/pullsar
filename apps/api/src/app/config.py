import os
import logging
from dotenv import load_dotenv
from dataclasses import dataclass
from typing import Optional
from datetime import date
from psycopg2.extensions import cursor

from app.db_utils import fetch_db_start_date


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


@dataclass
class BaseConfig:
    """A dataclass to hold general configurable variables."""

    export_max_days: int
    all_operators_catalog: str
    db_start_date: Optional[date] = None


def _load_base_conf() -> BaseConfig:
    """
    Loads general configuration from '.env' file.
    For example, see '.env.example' file.
    """
    load_dotenv()

    return BaseConfig(
        export_max_days=int(os.getenv("API_EXPORT_MAX_DAYS", "30")),
        all_operators_catalog=os.getenv("API_ALL_OPERATORS_CATALOG", "All Operators"),
    )


def load_db_dependent_config(db_cursor: cursor) -> None:
    """
    Fetches config values from the database and populates the base config object.
    This function should be called during application startup.
    """
    BASE_CONFIG.db_start_date = fetch_db_start_date(db_cursor)


DB_CONFIG = _load_db_conf()
BASE_CONFIG = _load_base_conf()
