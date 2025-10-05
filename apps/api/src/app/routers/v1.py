from fastapi import APIRouter, Depends, Query, Response, HTTPException
from psycopg2.extensions import cursor
from datetime import date, timedelta
from typing import Optional
import io
import csv

from app import crud, schemas
from app.database import get_db_cursor
from app.config import BASE_CONFIG

router = APIRouter()

DEFAULT_OCP_VERSION = "v4.18"
DEFAULT_DAYS_DELTA = 14
SORT_TYPES = [schemas.SortType.PULLS, schemas.SortType.NAME]
DEFAULT_SEARCH_QUERY = Query(None)
DEFAULT_SORT_TYPE = Query(schemas.SortType.PULLS)
DEFAULT_IS_DESC = Query(True)
DEFAULT_PAGE = Query(1, ge=1)
DEFAULT_PAGE_SIZE = Query(50, ge=1, le=100)


def get_db_start_date() -> date:
    return BASE_CONFIG.db_start_date or date.today()


def get_yesterday_date():
    return date.today() - timedelta(1)


def get_default_start_date():
    return get_yesterday_date() - timedelta(DEFAULT_DAYS_DELTA)


def get_default_end_date():
    return get_yesterday_date()


def clamp_date(date: date) -> date:
    """Fix the date to be inside the valid date range."""
    yesterday = get_yesterday_date()
    db_start_date = get_db_start_date()
    if date > yesterday:
        return yesterday
    if date < db_start_date:
        return db_start_date
    return date


def clamp_date_range(start_date: date, end_date: date) -> tuple[date, date]:
    """Make the provided date range valid."""
    start, end = (clamp_date(start_date), clamp_date(end_date))
    if start > end:
        start = end

    return (start, end)


@router.get("/")
def read_api_root():
    """Returns a simple API welcome message."""
    return {"message": "Welcome to the Pullsar API"}


@router.get("/config", response_model=schemas.ApiConfig)
def read_api_config(db_start_date: date = Depends(get_db_start_date)):
    """
    Returns the API configuration.
    """
    return {
        "db_start_date": db_start_date,
        "export_max_days": BASE_CONFIG.export_max_days,
        "all_operators_catalog": BASE_CONFIG.all_operators_catalog,
    }


@router.get("/ocp-versions", response_model=list[str])
def read_ocp_versions(db: cursor = Depends(get_db_cursor)):
    """Retrieves a list of all available OCP versions in the database."""
    return crud.get_ocp_versions(db)


@router.get("/sort-types", response_model=list[str])
def read_sort_types(db: cursor = Depends(get_db_cursor)):
    """Retrieves a list of all supported sort types."""
    return SORT_TYPES


@router.get("/summary", response_model=schemas.SummaryStats)
def read_summary_stats(db: cursor = Depends(get_db_cursor)):
    """Retrieves total numbers of recorded catalogs, packages, bundles and pulls."""
    return crud.get_summary_stats(db)


@router.get("/overall", response_model=schemas.AggregatedPulls)
def read_overall_summary(
    ocp_version: str = Query(DEFAULT_OCP_VERSION),
    start_date: date = get_default_start_date(),
    end_date: date = get_default_end_date(),
    db: cursor = Depends(get_db_cursor),
):
    """Retrieves overall pull count, trend and chart data combining all catalogs."""
    start_date, end_date = clamp_date_range(start_date, end_date)
    return crud.get_overall_pulls(db, ocp_version, start_date, end_date)


@router.get("/catalogs", response_model=schemas.PaginatedListResponse)
def read_catalogs(
    ocp_version: str = Query(DEFAULT_OCP_VERSION),
    start_date: date = get_default_start_date(),
    end_date: date = get_default_end_date(),
    search_query: Optional[str] = DEFAULT_SEARCH_QUERY,
    sort_type: schemas.SortType = DEFAULT_SORT_TYPE,
    is_desc: bool = DEFAULT_IS_DESC,
    page: int = DEFAULT_PAGE,
    page_size: int = DEFAULT_PAGE_SIZE,
    db: cursor = Depends(get_db_cursor),
):
    """Retrieves a paginated and sorted list of catalogs with stats."""
    start_date, end_date = clamp_date_range(start_date, end_date)
    return crud.get_paginated_items(
        db,
        level=crud.ItemLevel.CATALOG,
        ocp_version=ocp_version,
        start_date=start_date,
        end_date=end_date,
        sort_type=sort_type,
        is_desc=is_desc,
        page=page,
        page_size=page_size,
        search_query=search_query,
    )


@router.get(
    "/catalogs/{catalog_name:path}/packages",
    response_model=schemas.PaginatedListResponse,
)
def read_packages_in_catalog(
    catalog_name: str,
    ocp_version: str = Query(DEFAULT_OCP_VERSION),
    start_date: date = get_default_start_date(),
    end_date: date = get_default_end_date(),
    search_query: Optional[str] = DEFAULT_SEARCH_QUERY,
    sort_type: schemas.SortType = DEFAULT_SORT_TYPE,
    is_desc: bool = DEFAULT_IS_DESC,
    page: int = DEFAULT_PAGE,
    page_size: int = DEFAULT_PAGE_SIZE,
    db: cursor = Depends(get_db_cursor),
):
    """Retrieves a paginated and sorted list of packages within a catalog."""
    start_date, end_date = clamp_date_range(start_date, end_date)
    return crud.get_paginated_items(
        db,
        level=crud.ItemLevel.PACKAGE,
        ocp_version=ocp_version,
        start_date=start_date,
        end_date=end_date,
        sort_type=sort_type,
        is_desc=is_desc,
        page=page,
        page_size=page_size,
        catalog_name=catalog_name,
        search_query=search_query,
    )


@router.get(
    "/catalogs/{catalog_name:path}/packages/{package_name}/bundles",
    response_model=schemas.PaginatedListResponse,
)
def read_bundles_in_package(
    catalog_name: str,
    package_name: str,
    ocp_version: str = Query(DEFAULT_OCP_VERSION),
    start_date: date = get_default_start_date(),
    end_date: date = get_default_end_date(),
    search_query: Optional[str] = DEFAULT_SEARCH_QUERY,
    sort_type: schemas.SortType = DEFAULT_SORT_TYPE,
    is_desc: bool = DEFAULT_IS_DESC,
    page: int = DEFAULT_PAGE,
    page_size: int = DEFAULT_PAGE_SIZE,
    db: cursor = Depends(get_db_cursor),
):
    """Retrieves a paginated and sorted list of bundles within a package."""
    start_date, end_date = clamp_date_range(start_date, end_date)
    return crud.get_paginated_items(
        db,
        level=crud.ItemLevel.BUNDLE,
        ocp_version=ocp_version,
        start_date=start_date,
        end_date=end_date,
        sort_type=sort_type,
        is_desc=is_desc,
        page=page,
        page_size=page_size,
        catalog_name=catalog_name,
        package_name=package_name,
        search_query=search_query,
    )


@router.get("/export/csv")
async def export_items_to_csv(
    ocp_version: str = Query(DEFAULT_OCP_VERSION),
    start_date: date = get_default_start_date(),
    end_date: date = get_default_end_date(),
    search_query: Optional[str] = DEFAULT_SEARCH_QUERY,
    sort_type: schemas.SortType = DEFAULT_SORT_TYPE,
    is_desc: bool = DEFAULT_IS_DESC,
    catalog_name: Optional[str] = None,
    package_name: Optional[str] = None,
    db: cursor = Depends(get_db_cursor),
):
    """Generates and returns a CSV file for the given scope and filters."""
    start_date, end_date = clamp_date_range(start_date, end_date)
    level = (
        crud.ItemLevel.BUNDLE
        if package_name
        else crud.ItemLevel.PACKAGE
        if catalog_name
        else crud.ItemLevel.CATALOG
    )

    try:
        items = crud.get_all_items_for_export(
            db,
            level,
            ocp_version,
            start_date,
            end_date,
            sort_type,
            is_desc,
            catalog_name,
            package_name,
            search_query,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    output = io.StringIO()
    writer = csv.writer(output)

    date_headers = [
        (start_date + timedelta(days=i)).isoformat()
        for i in range((end_date - start_date).days + 1)
    ]
    writer.writerow(["Name", "Total Pulls", "Trend"] + date_headers)

    for item in items:
        pulls_by_date = {
            str(p["date"]): p["pulls"] for p in item["stats"]["chart_data"]
        }
        row = [item["name"], item["stats"]["total_pulls"], item["stats"]["trend"]]
        row.extend([pulls_by_date.get(d, 0) for d in date_headers])
        writer.writerow(row)

    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=pullsar_export_{date.today().isoformat()}.csv"
        },
    )
