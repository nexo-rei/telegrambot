"""Referral System Data Transfer Objects."""

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional


@dataclass
class ReferralStatsDTO:
    """Referral performance statistics transfer object."""
    user_id: int
    total_referrals: int = 0
    active_referrals: int = 0
    total_earnings: Decimal = Decimal("0.00")
    referral_code: Optional[str] = None
    pending_rewards: Decimal = Decimal("0.00")
