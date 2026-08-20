"""
Faithful Module FastAPI Endpoints
"""
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_db
from app.schemas.faithful import (
    FaithfulCreate,
    FaithfulResponse,
    FamilyCreate,
    FamilyResponse,
)
from app.services.faithful import FaithfulService
from app.utils.pagination import PaginatedResponse, PaginationParams
from app.utils.response import ApiResponse

router = APIRouter(prefix="/faithful", tags=["Faithful & Families"])


@router.get("", response_model=ApiResponse[PaginatedResponse[FaithfulResponse]])
async def list_faithful(
    parish_id: Optional[uuid.UUID] = None,
    search: Optional[str] = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """List registered parishioners with search, parish filtering and pagination."""
    service = FaithfulService(db)
    pagination = PaginationParams(page=page, page_size=page_size)
    data = await service.list_faithful(parish_id=parish_id, search=search, params=pagination)
    return ApiResponse.ok(data=data)


@router.get("/{faithful_id}", response_model=ApiResponse[FaithfulResponse])
async def get_faithful(faithful_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Get complete profile of a parishioner."""
    service = FaithfulService(db)
    data = await service.get_faithful_by_id(faithful_id)
    return ApiResponse.ok(data=data)


@router.post("", response_model=ApiResponse[FaithfulResponse], status_code=status.HTTP_201_CREATED)
async def create_faithful(data: FaithfulCreate, db: AsyncSession = Depends(get_db)):
    """Register a new faithful in the parish directory."""
    service = FaithfulService(db)
    created = await service.create_faithful(data)
    return ApiResponse.ok(data=created, message="Faithful registered successfully")


@router.post("/families", response_model=ApiResponse[FamilyResponse], status_code=status.HTTP_201_CREATED)
async def create_family(data: FamilyCreate, db: AsyncSession = Depends(get_db)):
    """Register a new household/family."""
    service = FaithfulService(db)
    created = await service.create_family(data)
    return ApiResponse.ok(data=created, message="Family registered successfully")
