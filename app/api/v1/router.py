"""
API Version 1 Router Aggregator
Combines all domain module routers into a unified endpoint registry
"""
from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.deaneries import router as deanery_router
from app.api.v1.parishes import router as parish_router
from app.api.v1.faithful import router as faithful_router
from app.api.v1.sacraments import router as sacraments_router
from app.api.v1.clergy import router as clergy_router
from app.api.v1.liturgy import router as liturgy_router
from app.api.v1.finance import router as finance_router
from app.api.v1.ministries import router as ministries_router
from app.api.v1.land import router as land_router
from app.api.v1.archive import router as archive_router
from app.api.v1.statistics import router as statistics_router

api_v1_router = APIRouter()

# Register domain routers
api_v1_router.include_router(auth_router)
api_v1_router.include_router(deanery_router)
api_v1_router.include_router(parish_router)
api_v1_router.include_router(faithful_router)
api_v1_router.include_router(sacraments_router)
api_v1_router.include_router(clergy_router)
api_v1_router.include_router(liturgy_router)
api_v1_router.include_router(finance_router)
api_v1_router.include_router(ministries_router)
api_v1_router.include_router(land_router)
api_v1_router.include_router(archive_router)
api_v1_router.include_router(statistics_router)
