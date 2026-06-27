# services.py
"""Production-grade Admin Panel Service.

Encapsulates business logic for platform administration, financial oversight, 
and user governance. Orchestrates high-privilege operations including 
transaction reconciliation, system status management, and analytics generation 
within the enterprise investment ecosystem.
"""

import logging
from typing import Final, Any
from decimal import Decimal

from src.modules.admin_panel.dtos import DashboardStatsDTO
from src.modules.admin_panel.exceptions import AdminPermissionError

logger = logging.getLogger("investment_platform.modules.admin_panel.services")


class AdminPanelService:
    """Core domain service for administrative operations and platform oversight."""

    def __init__(
        self,
        auth_service: Any,
        stats_service: Any,
        financial_repo: Any,
        cache_manager: Any,
        event_bus: Any
    ) -> None:
        self._auth: Final = auth_service
        self._stats: Final = stats_service
        self._financial_repo: Final = financial_repo
        self._cache: Final = cache_manager
        self._event_bus: Final = event_bus

    async def is_authorized(self, admin_id: int) -> bool:
        """Validates if the user possesses the necessary administrative roles."""
        return await self._auth.has_admin_privileges(admin_id)

    async def get_dashboard_statistics(self) -> DashboardStatsDTO:
        """Aggregates real-time platform KPIs, prioritizing cached values."""
        cache_key = "admin_dashboard_stats"
        cached = await self._cache.get(cache_key)
        
        if cached:
            return cached

        # Aggregate data across repositories
        stats = DashboardStatsDTO(
            user_count=await self._stats.get_total_users(),
            pending_deposits=await self._financial_repo.get_pending_deposits_total(),
            pending_withdrawals=await self._financial_repo.get_pending_withdrawals_total()
        )
        
        await self._cache.set(cache_key, stats, ttl=60)
        return stats

    async def approve_transaction(self, admin_id: int, transaction_id: str) -> bool:
        """Processes financial approval workflow with strict audit logging."""
        if not await self.is_authorized(admin_id):
            raise AdminPermissionError("Unauthorized access attempt.")

        try:
            async with self._financial_repo.transaction():
                success = await self._financial_repo.approve(transaction_id)
                if success:
                    await self._event_bus.publish("admin.transaction_approved", {
                        "admin_id": admin_id,
                        "transaction_id": transaction_id
                    })
                    await self._cache.delete("admin_dashboard_stats")
            return success
        except Exception as e:
            logger.error(f"Approval failed for transaction {transaction_id}: {e}")
            return False
