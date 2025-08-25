from psycopg2.extensions import cursor
from datetime import date, timedelta
from typing import Any, Optional, Sequence
import textwrap


def get_ocp_versions(db: cursor) -> list[str]:
    """Fetches a list of unique OCP versions from the database, sorted descending."""
    query = (
        "SELECT DISTINCT ocp_version FROM bundle_appearances ORDER BY ocp_version DESC;"
    )
    db.execute(query)
    return [row[0] for row in db.fetchall()]


def get_summary_stats(db: cursor) -> dict[str, int]:
    """Queries the database to get high-level summary statistics."""
    query = textwrap.dedent("""
        SELECT
            (SELECT COUNT(DISTINCT catalog_name) FROM bundle_appearances),
            (SELECT COUNT(DISTINCT package) FROM bundles),
            (SELECT COUNT(*) FROM bundles),
            (SELECT SUM(pull_count) FROM pull_counts)
    """)

    db.execute(query)
    result = db.fetchone()

    if result is None:
        raise RuntimeError("Unexpected: summary stats query returned no rows.")

    total_catalogs, total_packages, total_bundles, total_pulls = result

    return {
        "total_catalogs": total_catalogs or 0,
        "total_packages": total_packages or 0,
        "total_bundles": total_bundles or 0,
        "total_pulls": int(total_pulls) if total_pulls is not None else 0,
    }


def _calculate_trend(start: int, end: int) -> Optional[float]:
    """
    Utility to calculate percentage trend between two values.
    Returns percentage representing the change from value start
    to value end. Returns None in special case of start == 0 and end > 0,
    which would be a raise by 'infinity' %.
    """
    if start > 0:
        return ((end - start) / start) * 100
    elif end > 0:
        return None
    return 0.0


def _fill_date_gaps(
    sparse_data: list[dict[str, Any]], start_date: date, end_date: date
) -> list[dict[str, Any]]:
    """Fills missing dates in a time-series with zero pulls."""
    pulls_map = {item["date"]: item["pulls"] for item in sparse_data}
    complete_data = []
    current_date = start_date
    while current_date <= end_date:
        complete_data.append(
            {"date": current_date, "pulls": pulls_map.get(current_date, 0)}
        )
        current_date += timedelta(days=1)
    return complete_data


def _convert_dates_to_str(chart_data: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Replaces date objects in chart data for formatted string dates,
    preparing the final API response.
    """
    for data_point in chart_data:
        data_point["date"] = data_point["date"].strftime("%b %d")

    return chart_data


def get_overall_pulls(
    db: cursor, ocp_version: str, start_date: date, end_date: date
) -> dict:
    """
    Calculates total pull count and trend for a given OCP version between dates.
    Used for homepage graph.
    """
    query = textwrap.dedent("""
        SELECT pc.pull_date, SUM(pc.pull_count) AS total_pulls
        FROM pull_counts pc
        JOIN bundle_appearances ba ON pc.bundle_id = ba.bundle_id
        WHERE ba.ocp_version = %(ocp_version)s
          AND pc.pull_date BETWEEN %(start_date)s AND %(end_date)s
        GROUP BY pc.pull_date
        ORDER BY pc.pull_date ASC
    """)

    params = {
        "ocp_version": ocp_version,
        "start_date": start_date,
        "end_date": end_date,
    }
    db.execute(query, params)
    results = db.fetchall()

    sparse_chart_data = [{"date": row[0], "pulls": int(row[1])} for row in results]

    chart_data = _fill_date_gaps(sparse_chart_data, start_date, end_date)

    if not chart_data:
        return {"total_pulls": 0, "trend": 0.0, "chart_data": []}

    total_pulls = sum(item["pulls"] for item in chart_data)
    trend = _calculate_trend(chart_data[0]["pulls"], chart_data[-1]["pulls"])
    _convert_dates_to_str(chart_data)

    return {"total_pulls": total_pulls, "trend": trend, "chart_data": chart_data}


def _process_grouped_results(
    results: Sequence[tuple], start_date: date, end_date: date
) -> list[dict[str, Any]]:
    """Converts grouped SQL results into a structured dict with complete chart data."""
    if not results:
        return []

    grouped_data: dict[str, list[dict[str, Any]]] = {}
    for name, pull_date, daily_pulls in results:
        grouped_data.setdefault(name, []).append(
            {"date": pull_date, "pulls": int(daily_pulls)}
        )

    response = []
    for name, sparse_chart_data in grouped_data.items():
        chart_data = _fill_date_gaps(sparse_chart_data, start_date, end_date)

        total_pulls = sum(item["pulls"] for item in chart_data)
        trend = _calculate_trend(chart_data[0]["pulls"], chart_data[-1]["pulls"])
        _convert_dates_to_str(chart_data)

        response.append(
            {
                "name": name,
                "stats": {
                    "total_pulls": total_pulls,
                    "trend": trend,
                    "chart_data": chart_data,
                },
            }
        )

    return response


def get_items_with_stats(
    db: cursor,
    level: str,
    ocp_version: str,
    start_date: date,
    end_date: date,
    catalog_name: Optional[str] = None,
    package_name: Optional[str] = None,
) -> list[dict[str, Any]]:
    """Unified fetch for catalog/package/bundle stats in a date range."""
    level_column_map = {
        "catalog": "ba.catalog_name",
        "package": "b.package",
        "bundle": "b.name",
    }
    if level not in level_column_map:
        raise ValueError("Invalid level: must be 'catalog', 'package', or 'bundle'.")

    group_by_column = level_column_map[level]

    query_parts = [
        f"SELECT {group_by_column}, pc.pull_date, SUM(COALESCE(pc.pull_count, 0)) AS daily_pulls",
        "FROM bundles b JOIN bundle_appearances ba ON b.id = ba.bundle_id",
        "LEFT JOIN pull_counts pc ON pc.bundle_id = ba.bundle_id AND pc.pull_date BETWEEN %(start_date)s AND %(end_date)s",
        "WHERE ba.ocp_version = %(ocp_version)s",
    ]
    params: dict[str, Any] = {
        "ocp_version": ocp_version,
        "start_date": start_date,
        "end_date": end_date,
    }

    if catalog_name:
        query_parts.append("AND ba.catalog_name = %(catalog_name)s")
        params["catalog_name"] = catalog_name
    if package_name:
        query_parts.append("AND b.package = %(package_name)s")
        params["package_name"] = package_name

    query_parts.append(
        f"GROUP BY {group_by_column}, pc.pull_date ORDER BY {group_by_column}, pc.pull_date"
    )

    db.execute(" ".join(query_parts), params)
    return _process_grouped_results(db.fetchall(), start_date, end_date)
