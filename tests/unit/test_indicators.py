"""
Unit tests for the generic Statistic Indicator Engine
(app/services/indicators.py + app/repositories/indicators.py).

Uses the same live-DB rolled-back-transaction pattern as
tests/unit/test_hierarchy_resolver.py so the engine is exercised against real
SQLAlchemy models and the hierarchy_resolver rollup helpers it builds on.
"""
import uuid
from datetime import date

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.core.exceptions import IndicatorNotFoundException, IndicatorScopeRequiredException
from app.models.deanery import Archdiocese, Deanery
from app.models.donation import Donation
from app.models.faithful import Faithful, Gender
from app.models.parcel import LandParcel
from app.models.parish import Parish
from app.schemas.indicators import HierarchyGroup, TrendBucket
from app.services.indicators import AggregationService


def _code(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


@pytest.fixture
async def indicator_org():
    """Archdiocese -> 2 deaneries -> 3 parishes with source records attached."""
    async with AsyncSessionLocal() as db:
        arch = Archdiocese(name="Indicator Test Arch", see_city="Kigali")
        db.add(arch)
        await db.flush()

        dea_a = Deanery(archdiocese_id=arch.id, name="Deanery Alpha", code=_code("DOY"))
        dea_b = Deanery(archdiocese_id=arch.id, name="Deanery Beta", code=_code("DOY"))
        db.add_all([dea_a, dea_b])
        await db.flush()

        par_a1 = Parish(deanery_id=dea_a.id, name="Parish A1", code=_code("PAR"))
        par_a2 = Parish(deanery_id=dea_a.id, name="Parish A2", code=_code("PAR"))
        par_b1 = Parish(deanery_id=dea_b.id, name="Parish B1", code=_code("PAR"))
        db.add_all([par_a1, par_a2, par_b1])
        await db.flush()

        # --- Faithful: 2 in A1, 1 in A2, 1 in B1 (Deanery Alpha total 3). ---
        faithful = [
            Faithful(
                registration_number=f"REG-{i}-{uuid.uuid4().hex[:6]}",
                first_name="First",
                last_name="Last",
                christian_name="Christian",
                gender=Gender.MALE,
                parish_id=parish_id,
            )
            for i, parish_id in enumerate(
                [par_a1.id, par_a1.id, par_a2.id, par_b1.id], start=1
            )
        ]
        db.add_all(faithful)

        # --- Land parcels: Alpha total 3000, Beta total 5000. ---
        db.add_all(
            [
                LandParcel(
                    upi=f"UPI-A1-{uuid.uuid4().hex[:6]}",
                    parcel_name="Parcel A1-a",
                    area_sqm=100.0,
                    estimated_value_rwf=1000,
                    parish_id=par_a1.id,
                ),
                LandParcel(
                    upi=f"UPI-A1b-{uuid.uuid4().hex[:6]}",
                    parcel_name="Parcel A1-b",
                    area_sqm=200.0,
                    estimated_value_rwf=2000,
                    parish_id=par_a1.id,
                ),
                LandParcel(
                    upi=f"UPI-B1-{uuid.uuid4().hex[:6]}",
                    parcel_name="Parcel B1",
                    area_sqm=150.0,
                    estimated_value_rwf=5000,
                    parish_id=par_b1.id,
                ),
            ]
        )

        # --- Donations: A1 Jan=150, A2 Feb=300, B1 Jan=75, B1 Mar=25. ---
        db.add_all(
            [
                Donation(
                    parish_id=par_a1.id,
                    amount=100,
                    donation_date=date(2026, 1, 5),
                    receipt_number=f"REC-A1-{uuid.uuid4().hex[:6]}",
                ),
                Donation(
                    parish_id=par_a1.id,
                    amount=50,
                    donation_date=date(2026, 1, 20),
                    receipt_number=f"REC-A1b-{uuid.uuid4().hex[:6]}",
                ),
                Donation(
                    parish_id=par_a2.id,
                    amount=300,
                    donation_date=date(2026, 2, 10),
                    receipt_number=f"REC-A2-{uuid.uuid4().hex[:6]}",
                ),
                Donation(
                    parish_id=par_b1.id,
                    amount=75,
                    donation_date=date(2026, 1, 8),
                    receipt_number=f"REC-B1-{uuid.uuid4().hex[:6]}",
                ),
                Donation(
                    parish_id=par_b1.id,
                    amount=25,
                    donation_date=date(2026, 3, 15),
                    receipt_number=f"REC-B1b-{uuid.uuid4().hex[:6]}",
                ),
            ]
        )

        # The session factory uses autoflush=False, so pending source records
        # must be flushed before the engine's SELECTs can see them.
        await db.flush()

        try:
            yield db, arch, dea_a, dea_b, par_a1, par_a2, par_b1
        finally:
            await db.rollback()


def _service(db: AsyncSession) -> AggregationService:
    return AggregationService(db)


@pytest.mark.asyncio
async def test_list_indicators_returns_config(indicator_org):
    db, *_ = indicator_org
    views = _service(db).list_indicators()

    keys = {v.key for v in views}
    assert {"faithful_by_deanery", "land_value_by_vicariate", "donations_trend_by_parish"} <= keys

    vicariate = next(v for v in views if v.key == "land_value_by_vicariate")
    assert vicariate.group_by == HierarchyGroup.VICARIATE
    assert vicariate.source_model == "LandParcel"
    assert vicariate.metric_field == "estimated_value_rwf"


@pytest.mark.asyncio
async def test_faithful_by_deanery_archdiocese_scope(indicator_org):
    db, arch, dea_a, dea_b, *_ = indicator_org
    result = await _service(db).compute("faithful_by_deanery", archdiocese_id=arch.id)

    assert result.group_by == HierarchyGroup.DEANERY
    assert result.aggregation.value == "count"
    by_name = {row.group_name: row.value for row in result.rows}
    assert by_name["Deanery Alpha"] == 3
    assert by_name["Deanery Beta"] == 1


@pytest.mark.asyncio
async def test_faithful_by_deanery_deanery_scope_filters(indicator_org):
    db, arch, dea_a, *_ = indicator_org
    result = await _service(db).compute("faithful_by_deanery", deanery_id=dea_a.id)

    assert len(result.rows) == 1
    assert result.rows[0].group_name == "Deanery Alpha"
    assert result.rows[0].value == 3


@pytest.mark.asyncio
async def test_land_value_by_vicariate(indicator_org):
    db, arch, *_ = indicator_org
    result = await _service(db).compute("land_value_by_vicariate", archdiocese_id=arch.id)

    assert result.group_by == HierarchyGroup.VICARIATE
    assert result.unit == "RWF"
    by_name = {row.group_name: row.value for row in result.rows}
    assert by_name["Deanery Alpha"] == 3000
    assert by_name["Deanery Beta"] == 5000



@pytest.mark.asyncio
async def test_donations_trend_by_parish(indicator_org):
    db, arch, *_ = indicator_org
    result = await _service(db).compute("donations_trend_by_parish", archdiocese_id=arch.id)

    assert result.trend_bucket == TrendBucket.MONTH
    series = {(row.group_name, row.period): row.value for row in result.rows}
    assert series["Parish A1", "2026-01"] == 150
    assert series["Parish A2", "2026-02"] == 300
    assert series["Parish B1", "2026-01"] == 75
    assert series["Parish B1", "2026-03"] == 25


@pytest.mark.asyncio
async def test_donations_trend_date_range_filter(indicator_org):
    db, arch, *_ = indicator_org
    result = await _service(db).compute(
        "donations_trend_by_parish",
        archdiocese_id=arch.id,
        start_date=date(2026, 1, 1),
        end_date=date(2026, 1, 31),
    )

    # Only the January donations survive the window.
    assert all(row.period == "2026-01" for row in result.rows)
    series = {(row.group_name, row.period): row.value for row in result.rows}
    assert series["Parish A1", "2026-01"] == 150
    assert series["Parish B1", "2026-01"] == 75


@pytest.mark.asyncio
async def test_unknown_indicator_raises(indicator_org):
    db, *_ = indicator_org
    with pytest.raises(IndicatorNotFoundException):
        await _service(db).compute("no_such_indicator", archdiocese_id=uuid.uuid4())


@pytest.mark.asyncio
async def test_compute_requires_scope(indicator_org):
    db, *_ = indicator_org
    with pytest.raises(IndicatorScopeRequiredException):
        await _service(db).compute("faithful_by_deanery")

