import psycopg2
from psycopg2.extensions import cursor
from typing import Generator

from app.config import BaseConfig


def get_db_cursor() -> Generator[cursor, None, None]:
    """
    A FastAPI dependency that creates and yields a database cursor,
    ensuring the connection is always closed.
    """
    conn = None
    cur = None
    config = BaseConfig.DB_CONFIG
    try:
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
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
