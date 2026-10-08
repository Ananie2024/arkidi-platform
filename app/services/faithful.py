"""
Faithful Module Business Logic Service
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    DuplicateRegistrationNumberException,
    EntityNotFoundException,
    FaithfulNotFoundException,
    ValidationException,
)
from app.models.audit_log import AuditLog
from app.repositories.faithful import FaithfulRepository
from app.schemas.faithful import (
    FaithfulCreate,
    FaithfulResponse,
    FaithfulUpdate,
    FamilyCreate,
    FamilyResponse,
    FamilyUpdate,
)
from app.utils.audit import record_audit_event
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
        await self._validate_assignments(data.parish_id, data.family_id, data.scc_id)
        faithful = await self.repo.create_faithful(data)
        audit = AuditLog(
            user_id=current_user_id,
            action="FAITHFUL_REGISTERED",
            entity_name="faithful",
            entity_id=str(faithful.id),
            details={
                "parish_id": str(faithful.parish_id),
            },
        )
        self.repo.db.add(audit)
        return FaithfulResponse.model_validate(faithful)

    async def update_faithful(
        self, faithful_id: uuid.UUID, data: FaithfulUpdate
    ) -> FaithfulResponse:
        faithful = await self.repo.get_by_id(faithful_id)
        if not faithful:
            raise FaithfulNotFoundException(str(faithful_id))
        changes = data.model_dump(exclude_unset=True)
        await self._validate_assignments(
            faithful.parish_id,
            changes.get("family_id", faithful.family_id),
            changes.get("scc_id", faithful.scc_id),
        )
        await self.repo.update_faithful(faithful, data)
        record_audit_event(
            self.repo.db,
            action="FAITHFUL_UPDATED",
            entity_name="faithful",
            entity_id=faithful.id,
            details={"changed_fields": sorted(changes)},
        )
        return FaithfulResponse.model_validate(faithful)

    async def list_families(
        self, parish_id: uuid.UUID | None = None, search: str | None = None
    ) -> list[FamilyResponse]:
        return [
            FamilyResponse.model_validate(f)
            for f in await self.repo.list_families(parish_id, search)
        ]

    async def get_family(self, family_id: uuid.UUID) -> FamilyResponse:
        family = await self.repo.get_family_by_id(family_id)
        if family is None:
            raise EntityNotFoundException("errors.family_not_found")
        return FamilyResponse.model_validate(family)

    async def list_family_members(self, family_id: uuid.UUID) -> list[FaithfulResponse]:
        return [
            FaithfulResponse.model_validate(person)
            for person in await self.repo.list_family_members(family_id)
        ]

    async def update_family(self, family_id: uuid.UUID, data: FamilyUpdate) -> FamilyResponse:
        family = await self.repo.get_family_by_id(family_id)
        if family is None:
            raise EntityNotFoundException("errors.family_not_found")
        changes = data.model_dump(exclude_unset=True)
        await self._validate_assignments(
            family.parish_id,
            None,
            changes.get("scc_id", family.scc_id),
            centrale_id=changes.get("centrale_id", family.centrale_id),
        )
        await self.repo.update_family(family, data)
        record_audit_event(
            self.repo.db,
            action="FAMILY_UPDATED",
            entity_name="family",
            entity_id=family.id,
            details={"changed_fields": sorted(changes)},
        )
        return FamilyResponse.model_validate(family)

    async def _validate_assignments(
        self,
        parish_id: uuid.UUID,
        family_id: uuid.UUID | None,
        scc_id: uuid.UUID | None,
        *,
        centrale_id: uuid.UUID | None = None,
    ) -> None:
        from app.models.parish import Centrale, SmallChristianCommunity

        if family_id:
            family = await self.repo.get_family_by_id(family_id)
            if family is None or family.parish_id != parish_id:
                raise ValidationException("Family must belong to the selected parish.")
        if scc_id:
            scc = await self.repo.db.get(SmallChristianCommunity, scc_id)
            if scc is None or scc.is_deleted or scc.centrale_id is None:
                raise ValidationException("Community must belong to the selected parish.")
            centrale = await self.repo.db.get(Centrale, scc.centrale_id)
            if centrale is None or centrale.is_deleted or centrale.parish_id != parish_id:
                raise ValidationException("Community must belong to the selected parish.")
        if centrale_id:
            centrale = await self.repo.db.get(Centrale, centrale_id)
            if centrale is None or centrale.is_deleted or centrale.parish_id != parish_id:
                raise ValidationException("Centrale must belong to the selected parish.")
            if scc_id:
                scc = await self.repo.db.get(SmallChristianCommunity, scc_id)
                if scc is None or scc.centrale_id != centrale_id:
                    raise ValidationException("Community must belong to the selected centrale.")

    async def create_family(
        self, data: FamilyCreate, current_user_id: uuid.UUID | None = None
    ) -> FamilyResponse:
        await self._validate_assignments(
            data.parish_id, None, data.scc_id, centrale_id=data.centrale_id
        )
        family = await self.repo.create_family(data)
        audit = AuditLog(
            user_id=current_user_id,
            action="FAMILY_CREATED",
            entity_name="family",
            entity_id=str(family.id),
            details={
                "parish_id": str(family.parish_id),
            },
        )
        self.repo.db.add(audit)
        return FamilyResponse.model_validate(family)
