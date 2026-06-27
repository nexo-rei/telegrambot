# investment.py
"""Investment Database Domain Model.

Authoritative entity representing a user's locked or active capital investment allocation.
Tracks investment plan constraints, yields, temporal maturation timelines, and automated
profit distribution schedules using fixed-point Decimal representations.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from sqlalchemy import BigInteger, ForeignKey, Numeric, String, DateTime, Integer, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base, IDMixin, TimestampMixin


class Investment(Base, IDMixin, TimestampMixin):
    """Authoritative structural domain model mapping capital asset investments."""

    # --- Structural Ownership Linkages ---
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("user.telegram_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # --- Investment Plan Definitions ---
    plan_name: Mapped[str] = mapped_column(String(64), nullable=False)
    plan_code: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    plan_duration_days: Mapped[int] = mapped_column(Integer, nullable=False)
    daily_profit_percent: Mapped[Decimal] = mapped_column(Numeric(6, 3), nullable=False)
    total_profit_percent: Mapped[Decimal] = mapped_column(Numeric(8, 3), nullable=False)

    # --- Financial Performance Metrics ---
    invested_amount: Mapped[Decimal] = mapped_column(Numeric(20, 2), nullable=False)
    expected_profit: Mapped[Decimal] = mapped_column(Numeric(20, 2), nullable=False)
    total_expected_return: Mapped[Decimal] = mapped_column(Numeric(20, 2), nullable=False)
    current_profit: Mapped[Decimal] = mapped_column(Numeric(20, 2), default=Decimal("0.00"))
    withdrawn_profit: Mapped[Decimal] = mapped_column(Numeric(20, 2), default=Decimal("0.00"))

    # --- Investment Temporal Status Matrix ---
    status: Mapped[str] = mapped_column(String(32), default="ACTIVE", nullable=False, index=True)
    start_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    end_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    last_profit_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    next_profit_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # --- Operational Accumulation Metrics ---
    total_days_completed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    remaining_days: Mapped[int] = mapped_column(Integer, nullable=False)
    profit_paid_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # --- Downstream Relational Mapping Connections ---
    user = relationship("User", back_populates="investments")

    # --- Advanced Compositional Performance Optimization Indices ---
    __table_args__ = (
        Index("ix_investment_accrual_lookup", "status", "next_profit_at"),
        Index("ix_user_investments_timeline", "user_id", "status", "start_date"),
    )
    
