import argparse
from typing import NamedTuple, List, Optional

from pullsar.config import BaseConfig


class ParsedArgs(NamedTuple):
    """
    A NamedTuple to hold the parsed command-line arguments.
    """

    debug: bool
    log_days: int
    catalog_json_list: List[str]
    catalog_image_list: List[str]


def parse_arguments(argv: Optional[List[str]] = None) -> ParsedArgs:
    parser = argparse.ArgumentParser(
        description="Script for retrieving latest pull counts for all the operators "
        "and their versions defined in the input operators catalogs "
        "(catalog images or pre-rendered catalog JSON files)."
    )

    parser.add_argument("--debug", action="store_true", help="makes logs more verbose")
    parser.add_argument(
        "--log-days",
        type=int,
        default=BaseConfig.LOG_DAYS_DEFAULT,
        help="number of completed past days to include logs from (default: 7)",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--catalog-json-file",
        dest="catalog_json_list",
        action="append",
        default=[],
        help="path to pre-rendered catalog JSON file (repeatable)",
        metavar="CATALOG_JSON",
    )
    group.add_argument(
        "--catalog-image",
        dest="catalog_image_list",
        action="append",
        default=[],
        help="catalog image pullspec to render (repeatable)",
        metavar="CATALOG_IMAGE",
    )
    args = parser.parse_args(argv)

    if not (BaseConfig.LOG_DAYS_MIN <= args.log_days <= BaseConfig.LOG_DAYS_MAX):
        parser.error(
            f"argument --log-days: must be between {BaseConfig.LOG_DAYS_MIN} "
            f"and {BaseConfig.LOG_DAYS_MAX}"
        )

    return ParsedArgs(
        debug=args.debug,
        log_days=args.log_days,
        catalog_json_list=args.catalog_json_list,
        catalog_image_list=args.catalog_image_list,
    )
