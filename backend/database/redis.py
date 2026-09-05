"""
database/redis.py — Redis connection management (optional cache layer).

- Redis is an optional dependency; the application works without it
- TLS support for production
- TTL enforcement on cached data
- No long-term sensitive data storage
"""
from __future__ import annotations

import json
from typing import Any, Optional

from core import get_settings
from core.logging import get_logger

logger = get_logger(__name__)

_redis_client = None


def get_redis_client():
    global _redis_client
    settings = get_settings()

    if not settings.redis_url:
        return None

    if _redis_client is not None:
        try:
            _redis_client.ping()
            return _redis_client
        except Exception:
            logger.warning("Redis ping failed — reconnecting")
            _redis_client = None

    try:
        import redis
        _redis_client = redis.from_url(
            settings.redis_url,
            password=settings.redis_password or None,
            decode_responses=True,
            ssl=settings.redis_ssl,
            socket_timeout=5,
            socket_connect_timeout=5,
        )
        _redis_client.ping()
        logger.info("Redis connection established")
        return _redis_client
    except Exception as e:
        logger.info(f"Redis unavailable (optional): {type(e).__name__}")
        _redis_client = None
        return None


def cache_get(key: str) -> Optional[Any]:
    client = get_redis_client()
    if client is None:
        return None
    try:
        value = client.get(key)
        return json.loads(value) if value else None
    except Exception:
        return None


def cache_set(key: str, value: Any, ttl: Optional[int] = None) -> bool:
    client = get_redis_client()
    if client is None:
        return False
    try:
        settings = get_settings()
        expire = ttl or settings.redis_cache_ttl
        client.setex(key, expire, json.dumps(value, default=str))
        return True
    except Exception:
        return False


def cache_delete(key: str) -> bool:
    client = get_redis_client()
    if client is None:
        return False
    try:
        client.delete(key)
        return True
    except Exception:
        return False


def check_redis_health() -> bool:
    client = get_redis_client()
    if client is None:
        return False
    try:
        client.ping()
        return True
    except Exception:
        return False