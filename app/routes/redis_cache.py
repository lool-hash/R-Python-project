"""
Redis Cache Module
==================
Provides a simple get/set/delete interface on top of redis-py.
If Redis is not available (e.g. local dev without Docker), the functions
degrade gracefully — the app keeps working without caching.
"""

import json
from typing import Any, Optional
import redis
from app.core.config import settings
from app.logging.logger import logger

# ── Build the Redis client once ───────────────────────────────────────────────
_client: Optional[redis.Redis] = None
_checked: bool = False    # ensures we only try connecting once


def get_redis() -> Optional[redis.Redis]:
    """Return a shared Redis client, or None if Redis is unavailable."""
    global _client, _checked
    if _checked:
        return _client          # already tried — return cached result (may be None)
    _checked = True

    if not settings.REDIS_URL:
        return None

    try:
        _client = redis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            socket_connect_timeout=1,   # fail fast if Redis is not running
            socket_timeout=1,
        )
        _client.ping()          # verify connection immediately
        logger.info("Redis connected successfully at %s", settings.REDIS_URL)
    except Exception as exc:
        logger.warning("Redis unavailable — caching disabled. Reason: %s", exc)
        _client = None
    return _client


# ── Public helper functions ────────────────────────────────────────────────────

def cache_get(key: str) -> Optional[Any]:
    """
    Retrieve a cached value by key.
    Returns the Python object (list/dict) or None on miss / Redis down.
    """
    client = get_redis()
    if client is None:
        return None
    try:
        raw = client.get(key)
        if raw:
            logger.debug("Cache HIT  → %s", key)
            return json.loads(raw)
        logger.debug("Cache MISS → %s", key)
    except Exception as exc:
        logger.warning("cache_get error (%s): %s", key, exc)
    return None


def cache_set(key: str, value: Any, ttl: int = 300) -> None:
    """
    Store a value in Redis as JSON.
    ttl  – time-to-live in seconds (default: 5 minutes).
    """
    client = get_redis()
    if client is None:
        return
    try:
        client.setex(key, ttl, json.dumps(value))
        logger.debug("Cache SET  → %s  (TTL=%ds)", key, ttl)
    except Exception as exc:
        logger.warning("cache_set error (%s): %s", key, exc)


def cache_delete(key: str) -> None:
    """Remove a single key from the cache (call after updates/deletes)."""
    client = get_redis()
    if client is None:
        return
    try:
        client.delete(key)
        logger.debug("Cache DEL  → %s", key)
    except Exception as exc:
        logger.warning("cache_delete error (%s): %s", key, exc)


def cache_delete_pattern(pattern: str) -> None:
    """
    Remove all keys matching a glob pattern.
    Example: cache_delete_pattern('products:*')
    """
    client = get_redis()
    if client is None:
        return
    try:
        keys = client.keys(pattern)
        if keys:
            client.delete(*keys)
            logger.debug("Cache DEL pattern → %s (%d keys)", pattern, len(keys))
    except Exception as exc:
        logger.warning("cache_delete_pattern error (%s): %s", pattern, exc)
