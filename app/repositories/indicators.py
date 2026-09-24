"""
Generic Statistic Indicator Engine — Database Repository.

``IndicatorRepository`` only *fetches raw rows* scoped to a resolved set of
parish ids (produced by ``hierarchy_resolver.get_descendant_parish_ids``) and
fetches human-readable names for output buckets. The cross-level organisational
joins deliberately live in ``app/services/org/hierarchy_resolver.py``; this
repository never joins across hierarchy tables — the single exception is the
per-indicator via-join (e.g. ``ScannedPage -> ArchiveLedgerBook``), which is
declared explicitly in the indicator configuration.
"""

import uuid
from collections.abc import Iterable, Sequence
from datetime import date
from typing import Any

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import Base

PARISH_ID_ATTRIBUTE = "parish_id"
_NAME_ATTRIBUTE = "name"


class IndicatorRepository:
    """Fetch source rows and label buckets for the aggregation engine."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def fetch_rows(
        self,
        model: type[Base],
        parish_ids: Sequence[uuid.UUID],
        *,
        filters: list[dict] | None = None,
        date_field: str | None = None,
        start: date | None = None,
        end: date | None = None,
        via_model: type[Base] | None = None,
        via_local_field: str | None = None,
        via_scope_field: str = PARISH_ID_ATTRIBUTE,
        org_scope: dict | None = None,
    ) -> list[Any]:
        """Return every ``model`` row reachable from the resolved scope.

        Row shapes by scope mode:

        - **default / org_scope without via**: ``model`` instances. Rows are
          filtered by ``parish_id IN parish_ids``, or — when ``org_scope`` is
          supplied (polymorphic ``Document``-style sources) — by the union of
          parish/deanery/archdiocese scope columns.
        - **via_model supplied**: ``(instance, scope_parish_id)`` tuples where
          the second element is the joined ``via_model.via_scope_field`` value
          used for parish bucketing.

        Rows are filtered by the optional ``filters`` (list of
        ``{"field": ..., "value": ...}`` equality constraints) and, when the
        model exposes ``date_field``, by the optional ``start``/``end`` window.
        Soft-deletable models are automatically restricted to ``is_deleted``
        false rows.
        """
        if via_model is not None:
            assert via_local_field is not None  # required when via_model is supplied
            scope_col = getattr(via_model, via_scope_field)
            stmt = (
                select(model, scope_col)
                .join(via_model, getattr(via_model, "id") == getattr(model, via_local_field))
                .where(scope_col.in_(parish_ids))
            )
        elif org_scope is not None:
            # Polymorphic org scoping (Document registry): a row is in scope
            # when it is attached to one of the resolved parishes, one of the
            # resolved deaneries, or the scope archdiocese itself.
            clauses = []
            if org_scope.get("parish_ids"):
                clauses.append(getattr(model, PARISH_ID_ATTRIBUTE).in_(org_scope["parish_ids"]))
            if org_scope.get("deanery_ids"):
                clauses.append(getattr(model, "deanery_id").in_(org_scope["deanery_ids"]))
            if org_scope.get("archdiocese_id") is not None:
                clauses.append(getattr(model, "archdiocese_id") == org_scope["archdiocese_id"])
            if not clauses:
                return []
            stmt = select(model).where(or_(*clauses))
        else:
            if not parish_ids:
                return []
            stmt = select(model).where(getattr(model, PARISH_ID_ATTRIBUTE).in_(parish_ids))

        if hasattr(model, "is_deleted"):
            stmt = stmt.where(model.is_deleted.is_(False))  # type: ignore[attr-defined]

        for flt in filters or []:
            column = getattr(model, flt["field"])
            stmt = stmt.where(column == flt["value"])

        if date_field:
            column = getattr(model, date_field)
            if start is not None:
                stmt = stmt.where(column >= start)
            if end is not None:
                stmt = stmt.where(column <= end)

        result = await self.db.execute(stmt)
        if via_model is not None:
            return [(row[0], row[1]) for row in result.all()]
        return list(result.scalars().all())

    async def get_deanery_ids(self, archdiocese_id: uuid.UUID) -> list[uuid.UUID]:
        """Return every deanery id under ``archdiocese_id``.

        Used to build the deanery half of a polymorphic org scope; the
        parish half comes from ``hierarchy_resolver.get_descendant_parish_ids``.
        """
        from app.models.deanery import Deanery

        result = await self.db.execute(
            select(Deanery.id).where(Deanery.archdiocese_id == archdiocese_id)
        )
        return list(result.scalars().all())

    async def fetch_names(
        self,
        model: type[Base],
        ids: Iterable[uuid.UUID | None],
        *,
        field: str = _NAME_ATTRIBUTE,
    ) -> dict[uuid.UUID, str]:
        """Map ``model.id`` -> ``model.<field>`` for labelling output buckets.

        Only called with label models that expose ``field`` (Archdiocese,
        Deanery, Parish by ``name``; DocumentType by ``name_en``).
        """
        concrete = {i for i in ids if i is not None}
        if not concrete or not hasattr(model, field):
            return {}

        stmt = select(model.id, getattr(model, field)).where(  # type: ignore[attr-defined]
            model.id.in_(concrete)  # type: ignore[attr-defined]
        )
        result = await self.db.execute(stmt)
        return {row_id: name for row_id, name in result.all()}
