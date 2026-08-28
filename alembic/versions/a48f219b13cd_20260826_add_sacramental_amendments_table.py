"""add sacramental_amendments table

Revision ID: a48f219b13cd
Revises: 79c0d0f4670b
Create Date: 2026-08-26 15:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a48f219b13cd'
down_revision: Union[str, None] = '79c0d0f4670b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enum types if not exists
    amendment_status_enum = postgresql.ENUM('PENDING', 'APPROVED', 'REJECTED', name='amendment_status_enum')
    amendment_status_enum.create(op.get_bind(), checkfirst=True)

    amendment_type_enum = postgresql.ENUM(
        'CLERICAL_ERROR', 'NAME_RECTIFICATION', 'DATE_RECTIFICATION',
        'CANONICAL_DECREE', 'ADNOTATIO_MARGINALIS', 'OTHER',
        name='amendment_type_enum'
    )
    amendment_type_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        'sacramental_amendments',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column(
            'sacrament_type',
            postgresql.ENUM(
                'BAPTISM', 'FIRST_COMMUNION', 'CONFIRMATION', 'MATRIMONY',
                'HOLY_ORDERS', 'RELIGIOUS_PROFESSION', 'ANOINTING_OF_THE_SICK',
                'CHRISTIAN_FUNERAL',
                name='sacrament_type_enum',
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column('record_id', sa.UUID(), nullable=False),
        sa.Column(
            'amendment_type',
            postgresql.ENUM(
                'CLERICAL_ERROR', 'NAME_RECTIFICATION', 'DATE_RECTIFICATION',
                'CANONICAL_DECREE', 'ADNOTATIO_MARGINALIS', 'OTHER',
                name='amendment_type_enum',
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column('reason', sa.Text(), nullable=False),
        sa.Column('field_changes', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('supporting_document_id', sa.UUID(), nullable=True),
        sa.Column(
            'status',
            postgresql.ENUM(
                'PENDING', 'APPROVED', 'REJECTED',
                name='amendment_status_enum',
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column('requested_by_user_id', sa.UUID(), nullable=True),
        sa.Column('reviewed_by_user_id', sa.UUID(), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('review_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), default=False, nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_sacramental_amendments_id'), 'sacramental_amendments', ['id'], unique=False)
    op.create_index(op.f('ix_sacramental_amendments_record_id'), 'sacramental_amendments', ['record_id'], unique=False)
    op.create_index(op.f('ix_sacramental_amendments_is_deleted'), 'sacramental_amendments', ['is_deleted'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_sacramental_amendments_is_deleted'), table_name='sacramental_amendments')
    op.drop_index(op.f('ix_sacramental_amendments_record_id'), table_name='sacramental_amendments')
    op.drop_index(op.f('ix_sacramental_amendments_id'), table_name='sacramental_amendments')
    op.drop_table('sacramental_amendments')
    op.execute('DROP TYPE IF EXISTS amendment_type_enum')
    op.execute('DROP TYPE IF EXISTS amendment_status_enum')
