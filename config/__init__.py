"""Configuration module initialization."""

from config.base import settings

BOT_TOKEN = settings.bot.TOKEN
BOT_USERNAME = settings.bot.USERNAME
REDIS_HOST = settings.redis.HOST
REDIS_PORT = settings.redis.PORT
REDIS_PASSWORD = settings.redis.PASSWORD
REDIS_DB = settings.redis.DB
MAINTENANCE_MODE = settings.flags.DEBUG

__all__ = [
    "settings",
    "BOT_TOKEN",
    "BOT_USERNAME",
    "REDIS_HOST",
    "REDIS_PORT",
    "REDIS_PASSWORD",
    "REDIS_DB",
    "MAINTENANCE_MODE",
]
