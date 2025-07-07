from typing import Optional, Dict, List

from pullsar.config import BaseConfig
from pullsar.parse_operators_catalog import (
    render_operator_catalog,
    create_repository_paths_map,
)
from pullsar.operator_bundle_model import OperatorBundle


def update_operator_usage_stats(
    catalog_image: Optional[str] = None, catalog_json_file: Optional[str] = None
) -> Dict[str, List[OperatorBundle]]:
    """
    Scans input catalog of operators for operator bundles, then uses their metadata
    to retrieve their individual pull counts from their Quay repositories. Functions expects
    either one catalog image or one catalog json file, not both at the same time.

    Args:
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

    # TODO: scan repositories for usage logs and update pull counts for operator bundles
    # for now, showcase the data we have:
    counter = 1
    for repository_path, operator_bundles in repository_paths_map.items():
        print("=============================================================")
        print(repository_path)
        print("=============================================================")
        for operator_bundle in operator_bundles:
            print(f"{counter}.\n{operator_bundle}\n")
            counter += 1

    return repository_paths_map
