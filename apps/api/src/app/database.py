import psycopg2
from psycopg2.extensions import cursor
from typing import Generator

from app.config import DB_CONFIG


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
        conn = psycopg2.connect(
            dbname=DB_CONFIG.dbname,
            user=DB_CONFIG.user,
            password=DB_CONFIG.password,
            host=DB_CONFIG.host,
            port=DB_CONFIG.port,
            gssencmode="disable",
        )
        cur = conn.cursor()
        yield cur
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
