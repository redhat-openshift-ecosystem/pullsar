import requests
from typing import List, Dict, Any
from urllib.parse import quote
from requests_kerberos import HTTPKerberosAuth, DISABLED

from pullsar.config import logger


class PyxisClient:
    """A client for interacting with the Pyxis API."""

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json"})
        self.kerberos_auth = HTTPKerberosAuth(mutual_authentication=DISABLED)

    def get_images_for_repository(self, repo_path: str) -> List[Dict[str, Any]]:
        """
        Fetches all image data for a given repository from Pyxis.
        Handles pagination automatically.

        Args:
            repo_path (str): The repository path, e.g., "abinitio/runtime-operator-bundle"

        Returns:
            A list of all image data objects from all pages.
        """
        encoded_repo = quote(repo_path, safe="")
        endpoint = f"repositories/registry/registry.connect.redhat.com/repository/{encoded_repo}/images"
        fields = "data.image_id,data.repositories.registry,data.repositories.repository"

        all_images = []
        page = 0
        while True:
            api_url = f"{self.base_url}/{endpoint}"
            params: Dict[str, str | int] = {
                "page_size": 100,
                "page": page,
                "include": fields,
            }
            logger.debug(f"Fetching Pyxis data from {api_url} with params: {params}")

            try:
                response = self.session.get(
                    api_url, params=params, auth=self.kerberos_auth
                )
                response.raise_for_status()
                data = response.json()

                images_on_page = data.get("data", [])
                if not images_on_page:
                    break

                all_images.extend(images_on_page)
                page += 1

            except requests.exceptions.RequestException as e:
                logger.error(f"Pyxis API request failed for repo {repo_path}: {e}")
                return []

        logger.info(f"Found {len(all_images)} images in Pyxis for repo {repo_path}")
        return all_images
