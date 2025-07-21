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
        config = BaseConfig.DB_CONFIG
        conn = psycopg2.connect(
            dbname=config.dbname,
            user=config.user,
            password=config.password,
            host=config.host,
            port=config.port,
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
