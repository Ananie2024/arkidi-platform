"""
Statistics Module Database Repository
"""
import uuid
from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.deanery import Archdiocese
from app.models.parish import Parish
from app.models.priest import Priest
from app.models.survey import AnnualParishStatistic, Survey, SurveyResponse
from app.schemas.common import AnnualStatisticCreate
from app.schemas.survey import SurveyCreate, SurveyUpdate, SurveyAnswerSubmit


class StatisticsRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_parish_and_year(self, parish_id: uuid.UUID, year: int) -> Optional[AnnualParishStatistic]:
        stmt = select(AnnualParishStatistic).where(
            AnnualParishStatistic.parish_id == parish_id,
            AnnualParishStatistic.report_year == year,
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def save_statistic(self, data: AnnualStatisticCreate) -> AnnualParishStatistic:
        stat = AnnualParishStatistic(**data.model_dump())
        self.db.add(stat)
        await self.db.flush()
        return stat

    async def list_statistics(self, year: Optional[int] = None) -> List[AnnualParishStatistic]:
        stmt = select(AnnualParishStatistic).order_by(
            AnnualParishStatistic.report_year.desc(),
            AnnualParishStatistic.created_at.desc(),
        )
        if year is not None:
            stmt = stmt.where(AnnualParishStatistic.report_year == year)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def count_parishes(self) -> int:
        stmt = select(func.count()).select_from(Parish).where(Parish.is_deleted.is_(False))
        result = await self.db.execute(stmt)
        return int(result.scalar_one() or 0)

    async def count_active_priests(self) -> int:
        stmt = select(func.count()).select_from(Priest).where(Priest.is_deleted.is_(False))
        result = await self.db.execute(stmt)
        return int(result.scalar_one() or 0)

    async def list_archdioceses(self) -> List[Archdiocese]:
        """Every archdiocese, oldest first.

        The Annuario Pontificio composition iterates these as indicator
        computation scopes (see StatisticsService.generate_annuario_pontificio).
        """
        stmt = select(Archdiocese).order_by(Archdiocese.created_at.asc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())


class SurveyRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_survey(self, data: SurveyCreate) -> Survey:
        questions_json = [q.model_dump() for q in data.questions]
        survey = Survey(
            title=data.title,
            description=data.description,
            status=data.status.value if hasattr(data.status, "value") else str(data.status),
            survey_schema={"questions": questions_json},
            archdiocese_id=data.archdiocese_id,
            deanery_id=data.deanery_id,
            parish_id=data.parish_id,
        )
        self.db.add(survey)
        await self.db.flush()
        return survey

    async def get_survey_by_id(self, survey_id: uuid.UUID) -> Optional[Survey]:
        stmt = select(Survey).where(
            Survey.id == survey_id,
            Survey.is_deleted.is_(False),
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_surveys(
        self,
        archdiocese_id: Optional[uuid.UUID] = None,
        deanery_id: Optional[uuid.UUID] = None,
        parish_id: Optional[uuid.UUID] = None,
        status: Optional[str] = None,
    ) -> List[Survey]:
        stmt = select(Survey).where(Survey.is_deleted.is_(False))
        if archdiocese_id is not None:
            stmt = stmt.where(Survey.archdiocese_id == archdiocese_id)
        if deanery_id is not None:
            stmt = stmt.where(Survey.deanery_id == deanery_id)
        if parish_id is not None:
            stmt = stmt.where(Survey.parish_id == parish_id)
        if status is not None:
            stmt = stmt.where(Survey.status == status)

        stmt = stmt.order_by(Survey.created_at.desc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def update_survey(self, survey: Survey, data: SurveyUpdate) -> Survey:
        if data.title is not None:
            survey.title = data.title
        if data.description is not None:
            survey.description = data.description
        if data.status is not None:
            survey.status = data.status.value if hasattr(data.status, "value") else str(data.status)
        if data.questions is not None:
            questions_json = [q.model_dump() for q in data.questions]
            survey.survey_schema = {"questions": questions_json}
        if data.archdiocese_id is not None:
            survey.archdiocese_id = data.archdiocese_id
        if data.deanery_id is not None:
            survey.deanery_id = data.deanery_id
        if data.parish_id is not None:
            survey.parish_id = data.parish_id

        await self.db.flush()
        return survey

    async def delete_survey(self, survey: Survey) -> None:
        survey.soft_delete()
        await self.db.flush()

    async def create_response(
        self,
        survey_id: uuid.UUID,
        data: SurveyAnswerSubmit,
        submitted_by_user_id: Optional[uuid.UUID] = None,
    ) -> SurveyResponse:
        resp = SurveyResponse(
            survey_id=survey_id,
            respondent_name=data.respondent_name,
            respondent_parish_id=data.respondent_parish_id,
            submitted_by_user_id=submitted_by_user_id,
            answers=data.answers,
        )
        self.db.add(resp)
        await self.db.flush()
        return resp

    async def get_response_by_id(self, response_id: uuid.UUID) -> Optional[SurveyResponse]:
        stmt = select(SurveyResponse).where(
            SurveyResponse.id == response_id,
            SurveyResponse.is_deleted.is_(False),
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_responses(self, survey_id: uuid.UUID) -> List[SurveyResponse]:
        stmt = select(SurveyResponse).where(
            SurveyResponse.survey_id == survey_id,
            SurveyResponse.is_deleted.is_(False),
        ).order_by(SurveyResponse.created_at.desc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def count_responses(self, survey_id: uuid.UUID) -> int:
        stmt = select(func.count()).select_from(SurveyResponse).where(
            SurveyResponse.survey_id == survey_id,
            SurveyResponse.is_deleted.is_(False),
        )
        result = await self.db.execute(stmt)
        return int(result.scalar_one() or 0)

