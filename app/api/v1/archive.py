"""
Archive Module FastAPI Endpoints — Canonical Ledger Books & Scanned Pages
"""

import os
import uuid

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import EntityNotFoundException
from app.dependencies import enforce_parish_scope, get_db, require_roles
from app.models.document import ArchiveLedgerBook, ScannedPage
from app.models.enums import UserRole
from app.schemas.document import (
    ArchiveLedgerBookCreate,
    ArchiveLedgerBookResponse,
    ArchivePageReview,
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
    current_user: dict = Depends(require_roles([UserRole.READ_ONLY_AUDITOR])),
):
    await enforce_parish_scope(current_user, db, parish_id)
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
    current_user: dict = Depends(
        require_roles([
            UserRole.SUPER_ADMIN, UserRole.ARCHBISHOP, UserRole.CHANCELLOR,
            UserRole.PARISH_SECRETARY,
        ])
    ),
):
    await enforce_parish_scope(current_user, db, data.parish_id)
    service = ArchiveService(db)
    return ApiResponse.ok(
        data=await service.create_book(data), message="success.ledger_book_created"
    )


@router.get("/books/{book_id}/pages", response_model=ApiResponse[list[ScannedPageResponse]])
async def list_pages(
    book_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_roles([UserRole.READ_ONLY_AUDITOR])),
):
    parish_id = await db.scalar(
        select(ArchiveLedgerBook.parish_id).where(
            ArchiveLedgerBook.id == book_id, ArchiveLedgerBook.is_deleted.is_(False)
        )
    )
    if parish_id is None:
        raise EntityNotFoundException("errors.ledger_book_not_found")
    await enforce_parish_scope(current_user, db, parish_id)
    service = ArchiveService(db)
    return ApiResponse.ok(data=await service.list_pages(book_id))


@router.get("/pages/search", response_model=ApiResponse[list[ScannedPageResponse]])
async def search_pages(
    query: str = Query(min_length=2, max_length=100),
    parish_id: uuid.UUID | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_roles([UserRole.READ_ONLY_AUDITOR])),
):
    parish_id = await enforce_parish_scope(current_user, db, parish_id)
    service = ArchiveService(db)
    return ApiResponse.ok(data=await service.search_pages(query=query, parish_id=parish_id))


@router.get("/pages/{page_id}", response_model=ApiResponse[ScannedPageResponse])
async def get_page(
    page_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_roles([UserRole.READ_ONLY_AUDITOR])),
):
    book_id = await db.scalar(
        select(ScannedPage.ledger_book_id).where(ScannedPage.id == page_id)
    )
    parish_id = await db.scalar(
        select(ArchiveLedgerBook.parish_id).where(
            ArchiveLedgerBook.id == book_id, ArchiveLedgerBook.is_deleted.is_(False)
        )
    ) if book_id else None
    if parish_id is None:
        raise EntityNotFoundException("errors.scanned_page_not_found")
    await enforce_parish_scope(current_user, db, parish_id)
    service = ArchiveService(db)
    return ApiResponse.ok(data=await service.get_page(page_id))


@router.get("/pages/{page_id}/file")
async def download_page_image(
    page_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_roles([UserRole.READ_ONLY_AUDITOR])),
):
    page = await db.get(ScannedPage, page_id)
    if page is None:
        raise EntityNotFoundException("errors.scanned_page_not_found")
    parish_id = await db.scalar(
        select(ArchiveLedgerBook.parish_id).where(
            ArchiveLedgerBook.id == page.ledger_book_id,
            ArchiveLedgerBook.is_deleted.is_(False),
        )
    )
    if parish_id is None:
        raise EntityNotFoundException("errors.scanned_page_not_found")
    await enforce_parish_scope(current_user, db, parish_id)
    service = ArchiveService(db)
    path = await service.get_page_file_path(page_id)
    return FileResponse(path, media_type="application/octet-stream", filename=os.path.basename(path))


@router.post("/pages/{page_id}/review", response_model=ApiResponse[ScannedPageResponse])
async def review_page(
    page_id: uuid.UUID,
    review: ArchivePageReview,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(
        require_roles([
            UserRole.SUPER_ADMIN, UserRole.ARCHBISHOP, UserRole.CHANCELLOR,
            UserRole.PARISH_SECRETARY,
        ])
    ),
):
    page = await db.get(ScannedPage, page_id)
    if page is None:
        raise EntityNotFoundException("errors.scanned_page_not_found")
    parish_id = await db.scalar(
        select(ArchiveLedgerBook.parish_id).where(
            ArchiveLedgerBook.id == page.ledger_book_id,
            ArchiveLedgerBook.is_deleted.is_(False),
        )
    )
    if parish_id is None:
        raise EntityNotFoundException("errors.scanned_page_not_found")
    await enforce_parish_scope(current_user, db, parish_id)
    reviewer_id = uuid.UUID(current_user["sub"])
    updated = await ArchiveService(db).review_page(page_id, review, reviewer_id)
    return ApiResponse.ok(data=updated, message="success.archive_page_reviewed")


@router.post("/pages/{page_id}/rescan", response_model=ApiResponse[ScannedPageResponse])
async def replace_page_scan(
    page_id: uuid.UUID,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(
        require_roles([
            UserRole.SUPER_ADMIN, UserRole.ARCHBISHOP, UserRole.CHANCELLOR,
            UserRole.PARISH_SECRETARY,
        ])
    ),
):
    page = await db.get(ScannedPage, page_id)
    if page is None:
        raise EntityNotFoundException("errors.scanned_page_not_found")
    parish_id = await db.scalar(
        select(ArchiveLedgerBook.parish_id).where(
            ArchiveLedgerBook.id == page.ledger_book_id,
            ArchiveLedgerBook.is_deleted.is_(False),
        )
    )
    if parish_id is None:
        raise EntityNotFoundException("errors.scanned_page_not_found")
    await enforce_parish_scope(current_user, db, parish_id)
    updated = await ArchiveService(db).replace_page_scan(page_id, file)
    return ApiResponse.ok(data=updated, message="success.archive_page_rescanned")


@router.post("/pages/{page_id}/ocr", response_model=ApiResponse[dict])
async def trigger_page_ocr(
    page_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(
        require_roles([
            UserRole.SUPER_ADMIN, UserRole.ARCHBISHOP, UserRole.CHANCELLOR,
            UserRole.PARISH_SECRETARY,
        ])
    ),
):
    book_id = await db.scalar(
        select(ScannedPage.ledger_book_id).where(ScannedPage.id == page_id)
    )
    parish_id = await db.scalar(
        select(ArchiveLedgerBook.parish_id).where(
            ArchiveLedgerBook.id == book_id, ArchiveLedgerBook.is_deleted.is_(False)
        )
    ) if book_id else None
    if parish_id is None:
        raise EntityNotFoundException("errors.scanned_page_not_found")
    await enforce_parish_scope(current_user, db, parish_id)
    service = ArchiveService(db)
    return ApiResponse.ok(data=await service.trigger_ocr(page_id), message="success.ocr_enqueued")


@router.post(
    "/pages",
    response_model=ApiResponse[ScannedPageResponse],
    status_code=status.HTTP_201_CREATED,
)
async def add_page(
    ledger_book_id: uuid.UUID = Form(...),
    page_number: int = Form(..., gt=0),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(
        require_roles([UserRole.SUPER_ADMIN, UserRole.CHANCELLOR, UserRole.PARISH_SECRETARY])
    ),
):
    parish_id = await db.scalar(
        select(ArchiveLedgerBook.parish_id).where(
            ArchiveLedgerBook.id == ledger_book_id,
            ArchiveLedgerBook.is_deleted.is_(False),
        )
    )
    if parish_id is None:
        raise EntityNotFoundException("errors.ledger_book_not_found")
    await enforce_parish_scope(current_user, db, parish_id)
    service = ArchiveService(db)
    data = ScannedPageCreate(ledger_book_id=ledger_book_id, page_number=page_number)
    return ApiResponse.ok(
        data=await service.add_page(data, file), message="success.scanned_page_added"
    )
