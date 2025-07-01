from typing import Optional, Tuple, Dict


def extract_image_attributes(
    image: str,
) -> Tuple[Optional[str], Optional[str], Optional[str], Optional[str], Optional[str]]:
    """
    Parses image pullspec for attributes Quay registry, organization, repository and image sha/tag.

    Args:
        image (str): Operator image pullspec of format: quay.io/org/repo@sha OR quay.io/org/repo:tag

    Returns:
        Tuple[Optional[str], Optional[str], Optional[str], Optional[str], Optional[str]]: in order,
        Quay registry, organization, repository, image sha, image tag;
        attributes can be None if they were not found or the input format was unexpected.
    """
    # TODO: translate registry.connect.redhat.com proxy to quay.io registry if needed
    registry, org, repo, sha, tag = (None, None, None, None, None)
    registry_org_repo = image.split("/")

    if len(registry_org_repo) != 3:
        return (registry, org, repo, sha, tag)

    registry, org, repo_with_identifier = registry_org_repo
    if "@" in repo_with_identifier:
        repo_and_identifier = repo_with_identifier.split("@", 1)
        sha = repo_and_identifier[1]
    elif ":" in repo_with_identifier:
        repo_and_identifier = repo_with_identifier.split(":", 1)
        tag = repo_and_identifier[1]
    else:
        return (registry, org, repo, sha, tag)

    repo = repo_and_identifier[0]
    return (registry, org, repo, sha, tag)


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
    Represents an OLM operator bundle with getters for accessing important attributes.
    """

    def __init__(self, name: str, package: str, image: str):
        self.name = name
        self.package = package
        self.image = image
        self.tag = extract_tag(name)
        (self.registry, self.org, self.repo, self.sha, _) = extract_image_attributes(
            image
        )
        self.pull_count: Dict[str, int] = {}

    def get_name(self) -> str:
        return self.name

    def get_package(self) -> str:
        return self.package

    def get_image(self) -> str:
        return self.image

    def get_registry(self) -> Optional[str]:
        return self.registry

    def get_org(self) -> Optional[str]:
        return self.org

    def get_repo(self) -> Optional[str]:
        return self.repo

    def get_repo_path(self) -> Optional[str]:
        """Accesses path to Quay repository of the operator bundle.

        Returns:
            Optional[str]: path to Quay repository, e.g. org/repo
            or None if org or repo is None.
        """
        if self.org and self.repo:
            return f"{self.org}/{self.repo}"

        return None

    def get_tag(self) -> Optional[str]:
        return self.tag

    def get_sha(self) -> Optional[str]:
        return self.sha

    def set_sha(self, sha: str):
        self.sha = sha

    def get_pull_count(self) -> Dict[str, int]:
        """
        Accesses pull counts of an operator bundle for specific dates.

        Returns:
            Dict[str, int]: Dictionary of key-value pairs, key being a date,
            string formatted as: MM/DD/YYYY and value being an integer representing
            a number of pulls recorded for the operator bundle for that date.
        """
        return self.pull_count

    def __str__(self) -> str:
        return f"""Name: {self.get_name()}
Package: {self.get_package()}
Image: {self.get_image()}
    Registry: {self.get_registry()}
    Org: {self.get_org()}
    Repo: {self.get_repo()}
    Tag: {self.get_tag()}
    SHA: {self.get_sha()}
    Pull Count: {self.get_pull_count()}"""
