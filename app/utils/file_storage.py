"""
File Storage Provider Interface & Local/Cloud Storage Adapter
"""
import os
import aiofiles
from fastapi import UploadFile
from app.config import settings


class StorageService:
    """Manages file storage for documents, photos, and scanned canonical books."""

    def __init__(self, base_path: str = settings.FILE_STORAGE_PATH):
        self.base_path = base_path
        os.makedirs(self.base_path, exist_ok=True)

    async def save_file(self, file: UploadFile, subfolder: str = "general") -> str:
        """Save an uploaded file to the designated directory and return relative path."""
        target_dir = os.path.join(self.base_path, subfolder)
        os.makedirs(target_dir, exist_ok=True)

        filename = os.path.basename(file.filename or "upload.bin")
        file_path = os.path.join(target_dir, filename)

        async with aiofiles.open(file_path, "wb") as out_file:
            content = await file.read()
            await out_file.write(content)

        return os.path.relpath(file_path, self.base_path).replace("\\", "/")

    def get_full_path(self, relative_path: str) -> str:
        """Resolve full filesystem path from relative storage path."""
        return os.path.join(self.base_path, relative_path)


storage_service = StorageService()
