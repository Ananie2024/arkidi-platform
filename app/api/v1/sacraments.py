"""
Sacraments Module FastAPI Endpoints
"""
import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_db, get_current_user_payload
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
)
from app.services.sacrament import SacramentsService
from app.utils.response import ApiResponse

router = APIRouter(prefix="/sacraments", tags=["Sacraments & Canonical Registers"])


@router.post("/baptism", response_model=ApiResponse[BaptismResponse], status_code=status.HTTP_201_CREATED)
async def record_baptism(data: BaptismCreate, db: AsyncSession = Depends(get_db)):
    """Record official baptism entry in parish canonical registry."""
    service = SacramentsService(db)
    created = await service.record_baptism(data)
    return ApiResponse.ok(data=created, message="Baptism recorded successfully")


@router.post("/confirmation", response_model=ApiResponse[ConfirmationResponse], status_code=status.HTTP_201_CREATED)
async def record_confirmation(data: ConfirmationCreate, db: AsyncSession = Depends(get_db)):
    """Record confirmation entry in canonical register."""
    service = SacramentsService(db)
    created = await service.record_confirmation(data)
    return ApiResponse.ok(data=created, message="Confirmation recorded successfully")


@router.post("/matrimony", response_model=ApiResponse[MatrimonyResponse], status_code=status.HTTP_201_CREATED)
async def record_matrimony(data: MatrimonyCreate, db: AsyncSession = Depends(get_db)):
    """Record canonical marriage in parish register."""
    service = SacramentsService(db)
    created = await service.record_matrimony(data)
    return ApiResponse.ok(data=created, message="Matrimony recorded successfully")


@router.post("/first-communion", response_model=ApiResponse[FirstCommunionResponse], status_code=status.HTTP_201_CREATED)
async def record_first_communion(data: FirstCommunionCreate, db: AsyncSession = Depends(get_db)):
    """Record First Communion entry in the parish canonical register."""
    service = SacramentsService(db)
    created = await service.record_first_communion(data)
    return ApiResponse.ok(data=created, message="First Communion recorded successfully")


@router.post("/holy-orders", response_model=ApiResponse[HolyOrdersResponse], status_code=status.HTTP_201_CREATED)
async def record_holy_orders(data: HolyOrdersCreate, db: AsyncSession = Depends(get_db)):
    """Record ordination (Diaconate, Priesthood, Episcopate) in the canonical register."""
    service = SacramentsService(db)
    created = await service.record_holy_orders(data)
    return ApiResponse.ok(data=created, message="Holy Orders recorded successfully")


@router.post("/religious-profession", response_model=ApiResponse[ReligiousProfessionResponse], status_code=status.HTTP_201_CREATED)
async def record_religious_profession(data: ReligiousProfessionCreate, db: AsyncSession = Depends(get_db)):
    """Record religious profession (temporary or perpetual vows) in the canonical register."""
    service = SacramentsService(db)
    created = await service.record_religious_profession(data)
    return ApiResponse.ok(data=created, message="Religious Profession recorded successfully")


@router.post("/anointing", response_model=ApiResponse[AnointingOfTheSickResponse], status_code=status.HTTP_201_CREATED)
async def record_anointing(data: AnointingOfTheSickCreate, db: AsyncSession = Depends(get_db)):
    """Record anointing of the sick in the pastoral register."""
    service = SacramentsService(db)
    created = await service.record_anointing_of_the_sick(data)
    return ApiResponse.ok(data=created, message="Anointing of the Sick recorded successfully")


@router.post("/funerals", response_model=ApiResponse[ChristianFuneralResponse], status_code=status.HTTP_201_CREATED)
async def record_christian_funeral(data: ChristianFuneralCreate, db: AsyncSession = Depends(get_db)):
    """Record Christian funeral and burial in the canonical register."""
    service = SacramentsService(db)
    created = await service.record_christian_funeral(data)
    return ApiResponse.ok(data=created, message="Christian Funeral recorded successfully")


@router.post("/certificates/issue", response_model=ApiResponse[CertificateResponse], status_code=status.HTTP_201_CREATED)
async def issue_certificate(
    req: CertificateRequest,
    db: AsyncSession = Depends(get_db),
    user_payload: dict = Depends(get_current_user_payload),
):
    """Issue official sacramental certificate with verification QR code."""
    service = SacramentsService(db)
    issuer_id = uuid.UUID(user_payload["sub"])
    cert = await service.issue_certificate(req, issued_by_user_id=issuer_id)
    return ApiResponse.ok(data=cert, message="Certificate generated successfully")
