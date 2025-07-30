import pytest
from datetime import date

from pullsar.parse_operators_catalog import RepositoryMap
from pullsar.operator_bundle_model import OperatorBundle


@pytest.fixture
def sample_repo_map() -> RepositoryMap:
    """Provides a sample RepositoryMap."""
    bundles = [
        OperatorBundle(name="op-a.v1", package="op-a", image="quay.io/org/repo:v1"),
        OperatorBundle(name="op-a.v2", package="op-a", image="quay.io/org/repo:v2"),
        OperatorBundle(name="op-a.v3", package="op-a", image="quay.io/org/repo:v3"),
    ]
    bundles[0].pull_count[date(2025, 7, 20)] = 5
    bundles[1].pull_count[date(2025, 7, 21)] = 10
    bundles[2].pull_count[date(2025, 7, 21)] = 15
    return {"org/repo": bundles}
