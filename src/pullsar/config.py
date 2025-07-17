import os
import logging
import json
from typing import Dict
from dotenv import load_dotenv


# set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PULLSAR")


def load_quay_api_tokens() -> Dict[str, str]:
    """
    Loads environment variable QUAY_API_TOKENS_JSON
    and tries to convert it into a dictionary.
    Raises if fails to load the API tokens.

    Returns:
        Dict[str, str]: Dictionary of key-value pairs, key being a Quay organization
        and value being an OAuth API token with Administrator scope created
        in the organization.
    """
    quay_api_tokens_raw = os.getenv("QUAY_API_TOKENS_JSON")
    if quay_api_tokens_raw is None:
        logger.warning(
            "Environmental variable QUAY_API_TOKENS_JSON is undefined. "
            "To access logs from private repositories, consider defining it, e.g.:\n"
            'export QUAY_API_TOKENS_JSON=\'{"org1":"token1","org2":"token2"}\''
        )
        return {}

    try:
        quay_api_tokens = json.loads(quay_api_tokens_raw)
        return quay_api_tokens

    except json.JSONDecodeError:
        logger.error("Environmental variable QUAY_API_TOKENS_JSON is not a valid JSON.")
        raise


class BaseConfig(object):
    """
    Class that represents config variables. Quay API tokens
    and database configuration can be loaded from '.env' file.
    For example, see '.env.example' file.
    """
    load_dotenv()

    QUAY_API_TOKENS: Dict[str, str] = {}
    QUAY_API_BASE_URL = "https://quay.io/api/v1"

    # destination for output rendered JSON operators catalog files
    CATALOG_JSON_FILE = "operators_catalog.json"
    LOG_DAYS_DEFAULT = 7
    LOG_DAYS_MIN = 1
    LOG_DAYS_MAX = 30  # Quay limit

    # PostgreSQL configuration
    DB_CONFIG = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT", 5432),
    }
