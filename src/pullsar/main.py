"""The main module of the Pullsar application."""

import argparse
import logging

from pullsar.config import Config, logger, load_quay_api_tokens
from pullsar.update_operator_usage_stats import update_operator_usage_stats


def main() -> None:
    """
    The main function of the Pullsar application.
    Parses options and arguments.
    """
    parser = argparse.ArgumentParser(
        description="Script for retrieving latest pull counts for all the operators "
        "and their versions defined in the input operators catalogs "
        "(catalog images or pre-rendered catalog JSON files)."
    )

    parser.add_argument("--debug", action="store_true", help="makes logs more verbose")
    parser.add_argument(
        "--catalog-json-file",
        dest="catalog_json_list",
        action="append",
        default=[],
        help="path to pre-rendered catalog JSON file (repeatable)",
        metavar="CATALOG_JSON",
    )
    parser.add_argument(
        "--catalog-image",
        dest="catalog_image_list",
        action="append",
        default=[],
        help="catalog image pullspec to render (repeatable)",
        metavar="CATALOG_IMAGE",
    )
    args = parser.parse_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)

    Config.QUAY_API_TOKENS = load_quay_api_tokens()

    for catalog_json_file in args.catalog_json_list:
        update_operator_usage_stats(catalog_json_file=catalog_json_file)

    for catalog_image in args.catalog_image_list:
        update_operator_usage_stats(catalog_image=catalog_image)


if __name__ == "__main__":  # pragma: no cover
    main()
