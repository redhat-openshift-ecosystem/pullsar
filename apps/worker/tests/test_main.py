import logging
from pytest_mock import MockerFixture

from pullsar.main import main
from pullsar.cli import ParsedArgs, ParsedCatalogArg
from pullsar.db.manager import DatabaseManager
from pullsar.stats_resolver import OperatorUsageStatsResolver


def test_main_flow_with_db_and_debug(mocker: MockerFixture) -> None:
    """
    Simulates a full run with the database enabled and debug flag on.
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
    mocker.patch("pullsar.main.is_database_configured", return_value=True)
    mock_resolver_instance = mocker.Mock(spec=OperatorUsageStatsResolver)
    mock_resolver_instance.update_operator_usage_stats.return_value = {"org/repo": []}
    mocker.patch(
        "pullsar.main.OperatorUsageStatsResolver", return_value=mock_resolver_instance
    )

    mock_set_level = mocker.patch("pullsar.config.logger.setLevel")

    mock_db_instance = mocker.Mock(spec=DatabaseManager)
    mock_db_class = mocker.patch(
        "pullsar.main.DatabaseManager", return_value=mock_db_instance
    )

    main()

    mock_set_level.assert_called_once_with(logging.DEBUG)
    mock_db_class.assert_called_once()
    mock_db_instance.connect.assert_called_once()

    assert mock_resolver_instance.update_operator_usage_stats.call_count == 2
    mock_resolver_instance.update_operator_usage_stats.assert_any_call(
        mocker.ANY,
        mocker.ANY,
        7,
        "image:v1",
        None,
    )
    mock_resolver_instance.update_operator_usage_stats.assert_any_call(
        mocker.ANY,
        mocker.ANY,
        7,
        "image:v2",
        "rendered.json",
    )

    assert mock_db_instance.save_operator_usage_stats.call_count == 2

    mock_db_instance.close.assert_called_once()


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
    mock_resolver_instance = mocker.Mock(spec=OperatorUsageStatsResolver)
    mock_resolver_instance.update_operator_usage_stats.return_value = {"org/repo": []}
    mocker.patch(
        "pullsar.main.OperatorUsageStatsResolver", return_value=mock_resolver_instance
    )

    mock_db_class = mocker.patch("pullsar.main.DatabaseManager")

    main()

    mock_db_class.assert_not_called()


def test_main_flow_with_db_not_configured(mocker: MockerFixture) -> None:
    """
    Simulates a run where the database is not configured.
    """
    mock_args = ParsedArgs(
        dry_run=False,
        debug=False,
        log_days=7,
        catalogs=[ParsedCatalogArg("image:v4", None)],
    )
    mocker.patch("pullsar.main.parse_arguments", return_value=mock_args)
    mocker.patch("pullsar.main.load_quay_api_tokens")
    mocker.patch("pullsar.main.QuayClient")
    mocker.patch("pullsar.main.is_database_configured", return_value=False)
    mock_resolver_instance = mocker.Mock(spec=OperatorUsageStatsResolver)
    mock_resolver_instance.update_operator_usage_stats.return_value = {"org/repo": []}
    mocker.patch(
        "pullsar.main.OperatorUsageStatsResolver", return_value=mock_resolver_instance
    )

    mock_db_class = mocker.patch("pullsar.main.DatabaseManager")

    main()

    mock_db_class.assert_not_called()
