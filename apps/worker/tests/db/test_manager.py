from pytest_mock import MockerFixture
from pytest import LogCaptureFixture

from pullsar.db.manager import DatabaseManager
from pullsar.parse_operators_catalog import RepositoryMap
from pullsar.config import BaseConfig, DBConfig


def test_connect_success(mocker: MockerFixture) -> None:
    """
    Tests that the connect method correctly initializes the database connection
    and sets up the schema.
    """
    mock_connect = mocker.patch("psycopg2.connect")
    mock_conn = mock_connect.return_value
    mock_create_tables = mocker.patch("pullsar.db.manager.create_tables")
    mocker.patch.object(
        BaseConfig, "DB_CONFIG", DBConfig("db", "user", "pw", "host", 5432)
    )

    manager = DatabaseManager()
    manager.connect()

    mock_connect.assert_called_once_with(
        dbname="db",
        user="user",
        password="pw",
        host="host",
        port=5432,
        gssencmode="disable",
    )
    mock_create_tables.assert_called_once_with(mock_conn.cursor.return_value)
    mock_conn.commit.assert_called_once()


def test_save_stats_success(
    mocker: MockerFixture, sample_repo_map: RepositoryMap
) -> None:
    """
    Tests the success path of the save method, where data is correctly inserted.
    """
    mocker.patch(
        "pullsar.db.manager.extract_catalog_attributes",
        return_value=("community", "4.18"),
    )
    mock_insert = mocker.patch("pullsar.db.manager.insert_data")

    manager = DatabaseManager()
    manager.conn = mocker.Mock()
    manager.cur = mocker.Mock()

    manager.save_operator_usage_stats(sample_repo_map, "community:4.18")

    mock_insert.assert_called_once_with(
        manager.cur, sample_repo_map, "community", "4.18"
    )
    manager.conn.commit.assert_called_once()


def test_save_stats_parse_fail(
    mocker: MockerFixture, caplog: LogCaptureFixture, sample_repo_map: RepositoryMap
) -> None:
    """
    Tests that an error is logged and insert is not called if catalog parsing fails.
    """
    mocker.patch(
        "pullsar.db.manager.extract_catalog_attributes", return_value=(None, None)
    )
    mock_insert = mocker.patch("pullsar.db.manager.insert_data")

    manager = DatabaseManager()
    manager.conn = mocker.Mock()
    manager.cur = mocker.Mock()

    manager.save_operator_usage_stats(sample_repo_map, "bad-image-format")

    mock_insert.assert_not_called()
    assert "Cannot save data" in caplog.text


def test_save_stats_not_connected(
    mocker: MockerFixture, caplog: LogCaptureFixture, sample_repo_map: RepositoryMap
) -> None:
    """
    Tests that an error is logged if save is called before connect.
    """
    mock_insert = mocker.patch("pullsar.db.manager.insert_data")
    manager = DatabaseManager()

    manager.save_operator_usage_stats(sample_repo_map, "image:tag")

    mock_insert.assert_not_called()
    assert "Database is not connected" in caplog.text


def test_close_connection(mocker: MockerFixture) -> None:
    """Tests that the close method correctly closes the connection and cursor."""
    manager = DatabaseManager()
    manager.conn = mocker.Mock()
    manager.cur = mocker.Mock()

    manager.close()

    manager.cur.close.assert_called_once()
    manager.conn.close.assert_called_once()
