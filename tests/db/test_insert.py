from pytest_mock import MockerFixture
from datetime import date

from pullsar.db import insert
from pullsar.parse_operators_catalog import RepositoryMap


def test_insert_data_with_multiple_bundles(
    mocker: MockerFixture, sample_repo_map: RepositoryMap
) -> None:
    """
    Tests that insert_data generates the correct SQL statements for multiple bundles.
    """
    mock_connect = mocker.patch("psycopg2.connect")
    mock_conn = mock_connect.return_value
    mock_cur = mock_conn.cursor.return_value

    mock_cur.fetchone.side_effect = [(1,), (2,), (3,)]

    insert.insert_data(mock_cur, sample_repo_map, "catalog-name", "v4.18")

    # 3 calls for each bundle: bundles, bundle_appearances, pull_counts
    assert mock_cur.execute.call_count == 9

    all_params = [call.args[1] for call in mock_cur.execute.call_args_list]

    assert ("op-a.v1", "op-a", "quay.io/org/repo:v1") in all_params
    assert ("op-a.v2", "op-a", "quay.io/org/repo:v2") in all_params
    assert ("op-a.v3", "op-a", "quay.io/org/repo:v3") in all_params

    assert (1, "catalog-name", "v4.18") in all_params
    assert (2, "catalog-name", "v4.18") in all_params
    assert (3, "catalog-name", "v4.18") in all_params

    assert (1, date(2025, 7, 20), 5) in all_params
    assert (2, date(2025, 7, 21), 10) in all_params
    assert (3, date(2025, 7, 21), 15) in all_params
