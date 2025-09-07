from psycopg2.extensions import cursor
from datetime import date, timedelta
from typing import Any, Optional, Sequence
import textwrap

from app.config import BASE_CONFIG

# catalog name for fetching operators from all catalogs at once
ALL_OPERATORS = BASE_CONFIG.all_operators_catalog
EXPORT_MAX_DAYS = BASE_CONFIG.export_max_days


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
        data_point["date"] = data_point["date"].isoformat()

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


def _build_main_query_and_params(
    item_column: str,
    ocp_version: str,
    start_date: date,
    end_date: date,
    catalog_name: Optional[str],
    package_name: Optional[str],
    search_query: Optional[str],
) -> tuple[str, dict[str, Any]]:
    """Builds the CTE query to get aggregated stats needed for sorting and trend."""
    query = f"""
        WITH AggregatedStats AS (
            SELECT
                {item_column} AS item_name,
                SUM(COALESCE(pc.pull_count, 0)) AS total_pulls,
                SUM(
                    CASE WHEN pc.pull_date = %(start_date)s THEN COALESCE(pc.pull_count, 0) ELSE 0 END
                ) AS first_day_pulls,
                SUM(
                    CASE WHEN pc.pull_date = %(end_date)s THEN COALESCE(pc.pull_count, 0) ELSE 0 END
                ) AS last_day_pulls
            FROM
                bundles b
                JOIN bundle_appearances ba ON b.id = ba.bundle_id
                LEFT JOIN pull_counts pc ON pc.bundle_id = ba.bundle_id
                    AND pc.pull_date BETWEEN %(start_date)s AND %(end_date)s
            WHERE
                ba.ocp_version = %(ocp_version)s
                {"AND ba.catalog_name = %(catalog_name)s" if catalog_name and catalog_name != ALL_OPERATORS else ""}
                {"AND b.package = %(package_name)s" if package_name else ""}
                {"AND " + item_column + " LIKE %(search_query)s" if search_query else ""}
            GROUP BY
                item_name
        )
        SELECT item_name, total_pulls, first_day_pulls, last_day_pulls
        FROM AggregatedStats
    """
    params = {
        "ocp_version": ocp_version,
        "start_date": start_date,
        "end_date": end_date,
    }
    if catalog_name:
        params["catalog_name"] = catalog_name
    if package_name:
        params["package_name"] = package_name
    if search_query:
        params["search_query"] = f"%{search_query}%"

    return query, params


def _fetch_chart_data(
    db: cursor,
    item_column: str,
    item_names: list[str],
    params: dict[str, Any],
) -> Sequence[tuple]:
    """Fetches the daily pull count data for a specific list of items."""
    query = f"""
        SELECT
            {item_column} AS item_name,
            pc.pull_date,
            SUM(COALESCE(pc.pull_count, 0)) AS daily_pulls
        FROM
            bundles b
            JOIN bundle_appearances ba ON b.id = ba.bundle_id
            LEFT JOIN pull_counts pc ON pc.bundle_id = ba.bundle_id
                AND pc.pull_date BETWEEN %(start_date)s AND %(end_date)s
        WHERE
            ba.ocp_version = %(ocp_version)s
            AND {item_column} IN %(item_names)s
            {"AND ba.catalog_name = %(catalog_name)s" if "catalog_name" in params and params["catalog_name"] != ALL_OPERATORS else ""}
            {"AND b.package = %(package_name)s" if "package_name" in params else ""}
        GROUP BY
            item_name, pc.pull_date
        ORDER BY
            item_name, pc.pull_date
    """
    chart_params = {**params, "item_names": tuple(item_names)}
    db.execute(query, chart_params)
    return db.fetchall()


def _combine_results(
    paginated_items: Sequence[tuple],
    chart_results: Sequence[tuple],
    start_date: date,
    end_date: date,
) -> list[dict[str, Any]]:
    """Merges aggregated data with chart data, including trend calculation."""
    chart_data_map: dict[str, list[dict[str, Any]]] = {}
    for name, pull_date, daily_pulls in chart_results:
        if pull_date:
            chart_data_map.setdefault(name, []).append(
                {"date": pull_date, "pulls": int(daily_pulls)}
            )

    response_items = []
    for name, total_pulls, first_pulls, last_pulls in paginated_items:
        sparse_chart_data = chart_data_map.get(name, [])
        full_chart_data = _fill_date_gaps(sparse_chart_data, start_date, end_date)
        _convert_dates_to_str(full_chart_data)

        response_items.append(
            {
                "name": name,
                "stats": {
                    "total_pulls": int(total_pulls),
                    "trend": _calculate_trend(int(first_pulls), int(last_pulls)),
                    "chart_data": full_chart_data,
                },
            }
        )
    return response_items


def get_paginated_items(
    db: cursor,
    level: str,
    ocp_version: str,
    start_date: date,
    end_date: date,
    sort_type: str,
    is_desc: bool,
    page: int,
    page_size: int,
    catalog_name: Optional[str] = None,
    package_name: Optional[str] = None,
    search_query: Optional[str] = None,
) -> dict[str, Any]:
    """
    Orchestrates fetching, sorting (by pulls/name), and paginating item stats.
    """
    level_column_map = {
        "catalog": "ba.catalog_name",
        "package": "b.package",
        "bundle": "b.name",
    }
    if level not in level_column_map:
        raise ValueError("Invalid level provided.")

    item_column = level_column_map[level]

    # build the main query and its parameters
    main_query, params = _build_main_query_and_params(
        item_column,
        ocp_version,
        start_date,
        end_date,
        catalog_name,
        package_name,
        search_query,
    )

    # get the total count of items
    count_query = f"SELECT COUNT(*) FROM ({main_query}) AS total"
    db.execute(count_query, params)
    result = db.fetchone()
    total_count = result[0] if result else 0

    # fetch one page of sorted items
    sort_column_map = {
        "name": "item_name",
        "pulls": "total_pulls",
    }
    order_by_clause = f"ORDER BY {sort_column_map.get(sort_type, 'total_pulls')} {'DESC' if is_desc else 'ASC'}"
    pagination_clause = "LIMIT %(page_size)s OFFSET %(offset)s"
    paginated_query = f"{main_query} {order_by_clause} {pagination_clause}"

    paginated_params = {
        **params,
        "page_size": page_size,
        "offset": (page - 1) * page_size,
    }
    db.execute(paginated_query, paginated_params)
    paginated_items = db.fetchall()

    if not paginated_items:
        return {"total_count": total_count, "page_size": page_size, "items": []}

    # fetch the chart data for the current page
    item_names_on_page = [row[0] for row in paginated_items]
    chart_results = _fetch_chart_data(db, item_column, item_names_on_page, params)

    # combine the datasets into the final response
    response_items = _combine_results(
        paginated_items, chart_results, start_date, end_date
    )

    return {"total_count": total_count, "page_size": page_size, "items": response_items}


def get_all_items_for_export(
    db: cursor,
    level: str,
    ocp_version: str,
    start_date: date,
    end_date: date,
    sort_type: str,
    is_desc: bool,
    catalog_name: Optional[str] = None,
    package_name: Optional[str] = None,
    search_query: Optional[str] = None,
) -> list[dict[str, Any]]:
    """
    Fetches all items matching the filters, without pagination, for CSV export.
    This function mirrors the logic of get_paginated_items but without pagination.
    """
    if (end_date - start_date).days > EXPORT_MAX_DAYS:
        raise ValueError(
            f"The requested date range cannot exceed {EXPORT_MAX_DAYS} days for an export."
        )

    level_column_map = {
        "catalog": "ba.catalog_name",
        "package": "b.package",
        "bundle": "b.name",
    }
    if level not in level_column_map:
        raise ValueError("Invalid level provided.")

    item_column = level_column_map[level]

    # build the main query and its parameters
    main_query, params = _build_main_query_and_params(
        item_column,
        ocp_version,
        start_date,
        end_date,
        catalog_name,
        package_name,
        search_query,
    )

    # fetch all sorted items
    sort_column_map = {
        "name": "item_name",
        "pulls": "total_pulls",
    }
    order_by_clause = f"ORDER BY {sort_column_map.get(sort_type, 'total_pulls')} {'DESC' if is_desc else 'ASC'}"

    all_items_query = f"{main_query} {order_by_clause}"

    db.execute(all_items_query, params)
    all_aggregated_items = db.fetchall()

    if not all_aggregated_items:
        return []

    # fetch the chart data for ALL the items found
    all_item_names = [row[0] for row in all_aggregated_items]
    chart_results = _fetch_chart_data(db, item_column, all_item_names, params)

    # combine the datasets into the final response
    response_items = _combine_results(
        all_aggregated_items, chart_results, start_date, end_date
    )

    return response_items
