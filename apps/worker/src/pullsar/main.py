"""The main module of the Pullsar application."""

import logging
from typing import Dict, List

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
from pullsar.quay_client import QuayClient, QuayTag
from pullsar.db.manager import DatabaseManager
from pullsar.pyxis_client import PyxisClient
from pullsar.update_operator_usage_stats import PullLog, PyxisImage


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
    pyxis_client = PyxisClient(base_url=BaseConfig.PYXIS_API_BASE_URL)
    known_image_translations: Dict[str, str] = {}

    db = None
    is_db_allowed = is_database_configured() and not args.dry_run
    try:
        if is_db_allowed:
            db = DatabaseManager()
            db.connect()

        repo_path_to_logs: Dict[str, List[PullLog]] = {}
        repo_path_to_pyxis_images: Dict[str, List[PyxisImage]] = {}
        repo_path_to_tags: Dict[str, List[QuayTag]] = {}
        for catalog in args.catalogs:
            repository_paths = update_operator_usage_stats(
                quay_client,
                pyxis_client,
                known_image_translations,
                repo_path_to_logs,
                repo_path_to_pyxis_images,
                repo_path_to_tags,
                args.log_days,
                catalog.image,
                catalog.json_file,
            )

            if repository_paths and db:
                db.save_operator_usage_stats(repository_paths, catalog.image)
    except Exception as e:
        logger.error(f"A critical error occurred during processing: {e}")
    finally:
        if db:
            db.close()


if __name__ == "__main__":  # pragma: no cover
    main()
