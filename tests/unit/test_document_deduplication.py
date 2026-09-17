"""
Unit tests for archive/document deduplication behaviour.

Covers:
  * StorageService — content-addressed writes never overwrite existing files and
    identical bytes are physically stored only once.
  * DocumentService — duplicate content (same SHA-256 checksum) on /documents
    upload and /documents record creation is rejected with a 409 conflict.
  * ArchiveService — duplicate ledger books (parish + sacrament + volume) and
    duplicate scanned pages (book + page) are rejected.

These are pure unit tests: repository and storage interactions are faked, so no
PostgreSQL, Redis or disk files are required.
"""
import hashlib
import types
import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest

from app.core.exceptions import (
    DuplicateDocumentException,
    DuplicateLedgerBookException,
    DuplicateScannedPageException,
)
from app.models.sacrament import SacramentType
from app.schemas.document import ArchiveLedgerBookCreate, DocumentBase, ScannedPageCreate
from app.services import document as document_service_module
from app.services.document import ArchiveService, DocumentService
from app.utils.file_storage import StorageService


# ---------------------------------------------------------------------------
# Fakes
# ---------------------------------------------------------------------------
class _FakeUploadFile:
    """Duck-typed UploadFile: only read/seek/filename/content_type are used."""

    def __init__(self, filename, content, content_type="application/pdf"):
        self.filename = filename
        self.content = content
        self.content_type = content_type
        self._pos = 0

    async def read(self, size=-1):
        if size == -1 or size is None:
            start = self._pos
            self._pos = len(self.content)
            return self.content[start:]
        start = self._pos
        end = min(start + size, len(self.content))
        self._pos = end
        return self.content[start:end]

    async def seek(self, offset):
        self._pos = offset


class _FakeStorage:
    """Records saves so the service never touches a real disk."""

    def __init__(self):
        self.saved = []

    async def save_file(self, file, subfolder="general", *, checksum=None):
        content = await file.read()
        self.saved.append((subfolder, checksum, content))
        return f"{subfolder}/{checksum[:2]}/{checksum}_sample.pdf"

    def get_full_path(self, relative_path):
        return "/storage/" + relative_path


def _fake_document(**overrides):
    """Build an ORM-row-shaped object accepted by DocumentResponse."""
    base = {
        "id": uuid.uuid4(),
        "title": "Decree",
        "document_type_id": None,
        "classification": "OFFICIAL",
        "notes": None,
        "disposition_status": None,
        "archdiocese_id": None,
        "deanery_id": None,
        "parish_id": uuid.uuid4(),
        "commission_id": None,
        "council_id": None,
        "meeting_id": None,
        "priest_id": None,
        "parcel_id": None,
        "file_path": "documents/ab/checksum_sample.pdf",
        "file_size_bytes": 4,
        "mime_type": "application/pdf",
        "checksum_sha256": "0" * 64,
        "uploaded_by_user_id": None,
        "retention_flagged_at": None,
        "created_at": datetime(2026, 1, 1, tzinfo=UTC),
        "updated_at": datetime(2026, 1, 1, tzinfo=UTC),
    }
    base.update(overrides)
    return types.SimpleNamespace(**base)


def _fake_book(**overrides):
    base = {
        "id": uuid.uuid4(),
        "parish_id": uuid.uuid4(),
        "sacrament_type": SacramentType.BAPTISM,
        "book_title": "Baptisms Vol 1",
        "start_year": 1900,
        "end_year": 1920,
        "volume_number": "VOL-1",
        "shelf_location": None,
        "total_scanned_pages": 0,
        "created_at": datetime(2026, 1, 1, tzinfo=UTC),
    }
    base.update(overrides)
    return types.SimpleNamespace(**base)


def _fake_page(**overrides):
    base = {
        "id": uuid.uuid4(),
        "ledger_book_id": uuid.uuid4(),
        "page_number": 1,
        "image_file_path": "archive/pages/page-0001.png",
        "ocr_raw_text": None,
        "created_at": datetime(2026, 1, 1, tzinfo=UTC),
    }
    base.update(overrides)
    return types.SimpleNamespace(**base)


# ---------------------------------------------------------------------------
# StorageService: collision-proof, content-addressed writes
# ---------------------------------------------------------------------------
async def test_save_file_same_filename_different_content_never_overwrites(tmp_path):
    service = StorageService(base_path=str(tmp_path))
    content_a = b"first document bytes"
    content_b = b"totally different bytes"

    path_a = await service.save_file(
        _FakeUploadFile("report.pdf", content_a), subfolder="documents"
    )
    path_b = await service.save_file(
        _FakeUploadFile("report.pdf", content_b), subfolder="documents"
    )

    assert path_a != path_b
    assert (tmp_path / path_a.replace("/", "\\")).read_bytes() == content_a
    assert (tmp_path / path_b.replace("/", "\\")).read_bytes() == content_b


async def test_save_file_identical_content_stored_only_once(tmp_path):
    service = StorageService(base_path=str(tmp_path))
    content = b"the same bytes, no matter the filename"
    checksum = hashlib.sha256(content).hexdigest()

    path_a = await service.save_file(
        _FakeUploadFile("scan-001.pdf", content), subfolder="documents", checksum=checksum
    )
    path_b = await service.save_file(
        _FakeUploadFile("renamed-001.pdf", content), subfolder="documents", checksum=checksum
    )

    assert path_a == path_b


async def test_save_file_cleans_path_traversal_filenames(tmp_path):
    service = StorageService(base_path=str(tmp_path))
    path = await service.save_file(
        _FakeUploadFile("../../evil?.pdf", b"payload"), subfolder="documents"
    )
    # The relative path must stay inside the storage base.
    assert ".." not in path
    assert (tmp_path / path.replace("/", "\\")).read_bytes() == b"payload"


async def test_save_bytes_content_addressed(tmp_path):
    service = StorageService(base_path=str(tmp_path))
    content = b"raw byte payload"
    checksum = hashlib.sha256(content).hexdigest()

    path_a = await service.save_bytes(content, filename="a.pdf", subfolder="documents")
    path_b = await service.save_bytes(content, filename="b.pdf", subfolder="documents")

    assert path_a == path_b
    assert checksum in path_a
    assert (tmp_path / path_a.replace("/", "\\")).read_bytes() == content


# ---------------------------------------------------------------------------
# DocumentService: same checksum cannot be archived twice
# ---------------------------------------------------------------------------
async def test_upload_duplicate_content_rejected_before_save(monkeypatch):
    db = types.SimpleNamespace(rollback=AsyncMock())
    service = DocumentService(db)  # type: ignore[arg-type]
    service.repo = types.SimpleNamespace(
        get_document_by_checksum=AsyncMock(
            return_value=_fake_document(checksum_sha256="a" * 64)
        ),
        create_document=AsyncMock(return_value=None),
    )
    storage = _FakeStorage()
    monkeypatch.setattr(document_service_module, "storage_service", storage)

    metadata = DocumentBase(title="Decree", parish_id=uuid.uuid4())
    with pytest.raises(DuplicateDocumentException):
        await service.upload_and_create(
            _FakeUploadFile("duplicate.pdf", b"same bytes"), metadata
        )

    assert storage.saved == [], "the file must not be written when the content is a duplicate"


async def test_upload_happy_path_persists_with_checksum(monkeypatch):
    body = b"brand new bytes"
    checksum = hashlib.sha256(body).hexdigest()
    doc = _fake_document(checksum_sha256=checksum, title="Fresh Bill")

    db = types.SimpleNamespace(rollback=AsyncMock())
    service = DocumentService(db)  # type: ignore[arg-type]
    service.repo = types.SimpleNamespace(
        get_document_by_checksum=AsyncMock(return_value=None),
        create_document=AsyncMock(return_value=doc),
    )
    storage = _FakeStorage()
    monkeypatch.setattr(document_service_module, "storage_service", storage)

    metadata = DocumentBase(title="Fresh Bill", parish_id=uuid.uuid4())
    result = await service.upload_and_create(
        _FakeUploadFile("bill.pdf", body), metadata, uploaded_by_user_id=None
    )

    assert result.checksum_sha256 == checksum
    assert len(storage.saved) == 1
    assert storage.saved[0][1] == checksum


async def test_create_document_rejects_duplicate_checksum():
    db = types.SimpleNamespace(rollback=AsyncMock())
    service = DocumentService(db)  # type: ignore[arg-type]
    service.repo = types.SimpleNamespace(
        get_document_by_checksum=AsyncMock(
            return_value=_fake_document(checksum_sha256="a" * 64)
        ),
        create_document=AsyncMock(return_value=None),
    )

    data = DocumentBase(title="Decree", parish_id=uuid.uuid4())
    create = document_service_module.DocumentCreate(
        **data.model_dump(),
        file_path="documents/duplicate.pdf",
        checksum_sha256="a" * 64,
    )
    with pytest.raises(DuplicateDocumentException):
        await service.create_document(create)


async def test_create_document_raises_duplicate_on_integrity_race():
    from sqlalchemy.exc import IntegrityError

    db = types.SimpleNamespace(rollback=AsyncMock())
    service = DocumentService(db)  # type: ignore[arg-type]

    def boom(data, uploaded_by_user_id=None):
        raise IntegrityError(
            "INSERT INTO documents ...",
            {},
            Exception('duplicate key value violates unique constraint "uq_documents_checksum_active"'),
        )

    service.repo = types.SimpleNamespace(
        get_document_by_checksum=AsyncMock(return_value=None),
        create_document=AsyncMock(side_effect=boom),
    )

    data = DocumentBase(title="Decree", parish_id=uuid.uuid4())
    create = document_service_module.DocumentCreate(
        **data.model_dump(),
        file_path="documents/duplicate.pdf",
        checksum_sha256="b" * 64,
    )
    with pytest.raises(DuplicateDocumentException):
        await service.create_document(create)
    db.rollback.assert_awaited_once()


async def test_create_document_reraises_unrelated_integrity_error():
    from sqlalchemy.exc import IntegrityError

    db = types.SimpleNamespace(rollback=AsyncMock())
    service = DocumentService(db)  # type: ignore[arg-type]

    def boom(data, uploaded_by_user_id=None):
        # Foreign-key violation is NOT a duplicate — must not be masked.
        raise IntegrityError(
            "INSERT INTO documents ...",
            {},
            Exception('insert or update on table "documents" violates foreign key constraint'),
        )

    service.repo = types.SimpleNamespace(
        get_document_by_checksum=AsyncMock(return_value=None),
        create_document=AsyncMock(side_effect=boom),
    )

    data = DocumentBase(title="Decree", parish_id=uuid.uuid4())
    create = document_service_module.DocumentCreate(
        **data.model_dump(),
        file_path="documents/foreign.pdf",
        checksum_sha256="c" * 64,
    )
    with pytest.raises(IntegrityError):
        await service.create_document(create)


# ---------------------------------------------------------------------------
# ArchiveService: ledger books and scanned pages are canonically unique
# ---------------------------------------------------------------------------
async def test_create_book_rejects_duplicate_natural_key():
    db = types.SimpleNamespace(rollback=AsyncMock())
    service = ArchiveService(db)  # type: ignore[arg-type]
    service.repo = types.SimpleNamespace(
        get_ledger_book=AsyncMock(return_value=_fake_book()),
        create_ledger_book=AsyncMock(return_value=None),
    )

    payload = ArchiveLedgerBookCreate(
        parish_id=uuid.uuid4(),
        sacrament_type=SacramentType.BAPTISM,
        book_title="Baptisms",
        start_year=1900,
        end_year=1920,
        volume_number="VOL-1",
    )
    with pytest.raises(DuplicateLedgerBookException):
        await service.create_book(payload)


async def test_create_book_happy_path():
    db = types.SimpleNamespace(rollback=AsyncMock())
    service = ArchiveService(db)  # type: ignore[arg-type]
    book = _fake_book()
    service.repo = types.SimpleNamespace(
        get_ledger_book=AsyncMock(return_value=None),
        create_ledger_book=AsyncMock(return_value=book),
    )

    payload = ArchiveLedgerBookCreate(
        parish_id=book.parish_id,
        sacrament_type=SacramentType.BAPTISM,
        book_title="Baptisms",
        start_year=1900,
        end_year=1920,
        volume_number="VOL-1",
    )
    result = await service.create_book(payload)
    assert result.id == book.id


async def test_add_page_rejects_duplicate_book_page(monkeypatch):
    db = types.SimpleNamespace(rollback=AsyncMock())
    service = ArchiveService(db)  # type: ignore[arg-type]
    service.repo = types.SimpleNamespace(
        get_scanned_page=AsyncMock(return_value=_fake_page()),
        add_scanned_page=AsyncMock(return_value=None),
    )
    monkeypatch.setattr(
        document_service_module,
        "process_ocr_page",
        types.SimpleNamespace(delay=lambda page_id: None),
    )

    payload = ScannedPageCreate(
        ledger_book_id=uuid.uuid4(),
        page_number=7,
        image_file_path="archive/pages/page-0007.png",
    )
    with pytest.raises(DuplicateScannedPageException):
        await service.add_page(payload)


async def test_add_page_happy_path_enqueues_ocr_and_returns_page(monkeypatch):
    db = types.SimpleNamespace(rollback=AsyncMock())
    service = ArchiveService(db)  # type: ignore[arg-type]
    page = _fake_page(page_number=7)
    service.repo = types.SimpleNamespace(
        get_scanned_page=AsyncMock(return_value=None),
        add_scanned_page=AsyncMock(return_value=page),
    )
    enqueued = []

    class _FakeOCRTask:
        @staticmethod
        def delay(page_id):
            enqueued.append(page_id)

    monkeypatch.setattr(document_service_module, "process_ocr_page", _FakeOCRTask)

    payload = ScannedPageCreate(
        ledger_book_id=page.ledger_book_id,
        page_number=7,
        image_file_path="archive/pages/page-0007.png",
    )
    result = await service.add_page(payload)

    assert result.page_number == 7
    assert enqueued == [str(page.id)]
