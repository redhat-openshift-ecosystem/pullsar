from datetime import date
from psycopg2.extensions import cursor


def fetch_db_start_date(db_cursor: cursor) -> date:
    """
    Fetches the 'db_start_date' value from the 'app_metadata' table.

    Args:
        db_cursor (cursor): An active database cursor.

    Raises:
        RuntimeError: If the 'db_start_date' key is not found in the table.

    Returns:
        date: The configured start date.
    """
    db_cursor.execute("SELECT value FROM app_metadata WHERE key = 'db_start_date'")
    result = db_cursor.fetchone()
    if not result:
        raise RuntimeError("Configuration 'db_start_date' not found in the database.")

    return date.fromisoformat(result[0])
