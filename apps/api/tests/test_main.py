import pytest
from fastapi.testclient import TestClient
from pathlib import Path


@pytest.fixture
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    """
    A fixture that sets up a test environment and returns a TestClient.
    """
    static_path = tmp_path / "static"
    static_path.mkdir()
    (static_path / "index.html").write_text("<html><body>Test</body></html>")

    monkeypatch.chdir(tmp_path)

    # delayed import to make sure static files are ready
    from app.main import app

    return TestClient(app)


def test_read_api_root(client: TestClient) -> None:
    """
    Tests the API's hello endpoint.
    """
    response = client.get("/api/v1/")

    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Pullsar API"}


def test_read_frontend_root(client: TestClient) -> None:
    """
    Tests that the root path ("/") serves the static index.html file correctly.
    """
    response = client.get("/")

    assert response.status_code == 200
    assert "<html><body>Test</body></html>" in response.text
