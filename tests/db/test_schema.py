from pytest_mock import MockerFixture

from pullsar.db import schema


def test_create_tables(mocker: MockerFixture) -> None:
    """Tests that create_tables executes the correct CREATE TABLE statements."""
    mock_connect = mocker.patch("psycopg2.connect")
    mock_conn = mock_connect.return_value
    mock_cur = mock_conn.cursor.return_value

    schema.create_tables()

    assert mock_cur.execute.call_count == 3
    sql_calls = "".join(call.args[0] for call in mock_cur.execute.call_args_list)
    assert "CREATE TABLE IF NOT EXISTS bundles" in sql_calls
    assert "CREATE TABLE IF NOT EXISTS bundle_appearances" in sql_calls
    assert "CREATE TABLE IF NOT EXISTS pull_counts" in sql_calls
