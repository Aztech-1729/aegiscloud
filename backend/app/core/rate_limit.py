import time
from typing import Optional
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import redis.asyncio as redis

from app.core.config import settings

redis_client: Optional[redis.Redis] = None


async def get_redis() -> redis.Redis:
    global redis_client
    if redis_client is None:
        redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    return redis_client


async def check_rate_limit(request: Request, limit: int = 60, window: int = 60) -> None:
    r = await get_redis()
    client_ip = request.client.host if request.client else "unknown"
    key = f"rate_limit:{client_ip}:{request.url.path}"

    current = await r.incr(key)
    if current == 1:
        await r.expire(key, window)

    if current > limit:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please try again later.",
            headers={"Retry-After": str(window)},
        )


async def store_session(user_id: str, token: str, device_info: str = "") -> None:
    r = await get_redis()
    await r.setex(
        f"session:{token}",
        settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        f"{user_id}:{device_info}",
    )


async def invalidate_session(token: str) -> None:
    r = await get_redis()
    await r.delete(f"session:{token}")


async def publish_event(channel: str, data: dict) -> None:
    r = await get_redis()
    import json
    await r.publish(channel, json.dumps(data))
