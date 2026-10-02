"""
Document & Archive Module Business Logic Service
"""

from __future__ import annotations

import hashlib
import logging
import os
import uuid
from datetime import UTC, datetime
from pathlib import Path

from fastapi import UploadFile
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
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
    ArchivePageReview,
    DocumentBase,
    DocumentCreate,
    DocumentDispositionReview,
    DocumentResponse,
    DocumentTypeCreate,
    DocumentTypeResponse,
    DocumentTypeUpdate,
    DocumentUpdate,
    ScannedPageCreate,
    ScannedPageResponse,
)
from app.tasks.archive_ocr import process_ocr_page
from app.utils.audit import record_audit_event
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
        record_audit_event(
            self.db, action="ARCHIVE_LEDGER_BOOK_CREATED", entity_name="archive_ledger_book",
            entity_id=book.id,
            details={"parish_id": str(book.parish_id), "sacrament_type": book.sacrament_type.value,
                     "volume_number": book.volume_number},
        )
        return ArchiveLedgerBookResponse.model_validate(book)

    async def add_page(self, data: ScannedPageCreate, file: UploadFile) -> ScannedPageResponse:
        # Each page of a ledger book may only be scanned once — do not let a
        # re-uploaded scan create a duplicate archival record.
        existing = await self.repo.get_scanned_page(data.ledger_book_id, data.page_number)
        if existing:
            raise DuplicateScannedPageException(data.ledger_book_id, data.page_number)
        extension = Path(file.filename or "").suffix.lower()
        if extension not in {".tif", ".tiff", ".png", ".jpg", ".jpeg"}:
            raise ValidationException("Archive scans must be TIFF, PNG, or JPEG images.")
        content = await file.read(settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024 + 1)
        if not content:
            raise ValidationException("The uploaded archive scan is empty.")
        if len(content) > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
            raise ValidationException("The uploaded archive scan exceeds the configured size limit.")
        checksum = hashlib.sha256(content).hexdigest()
        await file.seek(0)
        relative_path = await storage_service.save_file(
            file, subfolder="archive-scans", checksum=checksum
        )
        try:
            page = await self.repo.add_scanned_page(data, image_file_path=relative_path)
        except IntegrityError as exc:
            await self.db.rollback()
            if _is_constraint_violation(exc, UQ_SCANNED_PAGE_BOOK_PAGE):
                # Race guard: a concurrent request stored this page already.
                raise DuplicateScannedPageException(data.ledger_book_id, data.page_number)
            raise
        page.ocr_metadata = {"status": "queued", "indexed": False}
        record_audit_event(
            self.db, action="ARCHIVE_PAGE_ADDED", entity_name="scanned_page", entity_id=page.id,
            details={"ledger_book_id": str(page.ledger_book_id), "page_number": page.page_number},
        )
        # Kick off the real Tesseract OCR extraction asynchronously so the
        # scanned page becomes full-text searchable without blocking the API
        # response. A broker outage must never fail the archival upload, so
        # enqueueing failures are only logged.
        try:
            process_ocr_page.delay(str(page.id))
        except Exception:  # noqa: BLE001 - broker/connection failures
            logger.warning("Could not enqueue OCR task for scanned page %s", page.id, exc_info=True)
        return ScannedPageResponse.model_validate(page)

    async def list_pages(self, book_id: uuid.UUID) -> list[ScannedPageResponse]:
        pages = await self.repo.list_pages(book_id)
        return [ScannedPageResponse.model_validate(p) for p in pages]

    async def get_page(self, page_id: uuid.UUID) -> ScannedPageResponse:
        page = await self.repo.get_page_by_id(page_id)
        if not page:
            raise EntityNotFoundException("errors.scanned_page_not_found")
        record_audit_event(
            self.db, action="ARCHIVE_PAGE_VIEWED", entity_name="scanned_page",
            entity_id=page.id,
        )
        return ScannedPageResponse.model_validate(page)

    async def review_page(
        self, page_id: uuid.UUID, review: ArchivePageReview, reviewer_id: uuid.UUID
    ) -> ScannedPageResponse:
        page = await self.repo.get_page_by_id(page_id)
        if page is None:
            raise EntityNotFoundException("errors.scanned_page_not_found")
        page.review_status = review.status
        page.reviewed_by_user_id = reviewer_id
        page.reviewed_at = datetime.now(UTC)
        page.review_notes = review.notes
        await self.db.flush()
        record_audit_event(
            self.db, action="ARCHIVE_PAGE_REVIEWED", entity_name="scanned_page",
            entity_id=page.id,
            details={"review_status": review.status, "notes_provided": bool(review.notes)},
        )
        return ScannedPageResponse.model_validate(page)

    async def replace_page_scan(
        self, page_id: uuid.UUID, file: UploadFile
    ) -> ScannedPageResponse:
        page = await self.repo.get_page_by_id(page_id)
        if page is None:
            raise EntityNotFoundException("errors.scanned_page_not_found")
        if page.review_status != "NEEDS_RESCAN":
            raise ValidationException("Only a page marked for rescanning can be replaced.")
        extension = Path(file.filename or "").suffix.lower()
        if extension not in {".tif", ".tiff", ".png", ".jpg", ".jpeg"}:
            raise ValidationException("Archive scans must be TIFF, PNG, or JPEG images.")
        content = await file.read(settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024 + 1)
        if not content:
            raise ValidationException("The uploaded archive scan is empty.")
        if len(content) > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
            raise ValidationException("The uploaded archive scan exceeds the configured size limit.")
        old_path = page.image_file_path
        checksum = hashlib.sha256(content).hexdigest()
        await file.seek(0)
        page.image_file_path = await storage_service.save_file(
            file, subfolder="archive-scans", checksum=checksum
        )
        page.ocr_raw_text = None
        page.ocr_metadata = {"status": "queued", "indexed": False}
        page.review_status = "PENDING"
        page.reviewed_by_user_id = None
        page.reviewed_at = None
        page.review_notes = None
        await self.db.flush()
        record_audit_event(
            self.db, action="ARCHIVE_PAGE_RESCAN_UPLOADED", entity_name="scanned_page",
            entity_id=page.id,
            details={"previous_file_path": old_path, "new_file_path": page.image_file_path},
        )
        try:
            process_ocr_page.delay(str(page.id))
        except Exception:  # noqa: BLE001 - OCR remains retryable from the page workflow
            logger.warning("Could not enqueue OCR task for rescanned page %s", page.id, exc_info=True)
        return ScannedPageResponse.model_validate(page)

    async def get_page_file_path(self, page_id: uuid.UUID) -> str:
        page = await self.repo.get_page_by_id(page_id)
        if page is None:
            raise EntityNotFoundException("errors.scanned_page_not_found")
        try:
            path = storage_service.get_full_path(page.image_file_path)
        except ValueError as exc:
            logger.error("Rejected unsafe archive path for scanned page %s", page.id)
            raise EntityNotFoundException("errors.physical_file_not_found") from exc
        if not os.path.isfile(path):
            raise EntityNotFoundException("errors.physical_file_not_found")
        record_audit_event(
            self.db, action="ARCHIVE_PAGE_IMAGE_DOWNLOADED", entity_name="scanned_page",
            entity_id=page.id,
        )
        return path

    async def trigger_ocr(self, page_id: uuid.UUID) -> dict:
        page = await self.repo.get_page_by_id(page_id)
        if not page:
            raise EntityNotFoundException("errors.scanned_page_not_found")
        page.review_status = "PENDING"
        page.reviewed_by_user_id = None
        page.reviewed_at = None
        page.review_notes = None
        page.ocr_metadata = {"status": "queued", "indexed": False}
        await self.db.flush()
        try:
            process_ocr_page.delay(str(page.id))
            status_msg = "enqueued"
        except Exception as exc:
            logger.warning("Could not enqueue OCR task for scanned page %s: %s", page.id, exc)
            status_msg = "enqueue_failed"
        record_audit_event(
            self.db, action="ARCHIVE_PAGE_OCR_REQUESTED", entity_name="scanned_page",
            entity_id=page.id, details={"enqueue_status": status_msg},
        )
        return {"scanned_page_id": str(page.id), "status": status_msg}

    async def search_pages(
        self, query: str, parish_id: uuid.UUID | None = None
    ) -> list[ScannedPageResponse]:
        pages = await self.repo.search_pages(query, parish_id)
        record_audit_event(
            self.db,
            action="ARCHIVE_SEARCH_PERFORMED",
            entity_name="scanned_page",
            entity_id=None,
            details={
                "query_length": len(query),
                "result_count": len(pages),
                "parish_id": str(parish_id) if parish_id else None,
            },
        )
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
            raise ValidationException(
                "errors.document_type_code_exists", message_params={"code": data.code}
            )
        doc_type = await self.repo.create_document_type(data)
        record_audit_event(
            self.db, action="DOCUMENT_TYPE_CREATED", entity_name="document_type",
            entity_id=doc_type.id, details={"code": doc_type.code},
        )
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

    async def update_document_type(
        self, type_id: uuid.UUID, data: DocumentTypeUpdate
    ) -> DocumentTypeResponse:
        doc_type = await self.repo.get_document_type_by_id(type_id)
        if not doc_type:
            raise EntityNotFoundException("errors.document_type_not_found")
        updated = await self.repo.update_document_type(doc_type, data)
        record_audit_event(
            self.db, action="DOCUMENT_TYPE_UPDATED", entity_name="document_type",
            entity_id=doc_type.id, details={"changed_fields": sorted(data.model_fields_set)},
        )
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
        content = await file.read(settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024 + 1)
        file_size = len(content)
        if file_size > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
            raise ValidationException("The uploaded document exceeds the configured size limit.")
        if not content:
            raise ValidationException("The uploaded document is empty.")
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
            doc = await self.repo.create_document(
                create_data, uploaded_by_user_id=uploaded_by_user_id
            )
        except IntegrityError as exc:
            await self.db.rollback()
            if _is_constraint_violation(exc, UQ_DOCUMENTS_CHECKSUM):
                # Race guard: a concurrent upload of the same bytes won the commit.
                raise DuplicateDocumentException(checksum)
            raise
        record_audit_event(
            self.db, action="DOCUMENT_UPLOADED", entity_name="document", entity_id=doc.id,
            details={"classification": doc.classification, "file_size_bytes": file_size,
                     "parish_id": str(doc.parish_id) if doc.parish_id else None,
                     "checksum_sha256": checksum},
            user_id=uploaded_by_user_id,
        )
        return DocumentResponse.model_validate(doc)

    async def create_document(
        self,
        data: DocumentCreate,
        uploaded_by_user_id: uuid.UUID | None = None,
    ) -> DocumentResponse:
        try:
            full_path = storage_service.get_full_path(data.file_path)
        except ValueError as exc:
            raise ValidationException("Document path must point inside managed file storage.") from exc
        if not os.path.isfile(full_path):
            raise EntityNotFoundException("errors.physical_file_not_found")
        if data.checksum_sha256:
            digest = hashlib.sha256()
            with open(full_path, "rb") as archived_file:
                for chunk in iter(lambda: archived_file.read(1024 * 1024), b""):
                    digest.update(chunk)
            if digest.hexdigest() != data.checksum_sha256:
                raise ValidationException("Document checksum does not match the stored file.")
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
        record_audit_event(
            self.db, action="DOCUMENT_REGISTERED", entity_name="document", entity_id=doc.id,
            details={"classification": doc.classification,
                     "parish_id": str(doc.parish_id) if doc.parish_id else None},
            user_id=uploaded_by_user_id,
        )
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
        disposition_status: str | None = None,
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
            disposition_status=disposition_status,
        )
        return [DocumentResponse.model_validate(d) for d in docs]

    async def update_document(
        self, document_id: uuid.UUID, data: DocumentUpdate
    ) -> DocumentResponse:
        doc = await self.repo.get_document_by_id(document_id)
        if not doc:
            raise EntityNotFoundException("errors.document_not_found")
        updated = await self.repo.update_document(doc, data)
        record_audit_event(
            self.db, action="DOCUMENT_UPDATED", entity_name="document", entity_id=doc.id,
            details={"changed_fields": sorted(data.model_fields_set)},
        )
        return DocumentResponse.model_validate(updated)

    async def delete_document(self, document_id: uuid.UUID) -> None:
        doc = await self.repo.get_document_by_id(document_id)
        if not doc:
            raise EntityNotFoundException("errors.document_not_found")
        await self.repo.delete_document(doc)
        record_audit_event(
            self.db, action="DOCUMENT_DELETED", entity_name="document", entity_id=doc.id,
            details={"parish_id": str(doc.parish_id) if doc.parish_id else None},
        )

    async def get_physical_path(self, document_id: uuid.UUID) -> str:
        doc = await self.repo.get_document_by_id(document_id)
        if not doc:
            raise EntityNotFoundException("errors.document_not_found")
        try:
            path = storage_service.get_full_path(doc.file_path)
        except ValueError as exc:
            logger.error("Rejected unsafe storage path for document %s", doc.id)
            raise EntityNotFoundException("errors.physical_file_not_found") from exc
        if not os.path.isfile(path):
            raise EntityNotFoundException("errors.physical_file_not_found")
        return path

    async def review_disposition(
        self,
        document_id: uuid.UUID,
        review: DocumentDispositionReview,
        reviewer_id: uuid.UUID,
    ) -> DocumentResponse:
        doc = await self.repo.get_document_by_id(document_id)
        if not doc:
            raise EntityNotFoundException("errors.document_not_found")
        old_status = doc.disposition_status or "ACTIVE"
        if review.action in {"DISPOSE", "PRESERVE"}:
            if old_status != "DUE_FOR_REVIEW":
                raise ValidationException("Only documents due for review may be dispositioned.")
            new_status = "DISPOSED" if review.action == "DISPOSE" else "PRESERVE_INDEFINITELY"
        else:
            if old_status not in {"DISPOSED", "PRESERVE_INDEFINITELY"}:
                raise ValidationException("Only a completed disposition can be reopened.")
            new_status = "DUE_FOR_REVIEW"
            doc.retention_flagged_at = datetime.now(UTC)

        doc.disposition_status = new_status
        await self.db.flush()
        record_audit_event(
            self.db,
            action=f"DOCUMENT_DISPOSITION_{review.action}",
            entity_name="document",
            entity_id=doc.id,
            details={"from_status": old_status, "to_status": new_status, "reason": review.reason},
            user_id=reviewer_id,
        )
        return DocumentResponse.model_validate(doc)
