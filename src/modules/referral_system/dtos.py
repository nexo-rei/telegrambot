"""Referral System Data Transfer Objects."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ReferralStatsDTO:
    """Referral statistics data transfer object."""
    total_referrals: int = 0
    active_referrals: int = 0
    total_earnings: float = 0.0
    referral_code: Optional[str] = None
