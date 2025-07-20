from pullsar.operator_bundle_model import extract_catalog_attributes
from pullsar.db.insert import insert_data
from pullsar.config import logger
from pullsar.parse_operators_catalog import RepositoryMap


def save_operator_usage_stats_to_db(
    repository_paths: RepositoryMap, catalog_image: str
) -> None:
    """Saves operator usage stats to the configured database.

    Args:
        repository_paths (RepositoryMap): Dictionary of key-value pairs,
        key being a quay repository and value being a list of OperatorBundle
        objects, images of which are stored in the repository.
        catalog_image (str): Operators catalog image.
    """
    catalog_name, ocp_version = extract_catalog_attributes(catalog_image)
    if catalog_name and ocp_version:
        logger.info(f"Saving data for catalog {catalog_image} to the database...")
        insert_data(repository_paths, catalog_name, ocp_version)
        logger.info("Data were successfully saved to the database.")
    else:
        logger.error(
            f"Cannot save data for {catalog_image} to the database. "
            "Catalog image format is not supported. Expected image format: "
            "<CATALOG_NAME>:<OCP_VERSION>. Please, re-run script"
            "to save retrieved pull stats to the database."
        )
