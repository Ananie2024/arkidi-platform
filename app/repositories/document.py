"""
Archive Module Database Repository
"""
import uuid
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.document import ArchiveLedgerBook, ScannedPage
from app.schemas.document import ArchiveLedgerBookCreate, ScannedPageCreate


class ArchiveRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_ledger_books(self, parish_id: uuid.UUID) -> List[ArchiveLedgerBook]:
        stmt = select(ArchiveLedgerBook).where(
            ArchiveLedgerBook.parish_id == parish_id,
            ArchiveLedgerBook.is_deleted.is_(False),
        ).order_by(ArchiveLedgerBook.start_year.desc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def create_ledger_book(self, data: ArchiveLedgerBookCreate) -> ArchiveLedgerBook:
        book = ArchiveLedgerBook(**data.model_dump())
        self.db.add(book)
        await self.db.flush()
        return book

    async def add_scanned_page(self, data: ScannedPageCreate) -> ScannedPage:
        page = ScannedPage(**data.model_dump())
        self.db.add(page)
        await self.db.flush()
        return page

    async def list_pages(self, ledger_book_id: uuid.UUID) -> List[ScannedPage]:
        stmt = select(ScannedPage).where(ScannedPage.ledger_book_id == ledger_book_id).order_by(ScannedPage.page_number)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
