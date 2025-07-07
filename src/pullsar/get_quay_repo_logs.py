import requests
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any

from pullsar.config import BaseConfig, logger


def extract_org(repo_path: str) -> str:
    """
    Extracts Quay organization name from a valid Quay repository path.

    Args:
        repo_path (str): Format: "organization/repository".

    Returns:
        str: Quay organization name.
    """
    return repo_path.split("/")[0]


def get_time_params(log_days: int) -> Dict[str, str]:
    """
    Based on a given number of log days, configure starttime and endtime
    parameters for Quay API requests. Date range covers last 'log_days'
    completed days, e.g. if 'log_days = 7' and it's May 8th at the moment,
    the range will include May 1st, May 7th and all the dates in between.

    Args:
        log_days (int): Number of log days.

    Returns:
        Dict[str, str]: Dictionary with configured keys 'starttime' and 'endtime',
        usable as Quay API request parameters.
    """
    end_time_utc = datetime.now(timezone.utc) - timedelta(days=1)
    start_time_utc = end_time_utc - timedelta(days=log_days - 1)

    return {
        "starttime": start_time_utc.strftime("%m/%d/%Y"),
        "endtime": end_time_utc.strftime("%m/%d/%Y"),
    }


def get_quay_repo_logs(repo_path: str, log_days: int) -> List[Dict[str, Any]]:
    """
    Fetches usage logs for a given Quay repository using Quay API.

    Args:
        repo_path (str): Format: "organization/repository".
        log_days (int): Fetch logs from the last 'log_days' completed days.

    Returns:
        List[Dict[str, any]]: All logs retrieved from Quay API
    """
    logger.info(f"Fetching logs for repository: {repo_path}")

    api_token = BaseConfig.QUAY_API_TOKENS.get(extract_org(repo_path))
    if not api_token:
        logger.error(
            "Quay API token not defined for the organization. Skipping repository..."
        )
        return []

    api_logs_url = f"{BaseConfig.QUAY_API_BASE_URL}/repository/{repo_path}/logs"
    api_params = get_time_params(log_days)
    api_headers = {
        "Authorization": f"Bearer {BaseConfig.QUAY_API_TOKENS[extract_org(repo_path)]}",
        "Accept": "application/json",
    }

    all_logs = []
    page_count = 0

    logger.debug(f"Initial request parameters: {api_params}")

    while True:
        page_count += 1
        logger.debug(f"Fetching page {page_count} with params: {api_params}")

        try:
            response = requests.get(
                api_logs_url, headers=api_headers, params=api_params
            )
            response.raise_for_status()
            data = response.json()

            if "logs" in data and data["logs"]:
                retrieved_count = len(data["logs"])
                all_logs.extend(data["logs"])
                logger.debug(f"Retrieved {retrieved_count} log entries from this page.")
            else:
                logger.debug("No more log entries found on this page.")

            if "next_page" in data and data["next_page"]:
                api_params["next_page"] = data["next_page"]
            else:
                logger.debug("No next page found.")
                break

        except requests.exceptions.RequestException as exception:
            logger.error(
                f"Request error occurred: {exception}. Skipping {repo_path}..."
            )
            return []

    logger.info(f"Total log entries retrieved: {len(all_logs)}")
    return all_logs


def extract_date(datetime_str: str) -> str:
    """Extracts date from datetime string used in Quay logs.

    Args:
        datetime_str (str): datetime, e.g.: "Mon, 09 Jun 2025 16:23:18 -0000"

    Returns:
        str: extracted date, e.g.: "06/09/2025"
    """
    dt = datetime.strptime(datetime_str, "%a, %d %b %Y %H:%M:%S %z")
    return dt.strftime("%m/%d/%Y")


def filter_pull_repo_logs(logs: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """
    Processes Quay logs, filters 'pull_repo' type logs and simplify them keeping
    only the data needed for futher processing ('date' and an operator version
    identifier, either 'digest' or 'tag').

    Args:
        logs (List[Dict[str: any]]): Mixed logs from Quay.

    Returns:
        List[Dict[str, str]]: List of objects representing 'pull_repo' actions
        with attributes 'date' and an identifier, either 'digest' or 'tag'.
    """
    pull_logs = []
    for log in logs:
        if (
            log.get("kind") == "pull_repo"
            and log.get("metadata")
            and log.get("datetime")
        ):
            date = extract_date(log["datetime"])
            if log["metadata"].get("tag"):
                pull_logs.append({"date": date, "tag": log["metadata"]["tag"]})
            elif log["metadata"].get("manifest_digest"):
                pull_logs.append(
                    {"date": date, "digest": log["metadata"]["manifest_digest"]}
                )

    return pull_logs
