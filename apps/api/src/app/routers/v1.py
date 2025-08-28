from fastapi import APIRouter, Depends, Query
from psycopg2.extensions import cursor
from datetime import date, timedelta
from typing import Optional

from app import crud, schemas
from app.database import get_db_cursor

router = APIRouter()

DEFAULT_OCP_VERSION = "v4.18"
DEFAULT_DAYS_DELTA = 14
SORT_TYPES = ["pulls", "name"]
DEFAULT_SEARCH_QUERY = Query(None)
DEFAULT_SORT_TYPE = Query("pulls")
DEFAULT_IS_DESC = Query(True)
DEFAULT_PAGE = Query(1, ge=1)
DEFAULT_PAGE_SIZE = Query(50, ge=1, le=100)


def get_default_start_date():
    return date.today() - timedelta(DEFAULT_DAYS_DELTA)


def get_default_end_date():
    return date.today()


@router.get("/")
def read_api_root():
    """Returns a simple API welcome message."""
    return {"message": "Welcome to the Pullsar API"}


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
    return crud.get_paginated_items(
        db,
        level="catalog",
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
    return crud.get_paginated_items(
        db,
        level="package",
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
    return crud.get_paginated_items(
        db,
        level="bundle",
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
