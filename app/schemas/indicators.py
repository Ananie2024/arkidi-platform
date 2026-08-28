"""
Generic Statistic Indicator Engine — Pydantic v2 Schemas.

``StatisticIndicator`` is a *declarative configuration* describing an aggregate
over a single source model that links to ``parish_id`` and is bucketed by a
hierarchical level (archdiocese / deanery / parish) using the rollup helpers in
``app/services/org/hierarchy_resolver.py``. New statistics are configuration
entries (see ``app/services/indicators.py``), not one-off hand-written methods.
"""
import uuid
from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Aggregation(str, Enum):
    """How ``metric_field`` (or the row count) is combined per bucket."""

    COUNT = "count"
    SUM = "sum"
    AVG = "avg"


class HierarchyGroup(str, Enum):
    """Organisational level the indicator is grouped by.

    ``VICARIATE`` is the ecclesiastical synonym for a deanery (a deanery is led
    by a Vicar Forane / Curé de Doyenné): it groups rows by ``deanery_id`` while
    keeping the ``vicariate`` label in the API output.
    """

    ARCHDIOCESE = "archdiocese"
    DEANERY = "deanery"
    VICARIATE = "vicariate"
    PARISH = "parish"


class TrendBucket(str, Enum):
    """Optional time bucket for trend indicators (e.g. donations by month)."""

    YEAR = "year"
    QUARTER = "quarter"
    MONTH = "month"


class StatisticIndicator(BaseModel):
    """Declarative configuration for a single aggregated statistic.

    ``source_model`` must expose a ``parish_id`` column (Faithful, Family,
    LandParcel, Donation, AnnualParishStatistic, ...). Only ``COUNT`` needs no
    ``metric_field``; ``SUM``/``AVG`` aggregate ``metric_field`` per bucket.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    key: str
    title: str
    description: str = ""
    source_model: type
    aggregation: Aggregation = Aggregation.COUNT
    metric_field: str | None = None
    group_by: HierarchyGroup = HierarchyGroup.PARISH
    trend_bucket: TrendBucket | None = None
    date_field: str | None = None
    filters: list[dict] = Field(default_factory=list)
    unit: str | None = None

    @field_validator("metric_field")
    @classmethod
    def _metric_required_for_sum_avg(cls, value: str | None, info) -> str | None:
        if info.data.get("aggregation") in (Aggregation.SUM, Aggregation.AVG) and not value:
            raise ValueError(
                "metric_field is required when aggregation is SUM or AVG"
            )
        return value


class IndicatorConfigView(BaseModel):
    """Serialisable projection of :class:`StatisticIndicator` for the API.

    ``source_model`` is rendered as the ORM class name rather than the class
    object itself so the config list endpoint can be JSON-encoded directly.
    """

    key: str
    title: str
    description: str
    source_model: str
    aggregation: Aggregation
    metric_field: str | None = None
    group_by: HierarchyGroup
    trend_bucket: TrendBucket | None = None
    date_field: str | None = None
    filters: list[dict] = Field(default_factory=list)
    unit: str | None = None


class IndicatorRow(BaseModel):
    """One computed bucket: a group (id + name), optional period, and value."""

    group_id: uuid.UUID | None = None
    group_name: str = ""
    period: str | None = None
    value: int | float


class IndicatorScope(BaseModel):
    """The organisational scope a computation was restricted to."""

    archdiocese_id: uuid.UUID | None = None
    deanery_id: uuid.UUID | None = None
    start_date: date | None = None
    end_date: date | None = None


class IndicatorResult(BaseModel):
    """Result of running one configured :class:`StatisticIndicator`."""

    key: str
    title: str
    description: str = ""
    aggregation: Aggregation
    group_by: HierarchyGroup
    trend_bucket: TrendBucket | None = None
    unit: str | None = None
    scope: IndicatorScope
    rows: list[IndicatorRow] = Field(default_factory=list)
    generated_at: datetime
