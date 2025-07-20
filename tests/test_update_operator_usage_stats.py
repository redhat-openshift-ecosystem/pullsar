import pytest
from pytest_mock import MockerFixture
from pytest import CaptureFixture
from datetime import date

from pullsar import update_operator_usage_stats as stats
from pullsar.operator_bundle_model import OperatorBundle
from pullsar.quay_client import QuayClient


@pytest.fixture
def sample_bundles() -> list[OperatorBundle]:
    """Provides a list of OperatorBundle objects for a single repo."""
    b1 = OperatorBundle("op.v1", "op", "quay.io/org/repo:v1")
    b2 = OperatorBundle("op.v2", "op", "quay.io/org/repo:v2")
    b3 = OperatorBundle("op.v3", "op", "quay.io/org/repo@sha256:abc")
    return [b1, b2, b3]


def test_tag_in_tag_map() -> None:
    """Tests the tag equivalence logic."""
    tag_map = {
        "v1.0": OperatorBundle("op.v1.0", "op", "img"),
        "2.0.0": OperatorBundle("op.2.0.0", "op", "img"),
    }
    assert stats.tag_in_tag_map("v1.0", tag_map) == "v1.0"
    assert stats.tag_in_tag_map("1.0", tag_map) == "v1.0"
    assert stats.tag_in_tag_map("v1.0.0", tag_map) is None

    assert stats.tag_in_tag_map("2.0.0", tag_map) == "2.0.0"
    assert stats.tag_in_tag_map("v2.0.0", tag_map) == "2.0.0"


def test_create_local_tag_digest_maps(sample_bundles: list[OperatorBundle]) -> None:
    """Tests the creation of local tag and digest maps."""
    tag_map, digest_map = stats.create_local_tag_digest_maps(sample_bundles)
    assert len(tag_map) == 3
    assert tag_map.get("v1") == sample_bundles[0]
    assert tag_map.get("v2") == sample_bundles[1]
    assert tag_map.get("v3") == sample_bundles[2]

    assert len(digest_map) == 1
    assert digest_map.get("sha256:abc") == sample_bundles[2]


def test_extract_date() -> None:
    """Tests the date extraction from Quay's log format."""
    datetime_str = "Mon, 14 Jul 2025 16:23:18 -0000"
    assert stats.extract_date(datetime_str) == date(2025, 7, 14)


def test_filter_pull_repo_logs() -> None:
    """Tests that 'pull_repo' logs are filtered and simplified."""
    quay_logs = [
        {"kind": "push_repo", "datetime": "Mon, 14 Jul 2025 10:00:00 -0000"},
        {
            "kind": "pull_repo",
            "datetime": "Tue, 15 Jul 2025 11:00:00 -0000",
            "metadata": {"tag": "v1"},
        },
        {
            "kind": "pull_repo",
            "datetime": "Wed, 16 Jul 2025 12:00:00 -0000",
            "metadata": {"manifest_digest": "sha256:123"},
        },
    ]
    pull_logs = stats.filter_pull_repo_logs(quay_logs)

    assert len(pull_logs) == 2
    assert pull_logs[0] == {"date": date(2025, 7, 15), "tag": "v1"}
    assert pull_logs[1] == {"date": date(2025, 7, 16), "digest": "sha256:123"}


def test_update_image_digests(
    mocker: MockerFixture, sample_bundles: list[OperatorBundle]
) -> None:
    """Tests that image digests are correctly updated from mocked Quay tags."""
    mock_quay_client = mocker.Mock(spec=QuayClient)
    mock_quay_client.get_repo_tags.return_value = [
        {"name": "1", "manifest_digest": "sha256:digest_for_v1"},
        {"name": "v2", "manifest_digest": "sha256:digest_for_v2"},
    ]
    repo_map = {"org/repo": sample_bundles}

    stats.update_image_digests(mock_quay_client, repo_map)

    # digests were updated
    assert sample_bundles[0].digest == "sha256:digest_for_v1"
    assert sample_bundles[1].digest == "sha256:digest_for_v2"
    # set digest stayed unchanged
    assert sample_bundles[2].digest == "sha256:abc"
    mock_quay_client.get_repo_tags.assert_called_once_with("org/repo")


def test_update_image_pull_counts(
    mocker: MockerFixture, sample_bundles: list[OperatorBundle]
) -> None:
    """Tests that pull counts are correctly retrieved from Quay logs."""
    mock_quay_client = mocker.Mock(spec=QuayClient)
    quay_logs = [
        {
            "kind": "pull_repo",
            "datetime": "Mon, 14 Jul 2025 10:00:00 -0000",
            "metadata": {"tag": "v1"},
        },
        {
            "kind": "pull_repo",
            "datetime": "Mon, 14 Jul 2025 11:00:00 -0000",
            "metadata": {"tag": "v1"},
        },
        {
            "kind": "push_repo",
            "datetime": "Mon, 14 Jul 2025 12:00:00 -0000",
            "metadata": {"tag": "v1.1"},
        },
        {
            "kind": "pull_repo",
            "datetime": "Tue, 15 Jul 2025 09:00:00 -0000",
            "metadata": {"manifest_digest": "sha256:abc"},
        },
    ]
    mock_quay_client.get_repo_logs.return_value = quay_logs
    repo_map = {"org/repo": sample_bundles}

    stats.update_image_pull_counts(mock_quay_client, repo_map, log_days=7)

    assert sample_bundles[0].pull_count == {date(2025, 7, 14): 2}
    assert sample_bundles[1].pull_count == {}
    assert sample_bundles[2].pull_count == {date(2025, 7, 15): 1}
    mock_quay_client.get_repo_logs.assert_called_once_with("org/repo", 7)


def test_update_image_pull_counts_no_logs(
    mocker: MockerFixture,
    sample_bundles: list[OperatorBundle],
) -> None:
    """
    Tests that the function handles the case where no logs are returned
    from the Quay API.
    """
    mock_quay_client = mocker.Mock(spec=QuayClient)
    mock_quay_client.get_repo_logs.return_value = []
    repo_map = {"org/repo": sample_bundles}

    stats.update_image_pull_counts(mock_quay_client, repo_map, log_days=7)

    for bundle in sample_bundles:
        assert bundle.pull_count == {}


def test_print_operator_usage_stats(
    capsys: CaptureFixture[str], sample_bundles: list[OperatorBundle]
) -> None:
    """Tests that only bundles with pull counts are printed."""
    sample_bundles[0].pull_count["07/14/2025"] = 5
    repo_map = {"org/repo": sample_bundles}

    stats.print_operator_usage_stats(repo_map)
    captured = capsys.readouterr()

    assert "op.v1" in captured.out
    assert "op.v2" not in captured.out


def test_update_operator_usage_stats_flow(mocker: MockerFixture) -> None:
    """
    Tests the main orchestration function, mocking its dependencies.
    """
    mock_render = mocker.patch(
        "pullsar.update_operator_usage_stats.render_operator_catalog"
    )
    mock_create_maps = mocker.patch(
        "pullsar.update_operator_usage_stats.create_repository_paths_maps",
        return_value=({"repo": []}, {"repo": []}, {"repo": []}),
    )
    mock_update_digests = mocker.patch(
        "pullsar.update_operator_usage_stats.update_image_digests"
    )
    mock_update_pulls = mocker.patch(
        "pullsar.update_operator_usage_stats.update_image_pull_counts"
    )
    mock_print_stats = mocker.patch(
        "pullsar.update_operator_usage_stats.print_operator_usage_stats"
    )
    mock_quay_client = mocker.Mock(spec=QuayClient)

    stats.update_operator_usage_stats(
        quay_client=mock_quay_client, log_days=7, catalog_image="my-image:latest"
    )

    mock_render.assert_called_once()
    mock_create_maps.assert_called_once()
    mock_update_digests.assert_called_once()
    mock_update_pulls.assert_called_once()
    mock_print_stats.assert_called_once()
