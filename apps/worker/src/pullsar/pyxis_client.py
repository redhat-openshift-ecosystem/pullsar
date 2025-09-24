import requests
from typing import List, Dict, Any, Optional
from urllib.parse import quote
from requests_kerberos import HTTPKerberosAuth, DISABLED

from pullsar.config import logger, BaseConfig


class _BasePyxisClient:
    """A base client for Pyxis API containing shared client logic."""

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json"})

    def _fetch_paginated_data(
        self, endpoint: str, params: Dict[str, Any], auth: Any = None
    ) -> List[Dict[str, Any]]:
        """
        A generic helper to handle pagination for Pyxis API endpoints.
        It fetches all pages of data for a given endpoint and set of parameters.

        Args:
            endpoint: The API endpoint to query (e.g., "operators/indices").
            params: A dictionary of query parameters for the request.
            auth: The authentication handler to use (e.g., Kerberos), if any.

        Returns:
            List[Dict[str, Any]]: A list of all items fetched from all pages.
        """
        all_items = []
        page = 0
        while True:
            full_params: Dict[str, str | int] = {
                **params,
                "page_size": 100,
                "page": page,
            }
            api_url = f"{self.base_url}/{endpoint}"
            logger.debug(
                f"Fetching Pyxis data from {api_url} with params: {full_params}"
            )

            try:
                response = self.session.get(api_url, params=full_params, auth=auth)
                response.raise_for_status()
                data = response.json()
                items_on_page = data.get("data", [])
                if not items_on_page:
                    break

                all_items.extend(items_on_page)
                page += 1
            except requests.exceptions.RequestException as e:
                logger.error(f"Pyxis API request failed for endpoint {endpoint}: {e}")
                return []
        return all_items


class PyxisClient(_BasePyxisClient):
    """A client for interacting with the Pyxis API. Uses mTLS or Kerberos authentication."""

    def __init__(self, base_url: str):
        super().__init__(base_url)
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

        Args:
            registry (str): The image registry e.g. "registry.connect.redhat.com".
            repo_path (str): The repository path, e.g., "abinitio/runtime-operator-bundle".
            include (str): The fields to include in the API response.

        Returns:
            List[Dict[str, Any]]: A list of all image data objects for given registry and repository path.
        """
        encoded_repo = quote(repo_path, safe="")
        endpoint = f"repositories/registry/{registry}/repository/{encoded_repo}/images"
        params = {"include": include}

        all_images = self._fetch_paginated_data(endpoint, params, auth=self.auth_method)

        logger.info(f"Found {len(all_images)} images in Pyxis for repo {repo_path}")
        return all_images


class PyxisClientPublic(_BasePyxisClient):
    """
    A client for interacting with the Pyxis API with no authentication.
    Used for discovering externally available data.
    """

    def get_operator_indices(
        self,
        ocp_versions_range: str,
        include: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Fetches all operator indices from the public Pyxis API for a given OCP version.

        Args:
            ocp_versions_range (str): OCP version range, e.g. '4.8' means version 4.8 and above,
                see Pyxis API endpoint operators/indices for more details on the range format.
            include (Optional[str]): The fields to include in the API response.
            filter (Optional[str]): The filter to query results by.

        Returns:
            List[Dict[str, Any]]: List of all supported index data objects. Key fields include
                'organization' - e.g. 'community-operators'
                'path' - e.g. <CATALOG_IMAGE_NAME>:<OCP_VERSION>
        """
        endpoint = "operators/indices"
        params = {"ocp_versions_range": ocp_versions_range}
        if filter:
            params["filter"] = filter
        if include:
            params["include"] = include

        all_indices = self._fetch_paginated_data(endpoint, params)
        return all_indices
