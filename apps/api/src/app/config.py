import os
import logging
from dotenv import load_dotenv
from dataclasses import dataclass
from typing import Optional
from datetime import date


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

    db_start_date: date
    export_max_days: int
    all_operators_catalog: str


def _load_base_conf() -> BaseConfig:
    """
    Loads general configuration from '.env' file.
    For example, see '.env.example' file.
    """
    load_dotenv()

    start_date_str = os.getenv("API_DB_START_DATE")
    if not start_date_str:
        raise ValueError("API_DB_START_DATE environment variable is not set.")

    return BaseConfig(
        db_start_date=date.fromisoformat(start_date_str),
        export_max_days=int(os.getenv("API_EXPORT_MAX_DAYS", "30")),
        all_operators_catalog=os.getenv("API_ALL_OPERATORS_CATALOG", "All Operators"),
    )


DB_CONFIG = _load_db_conf()
BASE_CONFIG = _load_base_conf()
