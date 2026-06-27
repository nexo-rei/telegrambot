"""Production-grade Daily Check-In Service.

Encapsulates business logic for daily user engagement, streak tracking, and 
loyalty reward distribution. Orchestrates atomic financial updates to user 
wallets upon successful check-in, maintaining data consistency and streak 
integrity across the platform.
"""

import logging
from typing import Final, Any
from decimal import Decimal
from datetime import datetime

from src.modules.daily_check_in.dtos import CheckInStatusDTO, CheckInResultDTO
from src.shared.utilities.math_precision import PrecisionMath

logger = logging.getLogger("investment_platform.modules.daily_check_in.services")


class DailyCheckInService:
    """Core domain service for attendance tracking and loyalty reward management."""

    def __init__(
        self,
        attendance_repo: Any,
        wallet_service: Any,
        transaction_repo: Any,
        cache_manager: Any,
        event_bus: Any
    ) -> None:
        self._attendance_repo: Final = attendance_repo
        self._wallet_service: Final = wallet_service
        self._transaction_repo: Final = transaction_repo
        self._cache: Final = cache_manager
        self._event_bus: Final = event_bus

    async def get_user_status(self, user_id: int) -> CheckInStatusDTO:
        """Retrieves real-time check-in eligibility and streak metrics."""
        cache_key = f"checkin_status_{user_id}"
        cached = await self._cache.get(cache_key)
        if cached:
            return cached

        data = await self._attendance_repo.get_user_summary(user_id)
        
        status = CheckInStatusDTO(
            current_streak=data.streak,
            today_reward=data.next_reward_amount,
            is_checked_in=data.last_checkin == datetime.now().date()
        )
        
        await self._cache.set(cache_key, status, ttl=300)
        return status

    async def process_checkin(self, user_id: int) -> CheckInResultDTO:
        """Processes the daily attendance check-in and distributes rewards atomically."""
        
        # 1. Eligibility Validation
        status = await self.get_user_status(user_id)
        if status.is_checked_in:
            return CheckInResultDTO(success=False, message="Already checked in today.")

        # 2. Atomic Financial and Streak Processing
        try:
            async with self._transaction_repo.transaction():
                # Update streak and register attendance
                attendance = await self._attendance_repo.register_attendance(user_id)
                
                # Credit reward to wallet
                await self._wallet_service.update_balance(
                    user_id, attendance.reward_amount, "daily_checkin_bonus"
                )
            
            # Publish domain events
            await self._event_bus.publish("daily_checkin.completed", {
                "user_id": user_id, 
                "amount": attendance.reward_amount
            })
            
            # Invalidate cache for immediate consistency
            await self._cache.delete(f"checkin_status_{user_id}")
            
            return CheckInResultDTO(
                success=True, 
                amount=attendance.reward_amount
            )

        except Exception as e:
            logger.error(f"Failed to process check-in for {user_id}: {e}")
            return CheckInResultDTO(success=False, message="Check-in processing error.")
