import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client(mock_env_vars: None) -> TestClient:
    """
    A fixture that creates a TestClient for the FastAPI app.
    It's scoped to 'module' so the app is imported only once per test file.
    """
    from app.main import app

    return TestClient(app)


@pytest.fixture(scope="module")
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
    monkeypatch.setenv("API_DB_START_DATE", "2025-08-08")
