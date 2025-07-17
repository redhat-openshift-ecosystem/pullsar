import logging
from pytest_mock import MockerFixture

from pullsar.main import main, ParsedArgs


def test_main_with_json_files_and_debug(mocker: MockerFixture) -> None:
    """
    Simulates running the app with two JSON files and the --debug flag.
    """
    mock_args = ParsedArgs(
        debug=True,
        log_days=7,
        catalog_json_list=["file1.json", "file2.json"],
        catalog_image_list=[],
    )
    mocker.patch("pullsar.main.parse_arguments", return_value=mock_args)
    mocker.patch("pullsar.main.load_quay_api_tokens", return_value={})
    mock_quay_client = mocker.patch("pullsar.main.QuayClient")
    mock_update_stats = mocker.patch("pullsar.main.update_operator_usage_stats")
    mock_set_level = mocker.patch("pullsar.config.logger.setLevel")

    main()

    mock_set_level.assert_called_once_with(logging.DEBUG)
    mock_quay_client.assert_called_once()
    assert mock_update_stats.call_count == 2
    mock_update_stats.assert_any_call(mocker.ANY, 7, catalog_json_file="file1.json")
    mock_update_stats.assert_any_call(mocker.ANY, 7, catalog_json_file="file2.json")


def test_main_with_catalog_images(mocker: MockerFixture) -> None:
    """
    Simulates running the app with a catalog image and no debug flag.
    """
    mock_args = ParsedArgs(
        debug=False,
        log_days=30,
        catalog_json_list=[],
        catalog_image_list=["image:1.0", "image:2.0", "image:3.0"],
    )
    mocker.patch("pullsar.main.parse_arguments", return_value=mock_args)
    mocker.patch("pullsar.main.load_quay_api_tokens")
    mocker.patch("pullsar.main.QuayClient")
    mock_update_stats = mocker.patch("pullsar.main.update_operator_usage_stats")
    mock_set_level = mocker.patch("pullsar.config.logger.setLevel")

    main()

    mock_set_level.assert_not_called()
    mock_update_stats.assert_any_call(mocker.ANY, 30, catalog_image="image:1.0")
    mock_update_stats.assert_any_call(mocker.ANY, 30, catalog_image="image:2.0")
    mock_update_stats.assert_any_call(mocker.ANY, 30, catalog_image="image:3.0")
