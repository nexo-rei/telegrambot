# referral.py
"""Referral Database Domain Model.

Authoritative entity mapping multi-level affiliate marketing trees, tracking upstream 
referrers and downstream referred network branches. Maintains isolated commission accounting 
records via high-precision decimals, engagement metrics, and network traversal path vectors.
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional

from sqlalchemy import (
    BigInteger,
    ForeignKey,
    Numeric,
    String,
    Integer,
    DateTime,
    Enum as SQLEnum,
    Index,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base, IDMixin, TimestampMixin


class ReferralStatus(str, Enum):
    """Defines the current state of engagement and validity for an active network node pairing."""
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    BLOCKED = "BLOCKED"
    EXPIRED = "EXPIRED"


class Referral(Base, IDMixin, TimestampMixin):
    """Authoritative structural domain model tracking multi-level marketing affiliate connections."""

    # --- Structural Ownership Linkages ---
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("user.telegram_id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    referred_user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("user.telegram_id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )

    # --- Structural Network Traversal Metaprogramming Matrix ---
    referral_code: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    referral_level: Mapped[int] = mapped_column(Integer, default=1, nullable=False, index=True)
    referral_path: Mapped[str] = mapped_column(String(512), nullable=False)  # Materialized path lineage tracking (e.g., "1001/1005/1210")
    referral_source: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    # --- Financial Performance Metrics ---
    referral_bonus: Mapped[Decimal] = mapped_column(Numeric(20, 2), default=Decimal("0.00"), nullable=False)
    total_commission: Mapped[Decimal] = mapped_column(Numeric(20, 2), default=Decimal("0.00"), nullable=False)
    pending_commission: Mapped[Decimal] = mapped_column(Numeric(20, 2), default=Decimal("0.00"), nullable=False)
    paid_commission: Mapped[Decimal] = mapped_column(Numeric(20, 2), default=Decimal("0.00"), nullable=False)

    # --- Direct Sub-Graph Performance Summaries ---
    total_referrals: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    active_referrals: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    inactive_referrals: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # --- State Classifications ---
    status: Mapped[ReferralStatus] = mapped_column(
        SQLEnum(ReferralStatus, name="referral_status_enum"),
        default=ReferralStatus.ACTIVE,
        nullable=False,
        index=True
    )

    # --- Audit & Timeline Tracking Vectors ---
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    first_deposit_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    first_investment_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_reward_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # --- Downstream Relational Mapping Connections ---
    user = relationship("User", foreign_keys=[user_id], back_populates="referral_records")
    referred_user = relationship("User", foreign_keys=[referred_user_id])

    # --- Relational Integrity Safeguards & Performance Indices ---
    __table_args__ = (
        UniqueConstraint("user_id", "referred_user_id", name="uq_referral_prevent_duplicate_pairs"),
        Index("ix_referral_lineage_lookup", "user_id", "referral_level", "status"),
    )
    
