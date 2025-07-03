import argparse
from typing import NamedTuple, List


class ParsedArgs(NamedTuple):
    """
    A NamedTuple to hold the parsed command-line arguments.
    """

    debug: bool
    catalog_json_list: List[str]
    catalog_image_list: List[str]


def parse_arguments() -> ParsedArgs:
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

    return ParsedArgs(
        debug=args.debug,
        catalog_json_list=args.catalog_json_list,
        catalog_image_list=args.catalog_image_list,
    )
