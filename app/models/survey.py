"""
Survey & Annual Statistic Models — pastoral surveys, responses and
annual parish statistical returns for the Holy See (Annuario Pontificio).
"""
import uuid

from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin, SoftDeleteMixin


class Survey(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """A pastoral or statistical survey form."""

    __tablename__ = "surveys"

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="DRAFT", nullable=False)
    survey_schema: Mapped[dict | None] = mapped_column(JSONB, nullable=True)  # JSON schema of questions

    archdiocese_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("archdioceses.id"), nullable=True)
    deanery_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("deaneries.id"), nullable=True)
    parish_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("parishes.id"), nullable=True)

    responses: Mapped[list["SurveyResponse"]] = relationship(  # type: ignore[name-defined]
        "SurveyResponse", back_populates="survey"
    )


class SurveyResponse(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """A submitted response to a survey."""

    __tablename__ = "survey_responses"

    survey_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("surveys.id"), nullable=False)
    respondent_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    respondent_parish_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("parishes.id"), nullable=True)
    submitted_by_user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    answers: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    survey: Mapped["Survey"] = relationship("Survey", back_populates="responses")  # type: ignore[name-defined]


class AnnualParishStatistic(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Annual parish statistical summary return for the Diocesan Curia & Holy See."""

    __tablename__ = "annual_parish_statistics"

    parish_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("parishes.id"), nullable=False)
    report_year: Mapped[int] = mapped_column(Integer, nullable=False)

    total_catholic_population: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_catechumens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_families: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    infant_baptisms: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    adult_baptisms: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    first_communions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    confirmations: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    marriages_both_catholic: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    marriages_mixed_religion: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    christian_funerals: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    catholic_schools_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    students_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    health_centers_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)