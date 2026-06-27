# create_admin.py
"""Administrator Account Provisioning Utility.

Provides a secure, idempotent interface for creating privileged administrative
accounts within the platform. Ensures strict validation of Telegram identities 
and role assignments, integrating directly with the production database layer.
"""

import asyncio
import logging
import sys
from typing import Final, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.models.user import User
from src.database.enums.account_roles import UserRole, AccountStatus
from src.config.database import DATABASE_URL

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("scripts.create_admin")


class AdminProvisioner:
    """Orchestrates secure administrative account creation."""

    def __init__(self, db_url: str) -> None:
        self.engine = create_async_engine(db_url, echo=False)
        self.async_session = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )

    async def create_admin(
        self,
        telegram_id: int,
        username: str,
        full_name: str,
        role: UserRole = UserRole.ADMINISTRATOR
    ) -> bool:
        """Atomically provisions a new administrator account."""
        async with self.async_session() as session:
            try:
                # Existence check
                existing = await session.execute(
                    select(User).where(User.telegram_id == telegram_id)
                )
                if existing.scalar_one_or_none():
                    logger.warning(f"Administrator with ID {telegram_id} already exists.")
                    return False

                # Account creation
                new_admin = User(
                    telegram_id=telegram_id,
                    username=username,
                    full_name=full_name,
                    role=role,
                    status=AccountStatus.ACTIVE
                )
                
                session.add(new_admin)
                await session.commit()
                logger.info(f"Administrator '{username}' created successfully with role {role}.")
                return True

            except Exception as e:
                await session.rollback()
                logger.error(f"Failed to provision administrator: {e}")
                return False
            finally:
                await self.engine.dispose()


async def main() -> None:
    """CLI entry point for administrative provisioning."""
    if len(sys.argv) < 4:
        print("Usage: python -m scripts.create_admin <telegram_id> <username> <full_name>")
        sys.exit(1)

    try:
        t_id = int(sys.argv[1])
        u_name = sys.argv[2]
        f_name = sys.argv[3]
    except ValueError:
        logger.error("Telegram ID must be an integer.")
        sys.exit(1)

    provisioner = AdminProvisioner(DATABASE_URL)
    success = await provisioner.create_admin(t_id, u_name, f_name)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
