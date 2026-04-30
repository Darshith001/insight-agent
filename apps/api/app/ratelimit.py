"""Per-user sliding-window rate limit on Redis. Gracefully disabled if Redis is not running."""
from __future__ import annotations
import time
import redis
from fastapi import HTTPException, status
from services.common.config import get_settings


def _get_redis():
    try:
        r = redis.Redis.from_url(get_settings().redis_url, decode_responses=True, socket_connect_timeout=1)
        r.ping()
        return r
    except Exception:
        return None


def check(user: str, limit: int = 30, window_s: int = 60) -> None:
    r = _get_redis()
    if r is None:
        return   # rate limiting disabled — skip silently
    try:
        now = time.time()
        key = f"rl:{user}"
        pipe = r.pipeline()
        pipe.zremrangebyscore(key, 0, now - window_s)
        pipe.zcard(key)
        pipe.zadd(key, {str(now): now})
        pipe.expire(key, window_s)
        _, count, _, _ = pipe.execute()
        if count >= limit:
            raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, "rate limit exceeded")
    except HTTPException:
        raise
    except Exception:
        pass   # Redis error — allow request through
