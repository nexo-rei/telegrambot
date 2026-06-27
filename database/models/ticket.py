# ticket.py
"""Ticket Database Domain Model.

Authoritative entity representing customer support and communication threads 
exchanged between platform participants and the administration desk. Tracks 
operational classification taxonomies, urgency states, ownership indices, 
and performance metric timestamps.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import (
    BigInteger,
    ForeignKey,
    String,
    DateTime,
    Enum as SQLEnum,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base, IDMixin, TimestampMixin


class TicketStatus(str, Enum):
    """Defines the current resolution milestone of an active support communication thread."""
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    WAITING_USER = "WAITING_USER"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"
    REJECTED = "REJECTED"


class TicketPriority(str, Enum):
    """Classifies the escalation intensity and response windows for the administrative queue."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"


class Ticket(Base, IDMixin, TimestampMixin):
    """Authoritative structural domain model mapping helpdesk customer support interactions."""

    # --- Structural Ownership Linkages ---
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("user.telegram_id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    assigned_admin_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        ForeignKey("user.telegram_id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    # --- Ticket Identity and Structural Payload ---
    ticket_number: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True)
    subject: Mapped[str] = mapped_column(String(128), nullable=False)
    category: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    
    # --- State and Urgency Classifications ---
    status: Mapped[TicketStatus] = mapped_column(
        SQLEnum(TicketStatus, name="ticket_status_enum"),
        default=TicketStatus.OPEN,
        nullable=False,
        index=True
    )
    priority: Mapped[TicketPriority] = mapped_column(
        SQLEnum(TicketPriority, name="ticket_priority_enum"),
        default=TicketPriority.MEDIUM,
        nullable=False,
        index=True
    )
    description: Mapped[str] = mapped_column(String(4000), nullable=False)

    # --- Operational SLA Metrics Timeline Tracking Vectors ---
    first_response_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # --- Downstream Relational Mapping Connections ---
    user = relationship("User", foreign_keys=[user_id], back_populates="tickets")
    assigned_admin = relationship("User", foreign_keys=[assigned_admin_id])

    # --- Composite Performance Optimization Indices ---
    __table_args__ = (
        Index("ix_ticket_queue_lookup", "status", "priority", "created_at"),
        Index("ix_user_tickets_lifecycle", "user_id", "status"),
    )
    
