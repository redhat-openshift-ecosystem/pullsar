from typing import Dict, List, Any, NotRequired, TypedDict
from datetime import date

from pullsar.quay_client import QuayTag


PyxisImage = Dict[str, Any]


class PullLog(TypedDict):
    date: date
    tag: NotRequired[str]
    digest: NotRequired[str]


class CachedContext:
    """
    Holds the operator data cached during a single catalog processing run.
    When processing multiple versions of the same catalog, the operators are often repeated.
    The idea is to avoid repeating API calls for data we already asked for previously.

    Attributes:
        known_image_translations: A mapping from a non-quay image to its
            corresponding quay image representation.
        repo_path_to_logs: A dictionary caching Quay pull logs. Keys are
            repository paths and values are lists of filtered Quay logs.
        repo_path_to_pyxis_images: A dictionary caching Pyxis images. Keys are
            repository paths and values are lists of Pyxis images for that path.
        repo_path_to_tags: A dictionary caching Quay tags. Keys are repository
            paths and values are lists of all Quay tags for that path.
    """

    def __init__(self) -> None:
        self.known_image_translations: Dict[str, str] = {}
        self.repo_path_to_logs: Dict[str, List[PullLog]] = {}
        self.repo_path_to_pyxis_images: Dict[str, List[PyxisImage]] = {}
        self.repo_path_to_tags: Dict[str, List[QuayTag]] = {}
