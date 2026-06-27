# test_redis_db.py
"""Integration Test Suite: Redis and PostgreSQL.

Validates the persistence and caching layers' integration, ensuring atomic
database operations and reliable Redis cache consistency. These tests exercise
the connection pooling and transaction lifecycle across the infrastructure.
"""

import pytest
import pytest_asyncio
from sqlalchemy import text
from redis.asyncio import Redis

# Assuming standard project structure
# from src.infrastructure.cache import redis_client (Placeholder for actual import)


@pytest.mark.asyncio
async def test_postgresql_connection_and_transaction(db_session) -> None:
    """Verifies PostgreSQL connectivity and transactional integrity."""
    # Test atomic write
    await db_session.execute(text("CREATE TABLE IF NOT EXISTS test_table (id SERIAL PRIMARY KEY, val TEXT)"))
    await db_session.execute(text("INSERT INTO test_table (val) VALUES ('integration_test')"))
    await db_session.commit()

    # Test read verification
    result = await db_session.execute(text("SELECT val FROM test_table WHERE val = 'integration_test'"))
    assert result.scalar() == "integration_test"


@pytest.mark.asyncio
async def test_redis_write_read_cycle() -> None:
    """Validates basic Redis read/write operations and cache persistence."""
    # In a real environment, use the configured Redis pool
    client = Redis(host="localhost", port=6379, db=1)
    
    try:
        key = "test_key_integration"
        value = "integration_value"
        
        await client.set(key, value, ex=10)
        retrieved = await client.get(key)
        
        assert retrieved.decode("utf-8") == value
    finally:
        await client.delete(key)
        await client.close()


@pytest.mark.asyncio
async def test_cache_consistency_with_db(db_session) -> None:
    """Verifies that data remains consistent between database and cache."""
    client = Redis(host="localhost", port=6379, db=1)
    
    try:
        # Simulate business logic: Update DB and Cache
        user_id = 999
        data = "user_data_999"
        
        # Database write
        await db_session.execute(text(f"CREATE TABLE IF NOT EXISTS users (id INT, data TEXT)"))
        await db_session.execute(text(f"INSERT INTO users (id, data) VALUES ({user_id}, '{data}')"))
        await db_session.commit()
        
        # Cache write
        await client.set(f"user:{user_id}", data)
        
        # Verify both sources
        db_res = await db_session.execute(text(f"SELECT data FROM users WHERE id = {user_id}"))
        cache_res = await client.get(f"user:{user_id}")
        
        assert db_res.scalar() == data
        assert cache_res.decode("utf-8") == data
    finally:
        await client.delete(f"user:{user_id}")
        await client.close()


@pytest.mark.asyncio
async def test_transaction_rollback_isolation(db_session) -> None:
    """Ensures that failed database transactions do not persist."""
    try:
        await db_session.execute(text("INSERT INTO test_table (val) VALUES ('rollback_test')"))
        raise Exception("Triggering transaction abort")
    except Exception:
        await db_session.rollback()
        
    result = await db_session.execute(text("SELECT val FROM test_table WHERE val = 'rollback_test'"))
    assert result.scalar() is None
