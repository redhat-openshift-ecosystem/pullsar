from fastapi import APIRouter, Depends, Query
from psycopg2.extensions import cursor
from datetime import date, timedelta

from app import crud, schemas
from app.database import get_db_cursor

router = APIRouter()

DEFAULT_END_DATE = date.today()
DEFAULT_START_DATE = DEFAULT_END_DATE - timedelta(days=14)
DEFAULT_OCP_VERSION = "v4.18"


@router.get("/")
def read_api_root():
    """Returns a simple API welcome message."""
    return {"message": "Welcome to the Pullsar API"}


@router.get("/summary", response_model=schemas.SummaryStats)
def read_summary_stats(db: cursor = Depends(get_db_cursor)):
    """Retrieves total numbers of recorded catalogs, packages, bundles and pulls."""
    return crud.get_summary_stats(db)


@router.get("/overall", response_model=schemas.AggregatedPulls)
def read_overall_summary(
    ocp_version: str = Query(DEFAULT_OCP_VERSION),
    start_date: date = DEFAULT_START_DATE,
    end_date: date = DEFAULT_END_DATE,
    db: cursor = Depends(get_db_cursor),
):
    """Retrieves overall pull count, trend and chart data combining all catalogs."""
    return crud.get_overall_pulls(db, ocp_version, start_date, end_date)


@router.get("/catalogs", response_model=list[schemas.ListItem])
def read_catalogs(
    ocp_version: str = Query(DEFAULT_OCP_VERSION),
    start_date: date = DEFAULT_START_DATE,
    end_date: date = DEFAULT_END_DATE,
    db: cursor = Depends(get_db_cursor),
):
    """Retrieves pull count, trend and chart data for each individual catalog."""
    return crud.get_items_with_stats(db, "catalog", ocp_version, start_date, end_date)


@router.get(
    "/catalogs/{catalog_name:path}/packages", response_model=list[schemas.ListItem]
)
def read_packages_in_catalog(
    catalog_name: str,
    ocp_version: str = Query(DEFAULT_OCP_VERSION),
    start_date: date = DEFAULT_START_DATE,
    end_date: date = DEFAULT_END_DATE,
    db: cursor = Depends(get_db_cursor),
):
    """
    Retrieves pull count, trend and chart data for each individual package
    in the given catalog.
    """
    return crud.get_items_with_stats(
        db, "package", ocp_version, start_date, end_date, catalog_name
    )


@router.get(
    "/catalogs/{catalog_name:path}/packages/{package_name}/bundles",
    response_model=list[schemas.ListItem],
)
def read_bundles_in_package(
    catalog_name: str,
    package_name: str,
    ocp_version: str = Query(DEFAULT_OCP_VERSION),
    start_date: date = DEFAULT_START_DATE,
    end_date: date = DEFAULT_END_DATE,
    db: cursor = Depends(get_db_cursor),
):
    """
    Retrieves pull count, trend and chart data for each individual bundle
    in the given package.
    """
    return crud.get_items_with_stats(
        db, "bundle", ocp_version, start_date, end_date, catalog_name, package_name
    )
