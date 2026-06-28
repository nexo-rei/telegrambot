# database.py
"""Database Configuration Engine.

Defines, configures, and exports the foundational asynchronous SQLAlchemy engine
and session factory parameters mapped precisely to enterprise-grade PostgreSQL
topological constraints.

BUG FIX: The original file instantiated create_async_engine() and async_sessionmaker()
at module import time. This caused:
  1. A double-engine problem (config/database.py AND database/engine.py both created engines)
  2. A crash if env vars were not yet loaded when this module was first imported
  3. A circular initialization issue since session.py also imported get_engine()

This file now exports only configuration constants. The actual engine and session
factory are managed exclusively by database/engine.py and database/session.py.
"""

from typing import Any, Dict
from config.base import settings

# 1. Export Declarative Synchronous / Asynchronous Connection Strings
DATABASE_URL: str = settings.database.ASYNC_URL

# 2. Advanced Performance Tuning Parameters Matrix
POOL_SIZE: int = 20
MAX_OVERFLOW: int = 10
POOL_RECYCLE_SECONDS: int = 1800
POOL_TIMEOUT_SECONDS: float = 30.0
STATEMENT_TIMEOUT_MS: int = 15000  # 15-second safety ceiling limit

# 3. Execution Flags Configuration Matrix
IS_ECHO_ENABLED: bool = settings.flags.DEBUG

# 4. Connection Pool Execution Arguments Mapping
CONNECT_ARGS: Dict[str, Any] = {
    "server_settings": {
        "timezone": "UTC",
        "statement_timeout": str(STATEMENT_TIMEOUT_MS),
    },
    "command_timeout": 20.0,
}


def get_database_runtime_metadata() -> Dict[str, Any]:
    """Retrieves operational monitoring parameters mapping engine configurations.

    Returns:
        Dict[str, Any]: Key-Value state schema of database parameters.
    """
    return {
        "database_url_host": settings.database.HOST,
        "pool_size": POOL_SIZE,
        "max_overflow": MAX_OVERFLOW,
        "pool_recycle": POOL_RECYCLE_SECONDS,
        "echo_mode": IS_ECHO_ENABLED,
        "isolation_level": "READ COMMITTED",
    }
