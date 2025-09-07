import requests
import os
from typing import List, Dict, Any
from urllib.parse import quote
from requests_kerberos import HTTPKerberosAuth, DISABLED

from pullsar.config import logger, BaseConfig


class PyxisClient:
    """A client for interacting with the Pyxis API."""

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json"})
        self.auth_method = None

        cert_path = BaseConfig.CLIENT_CERT_PATH
        key_path = BaseConfig.CLIENT_KEY_PATH

        if cert_path and key_path:
            logger.info(
                "Found client certificate paths. Configuring mTLS authentication for Pyxis."
            )
            self.session.cert = (cert_path, key_path)
        else:
            logger.info(
                "Client certificate paths not found. Falling back to Kerberos authentication for Pyxis."
            )
            self.auth_method = HTTPKerberosAuth(mutual_authentication=DISABLED)

    def get_images_for_repository(
        self, registry: str, repo_path: str, include: str
    ) -> List[Dict[str, Any]]:
        """
        Fetches all image data for a given repository from Pyxis.
        Handles pagination automatically.

        Args:
            repo_path (str): The repository path, e.g., "abinitio/runtime-operator-bundle"

        Returns:
            A list of all image data objects from all pages.
        """
        encoded_repo = quote(repo_path, safe="")
        endpoint = f"repositories/registry/{registry}/repository/{encoded_repo}/images"

        all_images = []
        page = 0
        while True:
            api_url = f"{self.base_url}/{endpoint}"
            params: Dict[str, str | int] = {
                "page_size": 100,
                "page": page,
                "include": include,
            }
            logger.debug(f"Fetching Pyxis data from {api_url} with params: {params}")

            try:
                response = self.session.get(
                    api_url, params=params, auth=self.auth_method
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
