"""
Archive Module Business Logic Service
"""
import uuid
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.document import ArchiveRepository
from app.schemas.document import (
    ArchiveLedgerBookCreate,
    ArchiveLedgerBookResponse,
    ScannedPageCreate,
    ScannedPageResponse,
)


class ArchiveService:
    def __init__(self, db: AsyncSession):
        self.repo = ArchiveRepository(db)

    async def list_books(self, parish_id: uuid.UUID) -> List[ArchiveLedgerBookResponse]:
        books = await self.repo.list_ledger_books(parish_id)
        return [ArchiveLedgerBookResponse.model_validate(b) for b in books]

    async def create_book(self, data: ArchiveLedgerBookCreate) -> ArchiveLedgerBookResponse:
        book = await self.repo.create_ledger_book(data)
        return ArchiveLedgerBookResponse.model_validate(book)

    async def add_page(self, data: ScannedPageCreate) -> ScannedPageResponse:
        page = await self.repo.add_scanned_page(data)
        return ScannedPageResponse.model_validate(page)

    async def list_pages(self, book_id: uuid.UUID) -> List[ScannedPageResponse]:
        pages = await self.repo.list_pages(book_id)
        return [ScannedPageResponse.model_validate(p) for p in pages]
