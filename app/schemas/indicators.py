
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

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Aggregation(str, Enum):
    """How ``metric_field`` (or the row count) is combined per bucket."""

    COUNT = "count"
    SUM = "sum"
    AVG = "avg"
    # Share (0..1) of rows in the bucket where ``metric_field`` is not NULL —
    # e.g. OCR completion rate counts ScannedPages whose ``ocr_raw_text`` has
    # been extracted.
    RATE = "rate"


class ScopeMode(str, Enum):
    """How the source model is linked to the organisational scope.

    ``PARISH`` — the source exposes a ``parish_id`` column (Faithful,
    Donation, LandParcel, ...). Default mode.

    ``VIA_JOIN`` — the source reaches a parish through another table (e.g.
    ``ScannedPage.ledger_book_id -> ArchiveLedgerBook.parish_id``); configured
    with ``via_model`` / ``via_local_field`` / ``via_scope_field``.

    ``POLYMORPHIC_ORG`` — the source is scoped to any organisational entity
    through optional ``archdiocese_id`` / ``deanery_id`` / ``parish_id``
    columns (the polymorphic ``Document`` registry). In-scope rows are the
    union of: parish in the resolved parish set, deanery in the resolved
    deanery set, or archdiocese equal to the scope archdiocese. Rows scoped
    only to a commission/council/meeting are outside every org scope.
    """

    PARISH = "parish"
    VIA_JOIN = "via_join"
    POLYMORPHIC_ORG = "polymorphic_org"


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

    ``source_model`` reaches the organisational scope according to
    ``scope_mode`` (parish column, via-join, or polymorphic org columns).
    Only ``COUNT``/``RATE`` need no ``metric_field``; ``SUM``/``AVG``
    aggregate ``metric_field`` per bucket and ``RATE`` uses it as the
    completion marker (NULL = not done).

    ``group_by`` buckets rows by a hierarchy level; when ``group_by_field``
    is set instead, rows are grouped by the value of that source attribute
    (e.g. ``document_type_id``) and labelled from ``label_model``.
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

    # --- Scope linking (see ScopeMode) ---------------------------------
    scope_mode: ScopeMode = ScopeMode.PARISH
    via_model: type | None = None
    via_local_field: str | None = None
    via_scope_field: str = "parish_id"

    # --- Non-hierarchical grouping (e.g. documents by type) ------------
    group_by_field: str | None = None
    label_model: type | None = None
    label_field: str = "name"

    @model_validator(mode="after")
    def _validate_config_consistency(self) -> "StatisticIndicator":
        if self.aggregation in (Aggregation.SUM, Aggregation.AVG, Aggregation.RATE) and (
            not self.metric_field
        ):
            raise ValueError(
                "metric_field is required when aggregation is SUM, AVG or RATE"
            )
        if self.scope_mode == ScopeMode.VIA_JOIN and (
            not self.via_model or not self.via_local_field
        ):
            raise ValueError(
                "scope_mode VIA_JOIN requires both via_model and via_local_field"
            )
        if self.group_by_field and self.label_model is None:
            raise ValueError("label_model is required when group_by_field is set")
        return self


class IndicatorConfigView(BaseModel):
    """Serialisable projection of :class:`StatisticIndicator` for the API.

    ``source_model`` / ``via_model`` / ``label_model`` are rendered as ORM
    class names rather than class objects so the config list endpoint can be
    JSON-encoded directly.
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
    scope_mode: ScopeMode = ScopeMode.PARISH
    via_model: str | None = None
    via_local_field: str | None = None
    via_scope_field: str = "parish_id"
    group_by_field: str | None = None
    label_model: str | None = None
    label_field: str = "name"


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
