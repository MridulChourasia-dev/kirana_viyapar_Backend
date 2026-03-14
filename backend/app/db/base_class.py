"""
SQLAlchemy Base model with common fields and metadata
"""
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy models.
    Provides automatic tabie name generation and common fields.
    """

    id: Any
    __name__: str

    @declared_attr
    def __tablename__(cls) -> str:
        """Generate table name from class name (lowercase)"""
        return cls.__name__.lower()

    # Common timestamp fields for all models
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


