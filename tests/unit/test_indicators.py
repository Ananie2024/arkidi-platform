"""
Unit tests for the generic Statistic Indicator Engine
(app/services/indicators.py + app/repositories/indicators.py).

Uses the same live-DB rolled-back-transaction pattern as
tests/unit/test_hierarchy_resolver.py so the engine is exercised against real
SQLAlchemy models and the hierarchy_resolver rollup helpers it builds on.
"""

import uuid
from datetime import date

import pydantic
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.core.exceptions import (
    IndicatorNotFoundException,
    IndicatorScopeRequiredException,
)
from app.models.deanery import Archdiocese, Deanery
from app.models.document import ArchiveLedgerBook, Document, ScannedPage
from app.models.document_type import DocumentType
from app.models.donation import Donation
from app.models.faithful import Faithful, Gender
from app.models.parcel import LandParcel
from app.models.parish import Parish
from app.models.sacrament import SacramentType
from app.models.survey import AnnualParishStatistic
from app.schemas.indicators import (
    Aggregation,
    HierarchyGroup,
    ScopeMode,
    StatisticIndicator,
    TrendBucket,
)
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
            for i, parish_id in enumerate([par_a1.id, par_a1.id, par_a2.id, par_b1.id], start=1)
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

        # ------------------------------------------------------------------
        # Archives domain entities.
        # Documents: A1 decree + A1 backlog doc, A2 decree, B1 letter,
        # one archdiocese-scoped letter and one deanery-scoped untyped doc.
        # ------------------------------------------------------------------
        doc_type_decree = DocumentType(
            code=f"DECREE-{uuid.uuid4().hex[:8]}",
            name_en="Decree",
            name_fr="Décret",
            name_rw="Itegeko",
        )
        doc_type_letter = DocumentType(
            code=f"LETTER-{uuid.uuid4().hex[:8]}",
            name_en="Letter",
            name_fr="Lettre",
            name_rw="Ibarua",
        )
        db.add_all([doc_type_decree, doc_type_letter])
        await db.flush()

        db.add_all(
            [
                Document(
                    title="Decree A1",
                    file_path="archive/decree-a1.pdf",
                    document_type_id=doc_type_decree.id,
                    parish_id=par_a1.id,
                ),
                Document(
                    title="Decree A2",
                    file_path="archive/decree-a2.pdf",
                    document_type_id=doc_type_decree.id,
                    parish_id=par_a2.id,
                ),
                Document(
                    title="Letter B1",
                    file_path="archive/letter-b1.pdf",
                    document_type_id=doc_type_letter.id,
                    parish_id=par_b1.id,
                ),
                Document(
                    title="Backlog A1",
                    file_path="archive/backlog-a1.pdf",
                    document_type_id=doc_type_letter.id,
                    parish_id=par_a1.id,
                    disposition_status="DUE_FOR_REVIEW",
                ),
                Document(
                    title="Curia Letter",
                    file_path="archive/curia-letter.pdf",
                    document_type_id=doc_type_letter.id,
                    archdiocese_id=arch.id,
                ),
                Document(
                    title="Deanery Note",
                    file_path="archive/deanery-note.pdf",
                    deanery_id=dea_a.id,
                ),
            ]
        )

        # Scanned pages via ledger books: A1 has 1/2 pages OCR'd, B1 has 0/1.
        ledger_a1 = ArchiveLedgerBook(
            parish_id=par_a1.id,
            sacrament_type=SacramentType.BAPTISM,
            book_title="Baptisms A1",
            start_year=1920,
            end_year=1950,
            volume_number="V1",
        )
        ledger_b1 = ArchiveLedgerBook(
            parish_id=par_b1.id,
            sacrament_type=SacramentType.MATRIMONY,
            book_title="Marriages B1",
            start_year=1930,
            end_year=1960,
            volume_number="V2",
        )
        db.add_all([ledger_a1, ledger_b1])
        await db.flush()
        db.add_all(
            [
                ScannedPage(
                    ledger_book_id=ledger_a1.id,
                    page_number=1,
                    image_file_path="scans/a1-1.png",
                    ocr_raw_text="Baptismus 1923",
                ),
                ScannedPage(
                    ledger_book_id=ledger_a1.id,
                    page_number=2,
                    image_file_path="scans/a1-2.png",
                ),
                ScannedPage(
                    ledger_book_id=ledger_b1.id,
                    page_number=1,
                    image_file_path="scans/b1-1.png",
                ),
            ]
        )

        # Annual parish statistical returns for the Annuario indicators.
        db.add_all(
            [
                AnnualParishStatistic(
                    parish_id=par_a1.id,
                    report_year=2025,
                    total_catholic_population=1200,
                    infant_baptisms=30,
                    adult_baptisms=10,
                    confirmations=25,
                    marriages_both_catholic=12,
                    marriages_mixed_religion=3,
                ),
                AnnualParishStatistic(
                    parish_id=par_b1.id,
                    report_year=2026,
                    total_catholic_population=800,
                    infant_baptisms=5,
                    adult_baptisms=2,
                    confirmations=8,
                    marriages_both_catholic=4,
                    marriages_mixed_religion=1,
                ),
            ]
        )

        # The session factory uses autoflush=False, so pending source records
        # must be flushed before the engine's SELECTs can see them.
        await db.flush()

        try:
            yield (
                db,
                arch,
                dea_a,
                dea_b,
                par_a1,
                par_a2,
                par_b1,
                doc_type_decree,
                doc_type_letter,
            )
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


# ---------------------------------------------------------------------------
# Archives domain indicators
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_documents_by_parish(indicator_org):
    db, arch, _dea_a, _dea_b, *_rest = indicator_org
    result = await _service(db).compute("documents_by_parish", archdiocese_id=arch.id)

    by_name = {row.group_name: row.value for row in result.rows}
    assert by_name["Parish A1"] == 2  # Decree A1 + Backlog A1
    assert by_name["Parish A2"] == 1
    assert by_name["Parish B1"] == 1
    # Deanery- and archdiocese-scoped documents land in the unassigned bucket.
    unassigned = next(row for row in result.rows if row.group_id is None)
    assert unassigned.value == 2


@pytest.mark.asyncio
async def test_documents_by_type(indicator_org):
    db, arch, *_rest = indicator_org
    result = await _service(db).compute("documents_by_type", archdiocese_id=arch.id)

    by_label = {row.group_name: row.value for row in result.rows}
    assert by_label["Decree"] == 2
    assert by_label["Letter"] == 3  # Letter B1 + Backlog A1 + Curia Letter
    # The deanery-scoped document has no type -> unlabelled bucket.
    untyped = next(row for row in result.rows if row.group_id is None)
    assert untyped.value == 1
    assert untyped.group_name == ""


@pytest.mark.asyncio
async def test_retention_review_backlog(indicator_org):
    db, arch, _dea_a, _dea_b, par_a1, *_rest = indicator_org
    result = await _service(db).compute("retention_review_backlog", archdiocese_id=arch.id)

    # Only the DUE_FOR_REVIEW document is counted, bucketed under its parish.
    assert sum(row.value for row in result.rows) == 1
    by_name = {row.group_name: row.value for row in result.rows}
    assert by_name.get("Parish A1") == 1


@pytest.mark.asyncio
async def test_ocr_completion_rate(indicator_org):
    db, arch, *_rest = indicator_org
    result = await _service(db).compute("ocr_completion_rate", archdiocese_id=arch.id)

    assert result.aggregation.value == "rate"
    assert result.unit == "ratio"
    by_name = {row.group_name: row.value for row in result.rows}
    # Parish A1: 1 of 2 scanned pages OCR'd. Parish B1: 0 of 1.
    assert by_name["Parish A1"] == pytest.approx(0.5)
    assert by_name["Parish B1"] == pytest.approx(0.0)


@pytest.mark.asyncio
async def test_ocr_completion_rate_deanery_scope(indicator_org):
    db, _arch, dea_a, _dea_b, *_rest = indicator_org
    result = await _service(db).compute("ocr_completion_rate", deanery_id=dea_a.id)

    by_name = {row.group_name: row.value for row in result.rows}
    assert by_name == {"Parish A1": pytest.approx(0.5)}


# ---------------------------------------------------------------------------
# Annual-return indicators (param_filters) & engine edge cases
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_annual_indicators_respect_param_filters(indicator_org):
    db, arch, *_rest = indicator_org
    result = await _service(db).compute(
        "annual_catholic_population_by_parish",
        archdiocese_id=arch.id,
        param_filters={"report_year": 2025},
    )

    by_name = {row.group_name: row.value for row in result.rows}
    assert by_name == {"Parish A1": 1200}


@pytest.mark.asyncio
async def test_annual_param_filter_for_other_year_yields_no_rows(indicator_org):
    db, arch, *_rest = indicator_org
    result = await _service(db).compute(
        "annual_catholic_population_by_parish",
        archdiocese_id=arch.id,
        param_filters={"report_year": 1999},
    )

    assert result.rows == []


@pytest.mark.asyncio
async def test_empty_scope_returns_no_rows(indicator_org):
    """A valid-but-empty scope (no parishes/deaneries) computes an empty result."""
    db, *_rest = indicator_org
    empty_arch = Archdiocese(name="Empty Arch", see_city="Kigali")
    db.add(empty_arch)
    await db.flush()

    result = await _service(db).compute("faithful_by_deanery", archdiocese_id=empty_arch.id)
    assert result.rows == []

    archive_result = await _service(db).compute("documents_by_type", archdiocese_id=empty_arch.id)
    assert archive_result.rows == []


@pytest.mark.asyncio
async def test_unknown_scope_id_returns_no_rows(indicator_org):
    """A scope id that does not exist resolves to zero parishes, not an error."""
    db, *_rest = indicator_org
    result = await _service(db).compute("documents_by_parish", archdiocese_id=uuid.uuid4())
    assert result.rows == []


def test_rate_aggregation_requires_metric_field():
    with pytest.raises(pydantic.ValidationError):
        StatisticIndicator(
            key="bad_rate",
            title="Bad Rate",
            source_model=ScannedPage,
            aggregation=Aggregation.RATE,
        )


def test_via_join_requires_via_model_and_field():
    with pytest.raises(pydantic.ValidationError):
        StatisticIndicator(
            key="bad_via",
            title="Bad Via",
            source_model=ScannedPage,
            scope_mode=ScopeMode.VIA_JOIN,
        )


def test_group_by_field_requires_label_model():
    with pytest.raises(pydantic.ValidationError):
        StatisticIndicator(
            key="bad_group",
            title="Bad Group",
            source_model=Document,
            group_by_field="document_type_id",
        )


@pytest.mark.asyncio
async def test_list_indicators_exposes_archives_config(indicator_org):
    db, *_rest = indicator_org
    views = {v.key: v for v in _service(db).list_indicators()}

    by_type = views["documents_by_type"]
    assert by_type.group_by_field == "document_type_id"
    assert by_type.label_model == "DocumentType"
    assert by_type.label_field == "name_en"
    assert by_type.scope_mode == ScopeMode.POLYMORPHIC_ORG
    assert by_type.source_model == "Document"

    backlog = views["retention_review_backlog"]
    assert backlog.filters == [{"field": "disposition_status", "value": "DUE_FOR_REVIEW"}]

    ocr = views["ocr_completion_rate"]
    assert ocr.scope_mode == ScopeMode.VIA_JOIN
    assert ocr.via_model == "ArchiveLedgerBook"
    assert ocr.via_local_field == "ledger_book_id"
    assert ocr.aggregation == Aggregation.RATE
    assert ocr.metric_field == "ocr_raw_text"

    annual = views["annual_catholic_population_by_parish"]
    assert annual.source_model == "AnnualParishStatistic"
    assert annual.metric_field == "total_catholic_population"
