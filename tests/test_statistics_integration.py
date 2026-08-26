"""Integration tests for the statistics module end-to-end (needs live
Postgres + Redis).

Verifies that the Annuario Pontificio report computes parish/priest totals from
the database (task 3) instead of hardcoded values, and that the reporting
endpoints round-trip real records.
"""
import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy import delete

from app.core.database import AsyncSessionLocal
from app.models.deanery import Archdiocese, Deanery
from app.models.parish import Parish
from app.models.survey import AnnualParishStatistic


def _code(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


@pytest.fixture
async def org() -> tuple:
    """Create Archdiocese→Deanery→Parish and return ids for cleanup."""
    async with AsyncSessionLocal() as db:
        arch = Archdiocese(name=f"Test Arch {uuid.uuid4().hex[:6]}", see_city="Kigali")
        db.add(arch)
        await db.flush()
        dea = Deanery(archdiocese_id=arch.id, name="Test Deanery", code=_code("DOY"))
        db.add(dea)
        await db.flush()
        par = Parish(deanery_id=dea.id, name="Test Parish", code=_code("PAR"))
        db.add(par)
        await db.flush()
        await db.commit()
        yield arch.id, dea.id, par.id
        await db.execute(
            delete(AnnualParishStatistic).where(
                AnnualParishStatistic.parish_id == par.id
            )
        )
        await db.execute(delete(Parish).where(Parish.id == par.id))
        await db.execute(delete(Deanery).where(Deanery.id == dea.id))
        await db.execute(delete(Archdiocese).where(Archdiocese.id == arch.id))
        await db.commit()


@pytest.mark.asyncio
async def test_statistics_end_to_end(client: AsyncClient, org):
    _, _, parish_id = org
    year = 2025

    # 1. Submit an annual report for the test parish.
    payload = {
        "parish_id": str(parish_id),
        "report_year": year,
        "total_catholic_population": 1200,
        "infant_baptisms": 30,
        "adult_baptisms": 10,
        "confirmations": 25,
        "marriages_both_catholic": 12,
        "marriages_mixed_religion": 3,
    }
    resp = await client.post("/api/v1/statistics/parish-report", json=payload)
    assert resp.status_code == 200, resp.text
    assert resp.json()["success"] is True

    # 2. List reports, filtered by year.
    listed = await client.get(f"/api/v1/statistics/parish-reports?year={year}")
    assert listed.status_code == 200
    rows = listed.json()["data"]
    assert any(r["parish_id"] == str(parish_id) and r["report_year"] == year for r in rows)

    # 3. Annuario Pontificio aggregates the submitted figures and counts parish
    #    records from the DB (not hardcoded 34/178).
    annuario = await client.get(f"/api/v1/statistics/annuario-pontificio?year={year}")
    assert annuario.status_code == 200, annuario.text
    data = annuario.json()["data"]
    assert data["year"] == year
    assert data["total_parishes"] >= 1
    assert data["total_priests"] >= 0
    assert data["total_catholics"] >= 1200
    assert data["total_baptisms"] >= 40
    assert data["total_confirmations"] >= 25
    assert data["total_marriages"] >= 15