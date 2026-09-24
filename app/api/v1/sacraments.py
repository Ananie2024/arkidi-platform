"""
Sacraments Module FastAPI Endpoints
"""

import io
import uuid

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, require_roles
from app.models.enums import UserRole
from app.models.sacrament import SacramentType
from app.schemas.sacrament import (
    AmendmentRequestCreate,
    AmendmentReviewRequest,
    AnointingOfTheSickCreate,
    AnointingOfTheSickResponse,
    BaptismCreate,
    BaptismResponse,
    CertificateRequest,
    CertificateResponse,
    ChristianFuneralCreate,
    ChristianFuneralResponse,
    ConfirmationCreate,
    ConfirmationResponse,
    FirstCommunionCreate,
    FirstCommunionResponse,
    HolyOrdersCreate,
    HolyOrdersResponse,
    MatrimonyCreate,
    MatrimonyResponse,
    ReligiousProfessionCreate,
    ReligiousProfessionResponse,
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


@router.post(
    "/baptism", response_model=ApiResponse[BaptismResponse], status_code=status.HTTP_201_CREATED
)
async def record_baptism(
    data: BaptismCreate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_roles([UserRole.PARISH_SECRETARY])),
):
    """Record official baptism entry in parish canonical registry."""
    service = SacramentsService(db)
    created = await service.record_baptism(data)
    return ApiResponse.ok(data=created, message="success.baptism_recorded")


@router.post(
    "/confirmation",
    response_model=ApiResponse[ConfirmationResponse],
    status_code=status.HTTP_201_CREATED,
)
async def record_confirmation(
    data: ConfirmationCreate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_roles([UserRole.PARISH_SECRETARY])),
):
    """Record confirmation entry in canonical register."""
    service = SacramentsService(db)
    created = await service.record_confirmation(data)
    return ApiResponse.ok(data=created, message="success.confirmation_recorded")


@router.post(
    "/matrimony", response_model=ApiResponse[MatrimonyResponse], status_code=status.HTTP_201_CREATED
)
async def record_matrimony(
    data: MatrimonyCreate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_roles([UserRole.PARISH_SECRETARY])),
):
    """Record canonical marriage in parish register."""
    service = SacramentsService(db)
    created = await service.record_matrimony(data)
    return ApiResponse.ok(data=created, message="success.matrimony_recorded")


@router.post(
    "/first-communion",
    response_model=ApiResponse[FirstCommunionResponse],
    status_code=status.HTTP_201_CREATED,
)
async def record_first_communion(
    data: FirstCommunionCreate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_roles([UserRole.PARISH_SECRETARY])),
):
    """Record First Communion entry in the parish canonical register."""
    service = SacramentsService(db)
    created = await service.record_first_communion(data)
    return ApiResponse.ok(data=created, message="success.first_communion_recorded")


@router.post(
    "/holy-orders",
    response_model=ApiResponse[HolyOrdersResponse],
    status_code=status.HTTP_201_CREATED,
)
async def record_holy_orders(
    data: HolyOrdersCreate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_roles([UserRole.SUPER_ADMIN, UserRole.CHANCELLOR])),
):
    """Record ordination (Diaconate, Priesthood, Episcopate) in the canonical register."""
    service = SacramentsService(db)
    created = await service.record_holy_orders(data)
    return ApiResponse.ok(data=created, message="success.holy_orders_recorded")


@router.post(
    "/religious-profession",
    response_model=ApiResponse[ReligiousProfessionResponse],
    status_code=status.HTTP_201_CREATED,
)
async def record_religious_profession(
    data: ReligiousProfessionCreate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_roles([UserRole.SUPER_ADMIN, UserRole.CHANCELLOR])),
):
    """Record religious profession (temporary or perpetual vows) in the canonical register."""
    service = SacramentsService(db)
    created = await service.record_religious_profession(data)
    return ApiResponse.ok(data=created, message="success.religious_profession_recorded")


@router.post(
    "/anointing",
    response_model=ApiResponse[AnointingOfTheSickResponse],
    status_code=status.HTTP_201_CREATED,
)
async def record_anointing(
    data: AnointingOfTheSickCreate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_roles([UserRole.PARISH_SECRETARY])),
):
    """Record anointing of the sick in the pastoral register."""
    service = SacramentsService(db)
    created = await service.record_anointing_of_the_sick(data)
    return ApiResponse.ok(data=created, message="success.anointing_recorded")


@router.post(
    "/funerals",
    response_model=ApiResponse[ChristianFuneralResponse],
    status_code=status.HTTP_201_CREATED,
)
async def record_christian_funeral(
    data: ChristianFuneralCreate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_roles([UserRole.PARISH_SECRETARY])),
):
    """Record Christian funeral and burial in the canonical register."""
    service = SacramentsService(db)
    created = await service.record_christian_funeral(data)
    return ApiResponse.ok(data=created, message="success.funeral_recorded")


@router.post(
    "/certificates/issue",
    response_model=ApiResponse[CertificateResponse],
    status_code=status.HTTP_201_CREATED,
)
async def issue_certificate(
    req: CertificateRequest,
    db: AsyncSession = Depends(get_db),
    user_payload: dict = Depends(require_roles([UserRole.PARISH_SECRETARY])),
):
    """Issue official sacramental certificate with verification QR code."""
    service = SacramentsService(db)
    issuer_id = uuid.UUID(user_payload["sub"])
    cert = await service.issue_certificate(req, issued_by_user_id=issuer_id)
    return ApiResponse.ok(data=cert, message="success.certificate_generated")


@router.get("/certificates/{certificate_id}/pdf")
async def download_certificate_pdf(
    certificate_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_roles([UserRole.PARISH_SECRETARY])),
):
    """Stream the official printable PDF certificate for a given issuance."""
    service = SacramentsService(db)
    pdf_bytes, filename = await service.get_certificate_pdf(certificate_id)
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get(
    "/certificates/verify/{verification_token}", response_model=ApiResponse[CertificateResponse]
)
async def verify_certificate(
    verification_token: str,
    db: AsyncSession = Depends(get_db),
):
    """Public QR verification for an issued sacramental certificate."""
    service = SacramentsService(db)
    data = await service.verify_certificate(verification_token)
    return ApiResponse.ok(data=data, message="success.certificate_verified")


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
    requester_id = (
        uuid.UUID(user_payload["sub"]) if user_payload and "sub" in user_payload else None
    )
    created = await service.request_amendment(data, requested_by_user_id=requester_id)
    return ApiResponse.ok(data=created, message="success.amendment_requested")


@router.get(
    "/amendments",
    response_model=ApiResponse[list[SacramentalAmendmentResponse]],
)
async def list_amendments(
    sacrament_type: SacramentType | None = Query(default=None),
    record_id: uuid.UUID | None = Query(default=None),
    status: str | None = Query(default=None),
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
    return ApiResponse.ok(
        data=reviewed,
        message="success.amendment_reviewed",
        message_params={"action": review.action.lower()},
    )
