"""Public aggregate statistics and ecclesiastical hierarchy."""

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.models.deanery import Archdiocese, Deanery
from app.models.faithful import CanonicalStatus, Faithful
from app.models.parish import Parish
from app.models.priest import ClergyStatus, ClergyType, Priest
from app.schemas.public import (
    PublicDeaneryNode,
    PublicOrganigram,
    PublicOverview,
    PublicStatistics,
)
from app.utils.response import ApiResponse

router = APIRouter(prefix="/public", tags=["Public Information"])


@router.get("/overview", response_model=ApiResponse[PublicOverview])
async def get_public_overview(db: AsyncSession = Depends(get_db)):
    """Return public totals and names in the diocesan hierarchy.

    The response intentionally excludes individual people, contact details,
    parish coordinates, and internal record identifiers.
    """
    archdiocese = await db.scalar(
        select(Archdiocese).order_by(Archdiocese.created_at).limit(1)
    )

    parish_join = and_(
        Parish.deanery_id == Deanery.id,
        Parish.is_deleted.is_(False),
    )
    hierarchy_query = (
        select(Deanery.id, Deanery.name, Parish.name)
        .outerjoin(Parish, parish_join)
        .where(Deanery.is_deleted.is_(False))
        .order_by(Deanery.name, Parish.name)
    )
    if archdiocese is not None:
        hierarchy_query = hierarchy_query.where(Deanery.archdiocese_id == archdiocese.id)

    hierarchy_rows = (await db.execute(hierarchy_query)).all()
    deanery_parishes: dict[uuid.UUID, tuple[str, list[str]]] = {}
    for deanery_id, deanery_name, parish_name in hierarchy_rows:
        parishes = deanery_parishes.setdefault(deanery_id, (deanery_name, []))[1]
        if parish_name is not None:
            parishes.append(parish_name)

    parish_ids = (
        select(Parish.id)
        .join(Deanery, Deanery.id == Parish.deanery_id)
        .where(Parish.is_deleted.is_(False), Deanery.is_deleted.is_(False))
    )
    if archdiocese is not None:
        parish_ids = parish_ids.where(Deanery.archdiocese_id == archdiocese.id)

    active_priests = await db.scalar(
        select(func.count(Priest.id)).where(
            Priest.is_deleted.is_(False),
            Priest.status == ClergyStatus.ACTIVE_DUTY,
            Priest.clergy_type.in_(
                [ClergyType.DIOCESAN_PRIEST, ClergyType.RELIGIOUS_PRIEST]
            ),
            or_(Priest.current_parish_id.in_(parish_ids), Priest.current_parish_id.is_(None)),
        )
    )
    faithful_query = (
        select(func.count(Faithful.id))
        .join(Parish, Parish.id == Faithful.parish_id)
        .join(Deanery, Deanery.id == Parish.deanery_id)
        .where(
            Faithful.is_deleted.is_(False),
            Faithful.canonical_status != CanonicalStatus.DECEASED,
            Parish.is_deleted.is_(False),
            Deanery.is_deleted.is_(False),
        )
    )
    if archdiocese is not None:
        faithful_query = faithful_query.where(Deanery.archdiocese_id == archdiocese.id)
    registered_faithful = await db.scalar(faithful_query)

    deaneries = [
        PublicDeaneryNode(name=name, parishes=parishes)
        for name, parishes in deanery_parishes.values()
    ]
    parish_count = sum(len(item.parishes) for item in deaneries)
    overview = PublicOverview(
        statistics=PublicStatistics(
            deaneries=len(deaneries),
            parishes=parish_count,
            active_priests=active_priests or 0,
            registered_faithful=registered_faithful or 0,
        ),
        organigram=PublicOrganigram(
            name=archdiocese.name if archdiocese else "Archdiocese of Kigali",
            deaneries=deaneries,
        ),
    )
    return ApiResponse.ok(data=overview)
