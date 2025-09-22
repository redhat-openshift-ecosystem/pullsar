import pytest
from pytest_mock import MockerFixture
from pytest import CaptureFixture
from datetime import date
from typing import List

from pullsar.stats_resolver import OperatorUsageStatsResolver
from pullsar.operator_bundle_model import OperatorBundle
from pullsar.quay_client import QuayClient
from pullsar.pyxis_client import PyxisClient
from pullsar.parse_operators_catalog import RepositoryMap


@pytest.fixture
def stats() -> OperatorUsageStatsResolver:
    """Provides an OperatorUsageStatsResolver object."""
    return OperatorUsageStatsResolver()


@pytest.fixture
def sample_bundles() -> list[OperatorBundle]:
    """Provides a list of OperatorBundle objects for a single repo."""
    b1 = OperatorBundle("op.v1", "op", "quay.io/org/repo:v1")
    b2 = OperatorBundle("op.v2", "op", "quay.io/org/repo:v2")
    b3 = OperatorBundle("op.v3", "op", "quay.io/org/repo@sha256:abc")
    return [b1, b2, b3]


def test_tag_in_tag_map(stats: OperatorUsageStatsResolver) -> None:
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


def test_create_local_tag_digest_maps(
    stats: OperatorUsageStatsResolver, sample_bundles: list[OperatorBundle]
) -> None:
    """Tests the creation of local tag and digest maps."""
    tag_map, digest_map = stats.create_local_tag_digest_maps(sample_bundles)
    assert len(tag_map) == 3
    assert tag_map.get("v1") == sample_bundles[0]
    assert tag_map.get("v2") == sample_bundles[1]
    assert tag_map.get("v3") == sample_bundles[2]

    assert len(digest_map) == 1
    assert digest_map.get("sha256:abc") == sample_bundles[2]


def test_extract_date(stats: OperatorUsageStatsResolver) -> None:
    """Tests the date extraction from Quay's log format."""
    datetime_str = "Mon, 14 Jul 2025 16:23:18 -0000"
    assert stats.extract_date(datetime_str) == date(2025, 7, 14)


def test_filter_pull_repo_logs(stats: OperatorUsageStatsResolver) -> None:
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


@pytest.fixture
def bundles_to_translate() -> List[OperatorBundle]:
    """Provides a sample list of OperatorBundles that need translation."""
    bundle1 = OperatorBundle(
        name="op-a.v1",
        package="op-a",
        image="registry.connect.redhat.com/connect-org-a/repo-a@sha256:digest1",
    )
    bundle2 = OperatorBundle(
        name="op-b.v1",
        package="op-b",
        image="registry.connect.redhat.com/connect-org-b/repo-b@sha256:digest2",
    )
    return [bundle1, bundle2]


def test_resolve_repositories_success_with_multiple_bundles(
    mocker: MockerFixture,
    stats: OperatorUsageStatsResolver,
    bundles_to_translate: List[OperatorBundle],
) -> None:
    """
    Tests that multiple non-Quay bundles from different repositories are
    successfully resolved and updated.
    """
    mock_pyxis_client = mocker.Mock(spec=PyxisClient)

    fake_response1 = [
        {
            "image_id": "sha256:digest1",
            "repositories": [
                {"registry": "quay.io", "repository": "quay-org-a/repo-a"}
            ],
        }
    ]
    fake_response2 = [
        {
            "image_id": "sha256:digest2",
            "repositories": [
                {"registry": "quay.io", "repository": "quay-org-b/repo-b"}
            ],
        }
    ]

    mock_pyxis_client.get_images_for_repository.side_effect = [
        fake_response1,
        fake_response2,
    ]

    not_quay_map: RepositoryMap = {
        "connect-org-a/repo-a": [bundles_to_translate[0]],
        "connect-org-b/repo-b": [bundles_to_translate[1]],
    }
    quay_map: RepositoryMap = {}

    stats.resolve_not_quay_repositories(
        mock_pyxis_client,
        not_quay_map,
        quay_map,
    )

    assert len(quay_map) == 2
    assert "quay-org-a/repo-a" in quay_map
    assert "quay-org-b/repo-b" in quay_map

    bundle_a = quay_map["quay-org-a/repo-a"][0]
    assert bundle_a.name == "op-a.v1"
    assert bundle_a.image == "quay.io/quay-org-a/repo-a@sha256:digest1"

    bundle_b = quay_map["quay-org-b/repo-b"][0]
    assert bundle_b.name == "op-b.v1"
    assert bundle_b.image == "quay.io/quay-org-b/repo-b@sha256:digest2"

    known_images_map = stats._cache.known_image_translations
    assert len(known_images_map) == 2
    assert known_images_map[bundles_to_translate[0].image] == bundle_a.image
    assert known_images_map[bundles_to_translate[1].image] == bundle_b.image


def test_update_image_digests(
    mocker: MockerFixture,
    stats: OperatorUsageStatsResolver,
    sample_bundles: list[OperatorBundle],
) -> None:
    """Tests that image digests are correctly updated from mocked Quay tags."""
    tags = [
        {"name": "1", "manifest_digest": "sha256:digest_for_v1"},
        {"name": "v2", "manifest_digest": "sha256:digest_for_v2"},
    ]
    repo = "org/repo"

    mock_quay_client = mocker.Mock(spec=QuayClient)
    mock_quay_client.get_repo_tags.return_value = tags
    repo_map = {repo: sample_bundles}

    stats.update_image_digests(mock_quay_client, repo_map)

    # digests were updated
    assert sample_bundles[0].digest == "sha256:digest_for_v1"
    assert sample_bundles[1].digest == "sha256:digest_for_v2"
    # set digest stayed unchanged
    assert sample_bundles[2].digest == "sha256:abc"
    mock_quay_client.get_repo_tags.assert_called_once_with("org/repo")

    cached_repo_path_to_tags = stats._cache.repo_path_to_tags
    assert len(cached_repo_path_to_tags) == 1

    cached_repo_tags = cached_repo_path_to_tags[repo]
    assert len(cached_repo_tags) == 2
    assert tags[0] in cached_repo_tags
    assert tags[1] in cached_repo_tags


def test_update_image_pull_counts(
    mocker: MockerFixture,
    stats: OperatorUsageStatsResolver,
    sample_bundles: list[OperatorBundle],
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
    repo = "org/repo"

    mock_quay_client.get_repo_logs.return_value = quay_logs
    repo_map = {repo: sample_bundles}

    stats.update_image_pull_counts(mock_quay_client, repo_map, log_days=7)

    assert sample_bundles[0].pull_count == {date(2025, 7, 14): 2}
    assert sample_bundles[1].pull_count == {}
    assert sample_bundles[2].pull_count == {date(2025, 7, 15): 1}
    mock_quay_client.get_repo_logs.assert_called_once_with(repo, 7)

    cached_repo_path_to_logs = stats._cache.repo_path_to_logs
    assert len(cached_repo_path_to_logs) == 1

    cached_repo_logs = cached_repo_path_to_logs[repo]
    assert len(cached_repo_logs) == 3


def test_update_image_pull_counts_no_logs(
    mocker: MockerFixture,
    stats: OperatorUsageStatsResolver,
    sample_bundles: list[OperatorBundle],
) -> None:
    """
    Tests that the function handles the case where no logs are returned
    from the Quay API.
    """
    mock_quay_client = mocker.Mock(spec=QuayClient)
    mock_quay_client.get_repo_logs.return_value = []
    repo = "org/repo"
    repo_map = {repo: sample_bundles}

    stats.update_image_pull_counts(mock_quay_client, repo_map, log_days=7)

    for bundle in sample_bundles:
        assert bundle.pull_count == {}

    cached_repo_path_to_logs = stats._cache.repo_path_to_logs
    assert len(cached_repo_path_to_logs) == 1
    assert len(cached_repo_path_to_logs[repo]) == 0


def test_print_operator_usage_stats(
    capsys: CaptureFixture[str],
    stats: OperatorUsageStatsResolver,
    sample_bundles: list[OperatorBundle],
) -> None:
    """Tests that only bundles with pull counts are printed."""
    sample_bundles[0].pull_count[date(2025, 7, 14)] = 5
    repo_map = {"org/repo": sample_bundles}

    stats.print_operator_usage_stats(repo_map)
    captured = capsys.readouterr()

    assert "op.v1" in captured.out
    assert "op.v2" not in captured.out


def test_update_operator_usage_stats_flow(
    mocker: MockerFixture, stats: OperatorUsageStatsResolver
) -> None:
    """
    Tests the main orchestration function, mocking its dependencies.
    """
    mock_render = mocker.patch("pullsar.stats_resolver.render_operator_catalog")
    mock_create_maps = mocker.patch(
        "pullsar.stats_resolver.create_repository_paths_maps",
        return_value=({"repo": []}, {"repo": []}, {}),
    )

    mock_resolve_repos = mocker.patch(
        "pullsar.stats_resolver.OperatorUsageStatsResolver.resolve_not_quay_repositories"
    )
    mock_update_digests = mocker.patch(
        "pullsar.stats_resolver.OperatorUsageStatsResolver.update_image_digests"
    )
    mock_update_pulls = mocker.patch(
        "pullsar.stats_resolver.OperatorUsageStatsResolver.update_image_pull_counts"
    )
    mock_print_stats = mocker.patch(
        "pullsar.stats_resolver.OperatorUsageStatsResolver.print_operator_usage_stats"
    )
    mock_quay_client = mocker.Mock(spec=QuayClient)
    mock_pyxis_client = mocker.Mock(spec=PyxisClient)
    mock_pyxis_client.get_images_for_repository.return_value = {"data": []}

    stats.update_operator_usage_stats(
        quay_client=mock_quay_client,
        pyxis_client=mock_pyxis_client,
        log_days=7,
        catalog_image="my-image:latest",
    )

    mock_render.assert_called_once()
    mock_create_maps.assert_called_once()
    mock_resolve_repos.assert_called_once()
    mock_update_digests.assert_called_once()
    mock_update_pulls.assert_called_once()
    mock_print_stats.assert_called_once()
