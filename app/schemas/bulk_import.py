"""
Pydantic Schemas for Batch/Bulk Data Ingestion (CSV / Legacy Registers)
"""

from pydantic import BaseModel


class BulkImportResult(BaseModel):
    """Result summary of a batch CSV/Excel import operation."""

    total_processed: int
    imported: int
    skipped: int
    errors: list[str] = []
    message: str | None = None
