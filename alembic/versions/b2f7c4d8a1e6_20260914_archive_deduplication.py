"""add archive deduplication unique constraints

Revision ID: b2f7c4d8a1e6
Revises: d2a5f8b1c3e7
Create Date: 2026-09-14 12:00:00.000000

The archive must never store the same content twice:

  * documents                    — unique SHA-256 checksum for active rows
  * archive_ledger_books         — one canonical book per
                                   (parish_id, sacrament_type, volume_number)
  * archive_scanned_pages       — one scan per (ledger_book_id, page_number)

Existing duplicate rows are collapsed before the constraints are installed so
the migration is safe on databases that already accumulated duplicates.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b2f7c4d8a1e6"
down_revision: Union[str, None] = "d2a5f8b1c3e7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    connection = op.get_bind()

    # ------------------------------------------------------------------
    # 1) documents — collapse duplicate checksum rows (keep earliest, soft-delete
    # the rest) then guard the checksum with a partial unique index restricted
    # to active rows so a soft-deleted document can be re-archived again later.
    connection.execute(
        sa.text(
        """
        WITH ranked AS (
            SELECT id,
                   ROW_NUMBER() OVER (
                       PARTITION BY checksum_sha256
                       ORDER BY created_at ASC, id ASC
                   ) AS rn
            FROM documents
            WHERE checksum_sha256 IS NOT NULL AND is_deleted = false
        )
        UPDATE documents
        SET is_deleted = true, deleted_at = NOW()
        WHERE id IN (SELECT id FROM ranked WHERE rn > 1)
        """
    )
    )

    op.create_index(
        "uq_documents_checksum_active",
        "documents",
        ["checksum_sha256"],
        unique=True,
        postgresql_where=sa.text("checksum_sha256 IS NOT NULL AND is_deleted = false"),
    )

    # ------------------------------------------------------------------
    # 2) archive_ledger_books — a physical canonical book is uniquely identified
    # by (parish, sacrament type, volume). Soft-delete duplicates first so the
    # partial unique index can be created.
    connection.execute(
        sa.text(
        """
        WITH ranked AS (
            SELECT id,
                   ROW_NUMBER() OVER (
                       PARTITION BY parish_id, sacrament_type, volume_number
                       ORDER BY created_at ASC, id ASC
                   ) AS rn
            FROM archive_ledger_books
            WHERE is_deleted = false
        )
        UPDATE archive_ledger_books
        SET is_deleted = true, deleted_at = NOW()
        WHERE id IN (SELECT id FROM ranked WHERE rn > 1)
        """
    )
    )

    op.create_index(
        "uq_ledger_book_parish_volume",
        "archive_ledger_books",
        ["parish_id", "sacrament_type", "volume_number"],
        unique=True,
        postgresql_where=sa.text("is_deleted = false"),
    )

    # ------------------------------------------------------------------
    # 3) archive_scanned_pages — one scan per (book, page). This table has no
    # soft-delete column, so duplicates are hard-deleted keeping the earliest
    # row, and the owning book page counters are recomputed afterwards.
    connection.execute(
        sa.text(
        """
        DELETE FROM archive_scanned_pages p
        USING archive_scanned_pages dup
        WHERE p.id <> dup.id
          AND p.ledger_book_id = dup.ledger_book_id
          AND p.page_number = dup.page_number
          AND (
              p.created_at > dup.created_at
              OR (p.created_at = dup.created_at AND p.id > dup.id)
          )
        """
    )
    )

    op.create_unique_constraint(
        "uq_scanned_page_book_page",
        "archive_scanned_pages",
        ["ledger_book_id", "page_number"],
    )

    connection.execute(
        sa.text(
        """
        UPDATE archive_ledger_books b
        SET total_scanned_pages = (
            SELECT COUNT(*)
            FROM archive_scanned_pages p
            WHERE p.ledger_book_id = b.id
        )
        """
    )
    )


def downgrade() -> None:
    op.drop_constraint("uq_scanned_page_book_page", "archive_scanned_pages", type_="unique")
    op.drop_index("uq_documents_checksum_active", table_name="documents")
    op.drop_index("uq_ledger_book_parish_volume", table_name="archive_ledger_books")
