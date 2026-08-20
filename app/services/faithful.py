"""
Faithful Module Business Logic Service
"""
import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.faithful import FaithfulRepository
from app.schemas.faithful import (
    FaithfulCreate,
    FaithfulResponse,
    FamilyCreate,
    FamilyResponse,
)
from app.core.exceptions import FaithfulNotFoundException, DuplicateRegistrationNumberException
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
        parish_id: Optional[uuid.UUID],
        search: Optional[str],
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

    async def create_faithful(self, data: FaithfulCreate) -> FaithfulResponse:
        existing = await self.repo.get_by_registration_number(data.registration_number)
        if existing:
            raise DuplicateRegistrationNumberException(data.registration_number)
        faithful = await self.repo.create_faithful(data)
        return FaithfulResponse.model_validate(faithful)

    async def create_family(self, data: FamilyCreate) -> FamilyResponse:
        family = await self.repo.create_family(data)
        return FamilyResponse.model_validate(family)
