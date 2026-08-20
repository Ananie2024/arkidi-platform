"""
Unit tests for the organisational hierarchy rollup helpers
(app/services/org/hierarchy_resolver.py).
"""
import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.models.deanery import Archdiocese, Deanery
from app.models.parish import Parish, Centrale, SmallChristianCommunity
from app.services.org.hierarchy_resolver import (
    get_ancestors,
    get_descendant_parish_ids,
)


def _unique_code(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


@pytest.fixture
async def org_chain():
    """Create a throwaway Archdiocese→Deanery→Parish→Centrale→SCC chain
    inside a rolled-back transaction so the test database stays clean.
    """
    async with AsyncSessionLocal() as db:
        archdiocese = Archdiocese(
            name="Test Archdiocese", see_city="Kigali"
        )
        db.add(archdiocese)
        await db.flush()

        deanery = Deanery(
            archdiocese_id=archdiocese.id,
            name="Test Deanery",
            code=_unique_code("DOY"),
        )
        db.add(deanery)
        await db.flush()

        parish = Parish(
            deanery_id=deanery.id,
            name="Test Parish",
            code=_unique_code("PAR"),
        )
        db.add(parish)
        await db.flush()

        centrale = Centrale(parish_id=parish.id, name="Test Centrale")
        db.add(centrale)
        await db.flush()

        scc = SmallChristianCommunity(
            centrale_id=centrale.id, name="Test SCC"
        )
        db.add(scc)
        await db.flush()

        try:
            yield db, archdiocese, deanery, parish, centrale, scc
        finally:
            await db.rollback()


@pytest.mark.asyncio
async def test_get_ancestors_resolves_full_chain_from_parish(org_chain):
    """A parish resolves its deanery and archdiocese ancestors."""
    db, archdiocese, deanery, parish, centrale, scc = org_chain

    chain = await get_ancestors(db, parish_id=parish.id)

    assert chain["parish_id"] == parish.id
    assert chain["deanery_id"] == deanery.id
    assert chain["archdiocese_id"] == archdiocese.id
    # A bare parish has no centrale/SCC attached.
    assert chain["centrale_id"] is None
    assert chain["scc_id"] is None


@pytest.mark.asyncio
async def test_get_ancestors_resolves_full_chain_from_scc(org_chain):
    """An SCC resolves its centrale, parish, deanery and archdiocese ancestors."""
    db, archdiocese, deanery, parish, centrale, scc = org_chain

    chain = await get_ancestors(db, scc_id=scc.id)

    assert chain["scc_id"] == scc.id
    assert chain["centrale_id"] == centrale.id
    assert chain["parish_id"] == parish.id
    assert chain["deanery_id"] == deanery.id
    assert chain["archdiocese_id"] == archdiocese.id


@pytest.mark.asyncio
async def test_get_ancestors_requires_exactly_one_level(org_chain):
    """Supplying zero — or more than one — scope id raises a ValueError."""
    db, *_ = org_chain

    with pytest.raises(ValueError):
        await get_ancestors(db)

    with pytest.raises(ValueError):
        await get_ancestors(db, parish_id=uuid.uuid4(), scc_id=uuid.uuid4())


@pytest.mark.asyncio
async def test_get_ancestors_unknown_parish_returns_none_chain(org_chain):
    """An unknown parish returns the skeleton chain with all ids None."""
    db, *_ = org_chain

    chain = await get_ancestors(db, parish_id=uuid.uuid4())

    assert chain["parish_id"] is None
    assert chain["deanery_id"] is None
    assert chain["archdiocese_id"] is None


@pytest.mark.asyncio
async def test_get_descendant_parish_ids_deanery(org_chain):
    """A deanery resolves all the parishes beneath it."""
    db, archdiocese, deanery, parish, centrale, scc = org_chain

    parish_ids = await get_descendant_parish_ids(db, deanery_id=deanery.id)

    assert parish.id in parish_ids
    # No other deanery's parishes leak in.
    assert len(parish_ids) == 1


@pytest.mark.asyncio
async def test_get_descendant_parish_ids_archdiocese(org_chain):
    """The archdiocese resolves every parish under all of its deaneries."""
    db, archdiocese, deanery, parish, centrale, scc = org_chain

    parish_ids = await get_descendant_parish_ids(
        db, archdiocese_id=archdiocese.id
    )

    assert parish.id in parish_ids


@pytest.mark.asyncio
async def test_get_descendant_parish_ids_empty_deanery(org_chain):
    """A deanery with no parishes returns [] instead of raising."""
    db, archdiocese, deanery, parish, centrale, scc = org_chain

    empty_deanery = Deanery(
        archdiocese_id=archdiocese.id,
        name="Empty Deanery",
        code=_unique_code("DOY"),
    )
    db.add(empty_deanery)
    await db.flush()

    parish_ids = await get_descendant_parish_ids(
        db, deanery_id=empty_deanery.id
    )

    assert parish_ids == []


@pytest.mark.asyncio
async def test_get_descendant_parish_ids_no_scope(org_chain):
    """With no scope supplied the helper returns [] rather than raising."""
    db, *_ = org_chain

    assert await get_descendant_parish_ids(db) == []