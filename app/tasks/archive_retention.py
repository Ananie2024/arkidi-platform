"""
Archive Retention & Disposition Review Background Tasks

Every day a Celery-beat scheduler invokes ``flag_documents_due_for_review``
which scans the documents table for records whose owning ``DocumentType`` has
a ``retention_years`` policy.  Any document whose creation date plus the
retention period has passed is flagged for archivist manual review (the
``disposition_status`` column is set to ``DUE_FOR_REVIEW`` and
``retention_flagged_at`` is stamped).  Documents with ``retention_years``
set to NULL are never flagged (indefinite retention).
"""
import asyncio
import logging
from datetime import datetime, timezone
from typing import List

from sqlalchemy import or_, select
from sqlalchemy.sql import func

from app.core.database import AsyncSessionLocal
from app.models.document import Document
from app.models.document_type import DocumentType
from app.tasks.celery_app import celery_app

logger = logging.getLogger("arkidi.tasks.archive_retention")

# Valid disposition status values (mirrors the CheckConstraint on documents).
DISPOSITION_ACTIVE = "ACTIVE"
DISPOSITION_DUE_FOR_REVIEW = "DUE_FOR_REVIEW"
DISPOSITION_DISPOSED = "DISPOSED"
DISPOSITION_PRESERVE_INDEFINITELY = "PRESERVE_INDEFINITELY"

# Documents whose disposition_action on the DocumentType requests permanent
# preservation are exempt from review even after the retention deadline.
DISPOSITION_ACTION_PRESERVE = "PRESERVE_INDEFINITELY"


@celery_app.task(name="archive_retention.flag_documents_due_for_review")
def flag_documents_due_for_review() -> dict:
    """Flag documents whose retention deadline has passed.

    A document is *due* when:
      * its ``DocumentType`` has a non-null ``retention_years``
      * the ``disposition_action`` on that type is NOT
        ``PRESERVE_INDEFINITELY``
      * ``created_at + retention_years`` is in the past
      * the document has not already been flagged (i.e.
        ``disposition_status`` is ``ACTIVE`` or NULL)

    Returns a summary dict with the number of documents flagged and their
    IDs, so the beat log / monitoring can verify the run.
    """
    logger.info("flag_documents_due_for_review: starting retention scan")

    async def _run() -> dict:
        async with AsyncSessionLocal() as db:
            # Compute the retention deadline inside PostgreSQL:
            #   created_at + make_interval(years => retention_years)
            # The `+` operator with a generated interval is the portable
            # PostgreSQL idiom (date_add() is MySQL-only).
            deadline_expr = Document.created_at + func.make_interval(
                years=DocumentType.retention_years
            )

            stmt = (
                select(Document)
                .join(DocumentType, Document.document_type_id == DocumentType.id)
                .where(DocumentType.retention_years.is_not(None))
                # NULL disposition_action means "not yet specified" — still
                # flag for review; only an explicit PRESERVE_INDEFINITELY
                # on the DocumentType exempts the document.
                .where(
                    or_(
                        DocumentType.disposition_action.is_(None),
                        DocumentType.disposition_action != DISPOSITION_ACTION_PRESERVE,
                    )
                )
                .where(
                    or_(
                        Document.disposition_status.is_(None),
                        Document.disposition_status == DISPOSITION_ACTIVE,
                    )
                )
                .where(deadline_expr <= func.now())
                .where(Document.is_deleted.is_(False))
            )

            result = await db.execute(stmt)
            due_docs: List[Document] = result.scalars().all()

            for doc in due_docs:
                doc.disposition_status = DISPOSITION_DUE_FOR_REVIEW
                doc.retention_flagged_at = datetime.now(timezone.utc)

            await db.commit()
            flagged_ids = [str(doc.id) for doc in due_docs]

            summary = {
                "scanned": len(flagged_ids),
                "flagged": len(flagged_ids),
                "flagged_ids": flagged_ids,
            }
            logger.info(
                "flag_documents_due_for_review: flagged %d document(s) "
                "for archivist review",
                summary["flagged"],
            )
            return summary

    return asyncio.run(_run())

