# engine.py
"""Database Engine Lifecycle Manager.

Orchestrates the active runtime lifecycle, connection pooling metrics, health checking
telemetry, and clean disposal hooks for the core asynchronous PostgreSQL database engine.
"""

import sys
import logging
from typing import Any, Dict
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy import text, exc

from config.database import (
    DATABASE_URL,
    IS_ECHO_ENABLED,
    POOL_SIZE,
    MAX_OVERFLOW,
    POOL_RECYCLE_SECONDS,
    POOL_TIMEOUT_SECONDS,
    CONNECT_ARGS,
)

logger = logging.getLogger("investment_platform.database.engine")

# Global internal tracking reference for the instantiated engine single context instance
_async_engine: AsyncEngine | None = None


def get_engine() -> AsyncEngine:
    """Initializes or retrieves the singular global production AsyncEngine instance.

    Guarantees thread-safe resource initialization and configures connection pool parameters.

    Returns:
        AsyncEngine: Configured database driver orchestration engine.
    """
    global _async_engine

    if _async_engine is None:
        try:
            _async_engine = create_async_engine(
                url=DATABASE_URL,
                echo=IS_ECHO_ENABLED,
                pool_size=POOL_SIZE,
                max_overflow=MAX_OVERFLOW,
                pool_recycle=POOL_RECYCLE_SECONDS,
                pool_timeout=POOL_TIMEOUT_SECONDS,
                pool_pre_ping=True,
                isolation_level="READ COMMITTED",
                connect_args=CONNECT_ARGS,
            )
            logger.info("Asynchronous database engine initialized successfully.")
        except Exception as error:
            sys.stderr.write(f"[CRITICAL_DATABASE_INIT_FAILURE] {error}\n")
            logger.critical(
                "Failed to build connection pool engine runtime abstraction.", exc_info=True
            )
            raise RuntimeError("Database engine subsystem initialization failure.") from error

    return _async_engine


async def dispose_engine() -> None:
    """Performs a graceful, non-blocking termination of the connection pool ecosystem.

    To be executed explicitly during system shutdown routines to prevent lingering active sockets.
    """
    global _async_engine

    if _async_engine is not None:
        logger.info("Initiating graceful teardown of database connection pool...")
        try:
            await _async_engine.dispose()
            logger.info("Database connection pool flushed and closed successfully.")
        except Exception:
            logger.error(
                "Error encountered during database engine pool disposal mapping.", exc_info=True
            )
        finally:
            _async_engine = None


async def check_database_connection() -> Dict[str, Any]:
    """Executes a low-overhead query statement to verify live connection pool health.

    Returns:
        Dict[str, Any]: Diagnostic payload mapping operational latency and connectivity flags.
    """
    current_engine = get_engine()
    diagnostic_payload: Dict[str, Any] = {
        "status": "UNHEALTHY",
        "latency_verified": False,
        "error_message": None,
    }

    try:
        async with current_engine.connect() as connection:
            await connection.execute(text("SELECT 1;"))

        diagnostic_payload["status"] = "HEALTHY"
        diagnostic_payload["latency_verified"] = True
    except exc.SQLAlchemyError as db_error:
        logger.error("Database connection health-check verification failed.", exc_info=True)
        diagnostic_payload["error_message"] = str(db_error)
    except Exception as generic_error:
        logger.critical(
            "Unexpected exception intercepted during infrastructure health-check.", exc_info=True
        )
        diagnostic_payload["error_message"] = str(generic_error)

    return diagnostic_payload
