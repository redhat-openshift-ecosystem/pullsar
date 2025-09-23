import psycopg2
from psycopg2.extensions import cursor, connection
from typing import Generator

from app.config import DB_CONFIG, load_db_dependent_config, logger


def get_db_connection() -> connection:
    """
    Creates and returns a raw database connection.
    The caller is responsible for closing the connection.
    """
    return psycopg2.connect(
        dbname=DB_CONFIG.dbname,
        user=DB_CONFIG.user,
        password=DB_CONFIG.password,
        host=DB_CONFIG.host,
        port=DB_CONFIG.port,
        gssencmode="disable",
    )


def get_db_cursor() -> Generator[cursor, None, None]:
    """
    A FastAPI dependency that creates and yields a database cursor,
    ensuring the connection is always closed. The gssencmode='disable'
    option is used to disable GSSAPI authentication and allow us to
    use password authentication instead.
    """
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        yield cur
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def initialize_db_config():
    """
    Establishes a temporary database connection to load and cache
    database-dependent configurations at application startup.
    This function is designed to be called from within the lifespan manager.
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        load_db_dependent_config(cursor)
        cursor.close()
    except Exception as e:
        logger.error(f"Could not load database-dependent configuration: {e}")
        raise
    finally:
        if conn:
            conn.close()
