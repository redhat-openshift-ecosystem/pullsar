from pydantic import BaseModel


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
    """Represents a single item in a list (e.g., a catalog or package)."""

    name: str
    stats: AggregatedPulls


class SummaryStats(BaseModel):
    """Represents the high-level summary statistics for the homepage."""

    total_catalogs: int
    total_packages: int
    total_bundles: int
    total_pulls: int
