from psycopg2.extensions import cursor


def create_tables(cur: cursor) -> None:
    """
    For the configured database, create 3 tables:
    'bundles' to see individual operator bundles (versions),
    'bundle_appearances' to see which bundles appear in which catalogs,
    'pull_counts' to see how many times were bundles pulled
    from Quay on each date since recording started.
    """
    cur.execute("""
    CREATE TABLE IF NOT EXISTS bundles (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        package TEXT NOT NULL,
        image TEXT UNIQUE NOT NULL
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS bundle_appearances (
        id SERIAL PRIMARY KEY,
        bundle_id INTEGER NOT NULL REFERENCES bundles(id) ON DELETE CASCADE,
        catalog_name TEXT NOT NULL,
        ocp_version TEXT NOT NULL,
        UNIQUE (bundle_id, catalog_name, ocp_version)
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS pull_counts (
        id SERIAL PRIMARY KEY,
        bundle_id INTEGER NOT NULL REFERENCES bundles(id) ON DELETE CASCADE,
        pull_date DATE NOT NULL,
        pull_count INTEGER NOT NULL,
        UNIQUE (bundle_id, pull_date)
    );
    """)
