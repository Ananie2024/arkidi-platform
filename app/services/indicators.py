"""
Generic Statistic Indicator Engine — Aggregation Service & Registry.

New statistics are *configuration*, not code: add a
:class:`~app.schemas.indicators.StatisticIndicator` to ``INDICATORS`` and the
generic :class:`AggregationService` pipeline (scope rollup via
``hierarchy_resolver`` -> source fetch -> group/aggregate) computes it.

Beyond the parish-scoped core (Faithful / LandParcel / Donation), the engine
also serves the Archives domain: polymorphic org-scoped ``Document`` counts,
via-join ``ScannedPage`` OCR completion rates, and the annual parish returns
that back the *Annuario Pontificio* report.
"""
import uuid
from datetime import UTC, date, datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    IndicatorNotFoundException,
    IndicatorScopeRequiredException,
    ValidationException,
)
from app.models.deanery import Archdiocese, Deanery
from app.models.document import ArchiveLedgerBook, Document, ScannedPage
from app.models.document_type import DocumentType
from app.models.donation import Donation
from app.models.faithful import Faithful
from app.models.parcel import LandParcel
from app.models.parish import Parish
from app.models.survey import AnnualParishStatistic
from app.repositories.indicators import IndicatorRepository
from app.schemas.indicators import (
    Aggregation,
    HierarchyGroup,
    IndicatorConfigView,
    IndicatorResult,
    IndicatorRow,
    IndicatorScope,
    ScopeMode,
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
    # -------------------------------------------------------------------
    # Archives domain (polymorphic org-scoped Document registry).
    # -------------------------------------------------------------------
    StatisticIndicator(
        key="documents_by_parish",
        title="Documents by Parish",
        description=(
            "Archived document counts grouped by parish. Documents attached "
            "only to a deanery or the archdiocese land in the unassigned "
            "(null-group) bucket."
        ),
        source_model=Document,
        aggregation=Aggregation.COUNT,
        group_by=HierarchyGroup.PARISH,
        scope_mode=ScopeMode.POLYMORPHIC_ORG,
        unit="documents",
    ),
    StatisticIndicator(
        key="documents_by_type",
        title="Documents by Type",
        description="Archived document counts grouped by document type.",
        source_model=Document,
        aggregation=Aggregation.COUNT,
        group_by=HierarchyGroup.PARISH,  # ignored: group_by_field drives the bucket
        group_by_field="document_type_id",
        label_model=DocumentType,
        label_field="name_en",
        scope_mode=ScopeMode.POLYMORPHIC_ORG,
        unit="documents",
    ),
    StatisticIndicator(
        key="retention_review_backlog",
        title="Retention Review Backlog",
        description=(
            "Documents flagged DUE_FOR_REVIEW by the archivist retention "
            "scheduler (app.tasks.archive_retention), grouped by parish."
        ),
        source_model=Document,
        aggregation=Aggregation.COUNT,
        group_by=HierarchyGroup.PARISH,
        scope_mode=ScopeMode.POLYMORPHIC_ORG,
        filters=[{"field": "disposition_status", "value": "DUE_FOR_REVIEW"}],
        unit="documents",
    ),
    StatisticIndicator(
        key="ocr_completion_rate",
        title="OCR Completion Rate",
        description=(
            "Share of scanned ledger pages whose OCR text has been extracted, "
            "grouped by the parish owning the ledger book."
        ),
        source_model=ScannedPage,
        aggregation=Aggregation.RATE,
        metric_field="ocr_raw_text",
        group_by=HierarchyGroup.PARISH,
        scope_mode=ScopeMode.VIA_JOIN,
        via_model=ArchiveLedgerBook,
        via_local_field="ledger_book_id",
        via_scope_field="parish_id",
        unit="ratio",
    ),
    # -------------------------------------------------------------------
    # Annual parish statistical returns — the engine-backed aggregates that
    # feed the Annuario Pontificio report (ADR 002 follow-up). Runtime
    # param_filters={"report_year": year} restricts each computation to one
    # reporting year.
    # -------------------------------------------------------------------
    StatisticIndicator(
        key="annual_catholic_population_by_parish",
        title="Annual Catholic Population by Parish",
        description="Sum of reported catholic population per parish for a reporting year.",
        source_model=AnnualParishStatistic,
        aggregation=Aggregation.SUM,
        metric_field="total_catholic_population",
        group_by=HierarchyGroup.PARISH,
        unit="faithful",
    ),
    StatisticIndicator(
        key="annual_infant_baptisms_by_parish",
        title="Annual Infant Baptisms by Parish",
        description="Sum of reported infant baptisms per parish for a reporting year.",
        source_model=AnnualParishStatistic,
        aggregation=Aggregation.SUM,
        metric_field="infant_baptisms",
        group_by=HierarchyGroup.PARISH,
        unit="baptisms",
    ),
    StatisticIndicator(
        key="annual_adult_baptisms_by_parish",
        title="Annual Adult Baptisms by Parish",
        description="Sum of reported adult baptisms per parish for a reporting year.",
        source_model=AnnualParishStatistic,
        aggregation=Aggregation.SUM,
        metric_field="adult_baptisms",
        group_by=HierarchyGroup.PARISH,
        unit="baptisms",
    ),
    StatisticIndicator(
        key="annual_confirmations_by_parish",
        title="Annual Confirmations by Parish",
        description="Sum of reported confirmations per parish for a reporting year.",
        source_model=AnnualParishStatistic,
        aggregation=Aggregation.SUM,
        metric_field="confirmations",
        group_by=HierarchyGroup.PARISH,
        unit="confirmations",
    ),
    StatisticIndicator(
        key="annual_marriages_both_catholic_by_parish",
        title="Annual Marriages (Both Catholic) by Parish",
        description="Sum of reported marriages between two catholics per parish for a reporting year.",
        source_model=AnnualParishStatistic,
        aggregation=Aggregation.SUM,
        metric_field="marriages_both_catholic",
        group_by=HierarchyGroup.PARISH,
        unit="marriages",
    ),
    StatisticIndicator(
        key="annual_marriages_mixed_religion_by_parish",
        title="Annual Mixed-Religion Marriages by Parish",
        description="Sum of reported mixed-religion marriages per parish for a reporting year.",
        source_model=AnnualParishStatistic,
        aggregation=Aggregation.SUM,
        metric_field="marriages_mixed_religion",
        group_by=HierarchyGroup.PARISH,
        unit="marriages",
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
                scope_mode=indicator.scope_mode,
                via_model=(
                    indicator.via_model.__name__ if indicator.via_model else None
                ),
                via_local_field=indicator.via_local_field,
                via_scope_field=indicator.via_scope_field,
                group_by_field=indicator.group_by_field,
                label_model=(
                    indicator.label_model.__name__ if indicator.label_model else None
                ),
                label_field=indicator.label_field,
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
        param_filters: dict[str, Any] | None = None,
    ) -> IndicatorResult:
        """Compute one registered indicator within an archdiocesan/deanery scope.

        When both ``deanery_id`` and ``archdiocese_id`` are supplied the more
        specific deanery scope wins (matching ``get_descendant_parish_ids``
        semantics).

        ``param_filters`` adds runtime equality constraints (``{"field":
        "report_year", "value": 2026}``) on top of the configured
        ``indicator.filters`` — used e.g. by the Annuario Pontificio report to
        pin the annual-return indicators to one reporting year.
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

        # 1b. Polymorphic org sources (Document registry) additionally match
        #     rows attached directly to the scoped deanery/deaneries or the
        #     archdiocese itself.
        org_scope = None
        if indicator.scope_mode == ScopeMode.POLYMORPHIC_ORG:
            if deanery_id is not None:
                deanery_ids = [deanery_id]
            else:
                deanery_ids = await self.repo.get_deanery_ids(archdiocese_id)
            org_scope = {
                "parish_ids": list(parish_ids),
                "deanery_ids": deanery_ids,
                "archdiocese_id": archdiocese_id,
            }

        # 2. Resolve ancestry (parish -> deanery/archdiocese) only for
        #    hierarchical bucketing above the parish level.
        ancestry = {}
        if indicator.group_by in _NEEDS_ANCESTRY and not indicator.group_by_field:
            ancestry = await get_parish_ancestry_map(self.db, parish_ids)

        # 3. Fetch the raw source rows scoped to those parishes. Runtime
        #    param filters are merged after the configured static filters.
        filters = [*indicator.filters]
        for field, value in (param_filters or {}).items():
            if not hasattr(indicator.source_model, field):
                raise ValidationException(
                    "errors.indicator_invalid_param_filter",
                    message_params={"key": indicator.key, "field": field},
                )
            filters.append({"field": field, "value": value})

        rows = await self.repo.fetch_rows(
            indicator.source_model,
            parish_ids,
            filters=filters,
            date_field=indicator.date_field,
            start=start_date,
            end=end_date,
            via_model=indicator.via_model,
            via_local_field=indicator.via_local_field,
            via_scope_field=indicator.via_scope_field,
            org_scope=org_scope,
        )

        # 4. Bucket by (period, group) and reduce.
        acc: dict[tuple[str | None, uuid.UUID | None], dict[str, float]] = {}
        for row, scope_parish_id in self._normalise_rows(indicator, rows):
            state = acc.setdefault(
                self._bucket_key(indicator, row, scope_parish_id, ancestry),
                {"n": 0.0, "sum": 0.0, "done": 0.0},
            )
            state["n"] += 1.0
            if indicator.aggregation in (Aggregation.SUM, Aggregation.AVG):
                state["sum"] += float(getattr(row, indicator.metric_field))
            elif indicator.aggregation == Aggregation.RATE and (
                getattr(row, indicator.metric_field) is not None
            ):
                state["done"] += 1.0

        # 5. Resolve human-readable labels for the buckets.
        group_ids = {group for _period, group in acc if group is not None}
        if indicator.group_by_field:
            label_model = indicator.label_model
            label_field = indicator.label_field
        else:
            label_model = _LABEL_GROUP_MODEL[indicator.group_by]
            label_field = "name"
        group_names = await self.repo.fetch_names(
            label_model,
            group_ids,
            field=label_field,
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
        if indicator.scope_mode == ScopeMode.VIA_JOIN:
            if not hasattr(indicator.via_model, indicator.via_scope_field) or not hasattr(
                indicator.source_model, indicator.via_local_field
            ):
                raise ValidationException(
                    "errors.indicator_source_no_parish",
                    message_params={"key": indicator.key},
                )
            return
        if indicator.scope_mode == ScopeMode.POLYMORPHIC_ORG:
            for attr in ("parish_id", "deanery_id", "archdiocese_id"):
                if not hasattr(indicator.source_model, attr):
                    raise ValidationException(
                        "errors.indicator_source_no_parish",
                        message_params={"key": indicator.key},
                    )
            return
        if not hasattr(indicator.source_model, "parish_id"):
            raise ValidationException(
                "errors.indicator_source_no_parish",
                message_params={"key": indicator.key},
            )

    @staticmethod
    def _normalise_rows(
        indicator: StatisticIndicator, rows: list
    ) -> list[tuple[Any, uuid.UUID | None]]:
        """Pair every fetched row with the parish id used for bucketing.

        Via-join fetches return ``(instance, scope_parish_id)`` tuples; plain
        fetches return instances whose own ``parish_id`` is the bucket key.
        """
        if indicator.scope_mode == ScopeMode.VIA_JOIN:
            return [(row, scope_parish_id) for row, scope_parish_id in rows]
        return [(row, None) for row in rows]

    def _bucket_key(
        self,
        indicator: StatisticIndicator,
        row,
        scope_parish_id: uuid.UUID | None,
        ancestry: dict,
    ) -> tuple[str | None, uuid.UUID | None]:
        period = None
        if indicator.date_field:
            period = self._bucket_label(
                indicator.trend_bucket, getattr(row, indicator.date_field)
            )

        # Non-hierarchical grouping dimension (e.g. documents by type).
        if indicator.group_by_field:
            return period, getattr(row, indicator.group_by_field, None)

        level_attr = _GROUP_LEVEL_ATTR[indicator.group_by]
        row_parish = (
            scope_parish_id
            if scope_parish_id is not None
            else getattr(row, "parish_id", None)
        )
        if level_attr == "parish_id":
            group_id = row_parish
        else:
            # Polymorphic org rows may carry their own deanery/archdiocese
            # link even without a parish (docs attached to a deanery, ...).
            own = getattr(row, level_attr, None)
            if own is not None:
                group_id = own
            else:
                entry = ancestry.get(row_parish) if row_parish else None
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
        elif indicator.aggregation == Aggregation.RATE:
            value = state["done"] / state["n"] if state["n"] else 0.0
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
