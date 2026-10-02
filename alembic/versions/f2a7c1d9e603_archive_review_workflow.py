"""add explicit scan review state

Revision ID: f2a7c1d9e603
Revises: e89f3a4c7b12
Create Date: 2026-10-02 15:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "f2a7c1d9e603"
down_revision: str | None = "e89f3a4c7b12"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "archive_scanned_pages",
        sa.Column("review_status", sa.String(length=30), nullable=False, server_default="PENDING"),
    )
    op.add_column(
        "archive_scanned_pages",
        sa.Column("reviewed_by_user_id", sa.UUID(), nullable=True),
    )
    op.add_column(
        "archive_scanned_pages",
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "archive_scanned_pages",
        sa.Column("review_notes", sa.Text(), nullable=True),
    )
    op.create_check_constraint(
        "ck_archive_scanned_page_review_status",
        "archive_scanned_pages",
        "review_status IN ('PENDING', 'REVIEWED', 'NEEDS_RESCAN')",
    )
    op.create_index(
        "ix_archive_scanned_page_review_status",
        "archive_scanned_pages",
        ["review_status"],
    )


def downgrade() -> None:
    op.drop_index("ix_archive_scanned_page_review_status", table_name="archive_scanned_pages")
    op.drop_constraint(
        "ck_archive_scanned_page_review_status",
        "archive_scanned_pages",
        type_="check",
    )
    op.drop_column("archive_scanned_pages", "review_notes")
    op.drop_column("archive_scanned_pages", "reviewed_at")
    op.drop_column("archive_scanned_pages", "reviewed_by_user_id")
    op.drop_column("archive_scanned_pages", "review_status")
