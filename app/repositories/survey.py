"""
Statistics Module Database Repository
"""

import uuid

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.deanery import Archdiocese
from app.models.parish import Parish
from app.models.priest import Priest
from app.models.sacrament import (
    BaptismRecord,
    ChristianFuneralRecord,
    ConfirmationRecord,
    FirstCommunionRecord,
    MatrimonyRecord,
)
from app.models.survey import AnnualParishStatistic, Survey, SurveyResponse
from app.schemas.common import AnnualStatisticCreate
from app.schemas.survey import SurveyAnswerSubmit, SurveyCreate, SurveyUpdate


class StatisticsRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def lock_parish_reporting_scope(self, parish_id: uuid.UUID) -> None:
        result = await self.db.execute(
            select(Parish.id)
            .where(Parish.id == parish_id, Parish.is_deleted.is_(False))
            .with_for_update()
        )
        if result.scalar_one_or_none() is None:
            from app.core.exceptions import EntityNotFoundException

            raise EntityNotFoundException("errors.parish_not_found")

    async def get_by_parish_and_year(
        self, parish_id: uuid.UUID, year: int
    ) -> AnnualParishStatistic | None:
        stmt = select(AnnualParishStatistic).where(
            AnnualParishStatistic.parish_id == parish_id,
            AnnualParishStatistic.report_year == year,
        )
        stmt = stmt.order_by(AnnualParishStatistic.created_at.desc(), AnnualParishStatistic.id.desc()).limit(1)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def save_statistic(self, data: AnnualStatisticCreate) -> AnnualParishStatistic:
        values = data.model_dump()
        stat = await self.get_by_parish_and_year(data.parish_id, data.report_year)
        if stat is None:
            stat = AnnualParishStatistic(**values)
            self.db.add(stat)
        else:
            for field, value in values.items():
                if field not in {"parish_id", "report_year"}:
                    setattr(stat, field, value)
        await self.db.flush()
        return stat

    async def list_statistics(
        self, year: int | None = None, parish_ids: list[uuid.UUID] | None = None
    ) -> list[AnnualParishStatistic]:
        latest = select(
            AnnualParishStatistic.id.label("id"),
            func.row_number().over(
                partition_by=(AnnualParishStatistic.parish_id, AnnualParishStatistic.report_year),
                order_by=(AnnualParishStatistic.created_at.desc(), AnnualParishStatistic.id.desc()),
            ).label("row_number"),
        ).subquery()
        stmt = select(AnnualParishStatistic).join(
            latest, latest.c.id == AnnualParishStatistic.id
        ).where(latest.c.row_number == 1).order_by(
            AnnualParishStatistic.report_year.desc(),
            AnnualParishStatistic.created_at.desc(),
        )
        if year is not None:
            stmt = stmt.where(AnnualParishStatistic.report_year == year)
        if parish_ids is not None:
            stmt = stmt.where(AnnualParishStatistic.parish_id.in_(parish_ids))
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def count_parishes(self) -> int:
        stmt = select(func.count()).select_from(Parish).where(Parish.is_deleted.is_(False))
        result = await self.db.execute(stmt)
        return int(result.scalar_one() or 0)

    async def count_active_priests(self) -> int:
        from app.models.priest import ClergyStatus, ClergyType

        stmt = select(func.count()).select_from(Priest).where(
            Priest.is_deleted.is_(False),
            Priest.status == ClergyStatus.ACTIVE_DUTY,
            Priest.clergy_type.in_([ClergyType.DIOCESAN_PRIEST, ClergyType.RELIGIOUS_PRIEST]),
        )
        result = await self.db.execute(stmt)
        return int(result.scalar_one() or 0)

    async def count_register_records(self, model: type, parish_id: uuid.UUID, year: int) -> int:
        from datetime import date

        result = await self.db.execute(
            select(func.count()).select_from(model).where(
                model.parish_id == parish_id,
                model.is_deleted.is_(False),
                model.celebration_date >= date(year, 1, 1),
                model.celebration_date < date(year + 1, 1, 1),
            )
        )
        return int(result.scalar_one() or 0)

    async def get_register_totals(self, parish_id: uuid.UUID, year: int) -> dict[str, int]:
        return {
            "baptisms": await self.count_register_records(BaptismRecord, parish_id, year),
            "confirmations": await self.count_register_records(ConfirmationRecord, parish_id, year),
            "first_communions": await self.count_register_records(FirstCommunionRecord, parish_id, year),
            "marriages": await self.count_register_records(MatrimonyRecord, parish_id, year),
            "christian_funerals": await self.count_register_records(ChristianFuneralRecord, parish_id, year),
        }

    async def list_archdioceses(self) -> list[Archdiocese]:
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

    async def get_survey_by_id(self, survey_id: uuid.UUID) -> Survey | None:
        stmt = select(Survey).where(
            Survey.id == survey_id,
            Survey.is_deleted.is_(False),
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_surveys(
        self,
        archdiocese_id: uuid.UUID | None = None,
        deanery_id: uuid.UUID | None = None,
        parish_id: uuid.UUID | None = None,
        status: str | None = None,
    ) -> list[Survey]:
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

    async def list_surveys_in_jurisdiction(
        self,
        parish_ids: list[uuid.UUID],
        deanery_ids: list[uuid.UUID],
        archdiocese_id: uuid.UUID,
        status: str | None = None,
    ) -> list[Survey]:
        scope_conditions = []
        if parish_ids:
            scope_conditions.append(Survey.parish_id.in_(parish_ids))
        if deanery_ids:
            scope_conditions.append(
                and_(Survey.parish_id.is_(None), Survey.deanery_id.in_(deanery_ids))
            )
        scope_conditions.append(
            and_(Survey.parish_id.is_(None), Survey.deanery_id.is_(None), Survey.archdiocese_id == archdiocese_id)
        )
        stmt = select(Survey).where(
            Survey.is_deleted.is_(False), or_(*scope_conditions)
        )
        if status is not None:
            stmt = stmt.where(Survey.status == status)
        result = await self.db.execute(stmt.order_by(Survey.created_at.desc()))
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
        submitted_by_user_id: uuid.UUID | None = None,
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

    async def get_response_by_id(self, response_id: uuid.UUID) -> SurveyResponse | None:
        stmt = select(SurveyResponse).where(
            SurveyResponse.id == response_id,
            SurveyResponse.is_deleted.is_(False),
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_responses(self, survey_id: uuid.UUID) -> list[SurveyResponse]:
        stmt = (
            select(SurveyResponse)
            .where(
                SurveyResponse.survey_id == survey_id,
                SurveyResponse.is_deleted.is_(False),
            )
            .order_by(SurveyResponse.created_at.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def count_responses(self, survey_id: uuid.UUID) -> int:
        stmt = (
            select(func.count())
            .select_from(SurveyResponse)
            .where(
                SurveyResponse.survey_id == survey_id,
                SurveyResponse.is_deleted.is_(False),
            )
        )
        result = await self.db.execute(stmt)
        return int(result.scalar_one() or 0)
