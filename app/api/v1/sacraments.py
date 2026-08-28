"""
Sacraments Module FastAPI Endpoints
"""
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_db, get_current_user_payload, require_roles
from app.models.enums import UserRole
from app.models.sacrament import SacramentType
from app.schemas.sacrament import (
    BaptismCreate,
    BaptismResponse,
    ConfirmationCreate,
    ConfirmationResponse,
    MatrimonyCreate,
    MatrimonyResponse,
    FirstCommunionCreate,
    FirstCommunionResponse,
    HolyOrdersCreate,
    HolyOrdersResponse,
    ReligiousProfessionCreate,
    ReligiousProfessionResponse,
    AnointingOfTheSickCreate,
    AnointingOfTheSickResponse,
    ChristianFuneralCreate,
    ChristianFuneralResponse,
    CertificateRequest,
    CertificateResponse,
    AmendmentRequestCreate,
    AmendmentReviewRequest,
    SacramentalAmendmentResponse,
)
from app.services.sacrament import SacramentsService
from app.utils.response import ApiResponse

router = APIRouter(prefix="/sacraments", tags=["Sacraments & Canonical Registers"])

@router.get("/baptism", response_model=ApiResponse[list[BaptismResponse]])
async def list_baptisms(
    parish_id: uuid.UUID | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_roles([UserRole.READ_ONLY_AUDITOR])),
):
    service = SacramentsService(db)
    return ApiResponse.ok(data=await service.list_baptisms(parish_id=parish_id))


@router.get("/confirmation", response_model=ApiResponse[list[ConfirmationResponse]])
async def list_confirmations(
    parish_id: uuid.UUID | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_roles([UserRole.READ_ONLY_AUDITOR])),
):
    service = SacramentsService(db)
    return ApiResponse.ok(data=await service.list_confirmations(parish_id=parish_id))


@router.get("/matrimony", response_model=ApiResponse[list[MatrimonyResponse]])
async def list_matrimonies(
    parish_id: uuid.UUID | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_roles([UserRole.READ_ONLY_AUDITOR])),
):
    service = SacramentsService(db)
    return ApiResponse.ok(data=await service.list_matrimonies(parish_id=parish_id))

@router.post("/baptism", response_model=ApiResponse[BaptismResponse], status_code=status.HTTP_201_CREATED)
async def record_baptism(
    data: BaptismCreate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_roles([UserRole.PARISH_SECRETARY])),
):
    """Record official baptism entry in parish canonical registry."""
    service = SacramentsService(db)
    created = await service.record_baptism(data)
    return ApiResponse.ok(data=created, message="Baptism recorded successfully")


@router.post("/confirmation", response_model=ApiResponse[ConfirmationResponse], status_code=status.HTTP_201_CREATED)
async def record_confirmation(
    data: ConfirmationCreate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_roles([UserRole.PARISH_SECRETARY])),
):
    """Record confirmation entry in canonical register."""
    service = SacramentsService(db)
    created = await service.record_confirmation(data)
    return ApiResponse.ok(data=created, message="Confirmation recorded successfully")


@router.post("/matrimony", response_model=ApiResponse[MatrimonyResponse], status_code=status.HTTP_201_CREATED)
async def record_matrimony(
    data: MatrimonyCreate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_roles([UserRole.PARISH_SECRETARY])),
):
    """Record canonical marriage in parish register."""
    service = SacramentsService(db)
    created = await service.record_matrimony(data)
    return ApiResponse.ok(data=created, message="Matrimony recorded successfully")


@router.post("/first-communion", response_model=ApiResponse[FirstCommunionResponse], status_code=status.HTTP_201_CREATED)
async def record_first_communion(
    data: FirstCommunionCreate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_roles([UserRole.PARISH_SECRETARY])),
):
    """Record First Communion entry in the parish canonical register."""
    service = SacramentsService(db)
    created = await service.record_first_communion(data)
    return ApiResponse.ok(data=created, message="First Communion recorded successfully")


@router.post("/holy-orders", response_model=ApiResponse[HolyOrdersResponse], status_code=status.HTTP_201_CREATED)
async def record_holy_orders(
    data: HolyOrdersCreate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_roles([UserRole.SUPER_ADMIN, UserRole.CHANCELLOR])),
):
    """Record ordination (Diaconate, Priesthood, Episcopate) in the canonical register."""
    service = SacramentsService(db)
    created = await service.record_holy_orders(data)
    return ApiResponse.ok(data=created, message="Holy Orders recorded successfully")


@router.post("/religious-profession", response_model=ApiResponse[ReligiousProfessionResponse], status_code=status.HTTP_201_CREATED)
async def record_religious_profession(
    data: ReligiousProfessionCreate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_roles([UserRole.SUPER_ADMIN, UserRole.CHANCELLOR])),
):
    """Record religious profession (temporary or perpetual vows) in the canonical register."""
    service = SacramentsService(db)
    created = await service.record_religious_profession(data)
    return ApiResponse.ok(data=created, message="Religious Profession recorded successfully")


@router.post("/anointing", response_model=ApiResponse[AnointingOfTheSickResponse], status_code=status.HTTP_201_CREATED)
async def record_anointing(
    data: AnointingOfTheSickCreate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_roles([UserRole.PARISH_SECRETARY])),
):
    """Record anointing of the sick in the pastoral register."""
    service = SacramentsService(db)
    created = await service.record_anointing_of_the_sick(data)
    return ApiResponse.ok(data=created, message="Anointing of the Sick recorded successfully")


@router.post("/funerals", response_model=ApiResponse[ChristianFuneralResponse], status_code=status.HTTP_201_CREATED)
async def record_christian_funeral(
    data: ChristianFuneralCreate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_roles([UserRole.PARISH_SECRETARY])),
):
    """Record Christian funeral and burial in the canonical register."""
    service = SacramentsService(db)
    created = await service.record_christian_funeral(data)
    return ApiResponse.ok(data=created, message="Christian Funeral recorded successfully")


@router.post("/certificates/issue", response_model=ApiResponse[CertificateResponse], status_code=status.HTTP_201_CREATED)
async def issue_certificate(
    req: CertificateRequest,
    db: AsyncSession = Depends(get_db),
    user_payload: dict = Depends(require_roles([UserRole.PARISH_SECRETARY])),
):
    """Issue official sacramental certificate with verification QR code."""
    service = SacramentsService(db)
    issuer_id = uuid.UUID(user_payload["sub"])
    cert = await service.issue_certificate(req, issued_by_user_id=issuer_id)
    return ApiResponse.ok(data=cert, message="Certificate generated successfully")


# ---------------------------------------------------------------------------
# Sacramental Amendment Workflow Endpoints
# ---------------------------------------------------------------------------

@router.post(
    "/amendments",
    response_model=ApiResponse[SacramentalAmendmentResponse],
    status_code=status.HTTP_201_CREATED,
)
async def request_amendment(
    data: AmendmentRequestCreate,
    db: AsyncSession = Depends(get_db),
    user_payload: dict = Depends(require_roles([UserRole.PARISH_SECRETARY])),
):
    """Submit a formal canonical amendment request for a sacramental record."""
    service = SacramentsService(db)
    requester_id = uuid.UUID(user_payload["sub"]) if user_payload and "sub" in user_payload else None
    created = await service.request_amendment(data, requested_by_user_id=requester_id)
    return ApiResponse.ok(data=created, message="Sacramental amendment requested successfully")


@router.get(
    "/amendments",
    response_model=ApiResponse[List[SacramentalAmendmentResponse]],
)
async def list_amendments(
    sacrament_type: Optional[SacramentType] = Query(default=None),
    record_id: Optional[uuid.UUID] = Query(default=None),
    status: Optional[str] = Query(default=None),
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_roles([UserRole.READ_ONLY_AUDITOR])),
):
    """List sacramental amendment requests with filters."""
    service = SacramentsService(db)
    items = await service.list_amendments(
        sacrament_type=sacrament_type,
        record_id=record_id,
        amendment_status=status,
    )
    return ApiResponse.ok(data=items)


@router.get(
    "/amendments/{amendment_id}",
    response_model=ApiResponse[SacramentalAmendmentResponse],
)
async def get_amendment(
    amendment_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_roles([UserRole.READ_ONLY_AUDITOR])),
):
    """Get single sacramental amendment detail."""
    service = SacramentsService(db)
    item = await service.get_amendment(amendment_id)
    return ApiResponse.ok(data=item)


@router.post(
    "/amendments/{amendment_id}/review",
    response_model=ApiResponse[SacramentalAmendmentResponse],
)
async def review_amendment(
    amendment_id: uuid.UUID,
    review: AmendmentReviewRequest,
    db: AsyncSession = Depends(get_db),
    user_payload: dict = Depends(require_roles([UserRole.PARISH_PRIEST, UserRole.CHANCELLOR])),
):
    """Review (APPROVE or REJECT) a sacramental amendment. On approval, applies changes with canonical annotation."""
    service = SacramentsService(db)
    reviewer_id = uuid.UUID(user_payload["sub"])
    reviewed = await service.review_amendment(
        amendment_id=amendment_id,
        review=review,
        reviewer_id=reviewer_id,
    )
    return ApiResponse.ok(data=reviewed, message=f"Amendment {review.action.lower()}d successfully")

