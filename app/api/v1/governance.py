"""
Governance Module FastAPI Endpoints
Commissions, Councils, Meetings, and Meeting Minutes
"""
import uuid
from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, require_roles
from app.models.enums import UserRole
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
    MeetingMinuteBase,
    MeetingMinuteCreate,
    MeetingMinuteUpdate,
    MeetingMinuteResponse,
)
from app.services.governance import GovernanceService
from app.utils.response import ApiResponse

router = APIRouter(prefix="/governance", tags=["Governance & Consultative Bodies"])


# ---------------------------------------------------------------------------
# Commission Endpoints
# ---------------------------------------------------------------------------

@router.post(
    "/commissions",
    response_model=ApiResponse[CommissionResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_commission(
    data: CommissionCreate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_roles([UserRole.SUPER_ADMIN, UserRole.CHANCELLOR, UserRole.PARISH_PRIEST])),
):
    """Create a new pastoral commission."""
    service = GovernanceService(db)
    created = await service.create_commission(data)
    return ApiResponse.ok(data=created, message="success.commission_created")


@router.get("/commissions", response_model=ApiResponse[List[CommissionResponse]])
async def list_commissions(
    archdiocese_id: Optional[uuid.UUID] = Query(default=None),
    deanery_id: Optional[uuid.UUID] = Query(default=None),
    parish_id: Optional[uuid.UUID] = Query(default=None),
    category: Optional[str] = Query(default=None),
    is_active: Optional[bool] = Query(default=None),
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_roles([UserRole.READ_ONLY_AUDITOR])),
):
    """List commissions with optional filters."""
    service = GovernanceService(db)
    items = await service.list_commissions(
        archdiocese_id=archdiocese_id,
        deanery_id=deanery_id,
        parish_id=parish_id,
        category=category,
        is_active=is_active,
    )
    return ApiResponse.ok(data=items)


@router.get("/commissions/{commission_id}", response_model=ApiResponse[CommissionResponse])
async def get_commission(
    commission_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_roles([UserRole.READ_ONLY_AUDITOR])),
):
    """Get single commission detail."""
    service = GovernanceService(db)
    item = await service.get_commission(commission_id)
    return ApiResponse.ok(data=item)


@router.put("/commissions/{commission_id}", response_model=ApiResponse[CommissionResponse])
async def update_commission(
    commission_id: uuid.UUID,
    data: CommissionUpdate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_roles([UserRole.SUPER_ADMIN, UserRole.CHANCELLOR, UserRole.PARISH_PRIEST])),
):
    """Update commission details."""
    service = GovernanceService(db)
    updated = await service.update_commission(commission_id, data)
    return ApiResponse.ok(data=updated, message="success.commission_updated")


@router.delete("/commissions/{commission_id}", response_model=ApiResponse[dict])
async def delete_commission(
    commission_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_roles([UserRole.SUPER_ADMIN, UserRole.CHANCELLOR, UserRole.PARISH_PRIEST])),
):
    """Soft delete a commission."""
    service = GovernanceService(db)
    await service.delete_commission(commission_id)
    return ApiResponse.ok(message="success.commission_deleted", data={"deleted": True})


# ---------------------------------------------------------------------------
# Council Endpoints
# ---------------------------------------------------------------------------

@router.post(
    "/councils",
    response_model=ApiResponse[CouncilResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_council(
    data: CouncilCreate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_roles([UserRole.SUPER_ADMIN, UserRole.CHANCELLOR, UserRole.PARISH_PRIEST])),
):
    """Create a new diocesan or parish consultative council."""
    service = GovernanceService(db)
    created = await service.create_council(data)
    return ApiResponse.ok(data=created, message="success.council_created")


@router.get("/councils", response_model=ApiResponse[List[CouncilResponse]])
async def list_councils(
    archdiocese_id: Optional[uuid.UUID] = Query(default=None),
    deanery_id: Optional[uuid.UUID] = Query(default=None),
    parish_id: Optional[uuid.UUID] = Query(default=None),
    council_type: Optional[str] = Query(default=None),
    is_active: Optional[bool] = Query(default=None),
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_roles([UserRole.READ_ONLY_AUDITOR])),
):
    """List councils with optional filters."""
    service = GovernanceService(db)
    items = await service.list_councils(
        archdiocese_id=archdiocese_id,
        deanery_id=deanery_id,
        parish_id=parish_id,
        council_type=council_type,
        is_active=is_active,
    )
    return ApiResponse.ok(data=items)


@router.get("/councils/{council_id}", response_model=ApiResponse[CouncilResponse])
async def get_council(
    council_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_roles([UserRole.READ_ONLY_AUDITOR])),
):
    """Get single council detail."""
    service = GovernanceService(db)
    item = await service.get_council(council_id)
    return ApiResponse.ok(data=item)


@router.put("/councils/{council_id}", response_model=ApiResponse[CouncilResponse])
async def update_council(
    council_id: uuid.UUID,
    data: CouncilUpdate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_roles([UserRole.SUPER_ADMIN, UserRole.CHANCELLOR, UserRole.PARISH_PRIEST])),
):
    """Update council details."""
    service = GovernanceService(db)
    updated = await service.update_council(council_id, data)
    return ApiResponse.ok(data=updated, message="success.council_updated")


@router.delete("/councils/{council_id}", response_model=ApiResponse[dict])
async def delete_council(
    council_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_roles([UserRole.SUPER_ADMIN, UserRole.CHANCELLOR, UserRole.PARISH_PRIEST])),
):
    """Soft delete a council."""
    service = GovernanceService(db)
    await service.delete_council(council_id)
    return ApiResponse.ok(message="success.council_deleted", data={"deleted": True})


# ---------------------------------------------------------------------------
# Meeting Endpoints
# ---------------------------------------------------------------------------

@router.post(
    "/meetings",
    response_model=ApiResponse[MeetingResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_meeting(
    data: MeetingCreate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_roles([UserRole.PARISH_SECRETARY, UserRole.MINISTRY_LEADER])),
):
    """Schedule a new council or commission meeting."""
    service = GovernanceService(db)
    created = await service.create_meeting(data)
    return ApiResponse.ok(data=created, message="success.meeting_created")


@router.get("/meetings", response_model=ApiResponse[List[MeetingResponse]])
async def list_meetings(
    council_id: Optional[uuid.UUID] = Query(default=None),
    commission_id: Optional[uuid.UUID] = Query(default=None),
    archdiocese_id: Optional[uuid.UUID] = Query(default=None),
    deanery_id: Optional[uuid.UUID] = Query(default=None),
    parish_id: Optional[uuid.UUID] = Query(default=None),
    meeting_status: Optional[str] = Query(default=None, alias="status"),
    from_date: Optional[date] = Query(default=None),
    to_date: Optional[date] = Query(default=None),
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_roles([UserRole.READ_ONLY_AUDITOR])),
):
    """List meetings with comprehensive filters."""
    service = GovernanceService(db)
    items = await service.list_meetings(
        council_id=council_id,
        commission_id=commission_id,
        archdiocese_id=archdiocese_id,
        deanery_id=deanery_id,
        parish_id=parish_id,
        status=meeting_status,
        from_date=from_date,
        to_date=to_date,
    )
    return ApiResponse.ok(data=items)


@router.get("/meetings/{meeting_id}", response_model=ApiResponse[MeetingResponse])
async def get_meeting(
    meeting_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_roles([UserRole.READ_ONLY_AUDITOR])),
):
    """Get single meeting detail."""
    service = GovernanceService(db)
    item = await service.get_meeting(meeting_id)
    return ApiResponse.ok(data=item)


@router.put("/meetings/{meeting_id}", response_model=ApiResponse[MeetingResponse])
async def update_meeting(
    meeting_id: uuid.UUID,
    data: MeetingUpdate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_roles([UserRole.PARISH_SECRETARY, UserRole.MINISTRY_LEADER])),
):
    """Update meeting agenda, status, decisions, or date/time."""
    service = GovernanceService(db)
    updated = await service.update_meeting(meeting_id, data)
    return ApiResponse.ok(data=updated, message="success.meeting_updated")


@router.delete("/meetings/{meeting_id}", response_model=ApiResponse[dict])
async def delete_meeting(
    meeting_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_roles([UserRole.PARISH_SECRETARY, UserRole.PARISH_PRIEST])),
):
    """Soft delete a meeting."""
    service = GovernanceService(db)
    await service.delete_meeting(meeting_id)
    return ApiResponse.ok(message="success.meeting_deleted", data={"deleted": True})


# ---------------------------------------------------------------------------
# Meeting Minute Endpoints
# ---------------------------------------------------------------------------

@router.post(
    "/meetings/{meeting_id}/minutes",
    response_model=ApiResponse[MeetingMinuteResponse],
    status_code=status.HTTP_201_CREATED,
)
async def add_meeting_minute(
    meeting_id: uuid.UUID,
    data: MeetingMinuteBase,
    db: AsyncSession = Depends(get_db),
    user_payload: dict = Depends(require_roles([UserRole.PARISH_SECRETARY, UserRole.MINISTRY_LEADER])),
):
    """Attach official minutes or report to a meeting."""
    user_id = uuid.UUID(user_payload["sub"]) if user_payload and "sub" in user_payload else None
    create_dto = MeetingMinuteCreate(
        meeting_id=meeting_id,
        title=data.title,
        content=data.content,
        document_path=data.document_path,
    )
    service = GovernanceService(db)
    created = await service.add_minute(create_dto, recorded_by_user_id=user_id)
    return ApiResponse.ok(data=created, message="success.minute_created")


@router.get("/meetings/{meeting_id}/minutes", response_model=ApiResponse[List[MeetingMinuteResponse]])
async def list_meeting_minutes(
    meeting_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_roles([UserRole.READ_ONLY_AUDITOR])),
):
    """List all minutes/decision records attached to a meeting."""
    service = GovernanceService(db)
    items = await service.list_minutes_for_meeting(meeting_id)
    return ApiResponse.ok(data=items)


@router.get("/minutes/{minute_id}", response_model=ApiResponse[MeetingMinuteResponse])
async def get_minute(
    minute_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_roles([UserRole.READ_ONLY_AUDITOR])),
):
    """Get single meeting minute record."""
    service = GovernanceService(db)
    item = await service.get_minute(minute_id)
    return ApiResponse.ok(data=item)


@router.put("/minutes/{minute_id}", response_model=ApiResponse[MeetingMinuteResponse])
async def update_minute(
    minute_id: uuid.UUID,
    data: MeetingMinuteUpdate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_roles([UserRole.PARISH_SECRETARY, UserRole.MINISTRY_LEADER])),
):
    """Update meeting minute content or document reference."""
    service = GovernanceService(db)
    updated = await service.update_minute(minute_id, data)
    return ApiResponse.ok(data=updated, message="success.minute_updated")


@router.delete("/minutes/{minute_id}", response_model=ApiResponse[dict])
async def delete_minute(
    minute_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_roles([UserRole.PARISH_SECRETARY, UserRole.PARISH_PRIEST])),
):
    """Delete a meeting minute record."""
    service = GovernanceService(db)
    await service.delete_minute(minute_id)
    return ApiResponse.ok(message="success.minute_deleted", data={"deleted": True})
