import requests
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta, timezone

from pullsar.config import logger

QuayOrgToTokenMap = Dict[str, str]
QuayLog = Dict[str, Any]
QuayTag = Dict[str, str]


class QuayClient:
    """
    A client for interacting with the Quay.io API, using a single session
    for all requests to improve performance.
    """

    def __init__(self, base_url: str, api_tokens: QuayOrgToTokenMap):
        """
        Initializes the QuayClient.

        Args:
            base_url (str): The base URL for the Quay API.
            api_tokens (QuayOrgToTokenMap): A dictionary mapping organization names
            to their API tokens.
        """
        self.base_url = base_url
        self.api_tokens = api_tokens
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json"})

    @staticmethod
    def _extract_org(repo_path: str) -> str:
        """
        Extracts Quay organization name from a valid Quay repository path.

        Args:
            repo_path (str): Format: "organization/repository".

        Returns:
            str: Quay organization name.
        """
        return repo_path.split("/")[0]

    def _make_paginated_request(
        self,
        repo_path: str,
        endpoint: str,
        results_key: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Makes a generic, paginated GET request to a Quay repository endpoint.

        It handles two types of pagination:
        1. 'next_page' token (used by /logs).
        2. 'page' number with 'has_additional' flag (used by /tag).

        Args:
            repo_path (str): The full repository path (e.g., "org/repo").
            endpoint (str): The API endpoint (e.g., "logs", "tag").
            results_key (str): The key in the JSON response containing the list of items.
            params (Optional[Dict[str, Any]]): Initial request parameters.

        Returns:
            List[Dict[str, Any]]: A list of all items retrieved from all pages.
        """
        org = self._extract_org(repo_path)
        api_token = self.api_tokens.get(org)

        if not api_token:
            logger.error(
                f"Quay API token not defined for organization '{org}'. Skipping repository {repo_path}..."
            )
            return []

        api_url = f"{self.base_url}/repository/{repo_path}/{endpoint}"
        api_headers = {"Authorization": f"Bearer {api_token}"}
        api_params = params.copy() if params else {}

        all_results = []
        page_num = 1

        while True:
            logger.debug(
                f"Fetching {results_key} for {repo_path}, params: {api_params}"
            )
            try:
                response = self.session.get(
                    api_url, headers=api_headers, params=api_params
                )
                response.raise_for_status()
                data = response.json()

                results = data.get(results_key, [])
                all_results.extend(results)
                logger.debug(f"Retrieved {len(results)} {results_key} from this page.")

                if "next_page" in data and data["next_page"]:
                    api_params["next_page"] = data["next_page"]
                elif data.get("has_additional"):
                    page_num += 1
                    api_params["page"] = page_num
                else:
                    break

            except requests.exceptions.RequestException as e:
                logger.error(f"Request error for {repo_path}: {e}. Skipping...")
                return []

        logger.info(
            f"Total {results_key} retrieved for {repo_path}: {len(all_results)}"
        )
        return all_results

    def get_repo_logs(self, repo_path: str, log_days: int) -> List[QuayLog]:
        """
        Fetches usage logs for a given Quay repository using Quay API.

        Args:
            repo_path (str): Format: "organization/repository".
            log_days (int): Fetch logs from the last 'log_days' completed days.

        Returns:
            List[Dict[str, any]]: All logs retrieved from Quay API.
        """
        logger.info(f"Fetching logs for repository: {repo_path}")

        end_time_utc = datetime.now(timezone.utc) - timedelta(days=1)
        start_time_utc = end_time_utc - timedelta(days=log_days - 1)
        time_params = {
            "starttime": start_time_utc.strftime("%m/%d/%Y"),
            "endtime": end_time_utc.strftime("%m/%d/%Y"),
        }

        return self._make_paginated_request(
            repo_path=repo_path,
            endpoint="logs",
            results_key="logs",
            params=time_params,
        )

    def get_repo_tags(self, repo_path: str) -> List[QuayTag]:
        """
        Fetches tags of a given Quay repository using Quay API.

        Args:
            repo_path (str): Format: "organization/repository".

        Returns:
            List[Dict[str, Any]]: All tags retrieved from Quay API in form
            of JSON objects, attributes we care for are tag 'name'
            and 'manifest_digest'.
        """
        logger.info(f"Fetching tags for repository: {repo_path}")

        return self._make_paginated_request(
            repo_path=repo_path,
            endpoint="tag",
            results_key="tags",
        )
