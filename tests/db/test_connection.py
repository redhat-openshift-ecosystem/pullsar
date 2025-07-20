import pytest
from pytest_mock import MockerFixture

from pullsar.db import connection


def test_managed_db_cursor_success(mocker: MockerFixture) -> None:
    """Tests that the context manager commits and closes on success."""
    mock_connect = mocker.patch("psycopg2.connect")
    mock_conn = mock_connect.return_value
    mock_cur = mock_conn.cursor.return_value

    with connection.managed_db_cursor() as cur:
        cur.execute("TEST")

    mock_connect.assert_called_once()
    mock_conn.cursor.assert_called_once()
    mock_cur.execute.assert_called_with("TEST")
    mock_conn.commit.assert_called_once()
    mock_cur.close.assert_called_once()
    mock_conn.close.assert_called_once()


def test_managed_db_cursor_failure(mocker: MockerFixture) -> None:
    """Tests that the context manager rolls back and closes on failure."""
    mock_connect = mocker.patch("psycopg2.connect")
    mock_conn = mock_connect.return_value

    with pytest.raises(ValueError, match="Test error"):
        with connection.managed_db_cursor():
            raise ValueError("Test error")

    mock_conn.rollback.assert_called_once()
    mock_conn.commit.assert_not_called()
    mock_conn.close.assert_called_once()
