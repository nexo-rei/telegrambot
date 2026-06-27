# core_logs.py
"""Core Operational Logs and Audit Trail Database Domain Model.

Authoritative entity representing immutable auditing tracks, security telemetry,
system failure events, and user interaction profiles. Employs PostgreSQL JSONB
dialects for structural schema flexibility alongside hard execution indexing constraints.
"""

from enum import Enum
from typing import Any, Dict, Optional
import uuid

from sqlalchemy import (
    BigInteger,
    ForeignKey,
    String,
    Enum as SQLEnum,
    Index,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base, IDMixin, TimestampMixin


class LogLevel(str, Enum):
    """Defines the prioritization level and execution severity of a systemic logging entry."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class CoreLog(Base, IDMixin, TimestampMixin):
    """Authoritative structural domain model mapping systemic telemetry and compliance forensic logs."""

    # --- Structural Ownership Linkages ---
    user_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        ForeignKey("user.telegram_id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    # --- Core Log Structural Identity Payload ---
    event_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        default=uuid.uuid4,
        unique=True,
        nullable=False,
        index=True
    )
    event_name: Mapped[str] = mapped_column(String(128), nullable=False)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    log_level: Mapped[LogLevel] = mapped_column(
        SQLEnum(LogLevel, name="log_level_enum"),
        default=LogLevel.INFO,
        nullable=False,
        index=True
    )
    source_module: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    action: Mapped[str] = mapped_column(String(64), nullable=False)
    message: Mapped[str] = mapped_column(String(4000), nullable=False)

    # --- Client Request Network Environment Telemetry ---
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    device: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    operating_system: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    browser: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)

    # --- Distributed Diagnostics Tracking Vectors ---
    request_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    correlation_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    
    # --- Structural Context Objects Schemas ---
    metadata_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB, 
        name="metadata", 
        nullable=True, 
        default=dict
    )
    extra_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB, 
        nullable=True, 
        default=dict
    )

    # --- Downstream Relational Mapping Connections ---
    user = relationship("User", back_populates="core_logs")

    # --- Composite Performance Optimization Forensic Search Indices ---
    __table_args__ = (
        Index("ix_core_log_forensic_search", "source_module", "log_level", "created_at"),
        Index("ix_core_log_correlation_flow", "correlation_id", "created_at"),
    )
    
