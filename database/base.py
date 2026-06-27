# base.py
"""Database Declarative Base Engine.

Provides the structural core blueprint for the enterprise object-relational mapping
layer. Implements automated snake_case table identification, unified metadata naming
conventions, mandatory auditing mixins, and serialization utilities.
"""

from datetime import datetime, UTC
from typing import Any, Dict
from re import sub

from sqlalchemy import MetaData, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, declared_attr


# 1. Standardized PostgreSQL Metadata Constraint Naming Matrix
# Enforces deterministic, collision-free naming protocols across migrations.
POSTGRES_NAMING_CONVENTION: Dict[str, str] = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata_instance = MetaData(naming_convention=POSTGRES_NAMING_CONVENTION)


class Base(DeclarativeBase):
    """Foundational Declarative Base for all PostgreSQL entities.

    Automates structural table reflections from Python class camel-case definitions
    directly into standardized lowercase snake_case structures.
    """
    metadata = metadata_instance

    @declared_attr.directive
    @classmethod
    def __tablename__(cls) -> str:
        """Converts class names safely to snake_case identifier strings."""
        return sub(r'(?<!^)(?=[A-Z])', '_', cls.__name__).lower()

    def to_dict(self) -> Dict[str, Any]:
        """Serializes local persistent column matrix parameters into a dictionary mapping.

        Excludes relationship sub-graphs to prevent lazy-loading pollution.
        """
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }

    def __repr__(self) -> str:
        """Generates an accurate, non-blocking administrative trace identity string."""
        columns_summary = ", ".join(
            f"{col.name}={getattr(self, col.name, None)!r}"
            for col in self.__table__.columns
            if col.primary_key or "name" in col.name or "status" in col.name
        )
        return f"<{self.__class__.__name__}({columns_summary})>"


class IDMixin:
    """Identity abstract mixin injecting auto-incrementing 64-bit integer keys.

    Engineered for rapid index scanning and seamless scaling beyond 100k+ records.
    """
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)


class TimestampMixin:
    """Auditing abstract mixin tracking creation and mutation timelines.

    Enforces deterministic timezone-aware UTC handling at the application layer.
    """
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        sort_order=-3
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        sort_order=-2
    )


class SoftDeleteMixin:
    """Compliance abstract mixin introducing logical record retention states.

    Prevents unexpected physical record deletion, enabling historical audit tracking.
    """
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        default=None,
        nullable=True,
        sort_order=-1
    )

    @property
    def is_deleted(self) -> bool:
        """Evaluates whether the instance is flagged as soft-deleted."""
        return self.deleted_at is not None
        
