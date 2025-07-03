"""The main module of the Pullsar application."""

import logging

from pullsar.config import BaseConfig, logger, load_quay_api_tokens
from pullsar.update_operator_usage_stats import update_operator_usage_stats
from pullsar.cli import parse_arguments, ParsedArgs


def main() -> None:
    """
    The main function of the Pullsar application.
    Updates usage stats for operators from input catalogs.
    """
    args: ParsedArgs = parse_arguments()

    if args.debug:
        logger.setLevel(logging.DEBUG)

    BaseConfig.QUAY_API_TOKENS = load_quay_api_tokens()

    for catalog_json_file in args.catalog_json_list:
        update_operator_usage_stats(catalog_json_file=catalog_json_file)

    for catalog_image in args.catalog_image_list:
        update_operator_usage_stats(catalog_image=catalog_image)


if __name__ == "__main__":  # pragma: no cover
    main()
