# user.py
"""User Database Domain Model.

Authoritative entity representing an active participant within the ecosystem. 
Tracks Telegram identity records, access controls, absolute financial indices 
represented in precise Decimal formulations, telemetry logs, and downstream relational trees.
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from sqlalchemy import BigInteger, String, Boolean, Numeric, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base, IDMixin, TimestampMixin, SoftDeleteMixin


class User(Base, IDMixin, TimestampMixin, SoftDeleteMixin):
    """Authoritative structural domain model mapping platform user nodes."""

    # --- Telegram Core Parameters ---
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False, index=True)
    username: Mapped[Optional[str]] = mapped_column(String(32), nullable=True, index=True)
    first_name: Mapped[str] = mapped_column(String(64), nullable=False)
    last_name: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    language_code: Mapped[str] = mapped_column(String(10), default="en")
    is_bot: Mapped[bool] = mapped_column(Boolean, default=False)
    profile_photo: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)

    # --- System Governance & Identification ---
    full_name: Mapped[str] = mapped_column(String(128), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(255), unique=True, nullable=True, index=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), unique=True, nullable=True)
    password_hash: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    account_status: Mapped[str] = mapped_column(String(32), default="ACTIVE", index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    is_moderator: Mapped[bool] = mapped_column(Boolean, default=False)

    # --- Investment Metrics ---
    vip_level: Mapped[int] = mapped_column(default=1)
    total_profit: Mapped[Decimal] = mapped_column(Numeric(20, 2), default=Decimal("0.00"))
    total_invested: Mapped[Decimal] = mapped_column(Numeric(20, 2), default=Decimal("0.00"))
    total_withdrawn: Mapped[Decimal] = mapped_column(Numeric(20, 2), default=Decimal("0.00"))
    total_deposited: Mapped[Decimal] = mapped_column(Numeric(20, 2), default=Decimal("0.00"))
    total_referral_bonus: Mapped[Decimal] = mapped_column(Numeric(20, 2), default=Decimal("0.00"))

    # --- Affiliate & Network Routing Configuration ---
    referral_code: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True)
    referred_by: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("user.telegram_id", ondelete="SET NULL"), nullable=True)
    referral_count: Mapped[int] = mapped_column(default=0)

    # --- Internal Liquid Wallet Allocations ---
    wallet_balance: Mapped[Decimal] = mapped_column(Numeric(20, 2), default=Decimal("0.00"))
    bonus_balance: Mapped[Decimal] = mapped_column(Numeric(20, 2), default=Decimal("0.00"))
    frozen_balance: Mapped[Decimal] = mapped_column(Numeric(20, 2), default=Decimal("0.00"))

    # --- Security Telemetry Infrastructure ---
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_ip: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    failed_login_attempts: Mapped[int] = mapped_column(default=0)
    account_locked_until: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # --- Interactivity Tracking Parameters ---
    last_activity: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_message: Mapped[Optional[str]] = mapped_column(String(4000), nullable=True)
    last_callback: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)

    # --- Client Profile Customization Preferences ---
    timezone: Mapped[str] = mapped_column(String(64), default="Africa/Lagos")
    currency: Mapped[str] = mapped_column(String(3), default="NGN")
    notification_enabled: Mapped[bool] = mapped_column(Boolean, default=True)

    # --- Upstream Relational Mapping Matrices ---
    referrer = relationship("User", remote_side=[telegram_id], back_populates="referrals")
    referrals = relationship("User", back_populates="referrer")
    
    wallet_rel = relationship("Wallet", back_populates="user", uselist=False, cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")
    investments = relationship("Investment", back_populates="user", cascade="all, delete-orphan")
    referral_records = relationship("Referral", foreign_keys="[Referral.user_id]", back_populates="user", cascade="all, delete-orphan")
    tickets = relationship("Ticket", back_populates="user", cascade="all, delete-orphan")
    core_logs = relationship("CoreLog", back_populates="user", cascade="all, delete-orphan")

    # --- Advanced Compositional Composite Performance Indices ---
    __table_args__ = (
        Index("ix_user_security_lookup", "telegram_id", "is_banned"),
        Index("ix_user_financials", "wallet_balance", "bonus_balance"),
    )
    
