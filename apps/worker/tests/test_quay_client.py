import requests
import pytest
from pytest_mock import MockerFixture
from pytest import LogCaptureFixture

from pullsar.quay_client import QuayClient

BASE_URL = "https://quay.io/api/v1"
API_TOKENS = {"org-a": "token-a", "org-b": "token-b"}


@pytest.fixture
def client() -> QuayClient:
    """Provides a QuayClient instance for testing."""
    return QuayClient(base_url=BASE_URL, api_tokens=API_TOKENS)


def test_extract_org() -> None:
    """Tests the static method for extracting the organization."""
    assert QuayClient._extract_org("my-org/my-repo") == "my-org"


def test_token_not_defined(client: QuayClient, caplog: LogCaptureFixture) -> None:
    """
    Tests that an empty list is returned and an error is logged
    if the API token for an organization is not defined.
    """
    repo_path = "unknown-org/repo"

    results = client.get_repo_tags(repo_path)

    assert results == []
    assert "Quay API token not defined for organization 'unknown-org'" in caplog.text


def test_request_exception(
    client: QuayClient, mocker: MockerFixture, caplog: LogCaptureFixture
) -> None:
    """
    Tests that an empty list is returned and an error is logged
    when a request fails.
    """
    mocker.patch.object(
        client.session,
        "get",
        side_effect=requests.exceptions.RequestException("Timeout"),
    )
    repo_path = "org-a/repo"

    results = client.get_repo_tags(repo_path)

    assert results == []
    assert "Request error for org-a/repo: Timeout" in caplog.text


def test_pagination_with_next_page(client: QuayClient, mocker: MockerFixture) -> None:
    """
    Tests the pagination logic that uses a 'next_page' token (like for /logs).
    """
    mock_response_page1 = mocker.Mock()
    mock_response_page1.json.return_value = {
        "logs": [{"id": 1}],
        "next_page": "token123",
    }

    mock_response_page2 = mocker.Mock()
    mock_response_page2.json.return_value = {"logs": [{"id": 2}]}

    mock_get = mocker.patch.object(
        client.session, "get", side_effect=[mock_response_page1, mock_response_page2]
    )

    results = client.get_repo_logs("org-a/repo", log_days=7)

    assert len(results) == 2
    assert results == [{"id": 1}, {"id": 2}]
    assert mock_get.call_count == 2

    second_call_args = mock_get.call_args_list[1]
    assert second_call_args.kwargs["params"]["next_page"] == "token123"


def test_pagination_with_has_additional(
    client: QuayClient, mocker: MockerFixture
) -> None:
    """
    Tests the pagination logic that uses a 'has_additional' flag (like for /tag).
    """
    mock_response_page1 = mocker.Mock()
    mock_response_page1.json.return_value = {
        "tags": [{"name": "v1"}],
        "has_additional": True,
    }

    mock_response_page2 = mocker.Mock()
    mock_response_page2.json.return_value = {
        "tags": [{"name": "v2"}],
        "has_additional": False,
    }

    mock_get = mocker.patch.object(
        client.session, "get", side_effect=[mock_response_page1, mock_response_page2]
    )

    results = client.get_repo_tags("org-b/repo")

    assert len(results) == 2
    assert results == [{"name": "v1"}, {"name": "v2"}]
    assert mock_get.call_count == 2

    second_call_args = mock_get.call_args_list[1]
    assert second_call_args.kwargs["params"]["page"] == 2
