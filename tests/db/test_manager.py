from pytest_mock import MockerFixture
from pytest import LogCaptureFixture

from pullsar.parse_operators_catalog import RepositoryMap
from pullsar.db.manager import save_operator_usage_stats_to_db


def test_save_operator_usage_stats_to_db_success(
    mocker: MockerFixture, sample_repo_map: RepositoryMap
) -> None:
    """Tests the success path of the save function."""
    mocker.patch(
        "pullsar.db.manager.extract_catalog_attributes",
        return_value=("community", "4.18"),
    )
    mock_insert = mocker.patch("pullsar.db.manager.insert_data")

    save_operator_usage_stats_to_db(sample_repo_map, "community:4.18")

    mock_insert.assert_called_once_with(sample_repo_map, "community", "4.18")


def test_save_operator_usage_stats_to_db_parse_fail(
    mocker: MockerFixture, caplog: LogCaptureFixture
) -> None:
    """Tests that an error is logged and insert is not called if catalog parsing fails."""
    mocker.patch(
        "pullsar.db.manager.extract_catalog_attributes", return_value=(None, None)
    )
    mock_insert = mocker.patch("pullsar.db.manager.insert_data")

    save_operator_usage_stats_to_db({}, "bad-image-format")

    mock_insert.assert_not_called()
    assert "Cannot save data" in caplog.text
