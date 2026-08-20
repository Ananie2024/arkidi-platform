"""
Deanery FastAPI Endpoints
"""
import uuid
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.schemas.deanery import DeaneryResponse
from app.services.deanery import DeaneryService
from app.utils.response import ApiResponse

router = APIRouter(prefix="/geography", tags=["Ecclesiastical Geography"])


@router.get("/deaneries", response_model=ApiResponse[List[DeaneryResponse]])
async def list_deaneries(db: AsyncSession = Depends(get_db)):
    """List all deaneries in the Archdiocese of Kigali."""
    service = DeaneryService(db)
    items = await service.get_all_deaneries()
    return ApiResponse.ok(data=items)


@router.get("/deaneries/{deanery_id}", response_model=ApiResponse[DeaneryResponse])
async def get_deanery(deanery_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Get single deanery detail."""
    service = DeaneryService(db)
    item = await service.get_deanery_by_id(deanery_id)
    return ApiResponse.ok(data=item)
