"""enforce unique active canonical sacramental register references

Revision ID: c7e4b2a91d63
Revises: b2f7c4d8a1e6
Create Date: 2026-09-30 12:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "c7e4b2a91d63"
down_revision: str | None = "b2f7c4d8a1e6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


REGISTER_REFERENCES = {
    "baptism_records": ("parish_id", "registry_year", "volume_number", "act_number"),
    "confirmation_records": ("parish_id", "registry_year", "volume_number", "act_number"),
    "matrimony_records": ("parish_id", "registry_year", "volume_number", "act_number"),
    "first_communion_records": ("parish_id", "registry_year", "volume_number", "act_number"),
    "holy_orders_records": ("parish_id", "register_book", "page_number", "act_number"),
    "religious_profession_records": (
        "parish_id", "register_book", "page_number", "act_number"
    ),
}


def upgrade() -> None:
    connection = op.get_bind()
    conflicts = []
    for table, fields in REGISTER_REFERENCES.items():
        columns = ", ".join(fields)
        duplicate_rows = connection.execute(
            sa.text(
                f"SELECT {columns}, COUNT(*) AS count FROM {table} "
                f"WHERE is_deleted = false GROUP BY {columns} HAVING COUNT(*) > 1 LIMIT 10"
            )
        ).mappings().all()
        if duplicate_rows:
            conflicts.append(f"{table}: {duplicate_rows}")

    if conflicts:
        raise RuntimeError(
            "Cannot enforce canonical sacramental register references because active "
            "duplicates exist. Reconcile these records before retrying migration: "
            + "; ".join(conflicts)
        )

    for table, fields in REGISTER_REFERENCES.items():
        index_name = f"uq_{table.removesuffix('_records')}_register_reference_active"
        op.create_index(
            index_name,
            table,
            list(fields),
            unique=True,
            postgresql_where=sa.text("is_deleted = false"),
        )


def downgrade() -> None:
    for table in reversed(tuple(REGISTER_REFERENCES)):
        index_name = f"uq_{table.removesuffix('_records')}_register_reference_active"
        op.drop_index(index_name, table_name=table)
