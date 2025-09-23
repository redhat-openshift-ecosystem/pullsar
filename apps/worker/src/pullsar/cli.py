import argparse
from typing import NamedTuple, List, Optional

from pullsar.config import BaseConfig, logger
from pullsar.pyxis_client import PyxisClientPublic


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


def discover_catalog_versions(
    base_image: str, pyxis_client: PyxisClientPublic
) -> List[ParsedCatalogArg]:
    """
    Calls the public Pyxis API to find all supported catalog image paths for
    a given base image name by fetching all indices and filtering locally.
    """
    logger.info(f"Discovering supported OCP versions for base image: {base_image}")
    try:
        indices = pyxis_client.get_operator_indices(
            ocp_versions_range=BaseConfig.MIN_OCP_VERSION
        )

        discovered_catalogs = []
        for index in indices:
            org = index.get("organization")
            path = index.get("path")
            if path and path.startswith(base_image) and org != "deleted":
                logger.info(f"Discovered: {path}")
                discovered_catalogs.append(ParsedCatalogArg(image=path, json_file=None))

        if not discovered_catalogs:
            logger.warning(
                f"No supported catalog versions found for base image: {base_image}"
            )

        discovered_catalogs.sort(key=lambda x: x.image)
        return discovered_catalogs

    except Exception as e:
        logger.error(f"Failed to discover catalog versions from Pyxis API: {e}")
        exit(1)


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

    catalog_group = parser.add_mutually_exclusive_group(required=True)
    catalog_group.add_argument(
        "--catalog-image",
        dest="catalogs",
        action="append",
        nargs="+",
        default=[],
        metavar="IMAGE [RENDERED_JSON_FILE]",
        help="operators catalog, e.g. '<CATALOG_IMAGE_PULLSPEC>:<OCP_VERSION>' "
        "to be rendered with 'opm' and used in database entry (keeping track of "
        "each operator's source catalogs). To skip render, provide optional second "
        "argument, a path to a pre-rendered catalog JSON file. Option is repeatable.",
    )
    catalog_group.add_argument(
        "--catalog-base-image",
        dest="catalogs_base",
        action="append",
        default=[],
        help="operators catalog without specified version, e.g. '<CATALOG_IMAGE_PULLSPEC>' "
        "to be rendered with 'opm' and used in database entry (keeping track of "
        "each operator's source catalogs). All supported OCP versions of that catalog will"
        "be looked up via Pyxis API and processed. Option is repeatable.",
    )

    args = parser.parse_args(argv)

    if not (BaseConfig.LOG_DAYS_MIN <= args.log_days <= BaseConfig.LOG_DAYS_MAX):
        parser.error(
            f"argument --log-days: must be between {BaseConfig.LOG_DAYS_MIN} "
            f"and {BaseConfig.LOG_DAYS_MAX}"
        )

    catalog_args: List[ParsedCatalogArg] = []
    if args.catalogs_base:
        # OCP versions of catalogs resolved dynamically via Pyxis API
        public_pyxis_client = PyxisClientPublic(
            base_url=BaseConfig.PYXIS_PUBLIC_API_BASE_URL
        )
        for base_image in args.catalogs_base:
            if ":" in base_image:
                parser.error(
                    "argument --catalog-base-image: invalid format, "
                    "OCP version shall not be specified for this argument."
                )
            discovered = discover_catalog_versions(base_image, public_pyxis_client)
            catalog_args.extend(discovered)
    else:
        # OCP versions of catalogs provided by user input
        for catalog_info in args.catalogs:
            if len(catalog_info) == 1:
                catalog_args.append(
                    ParsedCatalogArg(image=catalog_info[0], json_file=None)
                )
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
