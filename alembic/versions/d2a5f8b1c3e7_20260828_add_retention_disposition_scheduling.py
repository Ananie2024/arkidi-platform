"""add retention & disposition scheduling columns

Revision ID: d2a5f8b1c3e7
Revises: a48f219b13cd
Create Date: 2026-08-28 12:00:00.000000

Adds retention_years / disposition_action to DocumentType and
retention_flagged_at / disposition_status (with a CheckConstraint) to Document
so the Celery-beat archivist-review scheduler can flag documents whose
retention deadline has elapsed.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import geoalchemy2  # noqa: F401  (keep import parity with other migrations)


# revision identifiers, used by Alembic.
revision: str = "d2a5f8b1c3e7"
down_revision: Union[str, None] = "a48f219b13cd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ------------------------------------------------------------------
    # DocumentType: retention_years + disposition_action
    # ------------------------------------------------------------------
    op.add_column(
        "document_types",
        sa.Column(
            "retention_years",
            sa.Integer(),
            nullable=True,
            comment=(
                "Years to retain documents of this type from creation date. "
                "NULL = indefinite retention."
            ),
        ),
    )
    op.add_column(
        "document_types",
        sa.Column(
            "disposition_action",
            sa.String(length=50),
            nullable=True,
            comment=(
                "Action to take when retention expires: "
                "DESTROY|TRANSFER|MANUAL_REVIEW|PRESERVE_INDEFINITELY."
            ),
        ),
    )

    # ------------------------------------------------------------------
    # Document: retention_flagged_at + disposition_status + CK
    # ------------------------------------------------------------------
    op.add_column(
        "documents",
        sa.Column(
            "retention_flagged_at",
            sa.DateTime(timezone=True),
            nullable=True,
            comment="When the document was first flagged for archivist review.",
        ),
    )
    op.add_column(
        "documents",
        sa.Column(
            "disposition_status",
            sa.String(length=50),
            nullable=True,
            server_default="ACTIVE",
            comment="ACTIVE|DUE_FOR_REVIEW|DISPOSED|PRESERVE_INDEFINITELY",
        ),
    )
    # Back-fill existing rows so the server_default applies retroactively
    # and the CheckConstraint is satisfied for all rows.
    op.execute(
        "UPDATE documents SET disposition_status = 'ACTIVE' " "WHERE disposition_status IS NULL"
    )
    # Now that every row satisfies the constraint, add the CheckConstraint.
    op.create_check_constraint(
        "ck_documents_disposition_status",
        "documents",
        "disposition_status IS NULL OR disposition_status IN "
        "('ACTIVE', 'DUE_FOR_REVIEW', 'DISPOSED', 'PRESERVE_INDEFINITELY')",
    )
    # Remove the server_default so future INSERTs via the ORM (which sets
    # the value explicitly) are not surprising; application code sets the
    # value.  Keeping the column nullable with a CHECK covers the edge
    # where ORM code omits it.
    op.alter_column("documents", "disposition_status", server_default=None)


def downgrade() -> None:
    op.drop_constraint("ck_documents_disposition_status", "documents", type_="check")
    op.drop_column("documents", "disposition_status")
    op.drop_column("documents", "retention_flagged_at")
    op.drop_column("document_types", "disposition_action")
    op.drop_column("document_types", "retention_years")
