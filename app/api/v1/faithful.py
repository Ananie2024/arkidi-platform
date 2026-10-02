"""
Faithful Module FastAPI Endpoints
"""

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import enforce_parish_scope, get_db, require_roles
from app.models.enums import UserRole
from app.schemas.faithful import (
    FaithfulCreate,
    FaithfulResponse,
    FaithfulUpdate,
    FamilyCreate,
    FamilyResponse,
    FamilyUpdate,
)
from app.services.faithful import FaithfulService
from app.utils.pagination import PaginatedResponse, PaginationParams
from app.utils.response import ApiResponse

router = APIRouter(prefix="/faithful", tags=["Faithful & Families"])


@router.get("", response_model=ApiResponse[PaginatedResponse[FaithfulResponse]])
async def list_faithful(
    parish_id: uuid.UUID | None = None,
    search: str | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_roles([UserRole.READ_ONLY_AUDITOR])),
):
    """List registered parishioners with search, parish filtering and pagination."""
    service = FaithfulService(db)
    pagination = PaginationParams(page=page, page_size=page_size)
    scoped_parish_id = await enforce_parish_scope(current_user, db, parish_id)
    data = await service.list_faithful(
        parish_id=scoped_parish_id, search=search, params=pagination
    )
    return ApiResponse.ok(data=data)


@router.get("/families", response_model=ApiResponse[list[FamilyResponse]])
async def list_families(
    parish_id: uuid.UUID | None = None,
    search: str | None = Query(default=None, max_length=100),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_roles([UserRole.READ_ONLY_AUDITOR])),
):
    scoped_parish_id = await enforce_parish_scope(current_user, db, parish_id)
    return ApiResponse.ok(data=await FaithfulService(db).list_families(scoped_parish_id, search))


@router.get("/{faithful_id}", response_model=ApiResponse[FaithfulResponse])
async def get_faithful(
    faithful_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_roles([UserRole.READ_ONLY_AUDITOR])),
):
    """Get complete profile of a parishioner."""
    service = FaithfulService(db)
    data = await service.get_faithful_by_id(faithful_id)
    await enforce_parish_scope(current_user, db, data.parish_id)
    return ApiResponse.ok(data=data)


@router.patch("/{faithful_id}", response_model=ApiResponse[FaithfulResponse])
async def update_faithful(
    faithful_id: uuid.UUID,
    data: FaithfulUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_roles([UserRole.PARISH_SECRETARY])),
):
    service = FaithfulService(db)
    existing = await service.get_faithful_by_id(faithful_id)
    await enforce_parish_scope(current_user, db, existing.parish_id)
    return ApiResponse.ok(data=await service.update_faithful(faithful_id, data))


@router.post("", response_model=ApiResponse[FaithfulResponse], status_code=status.HTTP_201_CREATED)
async def create_faithful(
    data: FaithfulCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_roles([UserRole.PARISH_SECRETARY])),
):
    """Register a new faithful in the parish directory."""
    service = FaithfulService(db)
    await enforce_parish_scope(current_user, db, data.parish_id)
    user_id = uuid.UUID(current_user["sub"]) if current_user.get("sub") else None
    created = await service.create_faithful(data, current_user_id=user_id)
    return ApiResponse.ok(data=created, message="success.faithful_registered")


@router.post(
    "/families", response_model=ApiResponse[FamilyResponse], status_code=status.HTTP_201_CREATED
)
async def create_family(
    data: FamilyCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_roles([UserRole.PARISH_SECRETARY])),
):
    """Register a new household/family."""
    service = FaithfulService(db)
    await enforce_parish_scope(current_user, db, data.parish_id)
    user_id = uuid.UUID(current_user["sub"]) if current_user.get("sub") else None
    created = await service.create_family(data, current_user_id=user_id)
    return ApiResponse.ok(data=created, message="success.family_registered")


@router.get("/families/{family_id}", response_model=ApiResponse[FamilyResponse])
async def get_family(
    family_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_roles([UserRole.READ_ONLY_AUDITOR])),
):
    service = FaithfulService(db)
    family = await service.get_family(family_id)
    await enforce_parish_scope(current_user, db, family.parish_id)
    return ApiResponse.ok(data=family)


@router.get("/families/{family_id}/members", response_model=ApiResponse[list[FaithfulResponse]])
async def list_family_members(
    family_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_roles([UserRole.READ_ONLY_AUDITOR])),
):
    service = FaithfulService(db)
    family = await service.get_family(family_id)
    await enforce_parish_scope(current_user, db, family.parish_id)
    return ApiResponse.ok(data=await service.list_family_members(family_id))


@router.patch("/families/{family_id}", response_model=ApiResponse[FamilyResponse])
async def update_family(
    family_id: uuid.UUID,
    data: FamilyUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_roles([UserRole.PARISH_SECRETARY])),
):
    service = FaithfulService(db)
    family = await service.get_family(family_id)
    await enforce_parish_scope(current_user, db, family.parish_id)
    return ApiResponse.ok(data=await service.update_family(family_id, data))
