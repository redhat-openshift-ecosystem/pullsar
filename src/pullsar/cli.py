import argparse
from typing import NamedTuple, List, Optional

from pullsar.config import BaseConfig


class ParsedCatalogArg(NamedTuple):
    """A NamedTuple with image and optional rendered JSON file."""

    image: str
    json_file: Optional[str]


class ParsedArgs(NamedTuple):
    """
    A NamedTuple to hold the parsed command-line arguments.
    """

    dry_run: bool
    debug: bool
    log_days: int
    catalogs: List[ParsedCatalogArg]


def parse_arguments(argv: Optional[List[str]] = None) -> ParsedArgs:
    parser = argparse.ArgumentParser(
        description="Script for retrieving latest pull counts for all the operators "
        "and their versions defined in the input operators catalogs "
        "(catalog images or pre-rendered catalog JSON files)."
    )

    parser.add_argument(
        "--dry-run",
        "--test",
        action="store_true",
        help="run the script without saving any data to the database",
    )
    parser.add_argument("--debug", action="store_true", help="makes logs more verbose")
    parser.add_argument(
        "--log-days",
        type=int,
        default=BaseConfig.LOG_DAYS_DEFAULT,
        help="number of completed past days to include logs from (default: 7)",
    )
    parser.add_argument(
        "--catalog-image",
        dest="catalogs",
        action="append",
        nargs="+",
        default=[],
        required=True,
        metavar="IMAGE [RENDERED_JSON_FILE]",
        help="operators catalog, e.g. '<CATALOG_IMAGE_PULLSPEC>:<OCP_VERSION>' "
        "to be rendered with 'opm' and used in database entry (keeping track of "
        "each operator's source catalogs). To skip render, provide optional second "
        "argument, a path to a pre-rendered catalog JSON file. Option is repeatable.",
    )
    args = parser.parse_args(argv)

    if not (BaseConfig.LOG_DAYS_MIN <= args.log_days <= BaseConfig.LOG_DAYS_MAX):
        parser.error(
            f"argument --log-days: must be between {BaseConfig.LOG_DAYS_MIN} "
            f"and {BaseConfig.LOG_DAYS_MAX}"
        )

    catalog_args: List[ParsedCatalogArg] = []
    for catalog_info in args.catalogs:
        if len(catalog_info) == 1:
            catalog_args.append(ParsedCatalogArg(image=catalog_info[0], json_file=None))
        elif len(catalog_info) == 2:
            catalog_args.append(
                ParsedCatalogArg(image=catalog_info[0], json_file=catalog_info[1])
            )
        else:
            parser.error(
                f"argument --catalog-image: requires 1 or 2 arguments, "
                f"but received {len(catalog_info)}"
            )

    return ParsedArgs(
        dry_run=args.dry_run,
        debug=args.debug,
        log_days=args.log_days,
        catalogs=catalog_args,
    )
