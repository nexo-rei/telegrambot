# conftest.py
"""Global Test Configuration and Shared Fixtures.

Provides centralized test infrastructure, including asynchronous event loops,
transaction-scoped database sessions, and lifecycle management for Redis and 
Bot instances. Ensures test isolation and environmental consistency across 
the entire test suite.
"""

import asyncio
import pytest
from typing import AsyncGenerator, Generator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# Assuming configuration/models are accessible from the project root
from src.config.database import DATABASE_URL
from src.database.base import Base

# Configure pytest-asyncio to use function scope for individual test isolation
@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Creates an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def db_engine():
    """Initializes a temporary PostgreSQL engine for testing."""
    engine = create_async_engine(DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture(scope="function")
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Provides a transactional database session that rolls back after each test."""
    connection = await db_engine.connect()
    transaction = await connection.begin()
    session = AsyncSession(bind=connection, expire_on_commit=False)

    yield session

    await session.close()
    await transaction.rollback()
    await connection.close()


@pytest.fixture(scope="session")
async def redis_client():
    """Mock/Real Redis client fixture for cache testing."""
    # Logic for connecting to a test-container Redis instance would go here
    client = None 
    yield client


@pytest.fixture(scope="function")
def test_logger():
    """Provides a configured logger for test diagnostic output."""
    import logging
    return logging.getLogger("pytest.test_suite")


@pytest.fixture(scope="session")
def bot_instance():
    """Provides a base Aiogram Bot instance for testing."""
    from aiogram import Bot
    return Bot(token="TEST_TOKEN_BOT")


@pytest.fixture(scope="session")
def dispatcher():
    """Provides an Aiogram Dispatcher instance for testing."""
    from aiogram import Dispatcher
    return Dispatcher()
