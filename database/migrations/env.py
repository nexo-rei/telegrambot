"""Alembic Migration Environment Configuration.

Configures the migration environment to support asynchronous SQLAlchemy 2.x
migrations. Enables both online and offline migration modes by integrating
with the project's centralized database configuration and engine management layer.

BUG FIXES:
  - Wrong import paths: `src.config.database` and `src.database.base` do not exist.
    The correct paths are `config.database` and `database.base`.
  - Missing `Any` import used in do_run_migrations type hint.
  - alembic.ini had a placeholder `script_location = src/database/migrations` which
    doesn't match the actual location `database/migrations`. Fixed in alembic.ini separately.
"""

import asyncio
from logging.config import fileConfig
from typing import Any

from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine

from alembic import context

# BUG FIX: Original had `from src.config.database import DATABASE_URL` which fails
# because there is no `src/config` package - config lives at project root level.
from config.database import DATABASE_URL

# BUG FIX: Original had `from src.database.base import Base` which fails for the
# same reason - database lives at project root level, not under src/.
from database.base import Base

# Import all models so Alembic can discover them for autogenerate
import database.models  # noqa: F401 - registers all model metadata

# Alembic Config object, which provides access to the values within the .ini file
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set target metadata for 'autogenerate' support
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    Configures the context with just a URL and not an Engine.
    """
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Any) -> None:
    """Execution bridge for async online migration."""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """In 'online' mode, create an asynchronous engine and execute migrations."""
    connectable = create_async_engine(
        DATABASE_URL,
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
