"""
Parish / Centrale / Small Christian Communities FastAPI Endpoints
"""
import uuid

from typing import List, Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, require_roles
from app.models.enums import UserRole
from app.schemas.parish import (
    ParishCreate,
    ParishResponse,
    CentraleResponse,
    SCCResponse,
)
from app.services.parish import ParishService
from app.utils.response import ApiResponse

router = APIRouter(prefix="/geography", tags=["Ecclesiastical Geography"])


@router.get("/parishes", response_model=ApiResponse[List[ParishResponse]])
async def list_parishes(
    deanery_id: Optional[uuid.UUID] = None,
    db: AsyncSession = Depends(get_db),
):
    """List parishes, optionally filtered by deanery."""
    service = ParishService(db)
    items = await service.get_parishes(deanery_id=deanery_id)
    return ApiResponse.ok(data=items)


@router.get("/parishes/{parish_id}", response_model=ApiResponse[ParishResponse])
async def get_parish(parish_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Get single parish detail."""
    service = ParishService(db)
    item = await service.get_parish_by_id(parish_id)
    return ApiResponse.ok(data=item)


@router.post(
    "/parishes",
    response_model=ApiResponse[ParishResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_parish(
    data: ParishCreate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_roles([UserRole.SUPER_ADMIN, UserRole.CHANCELLOR])),
):
    """Admin endpoint to create a new parish."""
    service = ParishService(db)
    created = await service.create_parish(data)
    return ApiResponse.ok(data=created, message="Parish created successfully")


@router.get("/parishes/{parish_id}/centrales", response_model=ApiResponse[List[CentraleResponse]])
async def list_centrales(parish_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """List sub-parishes/centrales belonging to a parish."""
    service = ParishService(db)
    items = await service.get_centrales(parish_id)
    return ApiResponse.ok(data=items)


@router.get("/centrales/{centrale_id}/scc", response_model=ApiResponse[List[SCCResponse]])
async def list_scc(centrale_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """List Small Christian Communities (Imiryango-remezo) belonging to a centrale."""
    service = ParishService(db)
    items = await service.get_scc_list(centrale_id)
    return ApiResponse.ok(data=items)