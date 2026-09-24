"""
Document & Archive Module Database Repository
Handles generic Documents, Document Types, and Historical Ledger Books.
"""

from __future__ import annotations

import uuid

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import ArchiveLedgerBook, Document, ScannedPage
from app.models.document_type import DocumentType
from app.models.sacrament import SacramentType
from app.schemas.document import (
    ArchiveLedgerBookCreate,
    DocumentCreate,
    DocumentTypeCreate,
    DocumentTypeUpdate,
    DocumentUpdate,
    ScannedPageCreate,
)


class ArchiveRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_ledger_books(self, parish_id: uuid.UUID) -> list[ArchiveLedgerBook]:
        stmt = (
            select(ArchiveLedgerBook)
            .where(
                ArchiveLedgerBook.parish_id == parish_id,
                ArchiveLedgerBook.is_deleted.is_(False),
            )
            .order_by(ArchiveLedgerBook.start_year.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_ledger_book(
        self,
        parish_id: uuid.UUID,
        sacrament_type: SacramentType,
        volume_number: str,
    ) -> ArchiveLedgerBook | None:
        """Return the active canonical ledger book matching the natural key,
        so callers can refuse to re-create an already-registered physical book."""
        stmt = select(ArchiveLedgerBook).where(
            ArchiveLedgerBook.parish_id == parish_id,
            ArchiveLedgerBook.sacrament_type == sacrament_type,
            ArchiveLedgerBook.volume_number == volume_number,
            ArchiveLedgerBook.is_deleted.is_(False),
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_ledger_book(self, data: ArchiveLedgerBookCreate) -> ArchiveLedgerBook:
        book = ArchiveLedgerBook(**data.model_dump())
        self.db.add(book)
        await self.db.flush()
        return book

    async def get_scanned_page(
        self, ledger_book_id: uuid.UUID, page_number: int
    ) -> ScannedPage | None:
        """Return a scanned page matching the natural key (book, page number)."""
        stmt = select(ScannedPage).where(
            ScannedPage.ledger_book_id == ledger_book_id,
            ScannedPage.page_number == page_number,
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def add_scanned_page(self, data: ScannedPageCreate) -> ScannedPage:
        page = ScannedPage(**data.model_dump())
        self.db.add(page)
        # Keep the canonical book's scan counter in sync so the archive summary
        # never goes stale. The page row is added in the same transaction.
        book_stmt = select(ArchiveLedgerBook).where(ArchiveLedgerBook.id == data.ledger_book_id)
        book = (await self.db.execute(book_stmt)).scalar_one_or_none()
        if book is not None:
            book.total_scanned_pages += 1
        await self.db.flush()
        return page

    async def get_page_by_id(self, page_id: uuid.UUID) -> ScannedPage | None:
        stmt = select(ScannedPage).where(ScannedPage.id == page_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_pages(self, ledger_book_id: uuid.UUID) -> list[ScannedPage]:
        stmt = (
            select(ScannedPage)
            .where(ScannedPage.ledger_book_id == ledger_book_id)
            .order_by(ScannedPage.page_number)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def search_pages(
        self, query: str, parish_id: uuid.UUID | None = None
    ) -> list[ScannedPage]:
        stmt = select(ScannedPage).join(
            ArchiveLedgerBook, ScannedPage.ledger_book_id == ArchiveLedgerBook.id
        )
        if parish_id:
            stmt = stmt.where(ArchiveLedgerBook.parish_id == parish_id)
        stmt = stmt.where(
            or_(
                ScannedPage.ocr_raw_text.ilike(f"%{query}%"),
                ArchiveLedgerBook.book_title.ilike(f"%{query}%"),
            )
        ).order_by(ArchiveLedgerBook.start_year.desc(), ScannedPage.page_number)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())


class DocumentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    # -----------------------------------------------------------------------
    # Document Type Methods
    # -----------------------------------------------------------------------

    async def create_document_type(self, data: DocumentTypeCreate) -> DocumentType:
        doc_type = DocumentType(**data.model_dump())
        self.db.add(doc_type)
        await self.db.flush()
        return doc_type

    async def get_document_type_by_id(self, type_id: uuid.UUID) -> DocumentType | None:
        stmt = select(DocumentType).where(
            DocumentType.id == type_id,
            DocumentType.is_deleted.is_(False),
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_document_type_by_code(self, code: str) -> DocumentType | None:
        stmt = select(DocumentType).where(
            DocumentType.code == code,
            DocumentType.is_deleted.is_(False),
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_document_types(
        self,
        category: str | None = None,
        is_active: bool | None = None,
    ) -> list[DocumentType]:
        stmt = select(DocumentType).where(DocumentType.is_deleted.is_(False))
        if category is not None:
            stmt = stmt.where(DocumentType.category == category)
        if is_active is not None:
            stmt = stmt.where(DocumentType.is_active == is_active)
        stmt = stmt.order_by(DocumentType.name_en)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def update_document_type(
        self, doc_type: DocumentType, data: DocumentTypeUpdate
    ) -> DocumentType:
        update_dict = data.model_dump(exclude_unset=True)
        for key, val in update_dict.items():
            setattr(doc_type, key, val)
        await self.db.flush()
        return doc_type

    # -----------------------------------------------------------------------
    # Document Methods
    # -----------------------------------------------------------------------

    async def create_document(
        self,
        data: DocumentCreate,
        uploaded_by_user_id: uuid.UUID | None = None,
    ) -> Document:
        doc = Document(
            **data.model_dump(),
            uploaded_by_user_id=uploaded_by_user_id,
        )
        self.db.add(doc)
        await self.db.flush()
        return doc

    async def get_document_by_id(self, document_id: uuid.UUID) -> Document | None:
        stmt = select(Document).where(
            Document.id == document_id,
            Document.is_deleted.is_(False),
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_document_by_checksum(self, checksum: str) -> Document | None:
        """Return the oldest active document registered with this exact content
        checksum (SHA-256). The archive stores each byte content exactly once."""
        stmt = (
            select(Document)
            .where(
                Document.checksum_sha256 == checksum,
                Document.is_deleted.is_(False),
            )
            .order_by(Document.created_at.asc(), Document.id.asc())
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def list_documents(
        self,
        archdiocese_id: uuid.UUID | None = None,
        deanery_id: uuid.UUID | None = None,
        parish_id: uuid.UUID | None = None,
        commission_id: uuid.UUID | None = None,
        council_id: uuid.UUID | None = None,
        meeting_id: uuid.UUID | None = None,
        priest_id: uuid.UUID | None = None,
        parcel_id: uuid.UUID | None = None,
        document_type_id: uuid.UUID | None = None,
        classification: str | None = None,
        search: str | None = None,
    ) -> list[Document]:
        stmt = select(Document).where(Document.is_deleted.is_(False))

        if archdiocese_id is not None:
            stmt = stmt.where(Document.archdiocese_id == archdiocese_id)
        if deanery_id is not None:
            stmt = stmt.where(Document.deanery_id == deanery_id)
        if parish_id is not None:
            stmt = stmt.where(Document.parish_id == parish_id)
        if commission_id is not None:
            stmt = stmt.where(Document.commission_id == commission_id)
        if council_id is not None:
            stmt = stmt.where(Document.council_id == council_id)
        if meeting_id is not None:
            stmt = stmt.where(Document.meeting_id == meeting_id)
        if priest_id is not None:
            stmt = stmt.where(Document.priest_id == priest_id)
        if parcel_id is not None:
            stmt = stmt.where(Document.parcel_id == parcel_id)
        if document_type_id is not None:
            stmt = stmt.where(Document.document_type_id == document_type_id)
        if classification is not None:
            stmt = stmt.where(Document.classification == classification)
        if search:
            search_pattern = f"%{search}%"
            stmt = stmt.where(
                or_(
                    Document.title.ilike(search_pattern),
                    Document.notes.ilike(search_pattern),
                )
            )

        stmt = stmt.order_by(Document.created_at.desc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def update_document(self, doc: Document, data: DocumentUpdate) -> Document:
        update_dict = data.model_dump(exclude_unset=True)
        for key, val in update_dict.items():
            setattr(doc, key, val)
        await self.db.flush()
        return doc

    async def delete_document(self, doc: Document) -> None:
        doc.soft_delete()
        await self.db.flush()
