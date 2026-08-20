"""
Parish Module Business Logic Service — Parish, Centrale & Small Christian Communities.
"""
import uuid
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.parish import ParishRepository
from app.schemas.parish import (
    ParishCreate,
    ParishResponse,
    CentraleCreate,
    CentraleResponse,
    SCCCreate,
    SCCResponse,
)
from app.core.exceptions import ParishNotFoundException


class ParishService:
    def __init__(self, db: AsyncSession):
        self.repo = ParishRepository(db)

    async def get_parishes(self, deanery_id: Optional[uuid.UUID] = None) -> List[ParishResponse]:
        parishes = await self.repo.list_parishes(deanery_id)
        return [ParishResponse.model_validate(p) for p in parishes]

    async def get_parish_by_id(self, parish_id: uuid.UUID) -> ParishResponse:
        parish = await self.repo.get_parish(parish_id)
        if not parish:
            raise ParishNotFoundException(str(parish_id))
        return ParishResponse.model_validate(parish)

    async def create_parish(self, data: ParishCreate) -> ParishResponse:
        parish = await self.repo.create_parish(data)
        return ParishResponse.model_validate(parish)

    async def get_centrales(self, parish_id: uuid.UUID) -> List[CentraleResponse]:
        centrales = await self.repo.list_centrales(parish_id)
        return [CentraleResponse.model_validate(c) for c in centrales]

    async def create_centrale(self, data: CentraleCreate) -> CentraleResponse:
        centrale = await self.repo.create_centrale(data)
        return CentraleResponse.model_validate(centrale)

    async def get_scc_list(self, centrale_id: uuid.UUID) -> List[SCCResponse]:
        sccs = await self.repo.list_scc(centrale_id)
        return [SCCResponse.model_validate(s) for s in sccs]

    async def create_scc(self, data: SCCCreate) -> SCCResponse:
        scc = await self.repo.create_scc(data)
        return SCCResponse.model_validate(scc)