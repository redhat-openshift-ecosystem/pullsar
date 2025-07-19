from datetime import datetime
from typing import List

from pullsar.operator_bundle_model import OperatorBundle
from pullsar.db.connection import managed_db_cursor


def insert_data(
    operator_bundles: List[OperatorBundle], catalog_name: str, ocp_version: str
) -> None:
    """Inserts data into the set up 3-table schema."""
    with managed_db_cursor() as cur:
        for bundle in operator_bundles:
            # add bundle
            cur.execute(
                """
            INSERT INTO bundles (name, package, image)
            VALUES (%s, %s, %s)
            ON CONFLICT (name) DO UPDATE
            SET package = EXCLUDED.package, image = EXCLUDED.image
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
            for date_str, count in bundle.pull_count.items():
                # convert to YYYY-MM-DD for DATE type
                # TODO: have filter_pull_repo_logs() produce right date format
                # rightaway, so this conversion is not needed
                pull_date = datetime.strptime(date_str, "%m/%d/%Y").date()
                cur.execute(
                    """
                INSERT INTO pull_counts (bundle_id, pull_date, pull_count)
                VALUES (%s, %s, %s)
                ON CONFLICT (bundle_id, pull_date)
                DO UPDATE SET pull_count = EXCLUDED.pull_count;
                """,
                    (bundle_id, pull_date, count),
                )
