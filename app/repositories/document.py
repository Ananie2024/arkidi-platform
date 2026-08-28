"""
Document & Archive Module Database Repository
Handles generic Documents, Document Types, and Historical Ledger Books.
"""
import uuid
from typing import List, Optional
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.document import Document, ArchiveLedgerBook, ScannedPage
from app.models.document_type import DocumentType
from app.schemas.document import (
    ArchiveLedgerBookCreate,
    ScannedPageCreate,
    DocumentCreate,
    DocumentUpdate,
    DocumentTypeCreate,
    DocumentTypeUpdate,
)


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

    async def get_document_type_by_id(self, type_id: uuid.UUID) -> Optional[DocumentType]:
        stmt = select(DocumentType).where(
            DocumentType.id == type_id,
            DocumentType.is_deleted.is_(False),
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_document_type_by_code(self, code: str) -> Optional[DocumentType]:
        stmt = select(DocumentType).where(
            DocumentType.code == code,
            DocumentType.is_deleted.is_(False),
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_document_types(
        self,
        category: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> List[DocumentType]:
        stmt = select(DocumentType).where(DocumentType.is_deleted.is_(False))
        if category is not None:
            stmt = stmt.where(DocumentType.category == category)
        if is_active is not None:
            stmt = stmt.where(DocumentType.is_active == is_active)
        stmt = stmt.order_by(DocumentType.name_en)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def update_document_type(self, doc_type: DocumentType, data: DocumentTypeUpdate) -> DocumentType:
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
        uploaded_by_user_id: Optional[uuid.UUID] = None,
    ) -> Document:
        doc = Document(
            **data.model_dump(),
            uploaded_by_user_id=uploaded_by_user_id,
        )
        self.db.add(doc)
        await self.db.flush()
        return doc

    async def get_document_by_id(self, document_id: uuid.UUID) -> Optional[Document]:
        stmt = select(Document).where(
            Document.id == document_id,
            Document.is_deleted.is_(False),
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_documents(
        self,
        archdiocese_id: Optional[uuid.UUID] = None,
        deanery_id: Optional[uuid.UUID] = None,
        parish_id: Optional[uuid.UUID] = None,
        commission_id: Optional[uuid.UUID] = None,
        council_id: Optional[uuid.UUID] = None,
        meeting_id: Optional[uuid.UUID] = None,
        priest_id: Optional[uuid.UUID] = None,
        parcel_id: Optional[uuid.UUID] = None,
        document_type_id: Optional[uuid.UUID] = None,
        classification: Optional[str] = None,
        search: Optional[str] = None,
    ) -> List[Document]:
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
