"""
Document & Archive Module Business Logic Service
"""
from __future__ import annotations

import hashlib
import logging
import uuid

from fastapi import UploadFile
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    DuplicateDocumentException,
    DuplicateLedgerBookException,
    DuplicateScannedPageException,
    EntityNotFoundException,
    ValidationException,
)
from app.repositories.document import ArchiveRepository, DocumentRepository
from app.schemas.document import (
    ArchiveLedgerBookCreate,
    ArchiveLedgerBookResponse,
    DocumentBase,
    DocumentCreate,
    DocumentResponse,
    DocumentTypeCreate,
    DocumentTypeResponse,
    DocumentTypeUpdate,
    DocumentUpdate,
    ScannedPageCreate,
    ScannedPageResponse,
)
from app.tasks.archive_ocr import process_ocr_page
from app.utils.file_storage import storage_service

logger = logging.getLogger("arkidi.services.document")

# Index/constraint names created by the archive deduplication migration
# (alembic b2f7c4d8a1e6). IntegrityError race guards only re-interpret
# violations of THESE constraints; any other DB error is re-raised untouched.
UQ_DOCUMENTS_CHECKSUM = "uq_documents_checksum_active"
UQ_LEDGER_BOOK_PARISH_VOLUME = "uq_ledger_book_parish_volume"
UQ_SCANNED_PAGE_BOOK_PAGE = "uq_scanned_page_book_page"


def _is_constraint_violation(exc: IntegrityError, constraint: str) -> bool:
    """Return True if ``exc`` is a duplicate-key violation of ``constraint``.

    The constraint name is embedded in the driver message for both asyncpg and
    psycopg2, so a simple membership check against ``orig`` is portable without
    reaching into dialect-specific ``diag`` objects.
    """
    orig = getattr(exc, "orig", None)
    return orig is not None and constraint in str(orig)


class ArchiveService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = ArchiveRepository(db)

    async def list_books(self, parish_id: uuid.UUID) -> list[ArchiveLedgerBookResponse]:
        books = await self.repo.list_ledger_books(parish_id)
        return [ArchiveLedgerBookResponse.model_validate(b) for b in books]

    async def create_book(self, data: ArchiveLedgerBookCreate) -> ArchiveLedgerBookResponse:
        # A physical canonical ledger book is uniquely identified by its parish,
        # sacrament type and volume number — refuse to register the same book twice.
        existing = await self.repo.get_ledger_book(
            data.parish_id, data.sacrament_type, data.volume_number
        )
        if existing:
            raise DuplicateLedgerBookException(
                data.parish_id, data.sacrament_type, data.volume_number
            )
        try:
            book = await self.repo.create_ledger_book(data)
        except IntegrityError as exc:
            await self.db.rollback()
            if _is_constraint_violation(exc, UQ_LEDGER_BOOK_PARISH_VOLUME):
                # Race guard: a concurrent request registered this book first.
                raise DuplicateLedgerBookException(
                    data.parish_id, data.sacrament_type, data.volume_number
                )
            raise
        return ArchiveLedgerBookResponse.model_validate(book)

    async def add_page(self, data: ScannedPageCreate) -> ScannedPageResponse:
        # Each page of a ledger book may only be scanned once — do not let a
        # re-uploaded scan create a duplicate archival record.
        existing = await self.repo.get_scanned_page(data.ledger_book_id, data.page_number)
        if existing:
            raise DuplicateScannedPageException(data.ledger_book_id, data.page_number)
        try:
            page = await self.repo.add_scanned_page(data)
        except IntegrityError as exc:
            await self.db.rollback()
            if _is_constraint_violation(exc, UQ_SCANNED_PAGE_BOOK_PAGE):
                # Race guard: a concurrent request stored this page already.
                raise DuplicateScannedPageException(data.ledger_book_id, data.page_number)
            raise
        # Kick off the real Tesseract OCR extraction asynchronously so the
        # scanned page becomes full-text searchable without blocking the API
        # response. A broker outage must never fail the archival upload, so
        # enqueueing failures are only logged.
        try:
            process_ocr_page.delay(str(page.id))
        except Exception:  # noqa: BLE001 - broker/connection failures
            logger.warning(
                "Could not enqueue OCR task for scanned page %s", page.id, exc_info=True
            )
        return ScannedPageResponse.model_validate(page)

    async def list_pages(self, book_id: uuid.UUID) -> list[ScannedPageResponse]:
        pages = await self.repo.list_pages(book_id)
        return [ScannedPageResponse.model_validate(p) for p in pages]


class DocumentService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = DocumentRepository(db)

    # -----------------------------------------------------------------------
    # Document Type Methods
    # -----------------------------------------------------------------------

    async def create_document_type(self, data: DocumentTypeCreate) -> DocumentTypeResponse:
        existing = await self.repo.get_document_type_by_code(data.code)
        if existing:
            raise ValidationException("errors.document_type_code_exists", message_params={"code": data.code})
        doc_type = await self.repo.create_document_type(data)
        return DocumentTypeResponse.model_validate(doc_type)

    async def get_document_type(self, type_id: uuid.UUID) -> DocumentTypeResponse:
        doc_type = await self.repo.get_document_type_by_id(type_id)
        if not doc_type:
            raise EntityNotFoundException("errors.document_type_not_found")
        return DocumentTypeResponse.model_validate(doc_type)

    async def list_document_types(
        self,
        category: str | None = None,
        is_active: bool | None = None,
    ) -> list[DocumentTypeResponse]:
        types = await self.repo.list_document_types(category=category, is_active=is_active)
        return [DocumentTypeResponse.model_validate(t) for t in types]

    async def update_document_type(self, type_id: uuid.UUID, data: DocumentTypeUpdate) -> DocumentTypeResponse:
        doc_type = await self.repo.get_document_type_by_id(type_id)
        if not doc_type:
            raise EntityNotFoundException("errors.document_type_not_found")
        updated = await self.repo.update_document_type(doc_type, data)
        return DocumentTypeResponse.model_validate(updated)

    # -----------------------------------------------------------------------
    # Generic Document Methods
    # -----------------------------------------------------------------------

    async def upload_and_create(
        self,
        file: UploadFile,
        metadata: DocumentBase,
        uploaded_by_user_id: uuid.UUID | None = None,
    ) -> DocumentResponse:
        """Save file to storage, compute SHA256 checksum and persist Document entity.

        The archive is content-addressed: if the exact same bytes are already
        registered, the upload is rejected with a conflict instead of creating
        a duplicate record (and a duplicate physical copy) on disk.
        """
        content = await file.read()
        file_size = len(content)
        checksum = hashlib.sha256(content).hexdigest()

        existing = await self.repo.get_document_by_checksum(checksum)
        if existing:
            raise DuplicateDocumentException(checksum)

        # Reset file seek for saving
        await file.seek(0)
        rel_path = await storage_service.save_file(file, subfolder="documents", checksum=checksum)

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

        try:
            doc = await self.repo.create_document(create_data, uploaded_by_user_id=uploaded_by_user_id)
        except IntegrityError as exc:
            await self.db.rollback()
            if _is_constraint_violation(exc, UQ_DOCUMENTS_CHECKSUM):
                # Race guard: a concurrent upload of the same bytes won the commit.
                raise DuplicateDocumentException(checksum)
            raise
        return DocumentResponse.model_validate(doc)

    async def create_document(
        self,
        data: DocumentCreate,
        uploaded_by_user_id: uuid.UUID | None = None,
    ) -> DocumentResponse:
        if data.checksum_sha256:
            existing = await self.repo.get_document_by_checksum(data.checksum_sha256)
            if existing:
                raise DuplicateDocumentException(data.checksum_sha256)
        try:
            doc = await self.repo.create_document(data, uploaded_by_user_id=uploaded_by_user_id)
        except IntegrityError as exc:
            await self.db.rollback()
            if data.checksum_sha256 and _is_constraint_violation(exc, UQ_DOCUMENTS_CHECKSUM):
                raise DuplicateDocumentException(data.checksum_sha256)
            raise
        return DocumentResponse.model_validate(doc)

    async def get_document(self, document_id: uuid.UUID) -> DocumentResponse:
        doc = await self.repo.get_document_by_id(document_id)
        if not doc:
            raise EntityNotFoundException("errors.document_not_found")
        return DocumentResponse.model_validate(doc)

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
    ) -> list[DocumentResponse]:
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
            raise EntityNotFoundException("errors.document_not_found")
        updated = await self.repo.update_document(doc, data)
        return DocumentResponse.model_validate(updated)

    async def delete_document(self, document_id: uuid.UUID) -> None:
        doc = await self.repo.get_document_by_id(document_id)
        if not doc:
            raise EntityNotFoundException("errors.document_not_found")
        await self.repo.delete_document(doc)

    async def get_physical_path(self, document_id: uuid.UUID) -> str:
        doc = await self.repo.get_document_by_id(document_id)
        if not doc:
            raise EntityNotFoundException("errors.document_not_found")
        return storage_service.get_full_path(doc.file_path)
