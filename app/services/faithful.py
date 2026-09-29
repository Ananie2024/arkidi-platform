"""
Faithful Module Business Logic Service
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import DuplicateRegistrationNumberException, FaithfulNotFoundException
from app.models.audit_log import AuditLog
from app.repositories.faithful import FaithfulRepository
from app.schemas.faithful import (
    FaithfulCreate,
    FaithfulResponse,
    FamilyCreate,
    FamilyResponse,
)
from app.utils.pagination import PaginatedResponse, PaginationParams


class FaithfulService:
    def __init__(self, db: AsyncSession):
        self.repo = FaithfulRepository(db)

    async def get_faithful_by_id(self, faithful_id: uuid.UUID) -> FaithfulResponse:
        faithful = await self.repo.get_by_id(faithful_id)
        if not faithful:
            raise FaithfulNotFoundException(str(faithful_id))
        return FaithfulResponse.model_validate(faithful)

    async def list_faithful(
        self,
        parish_id: uuid.UUID | None,
        search: str | None,
        params: PaginationParams,
    ) -> PaginatedResponse[FaithfulResponse]:
        items, total = await self.repo.list_faithful(
            parish_id=parish_id,
            search=search,
            skip=params.offset,
            limit=params.page_size,
        )
        return PaginatedResponse.create(
            items=[FaithfulResponse.model_validate(f) for f in items],
            total=total,
            params=params,
        )

    async def create_faithful(
        self, data: FaithfulCreate, current_user_id: uuid.UUID | None = None
    ) -> FaithfulResponse:
        existing = await self.repo.get_by_registration_number(data.registration_number)
        if existing:
            raise DuplicateRegistrationNumberException(data.registration_number)
        faithful = await self.repo.create_faithful(data)
        audit = AuditLog(
            user_id=current_user_id,
            action="FAITHFUL_REGISTERED",
            entity_name="faithful",
            entity_id=str(faithful.id),
            details={
                "registration_number": faithful.registration_number,
                "first_name": faithful.first_name,
                "last_name": faithful.last_name,
                "parish_id": str(faithful.parish_id),
            },
        )
        self.repo.db.add(audit)
        return FaithfulResponse.model_validate(faithful)

    async def create_family(
        self, data: FamilyCreate, current_user_id: uuid.UUID | None = None
    ) -> FamilyResponse:
        family = await self.repo.create_family(data)
        audit = AuditLog(
            user_id=current_user_id,
            action="FAMILY_CREATED",
            entity_name="family",
            entity_id=str(family.id),
            details={
                "family_name": family.family_name,
                "parish_id": str(family.parish_id),
            },
        )
        self.repo.db.add(audit)
        return FamilyResponse.model_validate(family)

