import psycopg2

from pullsar.config import BaseConfig, logger
from pullsar.operator_bundle_model import extract_catalog_attributes
from pullsar.parse_operators_catalog import RepositoryMap
from pullsar.db.schema import create_tables
from pullsar.db.insert import insert_data


class DatabaseManager:
    """Manages the lifecycle of a single database connection for the application run."""

    def __init__(self):
        self.conn = None
        self.cur = None

    def connect(self):
        """Opens the database connection."""
        if self.conn:
            return

        config = BaseConfig.DB_CONFIG
        self.conn = psycopg2.connect(
            dbname=config.dbname,
            user=config.user,
            password=config.password,
            host=config.host,
            port=config.port,
            gssencmode="disable",
        )
        self.cur = self.conn.cursor()
        logger.info("Database connection established.")
        create_tables(self.cur)
        self.conn.commit()

    def save_operator_usage_stats(
        self, repository_paths: RepositoryMap, catalog_image: str
    ) -> None:
        """Saves operator usage stats to the configured database.

        Args:
            repository_paths (RepositoryMap): Dictionary of key-value pairs,
            key being a quay repository and value being a list of OperatorBundle
            objects, images of which are stored in the repository.
            catalog_image (str): Operators catalog image.
        """
        if not self.conn or not self.cur:
            logger.error("Database is not connected. Cannot save results.")
            return

        catalog_name, ocp_version = extract_catalog_attributes(catalog_image)
        if catalog_name and ocp_version:
            logger.info(f"Saving data for catalog {catalog_image} to the database...")
            insert_data(self.cur, repository_paths, catalog_name, ocp_version)
            self.conn.commit()
            logger.info("Data were successfully saved to the database.")
        else:
            logger.error(
                f"Cannot save data for {catalog_image} to the database. "
                "Catalog image format is not supported. Expected image format: "
                "<CATALOG_NAME>:<OCP_VERSION>. Please, re-run script"
                "to save retrieved pull stats to the database."
            )

    def close(self):
        """Closes the database connection."""
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed.")
