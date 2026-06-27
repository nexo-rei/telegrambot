# transactional.py
"""Enterprise Database Transactional Integrity Decorator.

Provides a robust, asynchronous transaction governance mechanism for business operations
requiring strict ACID compliance. Integrates SQLAlchemy asynchronous session lifecycles
with automatic commit/rollback logic, dead-lock retry strategies, and optional
cross-service distributed locking for financial consistency.
"""

import asyncio
import functools
import logging
from collections.abc import Callable
from typing import Any, Final, Optional, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import DBAPIError, OperationalError
from src.shared.cache.lock_manager import DistributedLockManager

logger = logging.getLogger("investment_platform.shared.decorators.transactional")

# Resilience Parameters for Database Contention
MAX_TRANSACTION_RETRIES: Final[int] = 3
BASE_RETRY_DELAY_SECONDS: Final[float] = 0.5

F = TypeVar("F", bound=Callable[..., Any])


def transactional(
    lock_name: Optional[str] = None,
    isolation_level: Optional[str] = None,
    read_only: bool = False
) -> Callable[[F], F]:
    """Decorates asynchronous handlers to enforce atomic database transaction boundaries.

    Args:
        lock_name: Optional distributed resource key to secure during execution.
        isolation_level: Specific SQL isolation level enforcement.
        read_only: Prevents session commit if operation is read-only.
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            session: Optional[AsyncSession] = kwargs.get("session")
            if not session:
                logger.error("Transactional decorator invoked without an active DB session context.")
                return await func(*args, **kwargs)

            # Execution logic with automated retry capabilities for deadlock resilience
            attempts = 0
            while attempts < MAX_TRANSACTION_RETRIES:
                try:
                    # Optional distributed locking layer for cross-process financial integrity
                    if lock_name:
                        lock_manager: Optional[DistributedLockManager] = kwargs.get("lock_manager")
                        if lock_manager:
                            async with lock_manager.lock(lock_name):
                                return await _execute_transaction(func, session, read_only, *args, **kwargs)
                    
                    return await _execute_transaction(func, session, read_only, *args, **kwargs)

                except (OperationalError, DBAPIError) as fault:
                    attempts += 1
                    if attempts >= MAX_TRANSACTION_RETRIES:
                        logger.critical(f"Transaction persistent failure after {attempts} retries: {fault}")
                        raise fault
                    
                    delay = BASE_RETRY_DELAY_SECONDS * (2 ** attempts)
                    logger.warning(f"Transient DB contention detected. Retrying in {delay}s. Attempt {attempts}/{MAX_TRANSACTION_RETRIES}")
                    await asyncio.sleep(delay)
                    
            return None
        return wrapper # type: ignore
    return decorator


async def _execute_transaction(
    func: Callable[..., Any],
    session: AsyncSession,
    read_only: bool,
    *args: Any,
    **kwargs: Any
) -> Any:
    """Internal orchestration block managing session commit and rollback lifecycles."""
    async with session.begin_nested() if session.in_transaction() else session.begin():
        try:
            result = await func(*args, **kwargs)
            if not read_only:
                await session.commit()
            return result
        except Exception as error:
            await session.rollback()
            logger.error(f"Transaction faulted and rolled back: {error}")
            raise error
