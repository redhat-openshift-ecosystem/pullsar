from typing import Optional, Dict, List, Tuple
from datetime import datetime
import json

from pullsar.config import BaseConfig, logger
from pullsar.parse_operators_catalog import (
    render_operator_catalog,
    create_repository_paths_maps,
    RepositoryMap,
)
from pullsar.operator_bundle_model import OperatorBundle
from pullsar.quay_client import QuayClient, QuayLog, QuayTag

TagToOperatorBundleMap = Dict[str, OperatorBundle]
DigestToOperatorBundleMap = Dict[str, OperatorBundle]
PullLog = Dict[str, str]


def tag_in_tag_map(tag: str, tag_map: TagToOperatorBundleMap) -> str | None:
    """
    If map contains equivalent tag (the same tag, or tag with or without prefix 'v'),
    function finds it, so we can count pull actions for equivalent tags towards one
    common pull count of the respective operator bundle.

    Args:
        tag (str): Operator image version tag, e.g. v1.2.3
        tag_map (TagToOperatorBundleMap): Dictionary with pairs TAG:OPERATOR_BUNDLE

    Returns:
        str: Tag equivalent used in the tag map if there is such, else None.
    """
    if tag in tag_map:
        return tag

    equivalent_tag = tag[1:] if tag.startswith("v") else f"v{tag}"
    return equivalent_tag if equivalent_tag in tag_map else None


def create_local_tag_digest_maps(
    operator_bundles: List[OperatorBundle],
) -> Tuple[TagToOperatorBundleMap, DigestToOperatorBundleMap]:
    """
    Create mappings between local tag/digest and respective operator bundle.

    Args:
        operator_bundles (List[OperatorBundle]): List of operator bundles belonging
        to one repository (with unique tags and digests identifying a specific
        operator bundle within that repository).

    Returns:
        Tuple[TagToOperatorBundleMap, DigestToOperatorBundleMap]: Two dictionaries
        with key-value pairs, key being the identifier and value being OperatorBundle.
        First dictionary - TAG:OPERATOR_BUNDLE
        Second dictionary - MANIFEST_DIGEST:OPERATOR_BUNDLE
    """
    tag_to_operator_bundle: TagToOperatorBundleMap = {}
    digest_to_operator_bundle: DigestToOperatorBundleMap = {}
    for operator_bundle in operator_bundles:
        if operator_bundle.tag:
            tag_to_operator_bundle[operator_bundle.tag] = operator_bundle
        if operator_bundle.digest:
            digest_to_operator_bundle[operator_bundle.digest] = operator_bundle

    return (tag_to_operator_bundle, digest_to_operator_bundle)


def update_image_digests(quay_client: QuayClient, repository_paths_map: RepositoryMap):
    """
    Looks up and updates image digests of all the operator bundles defined
    in the given repository paths map based on their defined tags using Quay API.

    Args:
        quay_client (QuayClient): Quay client used for API requests.
        repository_paths_map (RepositoryMap): Dictionary of key-value pairs,
        key being a quay repository and value being a list of OperatorBundle
        objects, images of which are stored in the repository.
    """
    for (
        repository_path,
        operator_bundles,
    ) in repository_paths_map.items():
        tag_to_operator_bundle, _ = create_local_tag_digest_maps(operator_bundles)
        tag_objects: List[QuayTag] = quay_client.get_repo_tags(repository_path)
        for tag_object in tag_objects:
            tag = tag_in_tag_map(tag_object["name"], tag_to_operator_bundle)
            if tag:
                tag_to_operator_bundle[tag].digest = tag_object["manifest_digest"]


def extract_date(datetime_str: str) -> str:
    """Extracts date from datetime string used in Quay logs.

    Args:
        datetime_str (str): datetime, e.g.: "Mon, 09 Jun 2025 16:23:18 -0000"

    Returns:
        str: extracted date, e.g.: "06/09/2025"
    """
    dt = datetime.strptime(datetime_str, "%a, %d %b %Y %H:%M:%S %z")
    return dt.strftime("%m/%d/%Y")


def filter_pull_repo_logs(logs: List[QuayLog]) -> List[PullLog]:
    """
    Processes Quay logs, filters 'pull_repo' type logs and simplify them keeping
    only the data needed for futher processing ('date' and an operator version
    identifier, either 'digest' or 'tag').

    Args:
        logs (List[QuayLog]): Mixed logs from Quay.

    Returns:
        List[PullLog]: List of objects representing 'pull_repo' actions
        with attributes 'date' and an identifier, either 'digest' or 'tag'.
    """
    pull_logs = []
    for log in logs:
        if (
            log.get("kind") == "pull_repo"
            and log.get("metadata")
            and log.get("datetime")
        ):
            date = extract_date(log["datetime"])
            if log["metadata"].get("tag"):
                pull_logs.append({"date": date, "tag": log["metadata"]["tag"]})
            elif log["metadata"].get("manifest_digest"):
                pull_logs.append(
                    {"date": date, "digest": log["metadata"]["manifest_digest"]}
                )

    logger.info(f"Total pull log entries retrieved: {len(pull_logs)}")
    return pull_logs


def update_image_pull_counts(
    quay_client: QuayClient, repository_paths_map: RepositoryMap, log_days: int
):
    """
    Looks up and updates pull counts of all the operator bundles defined in the given
    repository paths map based on their defined tags and digests using Quay API.

    Args:
        quay_client (QuayClient): Quay client used for API requests.
        repository_paths_map (RepositoryMap): Dictionary of key-value pairs, key being
        a quay repository and value being a list of OperatorBundle objects, images
        of which are stored in the repository.
        log_days (int): Update stats based on logs from the last 'log_days' completed days.
    """
    for repository_path, operator_bundles in repository_paths_map.items():
        logs = quay_client.get_repo_logs(repository_path, log_days)
        if not logs:
            logger.info(f"No logs found for repository path: {repository_path}")
            continue

        pull_logs = filter_pull_repo_logs(logs)
        logger.debug(f"\nPull logs:\n{json.dumps(pull_logs, indent=2)}")

        tag_to_operator_bundle, digest_to_operator_bundle = (
            create_local_tag_digest_maps(operator_bundles)
        )

        for log in pull_logs:
            if log.get("digest") and log["digest"] in digest_to_operator_bundle:
                pull_count = digest_to_operator_bundle[log["digest"]].pull_count
                pull_count[log["date"]] = pull_count.get(log["date"], 0) + 1
            elif log.get("tag"):
                tag = tag_in_tag_map(log["tag"], tag_to_operator_bundle)
                if tag:
                    pull_count = tag_to_operator_bundle[tag].pull_count
                    pull_count[log["date"]] = pull_count.get(log["date"], 0) + 1


def print_operator_usage_stats(repository_paths_map: RepositoryMap):
    """
    Prints repositories and their operator bundles on the stdout.

    Args:
        repository_paths_map (RepositoryMap): Dictionary of key-value pairs,
        key being a quay repository and value being a list of OperatorBundle objects,
        images of which are stored in the repository.
    """
    for repository_path, operator_bundles in repository_paths_map.items():
        print("\n===================================================================")
        print(repository_path)
        print("-------------------------------------------------------------------")

        counter = 1
        for operator_bundle in operator_bundles:
            if operator_bundle.pull_count:
                print(f"\n{counter}.\n{operator_bundle}")
                counter += 1


def update_operator_usage_stats(
    quay_client: QuayClient,
    log_days: int,
    catalog_image: Optional[str] = None,
    catalog_json_file: Optional[str] = None,
) -> RepositoryMap:
    """
    Scans input catalog of operators for operator bundles, then uses their metadata
    to retrieve their individual pull counts from their Quay repositories. Functions expects
    either one catalog image or one catalog json file, not both at the same time.
    Lists updated stats on the stdout.

    Args:
        quay_client (QuayClient): Quay client used for API requests.
        log_days (int): Update stats based on logs from the last 'log_days' completed days.
        catalog_image (Optional[str]): Operators catalog image. Defaults to None.
        catalog_json_file (Optional[str]): Pre-rendered operators catalog JSON file. Defaults to None.

    Returns:
        RepositoryMap: Dictionary of key-value pairs, key being a quay repository and value
        being a list of OperatorBundle objects, images of which are stored in the repository.
    """
    if catalog_image:
        render_operator_catalog(catalog_image, BaseConfig.CATALOG_JSON_FILE)

    repository_paths_map, repository_paths_map_missing_digests = (
        create_repository_paths_maps(catalog_json_file or BaseConfig.CATALOG_JSON_FILE)
    )

    logger.info("\nLooking up missing manifest digests if any...")
    update_image_digests(quay_client, repository_paths_map_missing_digests)

    logger.info("\nOperator bundles and their usage stats:")
    update_image_pull_counts(quay_client, repository_paths_map, log_days)

    logger.info(f"\nOperators pulled at least once in the last {log_days} days:")
    print_operator_usage_stats(repository_paths_map)

    return repository_paths_map
