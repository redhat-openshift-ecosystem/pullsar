import logging
from pytest_mock import MockerFixture

from pullsar.main import main
from pullsar.cli import ParsedArgs, ParsedCatalogArg


def test_main_flow_with_db_and_debug(mocker: MockerFixture) -> None:
    """
    Simulates a full run with different catalog types, debug flag,
    and with the database enabled.
    """
    mock_args = ParsedArgs(
        dry_run=False,
        debug=True,
        log_days=7,
        catalogs=[
            ParsedCatalogArg("image:v1", None),
            ParsedCatalogArg("image:v2", "rendered.json"),
        ],
    )
    mocker.patch("pullsar.main.parse_arguments", return_value=mock_args)
    mocker.patch("pullsar.main.load_quay_api_tokens", return_value={})
    mocker.patch("pullsar.main.QuayClient")
    mock_is_db_configured = mocker.patch(
        "pullsar.main.is_database_configured", return_value=True
    )
    mock_create_tables = mocker.patch("pullsar.main.create_tables")
    mock_update_stats = mocker.patch(
        "pullsar.main.update_operator_usage_stats", return_value={"org/repo": []}
    )
    mock_save_to_db = mocker.patch("pullsar.main.save_operator_usage_stats_to_db")
    mock_set_level = mocker.patch("pullsar.config.logger.setLevel")

    main()

    mock_set_level.assert_called_once_with(logging.DEBUG)
    mock_is_db_configured.assert_called_once()
    mock_create_tables.assert_called_once()

    assert mock_update_stats.call_count == 2
    mock_update_stats.assert_any_call(mocker.ANY, 7, "image:v1", None)
    mock_update_stats.assert_any_call(mocker.ANY, 7, "image:v2", "rendered.json")

    assert mock_save_to_db.call_count == 2


def test_main_flow_with_dry_run(mocker: MockerFixture) -> None:
    """
    Simulates a run where the database is configured but --dry-run is enabled.
    """
    mock_args = ParsedArgs(
        dry_run=True,
        debug=False,
        log_days=30,
        catalogs=[ParsedCatalogArg("image:v3", None)],
    )
    mocker.patch("pullsar.main.parse_arguments", return_value=mock_args)
    mocker.patch("pullsar.main.load_quay_api_tokens")
    mocker.patch("pullsar.main.QuayClient")
    mocker.patch("pullsar.main.is_database_configured", return_value=True)
    mock_create_tables = mocker.patch("pullsar.main.create_tables")
    mocker.patch(
        "pullsar.main.update_operator_usage_stats", return_value={"org/repo": []}
    )
    mock_save_to_db = mocker.patch("pullsar.main.save_operator_usage_stats_to_db")

    main()

    mock_create_tables.assert_not_called()
    mock_save_to_db.assert_not_called()


def test_main_flow_with_db_not_configured(mocker: MockerFixture) -> None:
    """
    Simulates a run where the database is not configured.
    """
    mock_args = ParsedArgs(
        debug=False,
        log_days=7,
        catalogs=[ParsedCatalogArg("image:v4", None)],
        dry_run=False,
    )
    mocker.patch("pullsar.main.parse_arguments", return_value=mock_args)
    mocker.patch("pullsar.main.load_quay_api_tokens")
    mocker.patch("pullsar.main.QuayClient")
    mocker.patch("pullsar.main.is_database_configured", return_value=False)
    mock_create_tables = mocker.patch("pullsar.main.create_tables")
    mocker.patch(
        "pullsar.main.update_operator_usage_stats", return_value={"org/repo": []}
    )
    mock_save_to_db = mocker.patch("pullsar.main.save_operator_usage_stats_to_db")

    main()

    mock_create_tables.assert_not_called()
    mock_save_to_db.assert_not_called()
