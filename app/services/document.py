"""
Document & Archive Module Business Logic Service
"""
import hashlib
import uuid
from typing import List, Optional
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import EntityNotFoundException, ValidationException
from app.models.document import Document
from app.models.document_type import DocumentType
from app.repositories.document import ArchiveRepository, DocumentRepository
from app.schemas.document import (
    ArchiveLedgerBookCreate,
    ArchiveLedgerBookResponse,
    ScannedPageCreate,
    ScannedPageResponse,
    DocumentCreate,
    DocumentUpdate,
    DocumentResponse,
    DocumentTypeCreate,
    DocumentTypeUpdate,
    DocumentTypeResponse,
    DocumentBase,
)
from app.utils.file_storage import storage_service


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


class DocumentService:
    def __init__(self, db: AsyncSession):
        self.repo = DocumentRepository(db)

    # -----------------------------------------------------------------------
    # Document Type Methods
    # -----------------------------------------------------------------------

    async def create_document_type(self, data: DocumentTypeCreate) -> DocumentTypeResponse:
        existing = await self.repo.get_document_type_by_code(data.code)
        if existing:
            raise ValidationException(f"Document type with code '{data.code}' already exists.")
        doc_type = await self.repo.create_document_type(data)
        return DocumentTypeResponse.model_validate(doc_type)

    async def get_document_type(self, type_id: uuid.UUID) -> DocumentTypeResponse:
        doc_type = await self.repo.get_document_type_by_id(type_id)
        if not doc_type:
            raise EntityNotFoundException("Document type not found.")
        return DocumentTypeResponse.model_validate(doc_type)

    async def list_document_types(
        self,
        category: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> List[DocumentTypeResponse]:
        types = await self.repo.list_document_types(category=category, is_active=is_active)
        return [DocumentTypeResponse.model_validate(t) for t in types]

    async def update_document_type(self, type_id: uuid.UUID, data: DocumentTypeUpdate) -> DocumentTypeResponse:
        doc_type = await self.repo.get_document_type_by_id(type_id)
        if not doc_type:
            raise EntityNotFoundException("Document type not found.")
        updated = await self.repo.update_document_type(doc_type, data)
        return DocumentTypeResponse.model_validate(updated)

    # -----------------------------------------------------------------------
    # Generic Document Methods
    # -----------------------------------------------------------------------

    async def upload_and_create(
        self,
        file: UploadFile,
        metadata: DocumentBase,
        uploaded_by_user_id: Optional[uuid.UUID] = None,
    ) -> DocumentResponse:
        """Save file to storage, compute SHA256 checksum and persist Document entity."""
        content = await file.read()
        file_size = len(content)
        checksum = hashlib.sha256(content).hexdigest()

        # Reset file seek for saving
        await file.seek(0)
        rel_path = await storage_service.save_file(file, subfolder="documents")

        create_data = DocumentCreate(
            title=metadata.title,
            document_type_id=metadata.document_type_id,
            classification=metadata.classification,
            notes=metadata.notes,
            archdiocese_id=metadata.archdiocese_id,
            deanery_id=metadata.deanery_id,
            parish_id=metadata.parish_id,
            commission_id=metadata.commission_id,
            council_id=metadata.council_id,
            meeting_id=metadata.meeting_id,
            priest_id=metadata.priest_id,
            parcel_id=metadata.parcel_id,
            file_path=rel_path,
            file_size_bytes=file_size,
            mime_type=file.content_type,
            checksum_sha256=checksum,
        )

        doc = await self.repo.create_document(create_data, uploaded_by_user_id=uploaded_by_user_id)
        return DocumentResponse.model_validate(doc)

    async def create_document(
        self,
        data: DocumentCreate,
        uploaded_by_user_id: Optional[uuid.UUID] = None,
    ) -> DocumentResponse:
        doc = await self.repo.create_document(data, uploaded_by_user_id=uploaded_by_user_id)
        return DocumentResponse.model_validate(doc)

    async def get_document(self, document_id: uuid.UUID) -> DocumentResponse:
        doc = await self.repo.get_document_by_id(document_id)
        if not doc:
            raise EntityNotFoundException("Document not found.")
        return DocumentResponse.model_validate(doc)

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
    ) -> List[DocumentResponse]:
        docs = await self.repo.list_documents(
            archdiocese_id=archdiocese_id,
            deanery_id=deanery_id,
            parish_id=parish_id,
            commission_id=commission_id,
            council_id=council_id,
            meeting_id=meeting_id,
            priest_id=priest_id,
            parcel_id=parcel_id,
            document_type_id=document_type_id,
            classification=classification,
            search=search,
        )
        return [DocumentResponse.model_validate(d) for d in docs]

    async def update_document(self, document_id: uuid.UUID, data: DocumentUpdate) -> DocumentResponse:
        doc = await self.repo.get_document_by_id(document_id)
        if not doc:
            raise EntityNotFoundException("Document not found.")
        updated = await self.repo.update_document(doc, data)
        return DocumentResponse.model_validate(updated)

    async def delete_document(self, document_id: uuid.UUID) -> None:
        doc = await self.repo.get_document_by_id(document_id)
        if not doc:
            raise EntityNotFoundException("Document not found.")
        await self.repo.delete_document(doc)

    async def get_physical_path(self, document_id: uuid.UUID) -> str:
        doc = await self.repo.get_document_by_id(document_id)
        if not doc:
            raise EntityNotFoundException("Document not found.")
        return storage_service.get_full_path(doc.file_path)
