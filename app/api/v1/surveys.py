"""
Surveys Module FastAPI Endpoints
Pastoral Surveys, Questionnaires, and Parish/Diocesan Responses
"""

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import enforce_parish_scope, get_db, require_roles
from app.models.deanery import Deanery
from app.models.enums import UserRole
from app.models.parish import Parish
from app.models.survey import Survey
from app.schemas.survey import (
    SurveyAnswerSubmit,
    SurveyCreate,
    SurveyResponse,
    SurveyResponseRecord,
    SurveySummaryResponse,
    SurveyUpdate,
)
from app.services.org.hierarchy_resolver import get_descendant_parish_ids
from app.services.survey import SurveyService
from app.utils.response import ApiResponse

router = APIRouter(prefix="/surveys", tags=["Pastoral Surveys & Returns"])


async def _enforce_survey_scope(db: AsyncSession, user: dict, survey_id: uuid.UUID) -> None:
    survey = await db.scalar(select(Survey).where(Survey.id == survey_id))
    if survey is None:
        return  # The service returns the standard not-found response.
    if survey.parish_id is not None:
        await enforce_parish_scope(user, db, survey.parish_id)
    elif user.get("parish_id"):
        parish_deanery_id = await db.scalar(
            select(Parish.deanery_id).where(Parish.id == uuid.UUID(user["parish_id"]))
        )
        belongs_to_survey = survey.deanery_id == parish_deanery_id
        if survey.deanery_id is None and survey.archdiocese_id is not None:
            parish_archdiocese_id = await db.scalar(
                select(Deanery.archdiocese_id).where(Deanery.id == parish_deanery_id)
            )
            belongs_to_survey = parish_archdiocese_id == survey.archdiocese_id
        if not belongs_to_survey:
            from app.core.exceptions import PermissionDeniedException

            raise PermissionDeniedException("Access forbidden outside assigned parish.")
    elif user.get("deanery_id"):
        assigned_deanery_id = uuid.UUID(user["deanery_id"])
        assigned_archdiocese_id = await db.scalar(
            select(Deanery.archdiocese_id).where(Deanery.id == assigned_deanery_id)
        )
        belongs_to_scope = survey.deanery_id == assigned_deanery_id or (
            survey.deanery_id is None
            and survey.parish_id is None
            and survey.archdiocese_id == assigned_archdiocese_id
        )
        if not belongs_to_scope:
            from app.core.exceptions import PermissionDeniedException

            raise PermissionDeniedException("Access forbidden outside assigned deanery.")
    else:
        await enforce_parish_scope(user, db, None)


@router.post(
    "",
    response_model=ApiResponse[SurveyResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_survey(
    data: SurveyCreate,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_roles([UserRole.PARISH_PRIEST, UserRole.CHANCELLOR])),
):
    if data.parish_id is not None:
        await enforce_parish_scope(user, db, data.parish_id)
    elif "parish_id" in data.model_fields_set and (user.get("parish_id") or user.get("deanery_id")):
        from app.core.exceptions import PermissionDeniedException

        raise PermissionDeniedException("A parish-scoped survey is required.")
    elif user.get("parish_id") or user.get("deanery_id"):
        from app.core.exceptions import PermissionDeniedException

        raise PermissionDeniedException("A parish-scoped survey is required.")
    else:
        await enforce_parish_scope(user, db, None)
    if (user.get("parish_id") or user.get("deanery_id")) and (
        data.deanery_id is not None or data.archdiocese_id is not None
    ):
        from app.core.exceptions import PermissionDeniedException

        raise PermissionDeniedException("Parish users cannot assign surveys to a broader scope.")
    """Create a new diocesan or parish pastoral survey."""
    service = SurveyService(db)
    created = await service.create_survey(data)
    return ApiResponse.ok(data=created, message="success.survey_created")


@router.get("", response_model=ApiResponse[list[SurveyResponse]])
async def list_surveys(
    archdiocese_id: uuid.UUID | None = Query(default=None),
    deanery_id: uuid.UUID | None = Query(default=None),
    parish_id: uuid.UUID | None = Query(default=None),
    survey_status: str | None = Query(default=None, alias="status"),
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_roles([UserRole.READ_ONLY_AUDITOR])),
):
    parish_id = await enforce_parish_scope(user, db, parish_id)
    """List pastoral surveys with optional geographic and status filters."""
    service = SurveyService(db)
    if user.get("parish_id"):
        assigned_parish_id = uuid.UUID(user["parish_id"])
        deanery_id = await db.scalar(
            select(Parish.deanery_id).where(Parish.id == assigned_parish_id)
        )
        archdiocese_id_for_scope = (
            await db.scalar(select(Deanery.archdiocese_id).where(Deanery.id == deanery_id))
            if deanery_id
            else None
        )
        deanery_ids = [deanery_id] if deanery_id else []
        items = await service.list_surveys_in_jurisdiction(
            [assigned_parish_id], deanery_ids, archdiocese_id_for_scope, survey_status
        )
    elif user.get("deanery_id"):
        assigned_deanery_id = uuid.UUID(user["deanery_id"])
        parish_ids = await get_descendant_parish_ids(db, deanery_id=assigned_deanery_id)
        archdiocese_id_for_scope = await db.scalar(
            select(Deanery.archdiocese_id).where(Deanery.id == assigned_deanery_id)
        )
        items = await service.list_surveys_in_jurisdiction(
            parish_ids, [assigned_deanery_id], archdiocese_id_for_scope, survey_status
        )
    else:
        items = await service.list_surveys(
            archdiocese_id=archdiocese_id,
            deanery_id=deanery_id,
            parish_id=parish_id,
            survey_status=survey_status,
        )
    return ApiResponse.ok(data=items)


@router.get("/{survey_id}", response_model=ApiResponse[SurveyResponse])
async def get_survey(
    survey_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_roles([UserRole.READ_ONLY_AUDITOR])),
):
    await _enforce_survey_scope(db, user, survey_id)
    """Get single survey with its question schema."""
    service = SurveyService(db)
    survey = await service.get_survey(survey_id)
    return ApiResponse.ok(data=survey)


@router.put("/{survey_id}", response_model=ApiResponse[SurveyResponse])
async def update_survey(
    survey_id: uuid.UUID,
    data: SurveyUpdate,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_roles([UserRole.PARISH_PRIEST, UserRole.CHANCELLOR])),
):
    await _enforce_survey_scope(db, user, survey_id)
    if data.parish_id is not None:
        await enforce_parish_scope(user, db, data.parish_id)
    elif "parish_id" in data.model_fields_set and (user.get("parish_id") or user.get("deanery_id")):
        from app.core.exceptions import PermissionDeniedException

        raise PermissionDeniedException("A parish-scoped survey is required.")
    if (user.get("parish_id") or user.get("deanery_id")) and (
        data.deanery_id is not None or data.archdiocese_id is not None
    ):
        from app.core.exceptions import PermissionDeniedException

        raise PermissionDeniedException("Parish users cannot reassign a survey's broader scope.")
    """Update survey metadata, questions, or status (e.g. DRAFT -> ACTIVE -> CLOSED)."""
    service = SurveyService(db)
    updated = await service.update_survey(survey_id, data)
    return ApiResponse.ok(data=updated, message="success.survey_updated")


@router.delete("/{survey_id}", response_model=ApiResponse[dict])
async def delete_survey(
    survey_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_roles([UserRole.PARISH_PRIEST, UserRole.CHANCELLOR])),
):
    await _enforce_survey_scope(db, user, survey_id)
    """Soft delete a pastoral survey."""
    service = SurveyService(db)
    await service.delete_survey(survey_id)
    return ApiResponse.ok(message="success.survey_deleted", data={"deleted": True})


@router.post(
    "/{survey_id}/responses",
    response_model=ApiResponse[SurveyResponseRecord],
    status_code=status.HTTP_201_CREATED,
)
async def submit_response(
    survey_id: uuid.UUID,
    data: SurveyAnswerSubmit,
    db: AsyncSession = Depends(get_db),
    user_payload: dict = Depends(require_roles([UserRole.PARISH_SECRETARY])),
):
    """Submit a response to an active pastoral survey."""
    survey_parish_id = await db.scalar(select(Survey.parish_id).where(Survey.id == survey_id))
    await _enforce_survey_scope(db, user_payload, survey_id)
    if data.respondent_parish_id is None and user_payload.get("parish_id"):
        data.respondent_parish_id = uuid.UUID(user_payload["parish_id"])
    if data.respondent_parish_id is None and user_payload.get("deanery_id"):
        from app.core.exceptions import PermissionDeniedException

        raise PermissionDeniedException("Select a respondent parish in the assigned deanery.")
    if data.respondent_parish_id is None:
        await enforce_parish_scope(user_payload, db, None)
        from app.core.exceptions import PermissionDeniedException

        raise PermissionDeniedException("A respondent parish is required.")
    if data.respondent_parish_id is not None:
        scoped_parish = await enforce_parish_scope(user_payload, db, data.respondent_parish_id)
        if survey_parish_id is not None and data.respondent_parish_id != survey_parish_id:
            from app.core.exceptions import PermissionDeniedException

            raise PermissionDeniedException("Response parish must match the survey parish.")
        if scoped_parish is not None and data.respondent_parish_id != scoped_parish:
            from app.core.exceptions import PermissionDeniedException

            raise PermissionDeniedException("Response parish is outside the assigned jurisdiction.")
    service = SurveyService(db)
    user_id = uuid.UUID(user_payload["sub"]) if user_payload and "sub" in user_payload else None
    response = await service.submit_response(
        survey_id=survey_id,
        data=data,
        submitted_by_user_id=user_id,
    )
    return ApiResponse.ok(data=response, message="success.survey_response_submitted")


@router.get("/{survey_id}/responses", response_model=ApiResponse[list[SurveyResponseRecord]])
async def list_responses(
    survey_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_roles([UserRole.READ_ONLY_AUDITOR])),
):
    await _enforce_survey_scope(db, user, survey_id)
    """List all responses for a survey."""
    service = SurveyService(db)
    responses = await service.list_responses(survey_id)
    return ApiResponse.ok(data=responses)


@router.get(
    "/{survey_id}/responses/{response_id}", response_model=ApiResponse[SurveyResponseRecord]
)
async def get_response(
    survey_id: uuid.UUID,
    response_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_roles([UserRole.READ_ONLY_AUDITOR])),
):
    await _enforce_survey_scope(db, user, survey_id)
    """Get single survey response record."""
    service = SurveyService(db)
    resp = await service.get_response(survey_id=survey_id, response_id=response_id)
    return ApiResponse.ok(data=resp)


@router.get("/{survey_id}/summary", response_model=ApiResponse[SurveySummaryResponse])
async def get_survey_summary(
    survey_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_roles([UserRole.READ_ONLY_AUDITOR])),
):
    await _enforce_survey_scope(db, user, survey_id)
    """Get aggregated answer analytics and response metrics for a survey."""
    service = SurveyService(db)
    summary = await service.get_summary(survey_id)
    return ApiResponse.ok(data=summary)
