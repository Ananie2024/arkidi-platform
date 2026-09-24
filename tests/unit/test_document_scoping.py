"""
Tests for the Document organisational-scoping CHECK constraint.
"""

import pytest
from sqlalchemy.exc import IntegrityError

from app.core.database import AsyncSessionLocal
from app.models.deanery import Archdiocese
from app.models.document import Document


@pytest.mark.asyncio
async def test_document_scoped_insert_succeeds_with_default_classification():
    """A Document with an archdiocese scope (and default 'OFFICIAL'
    classification, no enum) must insert cleanly."""
    async with AsyncSessionLocal() as db:
        try:
            archdiocese = Archdiocese(name="Scope Archdiocese", see_city="Kigali")
            db.add(archdiocese)
            await db.flush()

            doc = Document(
                title="Scoped Document",
                file_path="/tmp/scoped.pdf",
                archdiocese_id=archdiocese.id,
                # classification left at its default ('OFFICIAL')
            )
            db.add(doc)
            await db.flush()
            assert doc.id is not None
        finally:
            await db.rollback()


@pytest.mark.asyncio
async def test_unscoped_document_rejected():
    """A Document with no scoping FK must raise an IntegrityError, even though
    its classification falls back to 'OFFICIAL'."""
    async with AsyncSessionLocal() as db:
        try:
            doc = Document(
                title="Unscoped Document",
                file_path="/tmp/unscoped.pdf",
            )
            db.add(doc)
            with pytest.raises(IntegrityError):
                await db.flush()
        finally:
            await db.rollback()
