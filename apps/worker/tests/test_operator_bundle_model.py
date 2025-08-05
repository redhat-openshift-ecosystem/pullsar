import pytest

from pullsar.operator_bundle_model import (
    extract_image_attributes,
    extract_catalog_attributes,
    extract_tag,
    OperatorBundle,
    ImageAttributes,
    CatalogAttributes,
)


@pytest.mark.parametrize(
    ["image", "expected"],
    [
        (
            "quay.io/my-org/my-repo:v1.2.3",
            ("quay.io", "my-org", "my-repo", None, "v1.2.3"),
        ),
        (
            "quay.io/my-org/my-repo@sha256:abcdef123456",
            ("quay.io", "my-org", "my-repo", "sha256:abcdef123456", None),
        ),
        ("quay.io/my-repo-only", (None, None, None, None, None)),
        ("quay.io/my-org/my-repo", ("quay.io", "my-org", None, None, None)),
    ],
)
def test_extract_attributes_from_image(image: str, expected: ImageAttributes) -> None:
    """Test extracting attributes from image pullspec URL."""
    assert extract_image_attributes(image) == expected


def test_extract_tag_valid_name() -> None:
    """Test extracting a version tag from a standard bundle name."""
    name = "my-operator.v0.1.0"
    assert extract_tag(name) == "v0.1.0"


def test_extract_tag_no_dot() -> None:
    """Test a name with no version, expecting None."""
    name = "my-operator"
    assert extract_tag(name) is None


@pytest.mark.parametrize(
    ["image", "expected"],
    [
        ("community-operators:v4.18", ("community-operators", "v4.18")),
        ("community-operators", (None, None)),
        ("community-operators:latest", (None, None)),
    ],
)
def test_extract_catalog_attributes(image: str, expected: CatalogAttributes) -> None:
    assert extract_catalog_attributes(image) == expected


@pytest.fixture
def tagged_bundle() -> OperatorBundle:
    """A fixture for an OperatorBundle identified by a tag."""
    return OperatorBundle(
        name="alpha-operator.v1.0.0",
        package="alpha-operator",
        image="quay.io/alpha-org/alpha-repo:v1.0.0",
    )


@pytest.fixture
def digested_bundle() -> OperatorBundle:
    """A fixture for an OperatorBundle identified by a digest."""
    return OperatorBundle(
        name="beta-operator.v2.0.0",
        package="beta-operator",
        image="quay.io/beta-org/beta-repo@sha256:fake123",
    )


def test_bundle_initialization_with_tag(tagged_bundle: OperatorBundle) -> None:
    """Test that properties are correctly set for a tagged bundle."""
    assert tagged_bundle.name == "alpha-operator.v1.0.0"
    assert tagged_bundle.package == "alpha-operator"
    assert tagged_bundle.image == "quay.io/alpha-org/alpha-repo:v1.0.0"
    assert tagged_bundle.registry == "quay.io"
    assert tagged_bundle.org == "alpha-org"
    assert tagged_bundle.repo == "alpha-repo"
    assert tagged_bundle.tag == "v1.0.0"
    assert tagged_bundle.digest is None
    assert tagged_bundle.repo_path == "alpha-org/alpha-repo"
    assert tagged_bundle.pull_count == {}


def test_bundle_initialization_with_digest(digested_bundle: OperatorBundle) -> None:
    """Test that properties are correctly set for a digested bundle."""
    assert digested_bundle.name == "beta-operator.v2.0.0"
    assert digested_bundle.package == "beta-operator"
    assert digested_bundle.tag == "v2.0.0"
    assert digested_bundle.digest == "sha256:fake123"
    assert digested_bundle.repo_path == "beta-org/beta-repo"


def test_bundle_update_image_digest(tagged_bundle: OperatorBundle) -> None:
    """Test that the digest and image is set correctly."""
    assert tagged_bundle.digest is None
    tagged_bundle.update_image_digest("sha256:newdigest")
    assert tagged_bundle.digest == "sha256:newdigest"
    assert tagged_bundle.image == "quay.io/alpha-org/alpha-repo@sha256:newdigest"


def test_bundle_repo_path_none_case() -> None:
    """Test that repo_path is None if org or repo is missing."""
    bundle = OperatorBundle(name="invalid.v1", package="invalid", image="invalid-url")
    assert bundle.org is None
    assert bundle.repo is None
    assert bundle.repo_path is None


def test_bundle_str_method(tagged_bundle: OperatorBundle) -> None:
    """Test that the __str__ method returns a non-empty string."""
    assert isinstance(str(tagged_bundle), str)
    assert "Name: alpha-operator.v1.0.0" in str(tagged_bundle)
    assert "Package: alpha-operator" in str(tagged_bundle)
