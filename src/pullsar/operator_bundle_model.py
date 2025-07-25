from typing import Optional, Tuple, Dict
from datetime import date

ImageAttributes = Tuple[
    Optional[str], Optional[str], Optional[str], Optional[str], Optional[str]
]
CatalogAttributes = Tuple[Optional[str], Optional[str]]


def extract_catalog_attributes(catalog_image: str) -> CatalogAttributes:
    """
    Parses catalog pullspec for attributes catalog name and OCP version.

    Args:
        catalog_image (str): format, e.g. <CATALOG_NAME>:<OCP_VERSION>,
        OCP version 'latest' is not allowed.

    Returns:
        CatalogAttributes: Tuple with catalog name and OCP version, or both
        being None if the format is invalid.
    """
    if ":" in catalog_image:
        catalog, ocp_version = catalog_image.split(":", 1)
        if ocp_version != "latest":
            return (catalog, ocp_version)
    return (None, None)


def extract_image_attributes(
    image: str,
) -> ImageAttributes:
    """
    Parses image pullspec for attributes Quay registry, organization, repository and image digest/tag.

    Args:
        image (str): Operator image pullspec of format: registry/org/repo@digest OR registry/org/repo:tag

    Returns:
        ImageAttributes: tuple of 5 attributes that can be extracted from image pullspec URL, in order,
        Quay registry, organization, repository, image digest, image tag;
        attributes can be None if they were not found or the input format was unexpected.
    """
    registry, org, repo, digest, tag = (None, None, None, None, None)
    registry_org_repo = image.split("/")

    if len(registry_org_repo) != 3:
        return (registry, org, repo, digest, tag)

    registry, org, repo_with_identifier = registry_org_repo
    if "@" in repo_with_identifier:
        repo_and_identifier = repo_with_identifier.split("@", 1)
        digest = repo_and_identifier[1]
    elif ":" in repo_with_identifier:
        repo_and_identifier = repo_with_identifier.split(":", 1)
        tag = repo_and_identifier[1]
    else:
        return (registry, org, repo, digest, tag)

    repo = repo_and_identifier[0]
    return (registry, org, repo, digest, tag)


def extract_tag(name: str) -> Optional[str]:
    """Parses operator name and accesses the version tag.

    Args:
        name (str): Name of the operator bundle, e.g.: operator.v0.1.0

    Returns:
        Optional[str]: Operator version tag (substring after the first dot)
        or None if the name is of unexpected format.
    """
    return name.split(".", 1)[1] if "." in name else None


class OperatorBundle:
    """
    Represents an OLM operator bundle with easy access to important properties.
    """

    def __init__(self, name: str, package: str, image: str):
        self._name = name
        self._package = package
        self._image = image
        self._tag = extract_tag(name)
        (self._registry, self._org, self._repo, self._digest, _) = (
            extract_image_attributes(image)
        )
        self._pull_count: Dict[date, int] = {}

    @property
    def name(self) -> str:
        """The name of the operator bundle with version tag."""
        return self._name

    @property
    def package(self) -> str:
        """The package name of the operator bundle."""
        return self._package

    @property
    def image(self) -> str:
        """The full image pull spec of the operator bundle."""
        return self._image

    @image.setter
    def image(self, new_image: str):
        """Sets the image of the operator bundle."""
        self._image = new_image

    @property
    def registry(self) -> Optional[str]:
        """The registry of the operator bundle image, e.g. quay.io"""
        return self._registry

    @property
    def org(self) -> Optional[str]:
        """The organization name of the operator bundle image."""
        return self._org

    @property
    def repo(self) -> Optional[str]:
        """The repository name of the operator bundle image."""
        return self._repo

    @property
    def tag(self) -> Optional[str]:
        """The version tag of the operator bundle and its image."""
        return self._tag

    @property
    def digest(self) -> Optional[str]:
        """The manifest digest of the operator bundle image."""
        return self._digest

    @digest.setter
    def digest(self, new_digest: str):
        """Sets the manifest digest of the operator bundle image."""
        self._digest = new_digest

    @property
    def repo_path(self) -> Optional[str]:
        """Accesses path to the repository of the operator bundle.

        Returns:
            Optional[str]: path to repository, e.g. org/repo
            or None if org or repo is None.
        """
        if self.org and self.repo:
            return f"{self.org}/{self.repo}"

        return None

    @property
    def pull_count(self) -> Dict[date, int]:
        """
        Accesses pull counts of an operator bundle for specific dates.

        Returns:
            Dict[date, int]: Dictionary of key-value pairs, key being a date
            and value being an integer representing a number of pulls recorded
            for the operator bundle for that date.
        """
        return self._pull_count

    def update_image_digest(self, new_digest: str):
        """Updates image URL to have new digest identifier."""
        if self.repo_path:
            self.image = f"{self.registry}/{self.repo_path}@{new_digest}"
            self.digest = new_digest

    def __str__(self) -> str:
        return f"""Name: {self.name}
Package: {self.package}
Image: {self.image}
    Registry: {self.registry}
    Org: {self.org}
    Repo: {self.repo}
    Tag: {self.tag}
    Digest: {self.digest}
    Pull Count: {self.pull_count}"""
