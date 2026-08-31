"""
Unit tests for the Archive OCR task module (app/tasks/archive_ocr.py).

These are pure unit tests: the Celery task's database session and the
Tesseract engine are faked, so no PostgreSQL or tesseract binary is needed.
They cover the extraction helper and every task status contract:

* not_found            — page row missing
* indexed              — successful Tesseract extraction + indexing
* indexed_without_ocr  — OCR_ENABLED=false degraded fallback
* ocr_unavailable      — engine missing (TesseractNotFoundError)
* image_not_found      — page image file missing from storage
* ocr_failed           — engine raised while reading the image
"""
import sys
import types
import uuid

import pytest
from PIL import Image

from app.config import settings
from app.tasks import archive_ocr
from app.tasks.archive_ocr import (
    OcrEngineUnavailableError,
    extract_ocr_text,
    process_ocr_page,
)


# ---------------------------------------------------------------------------
# Fakes
# ---------------------------------------------------------------------------
class _FakePage:
    def __init__(self, image_file_path="archive/ledger/page-001.png"):
        self.id = uuid.uuid4()
        self.image_file_path = image_file_path
        self.ocr_raw_text = None
        self.ocr_metadata = None


class _FakeSession:
    """Minimal stand-in for AsyncSessionLocal() as used by the task."""

    def __init__(self, page):
        self._page = page
        self.committed = False

    async def get(self, model, pk):
        return self._page

    async def commit(self):
        self.committed = True

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return False


class _FakeStorage:
    def __init__(self, full_path):
        self.full_path = full_path

    def get_full_path(self, relative_path):
        return self.full_path


def _make_fake_pytesseract(text="Baptismus anno 1923", confidences=(92, 88, "-1", 95)):
    """Build a fake `pytesseract` module and return it with a call recorder."""
    fake = types.ModuleType("pytesseract")
    fake.TesseractNotFoundError = type("TesseractNotFoundError", (Exception,), {})

    calls = {"image_to_string": [], "image_to_data": []}

    def image_to_string(image, lang=None, config=None, timeout=None, output_type=None):
        calls["image_to_string"].append({"lang": lang, "config": config, "timeout": timeout})
        return text

    def image_to_data(image, lang=None, config=None, timeout=None, output_type=None):
        calls["image_to_data"].append({"lang": lang, "output_type": output_type})
        return {"conf": list(confidences)}

    fake.image_to_string = image_to_string
    fake.image_to_data = image_to_data
    fake.Output = types.SimpleNamespace(DICT="dict")
    fake.calls = calls
    return fake


@pytest.fixture
def fake_engine(monkeypatch):
    """Inject a fake pytesseract module and return its call recorder."""
    fake = _make_fake_pytesseract()
    monkeypatch.setitem(sys.modules, "pytesseract", fake)
    return fake


def _patch_task_env(monkeypatch, page, image_full_path="/storage/page-001.png"):
    """Point the task at the fake session + storage service."""
    session = _FakeSession(page)
    monkeypatch.setattr(archive_ocr, "AsyncSessionLocal", lambda: session)
    monkeypatch.setattr(archive_ocr, "storage_service", _FakeStorage(image_full_path))
    monkeypatch.setattr(settings, "OCR_ENABLED", True)
    return session


# ---------------------------------------------------------------------------
# extract_ocr_text helper
# ---------------------------------------------------------------------------
def test_extract_ocr_text_returns_text_and_engine_metadata(tmp_path, fake_engine):
    image_path = tmp_path / "page-001.png"
    Image.new("RGB", (10, 10), color="white").save(image_path)

    text, meta = extract_ocr_text(str(image_path))

    assert text == "Baptismus anno 1923"
    assert meta["engine"] == "tesseract"
    assert meta["language"] == settings.OCR_LANGUAGE
    assert meta["image_dpi"] == settings.OCR_DPI
    assert meta["mean_confidence"] == round((92 + 88 + 95) / 3, 2)
    assert meta["duration_ms"] >= 0
    # The lang/config were forwarded to the engine.
    assert fake_engine.calls["image_to_string"][0]["lang"] == settings.OCR_LANGUAGE
    assert "--dpi" in fake_engine.calls["image_to_string"][0]["config"]


def test_extract_ocr_text_missing_image_raises_file_not_found(tmp_path, fake_engine):
    with pytest.raises(FileNotFoundError):
        extract_ocr_text(str(tmp_path / "does-not-exist.png"))


def test_extract_ocr_text_missing_binary_maps_to_engine_unavailable(tmp_path, monkeypatch):
    """A missing tesseract binary surfaces as OcrEngineUnavailableError."""
    image_path = tmp_path / "page-001.png"
    Image.new("RGB", (5, 5)).save(image_path)

    fake = _make_fake_pytesseract()

    def raise_not_found(image, **kwargs):
        raise fake.TesseractNotFoundError("tesseract is not installed")

    fake.image_to_string = raise_not_found
    monkeypatch.setitem(sys.modules, "pytesseract", fake)

    with pytest.raises(OcrEngineUnavailableError):
        extract_ocr_text(str(image_path))


# ---------------------------------------------------------------------------
# process_ocr_page task statuses
# ---------------------------------------------------------------------------
def test_task_success_indexes_extracted_text(monkeypatch):
    page = _FakePage()
    session = _patch_task_env(monkeypatch, page)

    monkeypatch.setattr(
        archive_ocr,
        "extract_ocr_text",
        lambda path: (
            "Joannes Baptista",
            {"engine": "tesseract", "mean_confidence": 91.5, "duration_ms": 420},
        ),
    )

    result = process_ocr_page(str(page.id))

    assert result["status"] == "indexed"
    assert result["text_length"] == len("Joannes Baptista")
    assert result["word_count"] == 2
    assert result["mean_confidence"] == 91.5
    assert page.ocr_raw_text == "Joannes Baptista"
    meta = page.ocr_metadata
    assert meta["indexed"] is True
    assert meta["status"] == "ok"
    assert meta["engine"] == "tesseract"
    assert meta["word_count"] == 2
    assert session.committed is True


def test_task_page_not_found(monkeypatch):
    _patch_task_env(monkeypatch, None)

    result = process_ocr_page(str(uuid.uuid4()))

    assert result == {
        "scanned_page_id": result["scanned_page_id"],
        "status": "not_found",
    }


def test_task_ocr_disabled_indexes_preattached_text(monkeypatch):
    page = _FakePage()
    page.ocr_raw_text = "pre-attached archival transcription"
    session = _patch_task_env(monkeypatch, page)
    monkeypatch.setattr(settings, "OCR_ENABLED", False)

    result = process_ocr_page(str(page.id))

    assert result["status"] == "indexed_without_ocr"
    assert result["word_count"] == 3
    assert page.ocr_raw_text == "pre-attached archival transcription"
    assert page.ocr_metadata["ocr_engine"] == "disabled"
    assert page.ocr_metadata["indexed"] is True
    assert session.committed is True


def test_task_engine_unavailable(monkeypatch):
    page = _FakePage()
    session = _patch_task_env(monkeypatch, page)

    def raise_unavailable(path):
        raise OcrEngineUnavailableError("tesseract binary missing")

    monkeypatch.setattr(archive_ocr, "extract_ocr_text", raise_unavailable)

    result = process_ocr_page(str(page.id))

    assert result["status"] == "ocr_unavailable"
    assert "tesseract binary missing" in result["error"]
    assert page.ocr_metadata["indexed"] is False
    assert page.ocr_metadata["status"] == "ocr_unavailable"
    assert session.committed is True


def test_task_image_not_found(monkeypatch):
    page = _FakePage()
    session = _patch_task_env(monkeypatch, page, image_full_path="/nowhere/page.png")

    def raise_missing(path):
        raise FileNotFoundError(f"Scanned page image not found: {path}")

    monkeypatch.setattr(archive_ocr, "extract_ocr_text", raise_missing)

    result = process_ocr_page(str(page.id))

    assert result["status"] == "image_not_found"
    assert page.ocr_metadata["indexed"] is False
    assert session.committed is True


def test_task_engine_error_maps_to_ocr_failed(monkeypatch):
    page = _FakePage()
    session = _patch_task_env(monkeypatch, page)

    def raise_engine_error(path):
        raise RuntimeError("TesseractError: invalid image")

    monkeypatch.setattr(archive_ocr, "extract_ocr_text", raise_engine_error)

    result = process_ocr_page(str(page.id))

    assert result["status"] == "ocr_failed"
    assert page.ocr_metadata["indexed"] is False
    assert session.committed is True