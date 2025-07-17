import pytest
from typing import List

from pullsar.cli import parse_arguments, ParsedArgs
from pullsar.config import BaseConfig


@pytest.mark.parametrize(
    ["args_list", "expected"],
    [
        ([], ParsedArgs(False, BaseConfig.LOG_DAYS_DEFAULT, [], [])),
        (["--log-days", "15"], ParsedArgs(False, 15, [], [])),
        (["--log-days", str(BaseConfig.LOG_DAYS_MAX + 1)], None),
        (["--log-days", str(BaseConfig.LOG_DAYS_MIN - 1)], None),
        (["--log-days", "not-a-number"], None),
        (["--catalog-json-file", "file.json", "--catalog-image", "image:latest"], None),
        (
            [
                "--catalog-image",
                "image:1",
                "--catalog-image",
                "image:2",
                "--catalog-image",
                "image:3",
                "--debug",
                "--log-days",
                "30",
            ],
            ParsedArgs(True, 30, [], ["image:1", "image:2", "image:3"]),
        ),
    ],
)
def test_parse_arguments(args_list: List[str], expected: ParsedArgs | None) -> None:
    if expected:
        assert parse_arguments(args_list) == expected
    else:
        with pytest.raises(SystemExit):
            parse_arguments(args_list)
