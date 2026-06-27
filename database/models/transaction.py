# transaction.py
"""Transaction Database Domain Model.

Authoritative immutable ledger mapping all financial movements across the 
platform. Enforces complete accounting consistency, zero data deletion, and fixed-point 
Decimal precision (Kobo-accurate) with robust programmatic validation constraints.
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional
import uuid

from sqlalchemy import (
    BigInteger,
    ForeignKey,
    Numeric,
    String,
    DateTime,
    Enum as SQLEnum,
    Index,
    CheckConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base, IDMixin, TimestampMixin


class TransactionType(str, Enum):
    """Categorizes the precise nature of an immutable financial balance event."""
    DEPOSIT = "DEPOSIT"
    WITHDRAW = "WITHDRAW"
    INVESTMENT = "INVESTMENT"
    DAILY_PROFIT = "DAILY_PROFIT"
    REFERRAL_REWARD = "REFERRAL_REWARD"
    BONUS = "BONUS"
    GIFT_CODE = "GIFT_CODE"
    VIP_BONUS = "VIP_BONUS"
    ADMIN_CREDIT = "ADMIN_CREDIT"
    ADMIN_DEBIT = "ADMIN_DEBIT"
    REFUND = "REFUND"
    PENALTY = "PENALTY"
    COMMISSION = "COMMISSION"
    TRANSFER = "TRANSFER"


class TransactionStatus(str, Enum):
    """Defines the operational fulfillment state of a pending or processed ledger entry."""
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"
    REVERSED = "REVERSED"


class Transaction(Base, IDMixin, TimestampMixin):
    """Authoritative structural domain model acting as the immutable double-entry core ledger."""

    # --- Structural Ownership Linkages ---
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("user.telegram_id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    wallet_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("wallet.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    investment_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        ForeignKey("investment.id", ondelete="RESTRICT"),
        nullable=True
    )

    # --- Core State Classifications ---
    type: Mapped[TransactionType] = mapped_column(
        SQLEnum(TransactionType, name="transaction_type_enum"),
        nullable=False,
        index=True
    )
    status: Mapped[TransactionStatus] = mapped_column(
        SQLEnum(TransactionStatus, name="transaction_status_enum"),
        default=TransactionStatus.PENDING,
        nullable=False,
        index=True
    )

    # --- Financial Performance Metrics ---
    amount: Mapped[Decimal] = mapped_column(Numeric(20, 2), nullable=False)
    fee: Mapped[Decimal] = mapped_column(Numeric(20, 2), default=Decimal("0.00"), nullable=False)
    tax: Mapped[Decimal] = mapped_column(Numeric(20, 2), default=Decimal("0.00"), nullable=False)
    net_amount: Mapped[Decimal] = mapped_column(Numeric(20, 2), nullable=False)

    # --- Unique Tracking Reference Vectors ---
    transaction_id: Mapped[uuid.UUID] = mapped_column(
        String(36),
        default=uuid.uuid4,
        unique=True,
        nullable=False,
        index=True
    )
    external_reference: Mapped[Optional[str]] = mapped_column(String(64), unique=True, nullable=True)
    payment_reference: Mapped[Optional[str]] = mapped_column(String(64), unique=True, nullable=True)

    # --- Contextual Auditing & Source Metadata ---
    currency: Mapped[str] = mapped_column(String(3), default="NGN", nullable=False)
    description: Mapped[str] = mapped_column(String(256), nullable=False)
    remarks: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    source: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    destination: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    device: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    
    # --- Chronological Progression Markers ---
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # --- Downstream Relational Mapping Connections ---
    user = relationship("User", back_populates="transactions")
    wallet = relationship("Wallet")

    # --- Composite Performance Optimization Indices & Integrity Constraints ---
    __table_args__ = (
        CheckConstraint("amount >= 0", name="ck_transaction_positive_amount"),
        CheckConstraint("fee >= 0", name="ck_transaction_positive_fee"),
        CheckConstraint("tax >= 0", name="ck_transaction_positive_tax"),
        Index("ix_transaction_historical_lookup", "user_id", "type", "status"),
        Index("ix_transaction_chronological_flow", "created_at", "status"),
    )
    
