"""The main module of the Pullsar application."""

import logging

from pullsar.config import (
    BaseConfig,
    logger,
    load_quay_api_tokens,
    is_database_configured,
)
from pullsar.update_operator_usage_stats import (
    update_operator_usage_stats,
)
from pullsar.cli import parse_arguments, ParsedArgs
from pullsar.quay_client import QuayClient
from pullsar.operator_bundle_model import extract_catalog_attributes
from pullsar.db.schema import create_tables
from pullsar.db.insert import insert_data


def main() -> None:
    """
    The main function of the Pullsar application.
    Updates usage stats for operators from input catalogs.
    """
    args: ParsedArgs = parse_arguments()

    if args.debug:
        logger.setLevel(logging.DEBUG)

    BaseConfig.QUAY_API_TOKENS = load_quay_api_tokens()
    quay_client = QuayClient(
        base_url=BaseConfig.QUAY_API_BASE_URL, api_tokens=BaseConfig.QUAY_API_TOKENS
    )

    is_db_configured = is_database_configured()
    if is_db_configured:
        create_tables()

    for catalog_info in args.catalogs:
        repository_paths = update_operator_usage_stats(
            quay_client, args.log_days, *catalog_info
        )

        if repository_paths and is_db_configured:
            catalog_image = catalog_info[0]
            catalog_name, ocp_version = extract_catalog_attributes(catalog_image)
            if catalog_name and ocp_version:
                insert_data(repository_paths, catalog_name, ocp_version)


if __name__ == "__main__":  # pragma: no cover
    main()
