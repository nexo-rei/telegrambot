# dtos.py
"""Production-grade Dashboard Data Transfer Objects (DTOs).

Defines immutable, strongly-typed data structures for representing dashboard 
financials, investment performance, and user activity summaries. These DTOs 
ensure type safety and consistency when passing data between the Dashboard 
service, persistence layers, and Telegram presentation components.
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Final, Optional, List
from datetime import datetime


@dataclass(frozen=True)
class DashboardSummaryDTO:
    """Aggregated financial and activity summary for the user dashboard."""
    balance: Decimal
    active_investments: int
    daily_earnings: Decimal
    referral_earnings: Decimal
    vip_level: int
    last_updated: datetime = datetime.now()


@dataclass(frozen=True)
class WalletSummaryDTO:
    """Detailed breakdown of wallet state."""
    available_balance: Decimal
    locked_balance: Decimal
    total_deposits: Decimal
    total_withdrawals: Decimal


@dataclass(frozen=True)
class InvestmentSummaryDTO:
    """Summary of investment portfolio performance."""
    total_invested: Decimal
    active_count: int
    completed_count: int
    total_profit: Decimal


@dataclass(frozen=True)
class ReferralSummaryDTO:
    """Aggregated data for referral network performance."""
    referral_count: int
    total_earned: Decimal
    active_referrals: int


@dataclass(frozen=True)
class NotificationPreviewDTO:
    """DTO for previewing latest system or activity notifications."""
    notification_id: str
    title: str
    is_read: bool
    timestamp: datetime
