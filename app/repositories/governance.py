"""
Governance Module Database Repository
Commissions, Councils, Meetings, and Meeting Minutes
"""

import uuid
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.commission import Commission
from app.models.council import Council
from app.models.meeting import Meeting
from app.models.meeting_minute import MeetingMinute
from app.schemas.governance import (
    CommissionCreate,
    CommissionUpdate,
    CouncilCreate,
    CouncilUpdate,
    MeetingCreate,
    MeetingMinuteCreate,
    MeetingMinuteUpdate,
    MeetingUpdate,
)


class GovernanceRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    # -----------------------------------------------------------------------
    # Commission Methods
    # -----------------------------------------------------------------------

    async def create_commission(self, data: CommissionCreate) -> Commission:
        comm = Commission(**data.model_dump())
        self.db.add(comm)
        await self.db.flush()
        return comm

    async def get_commission_by_id(self, commission_id: uuid.UUID) -> Commission | None:
        stmt = select(Commission).where(
            Commission.id == commission_id,
            Commission.is_deleted.is_(False),
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_commissions(
        self,
        archdiocese_id: uuid.UUID | None = None,
        deanery_id: uuid.UUID | None = None,
        parish_id: uuid.UUID | None = None,
        category: str | None = None,
        is_active: bool | None = None,
    ) -> list[Commission]:
        stmt = select(Commission).where(Commission.is_deleted.is_(False))
        if archdiocese_id is not None:
            stmt = stmt.where(Commission.archdiocese_id == archdiocese_id)
        if deanery_id is not None:
            stmt = stmt.where(Commission.deanery_id == deanery_id)
        if parish_id is not None:
            stmt = stmt.where(Commission.parish_id == parish_id)
        if category is not None:
            stmt = stmt.where(Commission.category == category)
        if is_active is not None:
            stmt = stmt.where(Commission.is_active == is_active)

        stmt = stmt.order_by(Commission.name)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def update_commission(self, comm: Commission, data: CommissionUpdate) -> Commission:
        update_dict = data.model_dump(exclude_unset=True)
        for key, val in update_dict.items():
            setattr(comm, key, val)
        await self.db.flush()
        return comm

    async def delete_commission(self, comm: Commission) -> None:
        comm.soft_delete()
        await self.db.flush()

    # -----------------------------------------------------------------------
    # Council Methods
    # -----------------------------------------------------------------------

    async def create_council(self, data: CouncilCreate) -> Council:
        council = Council(**data.model_dump())
        self.db.add(council)
        await self.db.flush()
        return council

    async def get_council_by_id(self, council_id: uuid.UUID) -> Council | None:
        stmt = select(Council).where(
            Council.id == council_id,
            Council.is_deleted.is_(False),
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_councils(
        self,
        archdiocese_id: uuid.UUID | None = None,
        deanery_id: uuid.UUID | None = None,
        parish_id: uuid.UUID | None = None,
        council_type: str | None = None,
        is_active: bool | None = None,
    ) -> list[Council]:
        stmt = select(Council).where(Council.is_deleted.is_(False))
        if archdiocese_id is not None:
            stmt = stmt.where(Council.archdiocese_id == archdiocese_id)
        if deanery_id is not None:
            stmt = stmt.where(Council.deanery_id == deanery_id)
        if parish_id is not None:
            stmt = stmt.where(Council.parish_id == parish_id)
        if council_type is not None:
            stmt = stmt.where(Council.council_type == council_type)
        if is_active is not None:
            stmt = stmt.where(Council.is_active == is_active)

        stmt = stmt.order_by(Council.name)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def update_council(self, council: Council, data: CouncilUpdate) -> Council:
        update_dict = data.model_dump(exclude_unset=True)
        for key, val in update_dict.items():
            setattr(council, key, val)
        await self.db.flush()
        return council

    async def delete_council(self, council: Council) -> None:
        council.soft_delete()
        await self.db.flush()

    # -----------------------------------------------------------------------
    # Meeting Methods
    # -----------------------------------------------------------------------

    async def create_meeting(self, data: MeetingCreate) -> Meeting:
        meeting = Meeting(**data.model_dump())
        self.db.add(meeting)
        await self.db.flush()
        return meeting

    async def get_meeting_by_id(self, meeting_id: uuid.UUID) -> Meeting | None:
        stmt = select(Meeting).where(
            Meeting.id == meeting_id,
            Meeting.is_deleted.is_(False),
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_meetings(
        self,
        council_id: uuid.UUID | None = None,
        commission_id: uuid.UUID | None = None,
        archdiocese_id: uuid.UUID | None = None,
        deanery_id: uuid.UUID | None = None,
        parish_id: uuid.UUID | None = None,
        status: str | None = None,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> list[Meeting]:
        stmt = select(Meeting).where(Meeting.is_deleted.is_(False))
        if council_id is not None:
            stmt = stmt.where(Meeting.council_id == council_id)
        if commission_id is not None:
            stmt = stmt.where(Meeting.commission_id == commission_id)
        if archdiocese_id is not None:
            stmt = stmt.where(Meeting.archdiocese_id == archdiocese_id)
        if deanery_id is not None:
            stmt = stmt.where(Meeting.deanery_id == deanery_id)
        if parish_id is not None:
            stmt = stmt.where(Meeting.parish_id == parish_id)
        if status is not None:
            stmt = stmt.where(Meeting.status == status)
        if from_date is not None:
            stmt = stmt.where(Meeting.meeting_date >= from_date)
        if to_date is not None:
            stmt = stmt.where(Meeting.meeting_date <= to_date)

        stmt = stmt.order_by(Meeting.meeting_date.desc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def update_meeting(self, meeting: Meeting, data: MeetingUpdate) -> Meeting:
        update_dict = data.model_dump(exclude_unset=True)
        for key, val in update_dict.items():
            setattr(meeting, key, val)
        await self.db.flush()
        return meeting

    async def delete_meeting(self, meeting: Meeting) -> None:
        meeting.soft_delete()
        await self.db.flush()

    # -----------------------------------------------------------------------
    # Meeting Minute Methods
    # -----------------------------------------------------------------------

    async def create_minute(
        self,
        data: MeetingMinuteCreate,
        recorded_by_user_id: uuid.UUID | None = None,
    ) -> MeetingMinute:
        minute = MeetingMinute(
            **data.model_dump(),
            recorded_by_user_id=recorded_by_user_id,
        )
        self.db.add(minute)
        await self.db.flush()
        return minute

    async def get_minute_by_id(self, minute_id: uuid.UUID) -> MeetingMinute | None:
        stmt = select(MeetingMinute).where(MeetingMinute.id == minute_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_minutes_for_meeting(self, meeting_id: uuid.UUID) -> list[MeetingMinute]:
        stmt = (
            select(MeetingMinute)
            .where(MeetingMinute.meeting_id == meeting_id)
            .order_by(MeetingMinute.created_at.asc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def update_minute(
        self, minute: MeetingMinute, data: MeetingMinuteUpdate
    ) -> MeetingMinute:
        update_dict = data.model_dump(exclude_unset=True)
        for key, val in update_dict.items():
            setattr(minute, key, val)
        await self.db.flush()
        return minute

    async def delete_minute(self, minute: MeetingMinute) -> None:
        await self.db.delete(minute)
        await self.db.flush()
