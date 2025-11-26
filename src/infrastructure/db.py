"""
Database/cache helpers for the trading bot.

This module centralizes connections to MongoDB and Redis so the rest of the
codebase can reuse clients without spawning extra connections.
"""

from functools import lru_cache
import os
from typing import Optional

from pymongo import MongoClient
import redis


DEFAULT_MONGO_URI = "mongodb://localhost:27017"
DEFAULT_MONGO_DB = "hyperliquid_bot"
DEFAULT_REDIS_URL = "redis://localhost:6379/0"


def _get_env(key: str, default: str) -> str:
    value = os.getenv(key, default)
    return value.strip() if isinstance(value, str) else default


@lru_cache(maxsize=1)
def get_mongo_client() -> MongoClient:
    """
    Return a cached MongoDB client instance.

    Uses MONGO_URI env var, falling back to mongodb://localhost:27017.
    """

    mongo_uri = _get_env("MONGO_URI", DEFAULT_MONGO_URI)
    return MongoClient(mongo_uri)


@lru_cache(maxsize=1)
def get_mongo_db(name: Optional[str] = None):
    """
    Return a cached handle to the configured MongoDB database.

    Allows overriding the DB name if needed, but defaults to MONGO_DB.
    """

    db_name = name or _get_env("MONGO_DB", DEFAULT_MONGO_DB)
    return get_mongo_client()[db_name]


@lru_cache(maxsize=1)
def get_redis_client() -> redis.Redis:
    """
    Return a cached Redis client.

    Uses REDIS_URL env var, defaulting to redis://localhost:6379/0.
    """

    redis_url = _get_env("REDIS_URL", DEFAULT_REDIS_URL)
    return redis.from_url(redis_url, decode_responses=True)
