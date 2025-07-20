from pullsar.parse_operators_catalog import RepositoryMap
from pullsar.db.connection import managed_db_cursor


def insert_data(
    repository_paths: RepositoryMap, catalog_name: str, ocp_version: str
) -> None:
    """Inserts data into the set up 3-table schema."""
    with managed_db_cursor() as cur:
        for operator_bundles in repository_paths.values():
            for bundle in operator_bundles:
                # add bundle
                cur.execute(
                    """
                INSERT INTO bundles (name, package, image)
                VALUES (%s, %s, %s)
                ON CONFLICT (image) DO UPDATE
                SET package = EXCLUDED.package, name = EXCLUDED.name
                RETURNING id;
                """,
                    (bundle.name, bundle.package, bundle.image),
                )

                result = cur.fetchone()
                if not result:
                    continue

                bundle_id = result[0]

                # enter bundle's appearance in catalog
                cur.execute(
                    """
                INSERT INTO bundle_appearances (bundle_id, catalog_name, ocp_version)
                VALUES (%s, %s, %s)
                ON CONFLICT (bundle_id, catalog_name, ocp_version) DO NOTHING;
                """,
                    (bundle_id, catalog_name, ocp_version),
                )

                # update bundle's pull counts
                for pull_date, pull_count in bundle.pull_count.items():
                    cur.execute(
                        """
                    INSERT INTO pull_counts (bundle_id, pull_date, pull_count)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (bundle_id, pull_date)
                    DO UPDATE SET pull_count = EXCLUDED.pull_count;
                    """,
                        (bundle_id, pull_date, pull_count),
                    )
