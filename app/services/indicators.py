"""
Generic Statistic Indicator Engine — Aggregation Service & Registry.

New statistics are *configuration*, not code: add a
:class:`~app.schemas.indicators.StatisticIndicator` to ``INDICATORS`` and the
generic :class:`AggregationService` pipeline (scope rollup via
``hierarchy_resolver`` -> source fetch -> group/aggregate) computes it.

The three examples — "faithful by deanery", "land value by vicariate", and
"donations trend by parish" — are declared below as plain config instead of
one-off hand-written methods.
"""
import uuid
from datetime import UTC, date, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    IndicatorNotFoundException,
    IndicatorScopeRequiredException,
    ValidationException,
)
from app.models.deanery import Archdiocese, Deanery
from app.models.donation import Donation
from app.models.faithful import Faithful
from app.models.parcel import LandParcel
from app.models.parish import Parish
from app.repositories.indicators import IndicatorRepository
from app.schemas.indicators import (
    Aggregation,
    HierarchyGroup,
    IndicatorConfigView,
    IndicatorResult,
    IndicatorRow,
    IndicatorScope,
    StatisticIndicator,
    TrendBucket,
)
from app.services.org.hierarchy_resolver import (
    get_descendant_parish_ids,
    get_parish_ancestry_map,
)

# Group-by level -> which id from the row/ancestry names the bucket.
_GROUP_LEVEL_ATTR: dict[HierarchyGroup, str] = {
    HierarchyGroup.ARCHDIOCESE: "archdiocese_id",
    HierarchyGroup.DEANERY: "deanery_id",
    HierarchyGroup.VICARIATE: "deanery_id",
    HierarchyGroup.PARISH: "parish_id",
}

# Group-by level -> ORM model used to resolve human-readable bucket names.
_LABEL_GROUP_MODEL: dict[HierarchyGroup, type] = {
    HierarchyGroup.ARCHDIOCESE: Archdiocese,
    HierarchyGroup.DEANERY: Deanery,
    HierarchyGroup.VICARIATE: Deanery,
    HierarchyGroup.PARISH: Parish,
}

# Levels that roll up above the row's own parish and therefore need the
# parish -> ancestry map resolved through hierarchy_resolver.
_NEEDS_ANCESTRY = {
    HierarchyGroup.ARCHDIOCESE,
    HierarchyGroup.DEANERY,
    HierarchyGroup.VICARIATE,
}
# ---------------------------------------------------------------------------
# Registered statistic indicators (the "configuration" surface).
# ---------------------------------------------------------------------------
INDICATORS: list[StatisticIndicator] = [
    StatisticIndicator(
        key="faithful_by_deanery",
        title="Faithful by Deanery",
        description="Registered faithful population counted per deanery.",
        source_model=Faithful,
        aggregation=Aggregation.COUNT,
        group_by=HierarchyGroup.DEANERY,
        unit="faithful",
    ),
    StatisticIndicator(
        key="land_value_by_vicariate",
        title="Land Value by Vicariate",
        description="Sum of estimated land value (RWF) grouped by vicariate (deanery).",
        source_model=LandParcel,
        aggregation=Aggregation.SUM,
        metric_field="estimated_value_rwf",
        group_by=HierarchyGroup.VICARIATE,
        unit="RWF",
    ),
    StatisticIndicator(
        key="donations_trend_by_parish",
        title="Donations Trend by Parish",
        description="Monthly donations per parish, one time series per parish.",
        source_model=Donation,
        aggregation=Aggregation.SUM,
        metric_field="amount",
        group_by=HierarchyGroup.PARISH,
        trend_bucket=TrendBucket.MONTH,
        date_field="donation_date",
        unit="RWF",
    ),
]

INDICATOR_INDEX: dict[str, StatisticIndicator] = {
    indicator.key: indicator for indicator in INDICATORS
}
class AggregationService:
    """Runs the same generic pipeline over any configured indicator.

    1. Resolve the organisational scope to a concrete parish set through
       :func:`get_descendant_parish_ids`.
    2. When bucketing above the parish level, map each parish to its
       deanery/archdiocese ancestor via :func:`get_parish_ancestry_map`.
    3. Fetch the source rows for those parishes,
    4. bucket them by (period, group) and reduce by count/sum/avg.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = IndicatorRepository(db)

    # ------------------------------------------------------------------ #
    # Configuration access
    # ------------------------------------------------------------------ #
    def list_indicators(self) -> list[IndicatorConfigView]:
        """Serialise every registered indicator as a config view (for the API)."""
        return [
            IndicatorConfigView(
                key=indicator.key,
                title=indicator.title,
                description=indicator.description,
                source_model=indicator.source_model.__name__,
                aggregation=indicator.aggregation,
                metric_field=indicator.metric_field,
                group_by=indicator.group_by,
                trend_bucket=indicator.trend_bucket,
                date_field=indicator.date_field,
                filters=indicator.filters,
                unit=indicator.unit,
            )
            for indicator in INDICATORS
        ]

    def get_indicator(self, key: str) -> StatisticIndicator:
        """Look up a registered indicator or raise 404."""
        try:
            return INDICATOR_INDEX[key]
        except KeyError:
            raise IndicatorNotFoundException(key) from None

    # ------------------------------------------------------------------ #
    # Computation
    # ------------------------------------------------------------------ #
    async def compute(
        self,
        key: str,
        *,
        archdiocese_id: uuid.UUID | None = None,
        deanery_id: uuid.UUID | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> IndicatorResult:
        """Compute one registered indicator within an archdiocesan/deanery scope.

        When both ``deanery_id`` and ``archdiocese_id`` are supplied the more
        specific deanery scope wins (matching ``get_descendant_parish_ids``
        semantics).
        """
        indicator = self.get_indicator(key)
        self._validate_source(indicator)

        if deanery_id is None and archdiocese_id is None:
            raise IndicatorScopeRequiredException()

        # 1. Resolve the scope -> concrete parish ids (hierarchy_resolver owns
        #    the cross-level joins).
        parish_ids = await get_descendant_parish_ids(
            self.db,
            deanery_id=deanery_id,
            archdiocese_id=archdiocese_id,
        )

        # 2. Resolve ancestry (parish -> deanery/archdiocese) only for
        #    bucketing above the parish level.
        ancestry = {}
        if indicator.group_by in _NEEDS_ANCESTRY:
            ancestry = await get_parish_ancestry_map(self.db, parish_ids)

        # 3. Fetch the raw source rows scoped to those parishes.
        rows = await self.repo.fetch_rows(
            indicator.source_model,
            parish_ids,
            filters=indicator.filters,
            date_field=indicator.date_field,
            start=start_date,
            end=end_date,
        )

        # 4. Bucket by (period, group) and reduce.
        acc: dict[tuple[str | None, uuid.UUID | None], dict[str, float]] = {}
        for row in rows:
            state = acc.setdefault(
                self._bucket_key(indicator, row, ancestry),
                {"n": 0.0, "sum": 0.0},
            )
            state["n"] += 1.0
            if indicator.aggregation in (Aggregation.SUM, Aggregation.AVG):
                state["sum"] += float(getattr(row, indicator.metric_field))

        group_ids = {group for _period, group in acc if group is not None}
        group_names = await self.repo.fetch_names(
            _LABEL_GROUP_MODEL[indicator.group_by],
            group_ids,
        )

        out_rows = [
            self._build_row(indicator, period, group, group_names, state)
            for (period, group), state in acc.items()
        ]
        out_rows.sort(key=lambda r: (r.group_name, r.period or ""))

        return IndicatorResult(
            key=indicator.key,
            title=indicator.title,
            description=indicator.description,
            aggregation=indicator.aggregation,
            group_by=indicator.group_by,
            trend_bucket=indicator.trend_bucket,
            unit=indicator.unit,
            scope=IndicatorScope(
                archdiocese_id=archdiocese_id,
                deanery_id=deanery_id,
                start_date=start_date,
                end_date=end_date,
            ),
            rows=out_rows,
            generated_at=datetime.now(UTC),
        )

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #
    def _validate_source(self, indicator: StatisticIndicator) -> None:
        if not hasattr(indicator.source_model, "parish_id"):
            raise ValidationException(
                "errors.indicator_source_no_parish",
                message_params={"key": indicator.key},
            )

    def _bucket_key(
        self,
        indicator: StatisticIndicator,
        row,
        ancestry: dict,
    ) -> tuple[str | None, uuid.UUID | None]:
        period = None
        if indicator.date_field:
            period = self._bucket_label(
                indicator.trend_bucket, getattr(row, indicator.date_field)
            )

        level_attr = _GROUP_LEVEL_ATTR[indicator.group_by]
        if level_attr == "parish_id":
            group_id = row.parish_id
        else:
            entry = ancestry.get(row.parish_id)
            group_id = entry.get(level_attr) if entry else None
        return period, group_id

    def _build_row(
        self,
        indicator: StatisticIndicator,
        period: str | None,
        group_id: uuid.UUID | None,
        group_names: dict,
        state: dict[str, float],
    ) -> IndicatorRow:
        if indicator.aggregation == Aggregation.COUNT:
            value: int | float = int(state["n"])
        elif indicator.aggregation == Aggregation.AVG:
            value = state["sum"] / state["n"] if state["n"] else 0.0
        else:
            value = state["sum"]
        return IndicatorRow(
            group_id=group_id,
            group_name=group_names.get(group_id, "") if group_id else "",
            period=period,
            value=value,
        )

    @staticmethod
    def _bucket_label(bucket: TrendBucket | None, value) -> str | None:
        """Renderer of a row's date/int into a human-readable period label."""
        if bucket is None:
            return None
        # Annual statistical returns store year as an int (report_year).
        if isinstance(value, int):
            return str(value)
        year = value.year
        if bucket == TrendBucket.YEAR:
            return f"{year:04d}"
        if bucket == TrendBucket.QUARTER:
            return f"{year:04d}-Q{(value.month - 1) // 3 + 1}"
        if bucket == TrendBucket.MONTH:
            return f"{year:04d}-{value.month:02d}"
        return f"{year:04d}"
