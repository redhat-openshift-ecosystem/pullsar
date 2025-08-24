import pytest


@pytest.fixture(autouse=True)
def mock_env_vars() -> None:
    """
    A fixture that automatically mocks the necessary environment
    variables for all tests in this directory.
    """
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setenv("DB_NAME", "test_db")
    monkeypatch.setenv("DB_USER", "test_user")
    monkeypatch.setenv("DB_PASSWORD", "test_password")
    monkeypatch.setenv("DB_HOST", "localhost")
    monkeypatch.setenv("DB_PORT", "5432")
