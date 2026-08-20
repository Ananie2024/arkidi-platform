"""
Arkidi Platform - FastAPI Application Entrypoint
Archdiocese of Kigali Digital Archive, Parish Management & Statistical System
"""
import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.core.logging import setup_logging
from app.core.middleware import LanguageMiddleware, RequestLoggingMiddleware
from app.core.exceptions import setup_exception_handlers
from app.api.v1.router import api_v1_router

# Initialize structured logging
logger = setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager for startup and shutdown hooks."""
    logger.info("Starting up Arkidi Platform API...", extra={"version": settings.APP_VERSION})
    # Ensure storage directories exist
    os.makedirs(settings.FILE_STORAGE_PATH, exist_ok=True)
    os.makedirs(settings.BACKUP_BASE_PATH, exist_ok=True)
    os.makedirs(os.path.dirname(settings.LOG_FILE_PATH), exist_ok=True)
    yield
    logger.info("Shutting down Arkidi Platform API...")


def create_application() -> FastAPI:
    """Factory to instantiate and configure the FastAPI application."""
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=(
            "Enterprise modular monolith backend for the Archdiocese of Kigali "
            "(Parish Management, Sacraments, Land Intelligence GIS & Digital Archive)."
        ),
        docs_url="/docs",
        redoc="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # --------------------------------------------------------------------------
    # Middleware
    # --------------------------------------------------------------------------
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(LanguageMiddleware)

    # --------------------------------------------------------------------------
    # Exception Handlers
    # --------------------------------------------------------------------------
    setup_exception_handlers(app)

    # --------------------------------------------------------------------------
    # Static Files & Storage Mount
    # --------------------------------------------------------------------------
    if os.path.exists(settings.FILE_STORAGE_PATH):
        app.mount("/static", StaticFiles(directory=settings.FILE_STORAGE_PATH), name="static")

    # --------------------------------------------------------------------------
    # API Routers
    # --------------------------------------------------------------------------
    app.include_router(api_v1_router, prefix="/api/v1")

    @app.get("/health", tags=["System"])
    async def health_check():
        """Root health check endpoint."""
        return {
            "status": "healthy",
            "app": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
        }

    return app


app = create_application()