# database.py
"""Database Configuration Engine.

Defines, configures, and exports the foundational asynchronous SQLAlchemy engine
and session factory parameters mapped precisely to enterprise-grade PostgreSQL
topological constraints.
"""

from typing import Any, Dict
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from config.base import settings

# 1. Export Declarative Synchronous / Asynchronous Connection Strings
# Main url structure used for runtime connection and Alembic programmatic access
DATABASE_URL: str = settings.database.ASYNC_URL

# 2. Advanced Performance Tuning Parameters Matrix
# Engineered for sustained concurrent workloads exceeding 100,000 users
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
        "timezone": "UTC",                  # Force deterministic database engine alignment
        "statement_timeout": str(STATEMENT_TIMEOUT_MS),
    },
    "command_timeout": 20.0,                # Network socket response threshold
}

# 5. Core Engine Instantiation Pipeline
# Configures transaction isolation levels, pool size boundaries, and proactive pre-ping connectivity health checks.
engine: AsyncEngine = create_async_engine(
    url=DATABASE_URL,
    echo=IS_ECHO_ENABLED,
    pool_size=POOL_SIZE,
    max_overflow=MAX_OVERFLOW,
    pool_recycle=POOL_RECYCLE_SECONDS,
    pool_timeout=POOL_TIMEOUT_SECONDS,
    pool_pre_ping=True,                     # Optimistic reconnection health-check assertion
    isolation_level="READ COMMITTED",      # Prevents dirty reads while maintaining low lock overhead
    connect_args=CONNECT_ARGS,
)

# 6. Global Thread-Safe Transactional Worker Session Factory
async_session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,                 # Disables aggressive data-eviction strategies on safe commits
    autoflush=False,                        # Requires explicit logical control checkpoints for optimization
)


def get_database_runtime_metadata() -> Dict[str, Any]:
    """Retrieves operational monitoring parameters mapping engine configurations.

    Returns:
        Dict[str, Any]: Key-Value state schema of database parameters.
    """
    return {
        "engine_dialect": engine.dialect.name,
        "pool_size": POOL_SIZE,
        "max_overflow": MAX_OVERFLOW,
        "pool_recycle": POOL_RECYCLE_SECONDS,
        "echo_mode": IS_ECHO_ENABLED,
        "isolation_level": "READ COMMITTED",
    }
    
