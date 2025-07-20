import json
import pytest
from pytest import MonkeyPatch, LogCaptureFixture
from pytest_mock import MockerFixture

from pullsar.config import load_quay_api_tokens, is_database_configured, BaseConfig


def test_load_quay_api_tokens_success(monkeypatch: MonkeyPatch) -> None:
    """Test that tokens are loaded correctly from a valid JSON environment variable."""
    valid_json = '{"org1": "token1", "org2": "token2"}'
    monkeypatch.setenv("QUAY_API_TOKENS_JSON", valid_json)

    tokens = load_quay_api_tokens()

    expected_tokens = {"org1": "token1", "org2": "token2"}
    assert tokens == expected_tokens


def test_load_quay_api_tokens_not_set(
    monkeypatch: MonkeyPatch, caplog: LogCaptureFixture
) -> None:
    """
    Test that an empty dict is returned and a warning is logged
    when the environment variable is not set.
    """
    monkeypatch.delenv("QUAY_API_TOKENS_JSON", raising=False)

    tokens = load_quay_api_tokens()

    assert tokens == {}
    assert "QUAY_API_TOKENS_JSON is undefined" in caplog.text


def test_load_quay_api_tokens_invalid_json(
    monkeypatch: MonkeyPatch, caplog: LogCaptureFixture
) -> None:
    """
    Test that an error is logged and JSONDecodeError is raised
    for an invalid JSON string.
    """
    invalid_json = '{"org1": "token1", "org2": "token2"'
    monkeypatch.setenv("QUAY_API_TOKENS_JSON", invalid_json)

    with pytest.raises(json.JSONDecodeError):
        load_quay_api_tokens()

    assert "is not a valid JSON" in caplog.text


def test_is_database_configured_success(mocker: MockerFixture) -> None:
    """
    Tests that the function returns True when all DB config values are present.
    """
    mocker.patch.object(
        BaseConfig,
        "DB_CONFIG",
        {
            "dbname": "test_db",
            "user": "test_user",
            "password": "test_password",
            "host": "localhost",
        },
    )

    assert is_database_configured() is True


def test_is_database_configured_missing_value(
    mocker: MockerFixture, caplog: LogCaptureFixture
) -> None:
    """
    Tests that the function returns False and logs a warning when a value is missing.
    """
    mocker.patch.object(
        BaseConfig,
        "DB_CONFIG",
        {
            "dbname": "test_db",
            "user": "test_user",
            "password": None,
            "host": "localhost",
        },
    )

    assert is_database_configured() is False
    assert "To allow posting to database, set up database configuration" in caplog.text
