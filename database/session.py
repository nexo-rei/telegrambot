# session.py
"""Database Session Factory and Transaction Lifecycle Manager.

Establishes, isolates, and manages the execution lifecycles of asynchronous 
PostgreSQL database connections. Implements safe contextual transaction scopes,
fail-safe programmatic rollbacks, and clean dependency injection context targets.
"""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any, Optional
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
)
from sqlalchemy import exc

from database.engine import get_engine

logger = logging.getLogger("investment_platform.database.session")

# BUG FIX: The original code called get_engine() at module-level during import,
# before the engine is initialized and before env vars are loaded.
# This caused a RuntimeError / crash on import. Replaced with a lazy factory
# that creates the session maker on first use.
_async_session_factory: Optional[async_sessionmaker[AsyncSession]] = None


def _get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Lazily initializes and returns the session factory bound to the engine."""
    global _async_session_factory
    if _async_session_factory is None:
        _async_session_factory = async_sessionmaker(
            bind=get_engine(),
            class_=AsyncSession,
            expire_on_commit=False,  # Disables active entity data eviction on transaction completion
            autoflush=False,         # Requires explicit checkpoints for operational optimization
        )
    return _async_session_factory


@asynccontextmanager
async def session_scope() -> AsyncGenerator[AsyncSession, None]:
    """Context manager enforcing programmatic transaction boundaries.

    Provides automatic atomic commits, mandatory rollbacks on interception of
    runtime exceptions, and absolute structural session cleanup closure.

    Yields:
        AsyncSession: The isolated active database transactional connection.

    Raises:
        Exception: Re-raises any intercepted exception after asserting rollback state.
    """
    factory = _get_session_factory()
    session: AsyncSession = factory()
    try:
        yield session
        if session.in_transaction():
            await session.commit()
    except Exception as error:
        logger.error(
            "Exception encountered within transactional session scope. Initializing rollback...",
            exc_info=True,
        )
        if session.in_transaction():
            await session.rollback()
        raise error
    finally:
        await session.close()


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency injection compliance generator target interface.

    Maintains safe setup, yielding lifecycle frames, and absolute teardown 
    conforming with enterprise middleware abstraction pipelines.

    Yields:
        AsyncSession: Dedicated, isolated worker session context.
    """
    async with session_scope() as session:
        yield session


async def rollback_session(session: AsyncSession) -> bool:
    """Safely triggers an explicit, non-blocking operational recovery transaction reset.

    Args:
        session: The active database connection reference tracking changes.

    Returns:
        bool: True if rollback executed cleanly; False if no active transaction existed or errored.
    """
    try:
        if session.in_transaction() or session.is_active:
            await session.rollback()
            return True
    except exc.SQLAlchemyError:
        logger.error("Failed to cleanly rollback database transaction state.", exc_info=True)
    return False


async def close_session(session: AsyncSession) -> None:
    """Performs absolute explicit resource collection and connection closure.

    Args:
        session: Target connection context tracking transactional footprints.
    """
    try:
        await session.close()
    except exc.SQLAlchemyError:
        logger.error("Error intercepted during explicit connection close sequence.", exc_info=True)
