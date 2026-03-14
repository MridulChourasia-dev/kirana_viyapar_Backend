"""
AuditLog model - audit trail for tracking changes
"""
import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class AuditLog(Base):
    """
    AuditLog model - comprehensive audit trail of all business-critical changes
    Tracks who did what, when, on which entity
    """

    __tablename__ = "audit_log"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    business_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("business.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # What entity was affected
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    entity_id: Mapped[uuid.UUID] = mapped_column(nullable=False, index=True)

    # What action occurred (create, update, delete, view, export, etc.)
    action: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    # Change details
    description: Mapped[str] = mapped_column(String(500), nullable=False)

    # Before/After state (JSON strings for complex changes)
    old_values: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON
    new_values: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON

    # IP and user agent for security tracking
    ip_address: Mapped[str | None] = mapped_column(String(50), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Timestamp (created_at is auto-added by Base class)
    timestamp: Mapped[datetime] = mapped_column(nullable=False, index=True)

    # Relationships
    business: Mapped["Business"] = relationship("Business", back_populates="audit_logs")
    user: Mapped["User | None"] = relationship("User")

    def __repr__(self) -> str:
        return f"<AuditLog {self.entity_type} {self.action}>"
