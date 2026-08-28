"""
Governance Module Business Logic Service
Commissions, Councils, Meetings, and Meeting Minutes
"""
import uuid
from datetime import date
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import EntityNotFoundException, ValidationException
from app.repositories.governance import GovernanceRepository
from app.schemas.governance import (
    CommissionCreate,
    CommissionUpdate,
    CommissionResponse,
    CouncilCreate,
    CouncilUpdate,
    CouncilResponse,
    MeetingCreate,
    MeetingUpdate,
    MeetingResponse,
    MeetingMinuteCreate,
    MeetingMinuteUpdate,
    MeetingMinuteResponse,
)


class GovernanceService:
    def __init__(self, db: AsyncSession):
        self.repo = GovernanceRepository(db)

    # -----------------------------------------------------------------------
    # Commission Operations
    # -----------------------------------------------------------------------

    async def create_commission(self, data: CommissionCreate) -> CommissionResponse:
        comm = await self.repo.create_commission(data)
        return CommissionResponse.model_validate(comm)

    async def get_commission(self, commission_id: uuid.UUID) -> CommissionResponse:
        comm = await self.repo.get_commission_by_id(commission_id)
        if not comm:
            raise EntityNotFoundException("Commission not found.")
        return CommissionResponse.model_validate(comm)

    async def list_commissions(
        self,
        archdiocese_id: Optional[uuid.UUID] = None,
        deanery_id: Optional[uuid.UUID] = None,
        parish_id: Optional[uuid.UUID] = None,
        category: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> List[CommissionResponse]:
        items = await self.repo.list_commissions(
            archdiocese_id=archdiocese_id,
            deanery_id=deanery_id,
            parish_id=parish_id,
            category=category,
            is_active=is_active,
        )
        return [CommissionResponse.model_validate(c) for c in items]

    async def update_commission(self, commission_id: uuid.UUID, data: CommissionUpdate) -> CommissionResponse:
        comm = await self.repo.get_commission_by_id(commission_id)
        if not comm:
            raise EntityNotFoundException("Commission not found.")
        updated = await self.repo.update_commission(comm, data)
        return CommissionResponse.model_validate(updated)

    async def delete_commission(self, commission_id: uuid.UUID) -> None:
        comm = await self.repo.get_commission_by_id(commission_id)
        if not comm:
            raise EntityNotFoundException("Commission not found.")
        await self.repo.delete_commission(comm)

    # -----------------------------------------------------------------------
    # Council Operations
    # -----------------------------------------------------------------------

    async def create_council(self, data: CouncilCreate) -> CouncilResponse:
        council = await self.repo.create_council(data)
        return CouncilResponse.model_validate(council)

    async def get_council(self, council_id: uuid.UUID) -> CouncilResponse:
        council = await self.repo.get_council_by_id(council_id)
        if not council:
            raise EntityNotFoundException("Council not found.")
        return CouncilResponse.model_validate(council)

    async def list_councils(
        self,
        archdiocese_id: Optional[uuid.UUID] = None,
        deanery_id: Optional[uuid.UUID] = None,
        parish_id: Optional[uuid.UUID] = None,
        council_type: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> List[CouncilResponse]:
        items = await self.repo.list_councils(
            archdiocese_id=archdiocese_id,
            deanery_id=deanery_id,
            parish_id=parish_id,
            council_type=council_type,
            is_active=is_active,
        )
        return [CouncilResponse.model_validate(c) for c in items]

    async def update_council(self, council_id: uuid.UUID, data: CouncilUpdate) -> CouncilResponse:
        council = await self.repo.get_council_by_id(council_id)
        if not council:
            raise EntityNotFoundException("Council not found.")
        updated = await self.repo.update_council(council, data)
        return CouncilResponse.model_validate(updated)

    async def delete_council(self, council_id: uuid.UUID) -> None:
        council = await self.repo.get_council_by_id(council_id)
        if not council:
            raise EntityNotFoundException("Council not found.")
        await self.repo.delete_council(council)

    # -----------------------------------------------------------------------
    # Meeting Operations
    # -----------------------------------------------------------------------

    async def create_meeting(self, data: MeetingCreate) -> MeetingResponse:
        if data.council_id:
            council = await self.repo.get_council_by_id(data.council_id)
            if not council:
                raise ValidationException("Referenced council does not exist.")
        if data.commission_id:
            commission = await self.repo.get_commission_by_id(data.commission_id)
            if not commission:
                raise ValidationException("Referenced commission does not exist.")

        meeting = await self.repo.create_meeting(data)
        return MeetingResponse.model_validate(meeting)

    async def get_meeting(self, meeting_id: uuid.UUID) -> MeetingResponse:
        meeting = await self.repo.get_meeting_by_id(meeting_id)
        if not meeting:
            raise EntityNotFoundException("Meeting not found.")
        return MeetingResponse.model_validate(meeting)

    async def list_meetings(
        self,
        council_id: Optional[uuid.UUID] = None,
        commission_id: Optional[uuid.UUID] = None,
        archdiocese_id: Optional[uuid.UUID] = None,
        deanery_id: Optional[uuid.UUID] = None,
        parish_id: Optional[uuid.UUID] = None,
        status: Optional[str] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
    ) -> List[MeetingResponse]:
        items = await self.repo.list_meetings(
            council_id=council_id,
            commission_id=commission_id,
            archdiocese_id=archdiocese_id,
            deanery_id=deanery_id,
            parish_id=parish_id,
            status=status,
            from_date=from_date,
            to_date=to_date,
        )
        return [MeetingResponse.model_validate(m) for m in items]

    async def update_meeting(self, meeting_id: uuid.UUID, data: MeetingUpdate) -> MeetingResponse:
        meeting = await self.repo.get_meeting_by_id(meeting_id)
        if not meeting:
            raise EntityNotFoundException("Meeting not found.")
        updated = await self.repo.update_meeting(meeting, data)
        return MeetingResponse.model_validate(updated)

    async def delete_meeting(self, meeting_id: uuid.UUID) -> None:
        meeting = await self.repo.get_meeting_by_id(meeting_id)
        if not meeting:
            raise EntityNotFoundException("Meeting not found.")
        await self.repo.delete_meeting(meeting)

    # -----------------------------------------------------------------------
    # Meeting Minute Operations
    # -----------------------------------------------------------------------

    async def add_minute(
        self,
        data: MeetingMinuteCreate,
        recorded_by_user_id: Optional[uuid.UUID] = None,
    ) -> MeetingMinuteResponse:
        meeting = await self.repo.get_meeting_by_id(data.meeting_id)
        if not meeting:
            raise EntityNotFoundException("Meeting not found.")
        minute = await self.repo.create_minute(data, recorded_by_user_id=recorded_by_user_id)
        return MeetingMinuteResponse.model_validate(minute)

    async def get_minute(self, minute_id: uuid.UUID) -> MeetingMinuteResponse:
        minute = await self.repo.get_minute_by_id(minute_id)
        if not minute:
            raise EntityNotFoundException("Meeting minute not found.")
        return MeetingMinuteResponse.model_validate(minute)

    async def list_minutes_for_meeting(self, meeting_id: uuid.UUID) -> List[MeetingMinuteResponse]:
        meeting = await self.repo.get_meeting_by_id(meeting_id)
        if not meeting:
            raise EntityNotFoundException("Meeting not found.")
        minutes = await self.repo.list_minutes_for_meeting(meeting_id)
        return [MeetingMinuteResponse.model_validate(m) for m in minutes]

    async def update_minute(self, minute_id: uuid.UUID, data: MeetingMinuteUpdate) -> MeetingMinuteResponse:
        minute = await self.repo.get_minute_by_id(minute_id)
        if not minute:
            raise EntityNotFoundException("Meeting minute not found.")
        updated = await self.repo.update_minute(minute, data)
        return MeetingMinuteResponse.model_validate(updated)

    async def delete_minute(self, minute_id: uuid.UUID) -> None:
        minute = await self.repo.get_minute_by_id(minute_id)
        if not minute:
            raise EntityNotFoundException("Meeting minute not found.")
        await self.repo.delete_minute(minute)
