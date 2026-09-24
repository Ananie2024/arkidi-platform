"""
Surveys Module FastAPI Endpoints
Pastoral Surveys, Questionnaires, and Parish/Diocesan Responses
"""

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, require_roles
from app.models.enums import UserRole
from app.schemas.survey import (
    SurveyAnswerSubmit,
    SurveyCreate,
    SurveyResponse,
    SurveyResponseRecord,
    SurveySummaryResponse,
    SurveyUpdate,
)
from app.services.survey import SurveyService
from app.utils.response import ApiResponse

router = APIRouter(prefix="/surveys", tags=["Pastoral Surveys & Returns"])


@router.post(
    "",
    response_model=ApiResponse[SurveyResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_survey(
    data: SurveyCreate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_roles([UserRole.PARISH_PRIEST, UserRole.CHANCELLOR])),
):
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
    _: dict = Depends(require_roles([UserRole.READ_ONLY_AUDITOR])),
):
    """List pastoral surveys with optional geographic and status filters."""
    service = SurveyService(db)
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
    _: dict = Depends(require_roles([UserRole.READ_ONLY_AUDITOR])),
):
    """Get single survey with its question schema."""
    service = SurveyService(db)
    survey = await service.get_survey(survey_id)
    return ApiResponse.ok(data=survey)


@router.put("/{survey_id}", response_model=ApiResponse[SurveyResponse])
async def update_survey(
    survey_id: uuid.UUID,
    data: SurveyUpdate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_roles([UserRole.PARISH_PRIEST, UserRole.CHANCELLOR])),
):
    """Update survey metadata, questions, or status (e.g. DRAFT -> ACTIVE -> CLOSED)."""
    service = SurveyService(db)
    updated = await service.update_survey(survey_id, data)
    return ApiResponse.ok(data=updated, message="success.survey_updated")


@router.delete("/{survey_id}", response_model=ApiResponse[dict])
async def delete_survey(
    survey_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_roles([UserRole.PARISH_PRIEST, UserRole.CHANCELLOR])),
):
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
    _: dict = Depends(require_roles([UserRole.READ_ONLY_AUDITOR])),
):
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
    _: dict = Depends(require_roles([UserRole.READ_ONLY_AUDITOR])),
):
    """Get single survey response record."""
    service = SurveyService(db)
    resp = await service.get_response(survey_id=survey_id, response_id=response_id)
    return ApiResponse.ok(data=resp)


@router.get("/{survey_id}/summary", response_model=ApiResponse[SurveySummaryResponse])
async def get_survey_summary(
    survey_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_roles([UserRole.READ_ONLY_AUDITOR])),
):
    """Get aggregated answer analytics and response metrics for a survey."""
    service = SurveyService(db)
    summary = await service.get_summary(survey_id)
    return ApiResponse.ok(data=summary)
