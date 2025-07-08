import requests
from typing import List, Dict, Any

from pullsar.config import BaseConfig, logger
from pullsar.get_quay_repo_logs import extract_org


def get_quay_repo_tags(repo_path: str) -> List[Dict[str, Any]]:
    """
    Fetches tags of a given Quay repository using Quay API.

    Args:
        repo_path (str): Format: "organization/repository".

    Returns:
        List[Dict[str, Any]]: All tags retrieved from Quay API in form
        of JSON objects, attributes we care for are tag 'name'
        and 'manifest_digest'.
    """
    api_token = BaseConfig.QUAY_API_TOKENS.get(extract_org(repo_path))
    if not api_token:
        logger.error(
            "Quay API token not defined for the organization. Skipping repository..."
        )
        return []

    api_tags_url = f"{BaseConfig.QUAY_API_BASE_URL}/repository/{repo_path}/tag"
    api_headers = {"Authorization": f"Bearer {api_token}", "Accept": "application/json"}
    api_params = {}

    all_tags = []
    page = 1
    has_additional = True
    while has_additional:
        api_params["page"] = page
        logger.debug(f"Fetching tags for {repo_path}, page {page}...")
        try:
            response = requests.get(
                api_tags_url, headers=api_headers, params=api_params
            )
            response.raise_for_status()
            data = response.json()

            if "tags" in data:
                all_tags.extend(data["tags"])
            else:
                logger.warning(
                    f"Key 'tags' not found in response for page {page}. Skipping..."
                )
                break

            has_additional = data.get("has_additional", False)
            if has_additional:
                page += 1
            else:
                logger.debug(
                    f"No more pages for {repo_path}. Total tags retrieved: {len(all_tags)}"
                )

        except requests.exceptions.RequestException as exception:
            logger.error(
                f"Request exception occurred: {exception}. Skipping {repo_path}..."
            )
            return []

    return all_tags
