"""
Land Assets Module FastAPI Endpoints
"""

import uuid
from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import enforce_parish_scope, get_db, require_roles
from app.models.audit_log import AuditLog
from app.models.enums import UserRole
from app.models.lease_agreement import LeaseAgreement
from app.models.lease_payment_schedule import LeasePaymentSchedule
from app.models.tax_payment import TaxPayment
from app.models.tax_record import TaxRecord
from app.schemas.land import (
    BuildingAssetCreate,
    BuildingAssetResponse,
    LandParcelCreate,
    LandParcelResponse,
    LandParcelUpdate,
)
from app.schemas.land_finance import (
    LeaseCreate,
    LeaseInstallmentCreate,
    LeaseInstallmentPayment,
    LeaseInstallmentResponse,
    LeaseResponse,
    TaxAssessmentCreate,
    TaxAssessmentResponse,
    TaxPaymentCreate,
    TaxPaymentResponse,
)
from app.services.land import LandAssetsService
from app.utils.response import ApiResponse

router = APIRouter(prefix="/land-assets", tags=["Land Assets & Parcels"])
ASSET_MANAGERS = [UserRole.SUPER_ADMIN, UserRole.CHANCELLOR, UserRole.ECONOMO]


def _user_id(user: dict) -> uuid.UUID | None:
    return uuid.UUID(user["sub"]) if user.get("sub") else None


async def _scoped_parcel(db: AsyncSession, service: LandAssetsService, user: dict, parcel_id: uuid.UUID):
    parcel = await service.get_parcel(parcel_id)
    await enforce_parish_scope(user, db, parcel.parish_id)
    return parcel


@router.get("/parcels", response_model=ApiResponse[list[LandParcelResponse]])
async def list_parcels(
    parish_id: uuid.UUID | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_roles([UserRole.READ_ONLY_AUDITOR])),
):
    parish_id = await enforce_parish_scope(current_user, db, parish_id)
    service = LandAssetsService(db)
    return ApiResponse.ok(data=await service.list_parcels(parish_id=parish_id))


@router.get("/parcels/{parcel_id}", response_model=ApiResponse[LandParcelResponse])
async def get_parcel(
    parcel_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_roles([UserRole.READ_ONLY_AUDITOR])),
):
    service = LandAssetsService(db)
    item = await service.get_parcel(parcel_id)
    await enforce_parish_scope(current_user, db, item.parish_id)
    return ApiResponse.ok(data=item)


@router.put("/parcels/{parcel_id}", response_model=ApiResponse[LandParcelResponse])
async def update_parcel(
    parcel_id: uuid.UUID,
    data: LandParcelUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_roles(ASSET_MANAGERS)),
):
    service = LandAssetsService(db)
    user_id = uuid.UUID(current_user["sub"]) if current_user.get("sub") else None
    parcel = await service.get_parcel(parcel_id)
    await enforce_parish_scope(current_user, db, parcel.parish_id)
    if "parish_id" in data.model_fields_set and data.parish_id is not None:
        await enforce_parish_scope(current_user, db, data.parish_id)
    elif "parish_id" in data.model_fields_set and (
        current_user.get("parish_id") or current_user.get("deanery_id")
    ):
        from app.core.exceptions import PermissionDeniedException

        raise PermissionDeniedException("Parish users cannot remove the parcel parish scope.")
    return ApiResponse.ok(
        data=await service.update_parcel(parcel_id, data, current_user_id=user_id),
        message="success.parcel_updated",
    )


@router.post(
    "/parcels",
    response_model=ApiResponse[LandParcelResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_parcel(
    data: LandParcelCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_roles(ASSET_MANAGERS)),
):
    service = LandAssetsService(db)
    user_id = uuid.UUID(current_user["sub"]) if current_user.get("sub") else None
    await enforce_parish_scope(current_user, db, data.parish_id)
    return ApiResponse.ok(
        data=await service.create_parcel(data, current_user_id=user_id),
        message="success.parcel_registered",
    )


@router.get(
    "/parcels/{parcel_id}/buildings", response_model=ApiResponse[list[BuildingAssetResponse]]
)
async def list_parcel_buildings(
    parcel_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_roles([UserRole.READ_ONLY_AUDITOR])),
):
    service = LandAssetsService(db)
    parcel = await service.get_parcel(parcel_id)
    await enforce_parish_scope(current_user, db, parcel.parish_id)
    return ApiResponse.ok(data=await service.list_buildings(parcel_id))


@router.post(
    "/buildings",
    response_model=ApiResponse[BuildingAssetResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_building_asset(
    data: BuildingAssetCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_roles(ASSET_MANAGERS)),
):
    service = LandAssetsService(db)
    user_id = uuid.UUID(current_user["sub"]) if current_user.get("sub") else None
    parcel = await service.get_parcel(data.parcel_id)
    await enforce_parish_scope(current_user, db, parcel.parish_id)
    return ApiResponse.ok(
        data=await service.create_building_asset(data, current_user_id=user_id),
        message="success.building_registered",
    )


@router.get("/parcels/{parcel_id}/leases", response_model=ApiResponse[list[LeaseResponse]])
async def list_leases(
    parcel_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_roles([UserRole.READ_ONLY_AUDITOR])),
):
    await _scoped_parcel(db, LandAssetsService(db), user, parcel_id)
    rows = await db.scalars(select(LeaseAgreement).where(
        LeaseAgreement.parcel_id == parcel_id, LeaseAgreement.is_deleted.is_(False)
    ).order_by(LeaseAgreement.start_date.desc()))
    return ApiResponse.ok(data=[LeaseResponse.model_validate(row) for row in rows])


@router.post("/leases", response_model=ApiResponse[LeaseResponse], status_code=status.HTTP_201_CREATED)
async def create_lease(
    data: LeaseCreate,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_roles(ASSET_MANAGERS)),
):
    await _scoped_parcel(db, LandAssetsService(db), user, data.parcel_id)
    existing = await db.scalar(select(LeaseAgreement.id).where(
        LeaseAgreement.lease_number == data.lease_number
    ))
    if existing:
        raise HTTPException(status_code=409, detail="Lease number is already in use")
    lease = LeaseAgreement(**data.model_dump())
    db.add(lease)
    await db.flush()
    db.add(AuditLog(user_id=_user_id(user), action="LAND_LEASE_CREATED", entity_name="lease_agreement",
                    entity_id=str(lease.id), details={"parcel_id": str(lease.parcel_id), "lease_number": lease.lease_number}))
    return ApiResponse.ok(data=LeaseResponse.model_validate(lease), message="success.lease_created")


@router.get("/leases/{lease_id}/installments", response_model=ApiResponse[list[LeaseInstallmentResponse]])
async def list_lease_installments(
    lease_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_roles([UserRole.READ_ONLY_AUDITOR])),
):
    lease = await db.scalar(select(LeaseAgreement).where(
        LeaseAgreement.id == lease_id, LeaseAgreement.is_deleted.is_(False)
    ))
    if lease is None:
        raise HTTPException(status_code=404, detail="Lease not found")
    await _scoped_parcel(db, LandAssetsService(db), user, lease.parcel_id)
    rows = await db.scalars(select(LeasePaymentSchedule).where(
        LeasePaymentSchedule.lease_agreement_id == lease_id,
        LeasePaymentSchedule.is_deleted.is_(False),
    ).order_by(LeasePaymentSchedule.due_date))
    return ApiResponse.ok(data=[LeaseInstallmentResponse.model_validate(row) for row in rows])


@router.post("/leases/{lease_id}/installments", response_model=ApiResponse[LeaseInstallmentResponse], status_code=status.HTTP_201_CREATED)
async def create_lease_installment(
    lease_id: uuid.UUID,
    data: LeaseInstallmentCreate,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_roles(ASSET_MANAGERS)),
):
    lease = await db.scalar(select(LeaseAgreement).where(
        LeaseAgreement.id == lease_id, LeaseAgreement.is_deleted.is_(False)
    ))
    if lease is None:
        raise HTTPException(status_code=404, detail="Lease not found")
    await _scoped_parcel(db, LandAssetsService(db), user, lease.parcel_id)
    item = LeasePaymentSchedule(lease_agreement_id=lease_id, **data.model_dump())
    db.add(item)
    await db.flush()
    db.add(AuditLog(user_id=_user_id(user), action="LEASE_INSTALLMENT_SCHEDULED", entity_name="lease_payment_schedule",
                    entity_id=str(item.id), details={"lease_id": str(lease_id), "due_date": data.due_date.isoformat(), "amount_rwf": data.amount_rwf}))
    return ApiResponse.ok(data=LeaseInstallmentResponse.model_validate(item), message="success.lease_installment_scheduled")


@router.post("/leases/installments/{installment_id}/payment", response_model=ApiResponse[LeaseInstallmentResponse])
async def mark_lease_installment_paid(
    installment_id: uuid.UUID,
    data: LeaseInstallmentPayment,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_roles(ASSET_MANAGERS)),
):
    item = await db.scalar(select(LeasePaymentSchedule).where(
        LeasePaymentSchedule.id == installment_id, LeasePaymentSchedule.is_deleted.is_(False)
    ))
    if item is None:
        raise HTTPException(status_code=404, detail="Lease installment not found")
    lease = await db.scalar(select(LeaseAgreement).where(LeaseAgreement.id == item.lease_agreement_id))
    await _scoped_parcel(db, LandAssetsService(db), user, lease.parcel_id)
    if item.is_paid:
        raise HTTPException(status_code=409, detail="Lease installment is already marked paid")
    if data.paid_date > date.today():
        raise HTTPException(status_code=400, detail="Payment date cannot be in the future")
    item.is_paid = True
    item.paid_date = data.paid_date
    item.receipt_number = data.receipt_number
    await db.flush()
    db.add(AuditLog(user_id=_user_id(user), action="LEASE_INSTALLMENT_PAID", entity_name="lease_payment_schedule",
                    entity_id=str(item.id), details={"receipt_number": item.receipt_number, "paid_date": item.paid_date.isoformat()}))
    return ApiResponse.ok(data=LeaseInstallmentResponse.model_validate(item), message="success.lease_payment_recorded")


@router.get("/parcels/{parcel_id}/tax-assessments", response_model=ApiResponse[list[TaxAssessmentResponse]])
async def list_tax_assessments(
    parcel_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_roles([UserRole.READ_ONLY_AUDITOR])),
):
    await _scoped_parcel(db, LandAssetsService(db), user, parcel_id)
    rows = await db.scalars(select(TaxRecord).where(
        TaxRecord.parcel_id == parcel_id, TaxRecord.is_deleted.is_(False)
    ).order_by(TaxRecord.tax_year.desc()))
    return ApiResponse.ok(data=[TaxAssessmentResponse.model_validate(row) for row in rows])


@router.post("/parcels/{parcel_id}/tax-assessments", response_model=ApiResponse[TaxAssessmentResponse], status_code=status.HTTP_201_CREATED)
async def create_tax_assessment(
    parcel_id: uuid.UUID,
    data: TaxAssessmentCreate,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_roles(ASSET_MANAGERS)),
):
    await _scoped_parcel(db, LandAssetsService(db), user, parcel_id)
    duplicate = await db.scalar(select(TaxRecord.id).where(
        TaxRecord.parcel_id == parcel_id, TaxRecord.tax_year == data.tax_year, TaxRecord.is_deleted.is_(False)
    ))
    if duplicate:
        raise HTTPException(status_code=409, detail="A tax assessment already exists for this parcel and year")
    record = TaxRecord(parcel_id=parcel_id, **data.model_dump())
    db.add(record)
    await db.flush()
    db.add(AuditLog(user_id=_user_id(user), action="LAND_TAX_ASSESSED", entity_name="tax_record",
                    entity_id=str(record.id), details={"parcel_id": str(parcel_id), "tax_year": record.tax_year, "tax_amount_rwf": record.tax_amount_rwf}))
    return ApiResponse.ok(data=TaxAssessmentResponse.model_validate(record), message="success.tax_assessment_created")


@router.get("/tax-assessments/{tax_record_id}/payments", response_model=ApiResponse[list[TaxPaymentResponse]])
async def list_tax_payments(
    tax_record_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_roles([UserRole.READ_ONLY_AUDITOR])),
):
    record = await db.scalar(select(TaxRecord).where(TaxRecord.id == tax_record_id, TaxRecord.is_deleted.is_(False)))
    if record is None:
        raise HTTPException(status_code=404, detail="Tax assessment not found")
    await _scoped_parcel(db, LandAssetsService(db), user, record.parcel_id)
    rows = await db.scalars(select(TaxPayment).where(
        TaxPayment.tax_record_id == tax_record_id, TaxPayment.is_deleted.is_(False)
    ).order_by(TaxPayment.payment_date))
    return ApiResponse.ok(data=[TaxPaymentResponse.model_validate(row) for row in rows])


@router.post("/tax-assessments/{tax_record_id}/payments", response_model=ApiResponse[TaxPaymentResponse], status_code=status.HTTP_201_CREATED)
async def create_tax_payment(
    tax_record_id: uuid.UUID,
    data: TaxPaymentCreate,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_roles(ASSET_MANAGERS)),
):
    record = await db.scalar(select(TaxRecord).where(TaxRecord.id == tax_record_id, TaxRecord.is_deleted.is_(False)))
    if record is None:
        raise HTTPException(status_code=404, detail="Tax assessment not found")
    await _scoped_parcel(db, LandAssetsService(db), user, record.parcel_id)
    total_paid = await db.scalar(select(func.coalesce(func.sum(TaxPayment.amount_paid_rwf), 0)).where(
        TaxPayment.tax_record_id == tax_record_id, TaxPayment.is_deleted.is_(False)
    ))
    paid_amount = Decimal(str(total_paid or 0))
    payment_amount = Decimal(str(data.amount_paid_rwf))
    assessed_amount = Decimal(str(record.tax_amount_rwf))
    if paid_amount + payment_amount > assessed_amount:
        raise HTTPException(status_code=400, detail="Payment exceeds the remaining assessed tax balance")
    payment = TaxPayment(tax_record_id=tax_record_id, **data.model_dump())
    db.add(payment)
    await db.flush()
    new_total = paid_amount + payment_amount
    record.status = "PAID" if new_total >= assessed_amount else "PARTIALLY_PAID"
    db.add(AuditLog(user_id=_user_id(user), action="LAND_TAX_PAYMENT_RECORDED", entity_name="tax_payment",
                    entity_id=str(payment.id), details={"tax_record_id": str(record.id), "amount_paid_rwf": data.amount_paid_rwf,
                    "receipt_number": payment.receipt_number, "remaining_rwf": float(assessed_amount - new_total)}))
    return ApiResponse.ok(data=TaxPaymentResponse.model_validate(payment), message="success.tax_payment_recorded")
