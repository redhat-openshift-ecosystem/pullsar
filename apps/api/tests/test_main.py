from fastapi.testclient import TestClient


def test_read_root(client: TestClient) -> None:
    """
    Tests the root endpoint to ensure it returns a successful
    response and the correct welcome message.
    """
    response = client.get("/v1/")

    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Pullsar API"}
