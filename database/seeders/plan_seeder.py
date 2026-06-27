# plan_seeder.py
"""Production-grade Investment Plan Seeder.

Handles the idempotent initialization and synchronization of investment 
plan configurations within the PostgreSQL database. Utilizes atomic 
transactions to ensure that master plan data remains consistent across 
deployment environments.
"""

import logging
from decimal import Decimal
from dataclasses import dataclass
from typing import Final

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.investment import InvestmentPlan
from src.exceptions.database import DatabaseSeedingError

logger = logging.getLogger("investment_platform.database.seeders.plan_seeder")


@dataclass(frozen=True)
class SeedingResult:
    total_processed: int
    created: int
    updated: int
    skipped: int
    success: bool


class PlanSeeder:
    """Orchestrates the asynchronous seeding of default investment products."""

    DEFAULT_PLANS: Final[list[dict]] = [
        {
            "name": "Starter Savings",
            "display_order": 1,
            "min_investment": Decimal("10000.00"),
            "max_investment": Decimal("500000.00"),
            "daily_roi": Decimal("0.5"),
            "duration_days": 30,
            "is_active": True,
            "is_featured": False
        },
        {
            "name": "Enterprise Growth",
            "display_order": 2,
            "min_investment": Decimal("500001.00"),
            "max_investment": Decimal("5000000.00"),
            "daily_roi": Decimal("1.2"),
            "duration_days": 60,
            "is_active": True,
            "is_featured": True
        }
    ]

    async def run(self, session: AsyncSession) -> SeedingResult:
        """Executes the idempotent seeding process within a single transaction."""
        created = 0
        updated = 0
        skipped = 0

        try:
            async with session.begin_nested():
                for plan_data in self.DEFAULT_PLANS:
                    query = select(InvestmentPlan).where(InvestmentPlan.name == plan_data["name"])
                    result = await session.execute(query)
                    existing_plan = result.scalar_one_or_none()

                    if existing_plan:
                        # Synchronize existing plan attributes
                        for key, value in plan_data.items():
                            setattr(existing_plan, key, value)
                        updated += 1
                    else:
                        # Insert new plan
                        new_plan = InvestmentPlan(**plan_data)
                        session.add(new_plan)
                        created += 1

            await session.commit()
            logger.info(f"Seeding completed: Created {created}, Updated {updated}.")
            
            return SeedingResult(
                total_processed=len(self.DEFAULT_PLANS),
                created=created,
                updated=updated,
                skipped=skipped,
                success=True
            )

        except Exception as e:
            await session.rollback()
            logger.error(f"Seeding failed: {e}")
            raise DatabaseSeedingError("Failed to seed investment plans.") from e
