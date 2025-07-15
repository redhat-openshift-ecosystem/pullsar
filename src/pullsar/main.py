"""The main module of the Pullsar application."""

import logging

from pullsar.config import BaseConfig, logger, load_quay_api_tokens
from pullsar.update_operator_usage_stats import update_operator_usage_stats
from pullsar.cli import parse_arguments, ParsedArgs
from pullsar.quay_client import QuayClient


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

    for catalog_json_file in args.catalog_json_list:
        update_operator_usage_stats(
            quay_client, args.log_days, catalog_json_file=catalog_json_file
        )

    for catalog_image in args.catalog_image_list:
        update_operator_usage_stats(
            quay_client, args.log_days, catalog_image=catalog_image
        )


if __name__ == "__main__":  # pragma: no cover
    main()
