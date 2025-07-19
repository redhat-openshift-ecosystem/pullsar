import contextlib
import psycopg2
from pullsar.config import BaseConfig


@contextlib.contextmanager
def managed_db_cursor():
    """
    A context manager for handling database connections and transactions.
    It automatically connects, commits, and closes the connection.
    """
    conn = None
    cur = None
    try:
        conn = psycopg2.connect(
            dbname=BaseConfig.DB_CONFIG["dbname"],
            user=BaseConfig.DB_CONFIG["user"],
            password=BaseConfig.DB_CONFIG["password"],
            host=BaseConfig.DB_CONFIG["host"],
            port=BaseConfig.DB_CONFIG["port"],
            gssencmode="disable",
        )
        cur = conn.cursor()
        yield cur
        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
