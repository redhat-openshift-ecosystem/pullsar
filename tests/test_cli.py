import pytest
from typing import List

from pullsar.cli import parse_arguments, ParsedArgs, ParsedCatalogArg
from pullsar.config import BaseConfig


@pytest.mark.parametrize(
    ["args_list", "expected"],
    [
        ([], None),
        (
            ["--catalog-image", "image:1", "--test"],
            ParsedArgs(
                True,
                False,
                BaseConfig.LOG_DAYS_DEFAULT,
                [ParsedCatalogArg("image:1", None)],
            ),
        ),
        (["--log-days", str(BaseConfig.LOG_DAYS_MAX + 1)], None),
        (["--log-days", str(BaseConfig.LOG_DAYS_MIN - 1)], None),
        (["--log-days", "not-a-number"], None),
        (["--catalog-image", "image:latest", "rendered.json", "extra_arg"], None),
        (
            [
                "--catalog-image",
                "image:1",
                "--catalog-image",
                "image:2",
                "rendered.json",
                "--catalog-image",
                "image:3",
                "--debug",
                "--log-days",
                "30",
                "--dry-run",
            ],
            ParsedArgs(
                True,
                True,
                30,
                [
                    ParsedCatalogArg("image:1", None),
                    ParsedCatalogArg("image:2", "rendered.json"),
                    ParsedCatalogArg("image:3", None),
                ],
            ),
        ),
    ],
)
def test_parse_arguments(args_list: List[str], expected: ParsedArgs | None) -> None:
    if expected:
        assert parse_arguments(args_list) == expected
    else:
        with pytest.raises(SystemExit):
            parse_arguments(args_list)
