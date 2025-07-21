import requests
import pytest
from pytest_mock import MockerFixture
from pytest import LogCaptureFixture

from pullsar.pyxis_client import PyxisClient

BASE_URL = "https://my-fake-pyxis.com/v1"


@pytest.fixture
def client() -> PyxisClient:
    """Provides a PyxisClient instance for testing."""
    return PyxisClient(base_url=BASE_URL)


def test_get_images_single_page(client: PyxisClient, mocker: MockerFixture) -> None:
    """
    Tests the happy path where the API returns a single page of data.
    """
    mock_response_page1 = mocker.Mock()
    mock_response_page1.json.return_value = {"data": [{"image_id": "abc"}]}

    mock_response_page2 = mocker.Mock()
    mock_response_page2.json.return_value = {"data": []}

    mock_get = mocker.patch.object(
        client.session, "get", side_effect=[mock_response_page1, mock_response_page2]
    )

    images = client.get_images_for_repository("my-org/my-repo")

    assert len(images) == 1
    assert images[0]["image_id"] == "abc"

    assert mock_get.call_count == 2

    assert mock_get.call_args_list[0].kwargs["params"]["page"] == 0
    assert mock_get.call_args_list[1].kwargs["params"]["page"] == 1


def test_get_images_with_pagination(client: PyxisClient, mocker: MockerFixture) -> None:
    """
    Tests the pagination logic over multiple pages.
    """
    mock_response_page1 = mocker.Mock()
    mock_response_page1.json.return_value = {"data": [{"image_id": "p1"}]}

    mock_response_page2 = mocker.Mock()
    mock_response_page2.json.return_value = {"data": [{"image_id": "p2"}]}

    mock_response_page3 = mocker.Mock()
    mock_response_page3.json.return_value = {"data": []}

    mocker.patch.object(
        client.session,
        "get",
        side_effect=[mock_response_page1, mock_response_page2, mock_response_page3],
    )

    images = client.get_images_for_repository("my-org/my-repo")

    assert len(images) == 2
    assert images == [{"image_id": "p1"}, {"image_id": "p2"}]


def test_get_images_request_fails(
    client: PyxisClient, mocker: MockerFixture, caplog: LogCaptureFixture
) -> None:
    """
    Tests that an empty list is returned and an error is logged if the request fails.
    """
    mocker.patch.object(
        client.session,
        "get",
        side_effect=requests.exceptions.RequestException("Connection error"),
    )

    images = client.get_images_for_repository("my-org/my-repo")

    assert images == []
    assert "Pyxis API request failed for repo my-org/my-repo" in caplog.text
    assert "Connection error" in caplog.text


def test_repository_path_encoding(client: PyxisClient, mocker: MockerFixture) -> None:
    """
    Tests that the repository path is correctly URL-encoded.
    """
    mock_response = mocker.Mock()
    mock_response.json.return_value = {"data": []}
    mock_get = mocker.patch.object(client.session, "get", return_value=mock_response)

    repo_with_slash = "my-org/my-repo"
    client.get_images_for_repository(repo_with_slash)

    expected_url = f"{BASE_URL}/repositories/registry/registry.connect.redhat.com/repository/my-org%2Fmy-repo/images"
    called_url = mock_get.call_args.args[0]
    assert called_url == expected_url
