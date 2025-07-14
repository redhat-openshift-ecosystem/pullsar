import pytest

from pullsar.cli import parse_arguments
from pullsar.config import BaseConfig


def test_parse_arguments_defaults() -> None:
    """Test that default values are set correctly."""
    parsed_args = parse_arguments([])
    assert parsed_args.debug is False
    assert parsed_args.log_days == BaseConfig.LOG_DAYS_DEFAULT
    assert parsed_args.catalog_json_list == []
    assert parsed_args.catalog_image_list == []


def test_log_days_valid_range() -> None:
    """Test that a valid --log-days value is accepted."""
    args_list = ["--log-days", "15"]
    parsed_args = parse_arguments(args_list)
    assert parsed_args.log_days == 15


def test_log_days_invalid_above_max() -> None:
    """Test that a --log-days value above the max raises SystemExit."""
    invalid_days = BaseConfig.LOG_DAYS_MAX + 1
    args_list = ["--log-days", str(invalid_days)]

    with pytest.raises(SystemExit):
        parse_arguments(args_list)


def test_log_days_invalid_below_min() -> None:
    """Test that a --log-days value below the min raises SystemExit."""
    invalid_days = BaseConfig.LOG_DAYS_MIN - 1
    args_list = ["--log-days", str(invalid_days)]

    with pytest.raises(SystemExit):
        parse_arguments(args_list)


def test_log_days_invalid_type() -> None:
    """Test that non-integer --log-days raises SystemExit."""
    args_list = ["--log-days", "not-a-number"]

    with pytest.raises(SystemExit):
        parse_arguments(args_list)


def test_mutually_exclusive_group_error() -> None:
    """Test that argparse raises an error if both catalog types are provided."""
    args_list = ["--catalog-json-file", "file.json", "--catalog-image", "image:latest"]

    with pytest.raises(SystemExit):
        parse_arguments(args_list)


def test_multiple_options_at_once() -> None:
    """Test that multiple options are parsed correctly."""
    args_list = [
        "--catalog-image",
        "image:1",
        "--catalog-image",
        "image:2",
        "--catalog-image",
        "image:3",
        "--debug",
        "--log-days",
        "30",
    ]
    parsed_args = parse_arguments(args_list)
    image1, image2, image3 = parsed_args.catalog_image_list

    assert image1 == "image:1"
    assert image2 == "image:2"
    assert image3 == "image:3"
    assert parsed_args.debug is True
    assert parsed_args.log_days == 30
