"""
Rate Limiting Configuration Module
Uses slowapi backed by Redis for distributed throttling across API workers,
with graceful in-memory fallback during testing and error-swallowing for Redis outages.
"""

import logging

from slowapi import Limiter
from slowapi.util import get_remote_address

from app.config import settings

logger = logging.getLogger("arkidi.core.limiter")

_storage_uri = "memory://" if settings.ENVIRONMENT.lower() == "testing" else settings.REDIS_URL

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=_storage_uri,
    default_limits=[],
    swallow_errors=True,
)
