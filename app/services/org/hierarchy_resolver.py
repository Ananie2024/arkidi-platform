"""
Organisational Hierarchy Rollup Helpers.

The Archdiocese of Kigali's structure is a four/five-level tree:

    Archdiocese → Deanery → Parish → Centrale → SmallChristianCommunity

``Faithful`` and ``Family`` records link directly to ``parish_id`` (they do not
denormalise a deanery/archdiocese), so any "count faithful in deanery X" style
query must first resolve the set of parishes under that deanery. These helpers
are the sanctioned place for that multi-table join logic.

Future modules — especially the statistics aggregation engine — should call these
functions instead of writing ad-hoc cross-table joins inline.

The structure is intentionally kept as separate typed columns per level (rather
than a generic recursive hierarchy) to match real diocesan structure and preserve
type safety at each level; the accepted trade-off is that rollups are explicit
joins, which is what this module encapsulates.
"""

import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.parish import Parish, Centrale, SmallChristianCommunity
from app.models.deanery import Deanery


async def get_ancestors(
    db: AsyncSession,
    *,
    parish_id: Optional[uuid.UUID] = None,
    centrale_id: Optional[uuid.UUID] = None,
    scc_id: Optional[uuid.UUID] = None,
) -> dict:
    """Resolve the full ancestor chain up to the Archdiocese for a given node.

    Exactly one of ``parish_id``, ``centrale_id`` or ``scc_id`` should be
    supplied. Returns a dict keyed by level name with the ids of the resolved
    chain, ``None`` for levels above the supplied node that could not be
    resolved (e.g. a parish has no connected centrale/scc):

    >>> {
    ...     "scc_id": None,
    ...     "centrale_id": None,
    ...     "parish_id": "…",
    ...     "deanery_id": "…",
    ...     "archdiocese_id": "…",
    ... }
    """
    chain: dict[str, Optional[uuid.UUID]] = {
        "scc_id": None,
        "centrale_id": None,
        "parish_id": None,
        "deanery_id": None,
        "archdiocese_id": None,
    }

    supplied = [
        value
        for value in (parish_id, centrale_id, scc_id)
        if value is not None
    ]
    if len(supplied) != 1:
        raise ValueError(
            "get_ancestors requires exactly one of parish_id, centrale_id, scc_id"
        )

    if scc_id is not None:
        chain["scc_id"] = scc_id
        scc = await db.get(SmallChristianCommunity, scc_id)
        if scc is None:
            return chain
        centrale_id = scc.centrale_id
        chain["centrale_id"] = centrale_id

    if centrale_id is not None:
        centrale = await db.get(Centrale, centrale_id)
        if centrale is None:
            return chain
        parish_id = centrale.parish_id
        chain["parish_id"] = parish_id

    if parish_id is not None:
        parish = await db.get(Parish, parish_id)
        if parish is None:
            return chain
        deanery_id = parish.deanery_id
        chain["deanery_id"] = deanery_id
        deanery = await db.get(Deanery, deanery_id)
        if deanery is not None:
            chain["archdiocese_id"] = deanery.archdiocese_id

    return chain


async def get_descendant_parish_ids(
    db: AsyncSession,
    *,
    deanery_id: Optional[uuid.UUID] = None,
    archdiocese_id: Optional[uuid.UUID] = None,
) -> list[uuid.UUID]:
    """Return every ``Parish.id`` under a deanery or the whole archdiocese.

    Either ``deanery_id`` (every parish in the deanery) or ``archdiocese_id``
    (every parish in the archdiocese) should be supplied. If both are ``None``
    an empty list is returned — callers should raise their own domain errors
    when a scope is strictly required.
    """
    if deanery_id is not None:
        stmt = select(Parish.id).where(Parish.deanery_id == deanery_id)
    elif archdiocese_id is not None:
        # Parishes hang off deaneries, so an archdiocese scope resolves through
        # them rather than through a parishes.archdiocese_id column.
        stmt = (
            select(Parish.id)
            .join(Deanery, Deanery.id == Parish.deanery_id)
            .where(Deanery.archdiocese_id == archdiocese_id)
        )
    else:
        return []

    result = await db.execute(stmt)
    return list(result.scalars().all())