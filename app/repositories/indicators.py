"""
Generic Statistic Indicator Engine — Database Repository.

``IndicatorRepository`` only *fetches raw rows* scoped to a resolved set of
parish ids (produced by ``hierarchy_resolver.get_descendant_parish_ids``) and
fetches human-readable names for output buckets. The cross-level organisational
joins deliberately live in ``app/services/org/hierarchy_resolver.py``; this
repository never joins across hierarchy tables.
"""
import uuid
from collections.abc import Iterable, Sequence
from datetime import date
from typing import Any

from sqlalchemy import select
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
    ) -> list[Any]:
        """Return every ``model`` row linked to one of ``parish_ids``.

        Rows are filtered by the optional ``filters`` (list of
        ``{"field": ..., "value": ...}`` equality constraints) and, when the
        model exposes ``date_field``, by the optional ``start``/``end`` window.
        Soft-deletable models are automatically restricted to ``is_deleted``
        false rows.
        """
        if not parish_ids:
            return []

        stmt = select(model).where(
            getattr(model, PARISH_ID_ATTRIBUTE).in_(parish_ids)
        )

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
        return list(result.scalars().all())

    async def fetch_names(
        self,
        model: type[Base],
        ids: Iterable[uuid.UUID | None],
    ) -> dict[uuid.UUID, str]:
        """Map ``model.id`` -> ``model.name`` for label-building output buckets.

        Only called with label models that expose a ``name`` column
        (Archdiocese, Deanery, Parish).
        """
        concrete = {i for i in ids if i is not None}
        if not concrete or not hasattr(model, _NAME_ATTRIBUTE):
            return {}

        stmt = select(model.id, getattr(model, _NAME_ATTRIBUTE)).where(
            model.id.in_(concrete)  # type: ignore[attr-defined]
        )
        result = await self.db.execute(stmt)
        return {row_id: name for row_id, name in result.all()}
