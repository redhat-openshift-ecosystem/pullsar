from psycopg2.extensions import cursor
from datetime import date
from typing import Any, Optional, Sequence
import textwrap


def get_summary_stats(db: cursor) -> dict[str, int]:
    """
    Queries the database to get high-level summary statistics.

    Args:
        db (cursor): An active database cursor.

    Returns:
        A dictionary containing the summary statistics.
    """
    query = textwrap.dedent("""
        SELECT
            (SELECT COUNT(DISTINCT catalog_name) FROM bundle_appearances),
            (SELECT COUNT(DISTINCT package) FROM bundles),
            (SELECT COUNT(*) FROM bundles),
            (SELECT SUM(pull_count) FROM pull_counts)
    """)

    db.execute(query)
    result = db.fetchone() or (0, 0, 0, 0)

    total_catalogs, total_packages, total_bundles, total_pulls = result

    return {
        "total_catalogs": total_catalogs or 0,
        "total_packages": total_packages or 0,
        "total_bundles": total_bundles or 0,
        "total_pulls": int(total_pulls) if total_pulls is not None else 0,
    }


def _calculate_trend(start: int, end: int) -> float:
    """Utility to calculate percentage trend between two values."""
    if start > 0:
        return ((end - start) / start) * 100
    elif end > 0:
        return float("inf")
    return 0.0


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

    if not results:
        return {"total_pulls": 0, "trend": 0.0, "chart_data": []}

    chart_data = [
        {"date": row[0].strftime("%b %d"), "pulls": int(row[1])} for row in results
    ]
    total_pulls = sum(item["pulls"] for item in chart_data)
    trend = _calculate_trend(chart_data[0]["pulls"], chart_data[-1]["pulls"])

    return {"total_pulls": total_pulls, "trend": trend, "chart_data": chart_data}


def _process_grouped_results(results: Sequence[tuple]) -> list[dict[str, Any]]:
    """
    Converts grouped SQL results into structured dict format with chart data and stats.
    Each result row: (item_name, pull_date, pull_count)
    """
    if not results:
        return []

    grouped_data: dict[str, list[dict[str, Any]]] = {}

    for name, pull_date, daily_pulls in results:
        grouped_data.setdefault(name, []).append(
            {
                "date": pull_date.strftime("%b %d"),
                "pulls": int(daily_pulls),
            }
        )

    response = []
    for name, chart_data in grouped_data.items():
        total_pulls = sum(item["pulls"] for item in chart_data)
        trend = _calculate_trend(chart_data[0]["pulls"], chart_data[-1]["pulls"])

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
    """
    Unified fetch for catalog/package/bundle stats in a date range.
    Optionally filter by catalog/package.
    """
    level_column_map = {
        "catalog": "ba.catalog_name",
        "package": "b.package",
        "bundle": "b.name",
    }

    if level not in level_column_map:
        raise ValueError("Invalid level: must be 'catalog', 'package', or 'bundle'.")

    group_by_column = level_column_map[level]

    query = textwrap.dedent(f"""
        SELECT
            {group_by_column},
            pc.pull_date,
            SUM(pc.pull_count) AS daily_pulls
        FROM pull_counts pc
        JOIN bundle_appearances ba ON pc.bundle_id = ba.bundle_id
        JOIN bundles b ON pc.bundle_id = b.id
        WHERE ba.ocp_version = %(ocp_version)s
          AND pc.pull_date BETWEEN %(start_date)s AND %(end_date)s
    """)

    params: dict[str, Any] = {
        "ocp_version": ocp_version,
        "start_date": start_date,
        "end_date": end_date,
    }

    if catalog_name:
        query += " AND ba.catalog_name = %(catalog_name)s"
        params["catalog_name"] = catalog_name
    if package_name:
        query += " AND b.package = %(package_name)s"
        params["package_name"] = package_name

    query += f"""
        GROUP BY {group_by_column}, pc.pull_date
        ORDER BY {group_by_column}, pc.pull_date
    """

    db.execute(query, params)
    return _process_grouped_results(db.fetchall())
