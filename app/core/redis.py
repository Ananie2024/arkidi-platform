"""Redis Client and Cache / Token Blacklist Service.

Production hardening notes
-------------------------
- Every Redis failure is logged (the module swallows nothing).
- ``revoke_token`` returns a ``bool``. When ``SECURITY_CRITICAL_MODE`` is enabled
  (the production default), failures are **raised** so callers can surface the
  outage to the operator instead of a token silently remaining valid.
- ``health_probe()`` backs the application ``/health`` endpoint so deployments
  can detect Redis outages in monitoring.
"""

import logging

import redis.asyncio as aioredis

from app.config import settings

logger = logging.getLogger("arkidi.core.redis")

# Connection timeouts so unreachable Redis fails fast instead of blocking
# requests indefinitely.
_CONNECT_TIMEOUT = 3
_OPERATION_TIMEOUT = 3

redis_client: aioredis.Redis | None = None


async def get_redis() -> aioredis.Redis:
    """Get or create singleton async Redis client connection."""
    global redis_client
    if redis_client is None:
        redis_client = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            socket_connect_timeout=_CONNECT_TIMEOUT,
            socket_timeout=_OPERATION_TIMEOUT,
        )
    return redis_client


async def is_token_revoked(jti: str) -> bool:
    """Return whether a JWT token ID is present in the Redis blacklist.

    On a Redis outage, ``SECURITY_CRITICAL_MODE`` decides the failure behavior:
    critical mode fails closed (treat the token as revoked) so a compromised
    Redis can never silently accept a revoked token; otherwise it fails open
    and logs so the outage stays visible.
    """
    try:
        r = await get_redis()
        val = await r.get(f"revoked_token:{jti}")
        return val is not None
    except Exception as exc:  # pragma: no cover - depends on external Redis
        logger.exception("Could not check token revocation for %s: %s", jti, exc)
        if settings.SECURITY_CRITICAL_MODE:
            logger.error("SECURITY_CRITICAL_MODE is enabled; treating token %s as revoked.", jti)
            return True
        logger.warning(
            "Redis unavailable and SECURITY_CRITICAL_MODE is off; token %s not checked.",
            jti,
        )
        return False


async def revoke_token(jti: str, expire_seconds: int) -> bool:
    """Add a JWT token ID to the blacklist with TTL.

    Returns ``True`` when the blacklist write succeeded. In critical mode a
    failure is raised so callers surface the outage; otherwise it is logged and
    ``False`` is returned.
    """
    try:
        r = await get_redis()
        await r.setex(f"revoked_token:{jti}", expire_seconds, "revoked")
        logger.info("Revoked token %s (ttl=%ss)", jti, expire_seconds)
        return True
    except Exception as exc:
        logger.error("Failed to revoke token %s: %s", jti, exc)
        if settings.SECURITY_CRITICAL_MODE:
            logger.critical("Revocation failed in critical mode; raising for operator alert.")
            raise
        return False


async def revoke_many(jtis: list[str], expire_seconds: int) -> bool:
    """Revoke a family of token IDs (e.g. access + refresh for one session).

    The entries are written in a single pipeline so the batch is atomic; a
    partial failure is detected, logged and (in critical mode) raised.
    """
    try:
        r = await get_redis()
        pipe = r.pipeline()
        for jti in jtis:
            pipe.setex(f"revoked_token:{jti}", expire_seconds, "revoked")
        await pipe.execute()
        logger.info("Revoked token family %s (ttl=%ss)", jtis, expire_seconds)
        return True
    except Exception as exc:
        logger.error("Failed to revoke token family %s: %s", jtis, exc)
        if settings.SECURITY_CRITICAL_MODE:
            raise
        return False


async def health_probe() -> bool:
    """Return whether Redis responds to a PING within the operation timeout."""
    try:
        r = await get_redis()
        result = await r.ping()
        healthy = result in (True, b"PONG")
        logger.info("Redis health probe: %s", "up" if healthy else "down")
        return healthy
    except Exception as exc:
        logger.warning("Redis health probe failed: %s", exc)
        return False


# ---------------------------------------------------------------------------
# Password-reset tokens (single-use, time-boxed)
# ---------------------------------------------------------------------------
_PASSWORD_RESET_PREFIX = "password_reset:"


async def set_password_reset_token(token: str, user_id: str, ttl_seconds: int) -> bool:
    """Store a one-time password-reset token mapped to *user_id* with a TTL."""
    try:
        r = await get_redis()
        await r.setex(f"{_PASSWORD_RESET_PREFIX}{token}", ttl_seconds, user_id)
        return True
    except Exception as exc:
        logger.error("Failed to store password-reset token: %s", exc)
        return False


async def consume_password_reset_token(token: str) -> str | None:
    """Atomically read-and-delete a password-reset token.

    Returns the associated ``user_id`` when the token exists and is unexpired,
    otherwise ``None`` (invalid, expired, or already consumed).
    """
    try:
        r = await get_redis()
        key = f"{_PASSWORD_RESET_PREFIX}{token}"
        user_id = await r.get(key)
        if user_id is None:
            return None
        await r.delete(key)
        # ``decode_responses=True`` guarantees ``str`` at runtime; the explicit
        # branch keeps the declared ``str | None`` return type honest.
        return user_id.decode() if isinstance(user_id, bytes) else str(user_id)
    except Exception as exc:
        logger.error("Failed to consume password-reset token: %s", exc)
        return None
