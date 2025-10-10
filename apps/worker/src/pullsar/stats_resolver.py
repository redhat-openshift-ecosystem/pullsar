from typing import Optional, Dict, List, Tuple
from datetime import datetime, date

from pullsar.config import BaseConfig, logger
from pullsar.parse_operators_catalog import (
    render_operator_catalog,
    create_repository_paths_maps,
    RepositoryMap,
)
from pullsar.operator_bundle_model import OperatorBundle
from pullsar.quay_client import QuayClient, QuayLog, QuayTag
from pullsar.pyxis_client import PyxisClient
from pullsar.cached_context import CachedContext, PullLog

TagToOperatorBundleMap = Dict[str, OperatorBundle]
DigestToOperatorBundleMap = Dict[str, OperatorBundle]


class OperatorUsageStatsResolver:
    """
    Represents a resolver unifying methods for catalog processing and utilitary methods,
    scanning input catalog of operators for operator bundles, resolving their metadata
    and using them in order to retrieve their individual pull counts from their Quay
    repositories. Also, caches data for reuse to avoid repeating API calls for data
    we've already asked for previously.
    """

    def __init__(self) -> None:
        self._cache = CachedContext()

    def tag_in_tag_map(self, tag: str, tag_map: TagToOperatorBundleMap) -> str | None:
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
        self,
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

    def resolve_not_quay_repositories(
        self,
        pyxis_client: PyxisClient,
        not_quay_repos_map: RepositoryMap,
        quay_repos_map: RepositoryMap,
    ) -> None:
        """
        Resolves connect.redhat.com URLs to quay.io URLs using the Pyxis API
        and merges the results into the main quay_repos_map.

        Args:
            pyxis_client (PyxisClient): An instance of the PyxisClient.
            not_quay_repos_map (RepositoryMap): The map of repositories needing translation.
            quay_repos_map (RepositoryMap): The main map where successfully translated bundles
            will be added.
        """
        logger.info(
            f"Attempting to resolve {len(not_quay_repos_map)} non-Quay repositories via Pyxis..."
        )

        target_registry = "registry.connect.redhat.com"
        include_fields = (
            "data.image_id,data.repositories.registry,data.repositories.repository"
        )

        cache = self._cache
        for repo_path, bundles in not_quay_repos_map.items():
            pyxis_images = []
            if repo_path not in cache.repo_path_to_pyxis_images:
                pyxis_images = pyxis_client.get_images_for_repository(
                    target_registry, repo_path, include_fields
                )
                cache.repo_path_to_pyxis_images[repo_path] = pyxis_images
            else:
                logger.info(f"Reusing stored Pyxis images for repository: {repo_path}")
                pyxis_images = cache.repo_path_to_pyxis_images[repo_path]

            if not pyxis_images:
                continue

            _, digest_to_operator_bundle = self.create_local_tag_digest_maps(bundles)

            for pyxis_image in pyxis_images:
                digest = pyxis_image.get("image_id")
                if digest in digest_to_operator_bundle and pyxis_image.get(
                    "repositories"
                ):
                    for repo in pyxis_image["repositories"]:
                        repo_path = repo.get("repository")
                        registry = repo.get("registry")
                        if registry == "quay.io" and repo_path:
                            old_bundle = digest_to_operator_bundle[digest]
                            new_bundle = OperatorBundle(
                                old_bundle.name,
                                old_bundle.package,
                                f"{registry}/{repo_path}@{digest}",
                            )
                            quay_repos_map.setdefault(repo_path, []).append(new_bundle)
                            cache.known_image_translations[old_bundle.image] = (
                                new_bundle.image
                            )
                            break

    def update_image_digests(
        self,
        quay_client: QuayClient,
        repository_paths_map: RepositoryMap,
    ):
        """
        Looks up and updates image digests of all the operator bundles defined
        in the given repository paths map based on their defined tags using Quay API.

        Args:
            quay_client (QuayClient): Quay client used for API requests.
            repository_paths_map (RepositoryMap): Dictionary of key-value pairs,
            key being a quay repository and value being a list of OperatorBundle
            objects, images of which are stored in the repository.
        """
        cache = self._cache
        for (
            repository_path,
            operator_bundles,
        ) in repository_paths_map.items():
            tag_objects: List[QuayTag] = []
            if repository_path not in cache.repo_path_to_tags:
                tag_objects = quay_client.get_repo_tags(repository_path)
                cache.repo_path_to_tags[repository_path] = tag_objects
            else:
                logger.info(f"Reusing stored tags for repository: {repository_path}")
                tag_objects = cache.repo_path_to_tags[repository_path]

            tag_to_operator_bundle, _ = self.create_local_tag_digest_maps(
                operator_bundles
            )
            for tag_object in tag_objects:
                tag = self.tag_in_tag_map(tag_object["name"], tag_to_operator_bundle)
                if tag:
                    tag_to_operator_bundle[tag].update_image_digest(
                        tag_object["manifest_digest"]
                    )

    def extract_date(self, datetime_str: str) -> date:
        """Extracts date from datetime string used in Quay logs.

        Args:
            datetime_str (str): datetime, e.g.: "Mon, 09 Jun 2025 16:23:18 -0000"

        Returns:
            date: Extracted date object.
        """
        dt = datetime.strptime(datetime_str, "%a, %d %b %Y %H:%M:%S %z")
        return dt.date()

    def filter_pull_repo_logs(self, logs: List[QuayLog]) -> List[PullLog]:
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
                date = self.extract_date(log["datetime"])
                if log["metadata"].get("tag"):
                    pull_logs.append(PullLog(date=date, tag=log["metadata"]["tag"]))
                elif log["metadata"].get("manifest_digest"):
                    pull_logs.append(
                        PullLog(date=date, digest=log["metadata"]["manifest_digest"])
                    )

        logger.info(f"Total pull log entries retrieved: {len(pull_logs)}")
        return pull_logs

    def update_image_pull_counts(
        self,
        quay_client: QuayClient,
        repository_paths_map: RepositoryMap,
        log_days: int,
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
        cache = self._cache
        for repository_path, operator_bundles in repository_paths_map.items():
            pull_logs = []
            if repository_path not in cache.repo_path_to_logs:
                logs = quay_client.get_repo_logs(repository_path, log_days)
                pull_logs = self.filter_pull_repo_logs(logs)
                cache.repo_path_to_logs[repository_path] = pull_logs
            else:
                logger.info(f"Reusing stored logs for repository: {repository_path}")
                pull_logs = cache.repo_path_to_logs[repository_path]

            if not pull_logs:
                logger.info(
                    f"No pull logs found for repository path: {repository_path}"
                )
                continue

            tag_to_operator_bundle, digest_to_operator_bundle = (
                self.create_local_tag_digest_maps(operator_bundles)
            )
            for log in pull_logs:
                if "digest" in log and log["digest"] in digest_to_operator_bundle:
                    pull_count = digest_to_operator_bundle[log["digest"]].pull_count
                    pull_count[log["date"]] = pull_count.get(log["date"], 0) + 1
                elif "tag" in log:
                    tag = self.tag_in_tag_map(log["tag"], tag_to_operator_bundle)
                    if tag:
                        pull_count = tag_to_operator_bundle[tag].pull_count
                        pull_count[log["date"]] = pull_count.get(log["date"], 0) + 1

    def print_operator_usage_stats(self, repository_paths_map: RepositoryMap):
        """
        Prints repositories and their operator bundles on the stdout.

        Args:
            repository_paths_map (RepositoryMap): Dictionary of key-value pairs,
            key being a quay repository and value being a list of OperatorBundle objects,
            images of which are stored in the repository.
        """
        for repository_path, operator_bundles in repository_paths_map.items():
            print(
                "\n==================================================================="
            )
            print(repository_path)
            print("-------------------------------------------------------------------")

            counter = 1
            for operator_bundle in operator_bundles:
                if operator_bundle.pull_count:
                    print(f"\n{counter}.\n{operator_bundle}")
                    counter += 1

    def update_operator_usage_stats(
        self,
        quay_client: QuayClient,
        pyxis_client: PyxisClient,
        log_days: int,
        catalog_image: str,
        catalog_json_file: Optional[str] = None,
    ) -> RepositoryMap:
        """
        Scans input catalog of operators for operator bundles, then uses their metadata
        to retrieve their individual pull counts from their Quay repositories. If optional
        'catalog_json_file' is provided, 'opm render' on 'catalog_image' is skipped and
        the provided catalog file is used instead.

        Args:
            quay_client (QuayClient): Quay client used for API requests.
            pyxis_client (PyxisClient): Pyxis client used for API requests.
            log_days (int): Update stats based on logs from the last 'log_days' completed days.
            catalog_image (str): Operators catalog image.
            catalog_json_file (Optional[str]): Pre-rendered operators catalog JSON file. Defaults to None.

        Returns:
            RepositoryMap: Dictionary of key-value pairs, key being a quay repository and value
            being a list of OperatorBundle objects, images of which are stored in the repository.
        """
        if not catalog_json_file:
            is_success = render_operator_catalog(
                catalog_image, BaseConfig.CATALOG_JSON_FILE
            )
            if not is_success:
                return {}

        quay_repos_map, no_digest_repos_map, not_quay_repos_map = (
            create_repository_paths_maps(
                catalog_json_file or BaseConfig.CATALOG_JSON_FILE,
                self._cache.known_image_translations,
            )
        )

        logger.info("\nResolving non-Quay image URLs if any...")
        self.resolve_not_quay_repositories(
            pyxis_client,
            not_quay_repos_map,
            quay_repos_map,
        )

        logger.info("\nLooking up missing manifest digests if any...")
        self.update_image_digests(quay_client, no_digest_repos_map)

        logger.info("\nOperator bundles and their usage stats:")
        self.update_image_pull_counts(quay_client, quay_repos_map, log_days)

        logger.info(f"\nOperators pulled at least once in the last {log_days} days:")
        self.print_operator_usage_stats(quay_repos_map)

        return quay_repos_map
