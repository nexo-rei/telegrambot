# wallet.py
"""Wallet Database Domain Model.

Authoritative entity representing a user's liquid financial standing within the platform.
Tracks isolated balance allocations, historical performance aggregations, and transactional states
using fixed-point Decimal representations to prevent floating-point calculation drift.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from sqlalchemy import BigInteger, ForeignKey, Numeric, String, Boolean, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base, IDMixin, TimestampMixin


class Wallet(Base, IDMixin, TimestampMixin):
    """Authoritative structural domain model mapping user localized wallets."""

    # --- Structural Ownership Linkages ---
    user_id: Mapped[int] = mapped_column(
        BigInteger, 
        ForeignKey("user.telegram_id", ondelete="CASCADE"), 
        unique=True, 
        nullable=False, 
        index=True
    )

    # --- Granular Isolated Balances (Precision-Safe Minor Unit Computations) ---
    available_balance: Mapped[Decimal] = mapped_column(Numeric(20, 2), default=Decimal("0.00"))
    investment_balance: Mapped[Decimal] = mapped_column(Numeric(20, 2), default=Decimal("0.00"))
    referral_balance: Mapped[Decimal] = mapped_column(Numeric(20, 2), default=Decimal("0.00"))
    bonus_balance: Mapped[Decimal] = mapped_column(Numeric(20, 2), default=Decimal("0.00"))
    pending_balance: Mapped[Decimal] = mapped_column(Numeric(20, 2), default=Decimal("0.00"))
    frozen_balance: Mapped[Decimal] = mapped_column(Numeric(20, 2), default=Decimal("0.00"))

    # --- Lifetime Aggregated Financial Indices ---
    total_deposit: Mapped[Decimal] = mapped_column(Numeric(20, 2), default=Decimal("0.00"))
    total_withdraw: Mapped[Decimal] = mapped_column(Numeric(20, 2), default=Decimal("0.00"))
    total_profit: Mapped[Decimal] = mapped_column(Numeric(20, 2), default=Decimal("0.00"))
    total_bonus: Mapped[Decimal] = mapped_column(Numeric(20, 2), default=Decimal("0.00"))
    total_referral_income: Mapped[Decimal] = mapped_column(Numeric(20, 2), default=Decimal("0.00"))

    # --- Systemic Governance & State Telemetry ---
    currency: Mapped[str] = mapped_column(String(3), default="NGN")
    is_locked: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    last_transaction_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # --- Downstream Relational Mapping Connections ---
    user = relationship("User", back_populates="wallet_rel")

    # --- Advanced Compositional Performance Optimization Indices ---
    __table_args__ = (
        Index("ix_wallet_balances_lookup", "user_id", "available_balance", "is_locked"),
    )
    
