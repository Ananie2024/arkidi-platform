"""
Survey Module Business Logic Service
"""

import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import EntityNotFoundException, ValidationException
from app.models.survey import Survey
from app.repositories.survey import SurveyRepository
from app.schemas.survey import (
    SurveyAnswerSubmit,
    SurveyCreate,
    SurveyQuestion,
    SurveyResponseRecord,
    SurveySummaryResponse,
    SurveyUpdate,
)
from app.schemas.survey import (
    SurveyResponse as SurveyResponseSchema,
)


class SurveyService:
    def __init__(self, db: AsyncSession):
        self.repo = SurveyRepository(db)

    def _to_survey_response(self, survey: Survey, response_count: int = 0) -> SurveyResponseSchema:
        questions_raw = (survey.survey_schema or {}).get("questions", [])
        questions = [SurveyQuestion.model_validate(q) for q in questions_raw]
        return SurveyResponseSchema(
            id=survey.id,
            title=survey.title,
            description=survey.description,
            status=survey.status,
            questions=questions,
            archdiocese_id=survey.archdiocese_id,
            deanery_id=survey.deanery_id,
            parish_id=survey.parish_id,
            response_count=response_count,
            created_at=survey.created_at,
            updated_at=survey.updated_at,
        )

    async def create_survey(self, data: SurveyCreate) -> SurveyResponseSchema:
        survey = await self.repo.create_survey(data)
        return self._to_survey_response(survey, response_count=0)

    async def get_survey(self, survey_id: uuid.UUID) -> SurveyResponseSchema:
        survey = await self.repo.get_survey_by_id(survey_id)
        if not survey:
            raise EntityNotFoundException("errors.survey_not_found")
        count = await self.repo.count_responses(survey_id)
        return self._to_survey_response(survey, response_count=count)

    async def list_surveys(
        self,
        archdiocese_id: uuid.UUID | None = None,
        deanery_id: uuid.UUID | None = None,
        parish_id: uuid.UUID | None = None,
        survey_status: str | None = None,
    ) -> list[SurveyResponseSchema]:
        surveys = await self.repo.list_surveys(
            archdiocese_id=archdiocese_id,
            deanery_id=deanery_id,
            parish_id=parish_id,
            status=survey_status,
        )
        results = []
        for s in surveys:
            count = await self.repo.count_responses(s.id)
            results.append(self._to_survey_response(s, response_count=count))
        return results

    async def update_survey(self, survey_id: uuid.UUID, data: SurveyUpdate) -> SurveyResponseSchema:
        survey = await self.repo.get_survey_by_id(survey_id)
        if not survey:
            raise EntityNotFoundException("errors.survey_not_found")
        updated = await self.repo.update_survey(survey, data)
        count = await self.repo.count_responses(survey_id)
        return self._to_survey_response(updated, response_count=count)

    async def delete_survey(self, survey_id: uuid.UUID) -> None:
        survey = await self.repo.get_survey_by_id(survey_id)
        if not survey:
            raise EntityNotFoundException("errors.survey_not_found")
        await self.repo.delete_survey(survey)

    async def submit_response(
        self,
        survey_id: uuid.UUID,
        data: SurveyAnswerSubmit,
        submitted_by_user_id: uuid.UUID | None = None,
    ) -> SurveyResponseRecord:
        survey = await self.repo.get_survey_by_id(survey_id)
        if not survey:
            raise EntityNotFoundException("errors.survey_not_found")

        if survey.status != "ACTIVE":
            raise ValidationException(
                "errors.survey_inactive",
                message_params={"status": survey.status},
            )

        # Validate required questions
        questions_raw = (survey.survey_schema or {}).get("questions", [])
        for q in questions_raw:
            q_id = q.get("id")
            is_required = q.get("required", True)
            if is_required and (
                q_id not in data.answers or data.answers[q_id] is None or data.answers[q_id] == ""
            ):
                raise ValidationException(
                    "errors.missing_required_answer",
                    message_params={"question": q.get("question_text", q_id)},
                )

        resp = await self.repo.create_response(
            survey_id=survey_id,
            data=data,
            submitted_by_user_id=submitted_by_user_id,
        )
        return SurveyResponseRecord.model_validate(resp)

    async def list_responses(self, survey_id: uuid.UUID) -> list[SurveyResponseRecord]:
        survey = await self.repo.get_survey_by_id(survey_id)
        if not survey:
            raise EntityNotFoundException("errors.survey_not_found")
        responses = await self.repo.list_responses(survey_id)
        return [SurveyResponseRecord.model_validate(r) for r in responses]

    async def get_response(
        self, survey_id: uuid.UUID, response_id: uuid.UUID
    ) -> SurveyResponseRecord:
        resp = await self.repo.get_response_by_id(response_id)
        if not resp or resp.survey_id != survey_id:
            raise EntityNotFoundException("errors.survey_response_not_found")
        return SurveyResponseRecord.model_validate(resp)

    async def get_summary(self, survey_id: uuid.UUID) -> SurveySummaryResponse:
        survey = await self.repo.get_survey_by_id(survey_id)
        if not survey:
            raise EntityNotFoundException("errors.survey_not_found")

        responses = await self.repo.list_responses(survey_id)
        questions_raw = (survey.survey_schema or {}).get("questions", [])

        question_summaries: dict[str, Any] = {}
        for q in questions_raw:
            qid = q.get("id", "")
            qtype = q.get("question_type", "TEXT")
            answers = [
                r.answers.get(qid)
                for r in responses
                if r.answers and qid in r.answers and r.answers[qid] is not None
            ]

            if qtype in ("SINGLE_CHOICE", "BOOLEAN"):
                freq: dict[str, int] = {}
                for a in answers:
                    key = str(a)
                    freq[key] = freq.get(key, 0) + 1
                question_summaries[qid] = {
                    "type": qtype,
                    "total_answered": len(answers),
                    "frequencies": freq,
                }
            elif qtype == "MULTIPLE_CHOICE":
                multi_freq: dict[str, int] = {}
                for a in answers:
                    if isinstance(a, list):
                        for item in a:
                            multi_freq[str(item)] = multi_freq.get(str(item), 0) + 1
                    else:
                        multi_freq[str(a)] = multi_freq.get(str(a), 0) + 1
                question_summaries[qid] = {
                    "type": qtype,
                    "total_answered": len(answers),
                    "frequencies": multi_freq,
                }
            elif qtype in ("NUMBER", "RATING"):
                numeric_answers: list[float] = []
                for a in answers:
                    if a is None:
                        continue
                    try:
                        numeric_answers.append(float(a))
                    except (ValueError, TypeError):
                        pass
                avg = sum(numeric_answers) / len(numeric_answers) if numeric_answers else 0
                question_summaries[qid] = {
                    "type": qtype,
                    "total_answered": len(numeric_answers),
                    "average": round(avg, 2),
                    "min": min(numeric_answers) if numeric_answers else 0,
                    "max": max(numeric_answers) if numeric_answers else 0,
                }
            else:
                question_summaries[qid] = {
                    "type": qtype,
                    "total_answered": len(answers),
                    "sample_answers": answers[:5],
                }

        return SurveySummaryResponse(
            survey_id=survey_id,
            title=survey.title,
            total_responses=len(responses),
            question_summaries=question_summaries,
        )
