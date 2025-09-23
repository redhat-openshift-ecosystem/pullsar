from pydantic import BaseModel
from enum import Enum
from datetime import date


class DBStartDate(BaseModel):
    """Represents the earliest date from which data is available in the database"""

    db_start_date: date


class ChartDataPoint(BaseModel):
    """Represents a single point on a time-series chart."""

    date: str
    pulls: int


class AggregatedPulls(BaseModel):
    """
    Represents the aggregated pull count statistics for a given scope.
    """

    total_pulls: int
    trend: float
    chart_data: list[ChartDataPoint]


class ListItem(BaseModel):
    """Represents a single item in a list (e.g., a catalog, package or bundle)."""

    name: str
    stats: AggregatedPulls


class SummaryStats(BaseModel):
    """Represents the high-level summary statistics for the homepage."""

    total_catalogs: int
    total_packages: int
    total_bundles: int
    total_pulls: int


class PaginatedListResponse(BaseModel):
    """Represents paginated list of items for the dashboard."""

    total_count: int
    page_size: int
    items: list[ListItem]


class SortType(Enum):
    PULLS = "pulls"
    NAME = "name"
