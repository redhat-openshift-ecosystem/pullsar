from typing import Optional, Dict, List
import json

from pullsar.config import BaseConfig, logger
from pullsar.parse_operators_catalog import (
    render_operator_catalog,
    create_repository_paths_map,
)
from pullsar.operator_bundle_model import OperatorBundle
from pullsar.get_quay_repo_logs import get_quay_repo_logs, filter_pull_repo_logs


def tag_in_tag_map(tag: str, tag_map: Dict[str, OperatorBundle]) -> str | None:
    """
    If map contains equivalent tag (the same tag, or tag with or without prefix 'v'),
    function finds it, so we can count pull actions for equivalent tags towards one
    common pull count of the respective operator bundle.

    Args:
        tag (str): Operator image version tag, e.g. v1.2.3
        tag_map (Dict[str, OperatorBundle]): Dictionary with pairs TAG:OPERATOR_BUNDLE

    Returns:
        str: Tag equivalent used in the tag map if there is such, else None.
    """
    if tag in tag_map:
        return tag

    equivalent_tag = tag[1:] if tag.startswith("v") else f"v{tag}"
    return equivalent_tag if equivalent_tag in tag_map else None


def update_operator_usage_stats(
    log_days: int,
    catalog_image: Optional[str] = None,
    catalog_json_file: Optional[str] = None,
) -> Dict[str, List[OperatorBundle]]:
    """
    Scans input catalog of operators for operator bundles, then uses their metadata
    to retrieve their individual pull counts from their Quay repositories. Functions expects
    either one catalog image or one catalog json file, not both at the same time.

    Args:
        log_days (int): Update stats based on logs from the last 'log_days' completed days.
        catalog_image (Optional[str]): Operators catalog image. Defaults to None.
        catalog_json_file (Optional[str]): Pre-rendered perators catalog JSON file. Defaults to None.

    Returns:
        Dict[str, List[OperatorBundle]]: Dictionary of key-value pairs, key being a quay repository
        and value being a list of OperatorBundle objects, images of which are stored in the repository.
    """
    if catalog_image:
        render_operator_catalog(catalog_image, BaseConfig.CATALOG_JSON_FILE)

    repository_paths_map = create_repository_paths_map(
        catalog_json_file or BaseConfig.CATALOG_JSON_FILE
    )

    for repository_path, operator_bundles in repository_paths_map.items():
        print("\n===================================================================")
        print(repository_path)
        print("-------------------------------------------------------------------")

        logs = get_quay_repo_logs(repository_path, log_days)
        if not logs:
            logger.info(f"No logs found for repository path: {repository_path}")
            continue

        pull_logs = filter_pull_repo_logs(logs)
        logger.debug(f"\nPull logs:\n{json.dumps(pull_logs, indent=2)}")

        # create mappings between local tag/digest and respective operator bundle
        digest_to_operator_bundle: Dict[str, OperatorBundle] = {}
        tag_to_operator_bundle: Dict[str, OperatorBundle] = {}
        for operator_bundle in operator_bundles:
            if operator_bundle.tag:
                tag_to_operator_bundle[operator_bundle.tag] = operator_bundle
            if operator_bundle.digest:
                digest_to_operator_bundle[operator_bundle.digest] = operator_bundle

        for log in pull_logs:
            if log.get("digest") and log["digest"] in digest_to_operator_bundle:
                pull_count = digest_to_operator_bundle[log["digest"]].pull_count
                pull_count[log["date"]] = pull_count.get(log["date"], 0) + 1
            elif log.get("tag"):
                tag = tag_in_tag_map(log["tag"], tag_to_operator_bundle)
                if tag:
                    pull_count = tag_to_operator_bundle[tag].pull_count
                    pull_count[log["date"]] = pull_count.get(log["date"], 0) + 1

        # showcase results on stdout
        logger.info(
            f"\nOperator bundles pulled at least once in the last {log_days} days:"
        )
        counter = 1
        for operator_bundle in operator_bundles:
            if operator_bundle.pull_count:
                print(f"\n{counter}.\n{operator_bundle}")
                counter += 1

    return repository_paths_map
