"""
File Storage Provider Interface & Local/Cloud Storage Adapter
"""

import hashlib
import os
import re

import aiofiles
from fastapi import UploadFile

from app.config import settings


def _sanitize_filename(filename: str) -> str:
    """Return a filesystem-safe basename, dropping path separators and control chars."""
    name = os.path.basename(filename or "upload.bin").strip()
    name = re.sub(r"[\\/:*?\"<>|\x00-\x1f]", "_", name)
    return name or "upload.bin"


class StorageService:
    """Manages file storage for documents, photos, and scanned canonical books.

    Stored files use a *content-addressed* layout:

        <base_path>/<subfolder>/<checksum>/<checksum>_<safe_filename>

    This guarantees that:
      * two uploads that happen to share a filename never overwrite each other
        (a silent data-loss bug in the previous basename-only layout), and
      * identical byte content is physically stored only once — re-saving the
        same bytes returns the already persisted path without rewiring disk I/O.
    """

    def __init__(self, base_path: str = settings.FILE_STORAGE_PATH):
        self.base_path = base_path
        os.makedirs(self.base_path, exist_ok=True)

    async def save_file(
        self,
        file: UploadFile,
        subfolder: str = "general",
        *,
        checksum: str | None = None,
    ) -> str:
        """Save an uploaded file and return its storage-relative path.

        If ``checksum`` is not supplied it is computed from the file bytes so
        content-addressing (and therefore single-copy storage) always applies.
        """
        content = await file.read()
        if not checksum:
            checksum = hashlib.sha256(content).hexdigest()
        if len(checksum) < 2:
            raise ValueError("checksum is too short to build a content-addressed path")

        safe_name = _sanitize_filename(file.filename or "upload.bin")
        existing = self._existing_checksum_file(subfolder, checksum)
        if existing is not None:
            # Idempotent write: the exact bytes are already archived under this
            # checksum (whatever the uploader's filename is), so the file is
            # never copied a second time — return the existing stored path.
            return os.path.join(subfolder, checksum[:2], existing).replace("\\", "/")

        rel_path = self._content_addressed_path(subfolder, checksum, safe_name)
        full_path = os.path.join(self.base_path, rel_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        async with aiofiles.open(full_path, "wb") as out_file:
            await out_file.write(content)
        return rel_path

    async def save_bytes(
        self,
        content: bytes,
        filename: str = "upload.bin",
        subfolder: str = "general",
        *,
        checksum: str | None = None,
    ) -> str:
        """Content-addressed save for raw bytes (no ``UploadFile`` required)."""
        if not checksum:
            checksum = hashlib.sha256(content).hexdigest()
        if len(checksum) < 2:
            raise ValueError("checksum is too short to build a content-addressed path")

        safe_name = _sanitize_filename(filename)
        existing = self._existing_checksum_file(subfolder, checksum)
        if existing is not None:
            return os.path.join(subfolder, checksum[:2], existing).replace("\\", "/")

        rel_path = self._content_addressed_path(subfolder, checksum, safe_name)
        full_path = os.path.join(self.base_path, rel_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        async with aiofiles.open(full_path, "wb") as out_file:
            await out_file.write(content)
        return rel_path

    def _content_addressed_path(self, subfolder: str, checksum: str, safe_name: str) -> str:
        """Relative storage path for a file: <subfolder>/<checksum[:2]>/<checksum>_<name>."""
        stored_name = f"{checksum}_{safe_name}"
        return os.path.join(subfolder, checksum[:2], stored_name).replace("\\", "/")

    def _existing_checksum_file(self, subfolder: str, checksum: str) -> str | None:
        """Return the stored name of an already-archived file for ``checksum``.

        Files in the content-addressed directory are named ``<checksum>_<original
        name>``; any entry whose prefix matches means the exact same bytes are
        already on disk, so a re-save can return immediately.
        """
        checksum_dir = os.path.join(self.base_path, subfolder, checksum[:2])
        try:
            entries = os.listdir(checksum_dir)
        except FileNotFoundError:
            return None
        prefix = f"{checksum}_"
        for entry in entries:
            if entry.startswith(prefix):
                return entry
        return None

    def get_full_path(self, relative_path: str) -> str:
        """Resolve full filesystem path from relative storage path."""
        return os.path.join(self.base_path, relative_path)


storage_service = StorageService()
