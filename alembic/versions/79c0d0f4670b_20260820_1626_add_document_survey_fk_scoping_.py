"""add document survey FK scoping constraints

Revision ID: 79c0d0f4670b
Revises: e143918e6d1a
Create Date: 2026-08-20 16:26:17.643047

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import geoalchemy2


# revision identifiers, used by Alembic.
revision: str = '79c0d0f4670b'
down_revision: Union[str, None] = 'e143918e6d1a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --------------------------------------------------------------------
    # Foreign keys on Document organisational-scoping columns.
    # NOTE: `spatial_ref_sys` is managed by the PostGIS extension — autogenerate
    # may emit a spurious drop for it; that must never be executed (removed).
    # --------------------------------------------------------------------
    op.create_foreign_key('documents_archdiocese_id_fkey', 'documents', 'archdioceses', ['archdiocese_id'], ['id'])
    op.create_foreign_key('documents_deanery_id_fkey', 'documents', 'deaneries', ['deanery_id'], ['id'])
    op.create_foreign_key('documents_parish_id_fkey', 'documents', 'parishes', ['parish_id'], ['id'])
    op.create_foreign_key('documents_commission_id_fkey', 'documents', 'commissions', ['commission_id'], ['id'])
    op.create_foreign_key('documents_council_id_fkey', 'documents', 'councils', ['council_id'], ['id'])
    op.create_foreign_key('documents_meeting_id_fkey', 'documents', 'meetings', ['meeting_id'], ['id'])
    op.create_foreign_key('documents_priest_id_fkey', 'documents', 'priests', ['priest_id'], ['id'])
    op.create_foreign_key('documents_parcel_id_fkey', 'documents', 'land_parcels', ['parcel_id'], ['id'])

    # --------------------------------------------------------------------
    # Foreign keys on Survey and SurveyResponse scoping columns.
    # --------------------------------------------------------------------
    op.create_foreign_key('surveys_archdiocese_id_fkey', 'surveys', 'archdioceses', ['archdiocese_id'], ['id'])
    op.create_foreign_key('surveys_deanery_id_fkey', 'surveys', 'deaneries', ['deanery_id'], ['id'])
    op.create_foreign_key('surveys_parish_id_fkey', 'surveys', 'parishes', ['parish_id'], ['id'])
    op.create_foreign_key('survey_responses_respondent_parish_id_fkey', 'survey_responses', 'parishes', ['respondent_parish_id'], ['id'])

    # --------------------------------------------------------------------
    # CHECK constraint on documents: at least one scoping column must be set,
    # OR `classification` explicitly allows an unscoped/general document.
    # --------------------------------------------------------------------
    op.create_check_constraint(
        'ck_documents_scoping_required',
        'documents',
        "archdiocese_id IS NOT NULL OR deanery_id IS NOT NULL OR "
        "parish_id IS NOT NULL OR commission_id IS NOT NULL OR "
        "council_id IS NOT NULL OR meeting_id IS NOT NULL OR "
        "priest_id IS NOT NULL OR parcel_id IS NOT NULL OR "
        "classification IN ('GENERAL', 'DICOESAN', 'CURIA')",
    )


def downgrade() -> None:
    op.drop_constraint('ck_documents_scoping_required', 'documents', type_='check')
    op.drop_constraint('survey_responses_respondent_parish_id_fkey', 'survey_responses', type_='foreignkey')
    op.drop_constraint('surveys_parish_id_fkey', 'surveys', type_='foreignkey')
    op.drop_constraint('surveys_deanery_id_fkey', 'surveys', type_='foreignkey')
    op.drop_constraint('surveys_archdiocese_id_fkey', 'surveys', type_='foreignkey')
    op.drop_constraint('documents_parcel_id_fkey', 'documents', type_='foreignkey')
    op.drop_constraint('documents_priest_id_fkey', 'documents', type_='foreignkey')
    op.drop_constraint('documents_meeting_id_fkey', 'documents', type_='foreignkey')
    op.drop_constraint('documents_council_id_fkey', 'documents', type_='foreignkey')
    op.drop_constraint('documents_commission_id_fkey', 'documents', type_='foreignkey')
    op.drop_constraint('documents_parish_id_fkey', 'documents', type_='foreignkey')
    op.drop_constraint('documents_deanery_id_fkey', 'documents', type_='foreignkey')
    op.drop_constraint('documents_archdiocese_id_fkey', 'documents', type_='foreignkey')
