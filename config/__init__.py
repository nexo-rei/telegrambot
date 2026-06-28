"""Configuration module initialization."""

from config.base import settings

BOT_TOKEN = settings.bot.TOKEN
BOT_USERNAME = settings.bot.USERNAME
REDIS_HOST = settings.redis.HOST
REDIS_PORT = settings.redis.PORT
REDIS_PASSWORD = settings.redis.PASSWORD
REDIS_DB = settings.redis.DB

# BUG FIX: MAINTENANCE_MODE was incorrectly set to DEBUG flag.
# DEBUG mode is not maintenance mode. Added a proper default (False).
MAINTENANCE_MODE: bool = False

# BUG FIX: main_worker.py imports REDIS_URL and DATABASE_URL from config,
# but these were never exported here. Added them.
def _build_redis_url() -> str:
    auth = f":{settings.redis.PASSWORD}@" if settings.redis.PASSWORD else ""
    return f"redis://{auth}{settings.redis.HOST}:{settings.redis.PORT}/{settings.redis.DB}"

REDIS_URL: str = _build_redis_url()
DATABASE_URL: str = settings.database.ASYNC_URL

__all__ = [
    "settings",
    "BOT_TOKEN",
    "BOT_USERNAME",
    "REDIS_HOST",
    "REDIS_PORT",
    "REDIS_PASSWORD",
    "REDIS_DB",
    "MAINTENANCE_MODE",
    "REDIS_URL",
    "DATABASE_URL",
]
