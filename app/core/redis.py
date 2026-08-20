"""
Redis Client and Cache / Token Blacklist Service
"""
from typing import Optional
import redis.asyncio as aioredis
from app.config import settings

redis_client: Optional[aioredis.Redis] = None


async def get_redis() -> aioredis.Redis:
    """Get or create singleton async Redis client connection."""
    global redis_client
    if redis_client is None:
        redis_client = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )
    return redis_client


async def is_token_revoked(jti: str) -> bool:
    """Check whether a JWT access token ID is present in the Redis blacklist."""
    try:
        r = await get_redis()
        val = await r.get(f"revoked_token:{jti}")
        return val is not None
    except Exception:
        # If security critical mode is enabled, treat Redis outage as revoked
        return settings.SECURITY_CRITICAL_MODE


async def revoke_token(jti: str, expire_seconds: int) -> None:
    """Add a JWT token ID to the blacklist with TTL."""
    try:
        r = await get_redis()
        await r.setex(f"revoked_token:{jti}", expire_seconds, "revoked")
    except Exception:
        pass
