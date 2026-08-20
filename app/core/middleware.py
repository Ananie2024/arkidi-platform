"""
Custom Application Middlewares
Logging, Correlation ID, and Internationalization (i18n) handling
"""
import time
import uuid
from typing import Callable
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from contextvars import ContextVar

from app.config import settings

# Context variable for holding active language per request
current_language_ctx: ContextVar[str] = ContextVar("current_language", default=settings.DEFAULT_LANGUAGE)
request_id_ctx: ContextVar[str] = ContextVar("request_id", default="")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Logs incoming HTTP requests, assigns correlation IDs, and measures duration."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        req_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request_id_ctx.set(req_id)

        start_time = time.time()
        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000

        response.headers["X-Request-ID"] = req_id
        response.headers["X-Process-Time-Ms"] = f"{process_time:.2f}"
        return response


class LanguageMiddleware(BaseHTTPMiddleware):
    """Detects and stores language preference from Accept-Language header or query param."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        lang = request.query_params.get("lang")
        if not lang:
            accept_lang = request.headers.get("Accept-Language", "")
            if accept_lang:
                # Basic parsing for 'fr', 'rw', 'en'
                primary_lang = accept_lang.split(",")[0].split(";")[0].strip()[:2].lower()
                if primary_lang in settings.SUPPORTED_LANGUAGES:
                    lang = primary_lang

        if not lang or lang not in settings.SUPPORTED_LANGUAGES:
            lang = settings.DEFAULT_LANGUAGE

        current_language_ctx.set(lang)
        response = await call_next(request)
        response.headers["Content-Language"] = lang
        return response
