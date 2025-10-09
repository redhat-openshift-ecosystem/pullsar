CREATE TABLE IF NOT EXISTS bundles (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    package TEXT NOT NULL,
    image TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS bundle_appearances (
    id SERIAL PRIMARY KEY,
    bundle_id INTEGER NOT NULL REFERENCES bundles(id) ON DELETE CASCADE,
    catalog_name TEXT NOT NULL,
    ocp_version TEXT NOT NULL,
    UNIQUE (bundle_id, catalog_name, ocp_version)
);

CREATE TABLE IF NOT EXISTS pull_counts (
    id SERIAL PRIMARY KEY,
    bundle_id INTEGER NOT NULL REFERENCES bundles(id) ON DELETE CASCADE,
    pull_date DATE NOT NULL,
    pull_count INTEGER NOT NULL,
    UNIQUE (bundle_id, pull_date)
);

CREATE TABLE IF NOT EXISTS app_metadata (
    key VARCHAR(50) PRIMARY KEY,
    value VARCHAR(255) NOT NULL,
    description TEXT,
    last_updated TIMESTAMPTZ DEFAULT NOW()
);

INSERT INTO app_metadata (key, value, description)
VALUES ('db_start_date', CURRENT_DATE::text, 'The earliest date from which pull count data is available.')
ON CONFLICT (key) DO NOTHING;
