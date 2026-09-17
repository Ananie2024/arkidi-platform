"""
Archive Module FastAPI Endpoints — Canonical Ledger Books & Scanned Pages
"""
import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, require_roles
from app.models.enums import UserRole
from app.schemas.document import (
    ArchiveLedgerBookCreate,
    ArchiveLedgerBookResponse,
    ScannedPageCreate,
    ScannedPageResponse,
)
from app.services.document import ArchiveService
from app.utils.response import ApiResponse

router = APIRouter(prefix="/archive", tags=["Archive & Canonical Registers"])


@router.get("/books", response_model=ApiResponse[list[ArchiveLedgerBookResponse]])
async def list_books(
    parish_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_roles([UserRole.READ_ONLY_AUDITOR])),
):
    service = ArchiveService(db)
    return ApiResponse.ok(data=await service.list_books(parish_id))


@router.post(
    "/books",
    response_model=ApiResponse[ArchiveLedgerBookResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_book(
    data: ArchiveLedgerBookCreate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_roles([UserRole.SUPER_ADMIN, UserRole.ARCHBISHOP])),
):
    service = ArchiveService(db)
    return ApiResponse.ok(data=await service.create_book(data), message="success.ledger_book_created")


@router.get("/books/{book_id}/pages", response_model=ApiResponse[list[ScannedPageResponse]])
async def list_pages(
    book_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_roles([UserRole.READ_ONLY_AUDITOR])),
):
    service = ArchiveService(db)
    return ApiResponse.ok(data=await service.list_pages(book_id))


@router.get("/pages/search", response_model=ApiResponse[list[ScannedPageResponse]])
async def search_pages(
    query: str,
    parish_id: uuid.UUID | None = None,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_roles([UserRole.READ_ONLY_AUDITOR])),
):
    service = ArchiveService(db)
    return ApiResponse.ok(data=await service.search_pages(query=query, parish_id=parish_id))


@router.get("/pages/{page_id}", response_model=ApiResponse[ScannedPageResponse])
async def get_page(
    page_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_roles([UserRole.READ_ONLY_AUDITOR])),
):
    service = ArchiveService(db)
    return ApiResponse.ok(data=await service.get_page(page_id))


@router.post("/pages/{page_id}/ocr", response_model=ApiResponse[dict])
async def trigger_page_ocr(
    page_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_roles([UserRole.SUPER_ADMIN, UserRole.CHANCELLOR, UserRole.PARISH_SECRETARY])),
):
    service = ArchiveService(db)
    return ApiResponse.ok(data=await service.trigger_ocr(page_id), message="success.ocr_enqueued")


@router.post(
    "/pages",
    response_model=ApiResponse[ScannedPageResponse],
    status_code=status.HTTP_201_CREATED,
)
async def add_page(
    data: ScannedPageCreate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_roles([UserRole.SUPER_ADMIN, UserRole.CHANCELLOR, UserRole.PARISH_SECRETARY])),
):
    service = ArchiveService(db)
    return ApiResponse.ok(data=await service.add_page(data), message="success.scanned_page_added")

