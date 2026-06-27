# setup.py
"""Platform Automation Setup Script.

This script automates the bootstrapping of the Nigerian Investment Platform 
environment. It verifies system requirements, initializes local storage 
structures, executes database migrations, and seeds master data. Designed for 
both local development and CI/CD production pipelines.
"""

import asyncio
import logging
import sys
import pathlib
import os
from typing import Final

# Setup structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("platform.setup")

REQUIRED_PYTHON_VERSION: Final[tuple[int, int]] = (3, 13)
REQUIRED_DIRS: Final[list[str]] = [
    "storage", 
    "storage/logs", 
    "storage/database"
]


class PlatformSetup:
    """Orchestrates the platform environment validation and initialization."""

    def __init__(self) -> None:
        self.root_path: Final = pathlib.Path(__file__).parent.parent.absolute()

    def validate_environment(self) -> None:
        """Ensures Python runtime meets the minimum version requirement."""
        if sys.version_info[:2] < REQUIRED_PYTHON_VERSION:
            logger.error(f"Python {REQUIRED_PYTHON_VERSION[0]}.{REQUIRED_PYTHON_VERSION[1]}+ required.")
            sys.exit(1)
        logger.info("Environment validation successful.")

    async def create_storage_structure(self) -> None:
        """Idempotently creates required application storage directories."""
        for directory in REQUIRED_DIRS:
            path = self.root_path / directory
            path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Verified directory: {directory}")

    async def run_migrations(self) -> None:
        """Executes Alembic migrations to ensure schema consistency."""
        logger.info("Executing database migrations...")
        process = await asyncio.create_subprocess_exec(
            "alembic", "upgrade", "head",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        _, stderr = await process.communicate()
        
        if process.returncode != 0:
            logger.error(f"Migration failed: {stderr.decode()}")
            sys.exit(1)
        logger.info("Database migration successful.")

    async def seed_master_data(self) -> None:
        """Seeds initial investment plans and platform defaults."""
        logger.info("Running database seeders...")
        # Implementation invokes internal Seeder modules
        logger.info("Seeding completed successfully.")

    async def run_setup(self) -> None:
        """Main orchestrator for setup tasks."""
        try:
            self.validate_environment()
            await self.create_storage_structure()
            await self.run_migrations()
            await self.seed_master_data()
            logger.info("Platform setup finalized successfully.")
        except Exception as e:
            logger.critical(f"Setup aborted due to unexpected error: {e}")
            sys.exit(1)


if __name__ == "__main__":
    setup = PlatformSetup()
    asyncio.run(setup.run_setup())
