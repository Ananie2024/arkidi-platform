"""link new sacramental certificates to their source register entry

Revision ID: d1f8a6c4e203
Revises: c7e4b2a91d63
Create Date: 2026-09-30 12:30:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "d1f8a6c4e203"
down_revision: str | None = "c7e4b2a91d63"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "certificate_issues",
        sa.Column("source_record_id", sa.UUID(), nullable=True),
    )
    op.create_index(
        "ix_certificate_issues_source_record_id",
        "certificate_issues",
        ["source_record_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_certificate_issues_source_record_id", table_name="certificate_issues")
    op.drop_column("certificate_issues", "source_record_id")
