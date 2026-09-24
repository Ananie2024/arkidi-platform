"""
Unit tests for the sacramental amendment-review workflow
(app/services/sacrament.py::SacramentsService.review_amendment).

The amendment workflow carries the highest canonical-correctness risk of the
newer surfaces: an approval must mutate the register record, append the
marginal annotation, write an audit-log entry, and advance the amendment
state — exactly once. These tests drive the service against the live schema
with a rolled-back transaction (same pattern as tests/unit/test_indicators.py).
"""

import uuid
from datetime import date

import pytest
from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.core.exceptions import EntityNotFoundException, ValidationException
from app.models.audit_log import AuditLog
from app.models.deanery import Archdiocese, Deanery
from app.models.faithful import Faithful, Gender
from app.models.parish import Parish
from app.models.sacrament import (
    AmendmentStatus,
    AmendmentType,
    BaptismRecord,
    SacramentalAmendment,
    SacramentType,
)
from app.schemas.sacrament import AmendmentReviewRequest
from app.services.sacrament import SacramentsService


@pytest.fixture
async def amendment_org():
    """Parish + faithful + baptism register record, rolled back afterwards."""
    async with AsyncSessionLocal() as db:
        arch = Archdiocese(name=f"Amend Arch {uuid.uuid4().hex[:6]}", see_city="Kigali")
        db.add(arch)
        await db.flush()
        dea = Deanery(
            archdiocese_id=arch.id,
            name=f"Amend Deanery {uuid.uuid4().hex[:6]}",
            code=f"DOY-{uuid.uuid4().hex[:8]}",
        )
        db.add(dea)
        await db.flush()
        par = Parish(
            deanery_id=dea.id,
            name=f"Amend Parish {uuid.uuid4().hex[:6]}",
            code=f"PAR-{uuid.uuid4().hex[:8]}",
        )
        db.add(par)
        await db.flush()

        faithful = Faithful(
            registration_number=f"REG-{uuid.uuid4().hex[:10]}",
            first_name="Jean",
            last_name="Mugisha",
            christian_name="Jean",
            gender=Gender.MALE,
            date_of_birth=date(2000, 1, 1),
            parish_id=par.id,
        )
        db.add(faithful)
        await db.flush()

        baptism = BaptismRecord(
            parish_id=par.id,
            faithful_id=faithful.id,
            registry_year=2000,
            volume_number="Vol 1",
            page_number="12",
            act_number="045",
            celebration_date=date(2000, 2, 2),
            minister_name="Abbé Jean",
            godfather_name="Pierre Nkurunziza",
        )
        db.add(baptism)
        await db.flush()

        amendment = SacramentalAmendment(
            sacrament_type=SacramentType.BAPTISM,
            record_id=baptism.id,
            amendment_type=AmendmentType.CLERICAL_ERROR,
            reason="Rectification of minister full canonical name",
            field_changes={
                "minister_name": {"old": "Abbé Jean", "new": "Abbé Jean-Baptiste Gasana"}
            },
            status=AmendmentStatus.PENDING,
        )
        db.add(amendment)
        await db.flush()

        reviewer_id = uuid.uuid4()
        try:
            yield db, baptism, amendment, reviewer_id
        finally:
            await db.rollback()


def _approve_request(
    review_notes: str = "Verified against diocesan archives",
) -> AmendmentReviewRequest:
    return AmendmentReviewRequest(action="APPROVE", review_notes=review_notes)


def _reject_request(review_notes: str = "Evidence insufficient") -> AmendmentReviewRequest:
    return AmendmentReviewRequest(action="REJECT", review_notes=review_notes)


@pytest.mark.asyncio
async def test_approval_applies_changes_marginal_note_and_audit(amendment_org):
    db, baptism, amendment, reviewer_id = amendment_org
    service = SacramentsService(db)

    reviewed = await service.review_amendment(
        amendment_id=amendment.id,
        review=_approve_request(),
        reviewer_id=reviewer_id,
    )

    assert reviewed.status == AmendmentStatus.APPROVED
    assert reviewed.reviewed_by_user_id == reviewer_id
    assert reviewed.reviewed_at is not None
    assert reviewed.review_notes == "Verified against diocesan archives"

    await db.refresh(baptism)
    # The field change was applied to the register record...
    assert baptism.minister_name == "Abbé Jean-Baptiste Gasana"
    # ...and the canonical marginal annotation was appended.
    assert "Canonical Amendment Approved" in (baptism.marginal_notes or "")
    assert "Rectification of minister full canonical name" in baptism.marginal_notes

    # An audit entry records who approved what, and why.
    audit = (
        await db.execute(
            select(AuditLog).where(
                AuditLog.action == "SACRAMENTAL_AMENDMENT_APPROVED",
                AuditLog.entity_id == str(baptism.id),
            )
        )
    ).scalar_one()
    assert audit.entity_name == SacramentType.BAPTISM.value
    assert audit.details["amendment_id"] == str(amendment.id)
    assert audit.details["changes"] == amendment.field_changes


@pytest.mark.asyncio
async def test_rejection_leaves_record_untouched_and_audits(amendment_org):
    db, baptism, amendment, reviewer_id = amendment_org
    service = SacramentsService(db)

    reviewed = await service.review_amendment(
        amendment_id=amendment.id,
        review=_reject_request(),
        reviewer_id=reviewer_id,
    )

    assert reviewed.status == AmendmentStatus.REJECTED
    await db.refresh(baptism)
    # Rejection must not mutate the canonical record.
    assert baptism.minister_name == "Abbé Jean"
    assert not baptism.marginal_notes

    audit = (
        await db.execute(
            select(AuditLog).where(
                AuditLog.action == "SACRAMENTAL_AMENDMENT_REJECTED",
                AuditLog.entity_id == str(baptism.id),
            )
        )
    ).scalar_one()
    assert audit.details["amendment_id"] == str(amendment.id)


@pytest.mark.asyncio
async def test_second_review_of_decided_amendment_raises(amendment_org):
    db, _baptism, amendment, reviewer_id = amendment_org
    service = SacramentsService(db)

    await service.review_amendment(
        amendment_id=amendment.id,
        review=_approve_request(),
        reviewer_id=reviewer_id,
    )

    # Re-reviewing (approve or reject) a no-longer-pending amendment is invalid.
    with pytest.raises(ValidationException) as exc_info:
        await service.review_amendment(
            amendment_id=amendment.id,
            review=_reject_request(),
            reviewer_id=reviewer_id,
        )
    assert exc_info.value.message_key == "errors.amendment_not_pending"


@pytest.mark.asyncio
async def test_review_unknown_amendment_raises(amendment_org):
    db, *_rest = amendment_org
    service = SacramentsService(db)

    with pytest.raises(EntityNotFoundException):
        await service.review_amendment(
            amendment_id=uuid.uuid4(),
            review=_approve_request(),
            reviewer_id=uuid.uuid4(),
        )


@pytest.mark.asyncio
async def test_approval_with_missing_target_record_raises(amendment_org):
    db, _baptism, amendment, reviewer_id = amendment_org
    service = SacramentsService(db)

    # Point the amendment at a register record that no longer exists.
    amendment.record_id = uuid.uuid4()

    with pytest.raises(EntityNotFoundException):
        await service.review_amendment(
            amendment_id=amendment.id,
            review=_approve_request(),
            reviewer_id=reviewer_id,
        )
    # The amendment itself stays pending after the failed approval.
    assert amendment.status == AmendmentStatus.PENDING
