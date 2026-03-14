"""
Notification model - user notifications and alerts
"""
import enum
import uuid

from sqlalchemy import Enum as SQLEnum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class NotificationType(str, enum.Enum):
    """Notification type enumeration"""

    INVOICE = "invoice"
    PAYMENT = "payment"
    PURCHASE = "purchase"
    INVENTORY = "inventory"
    EXPENSE = "expense"
    ALERT = "alert"
    SYSTEM = "system"
    OTHER = "other"


class Notification(Base):
    """
    Notification model - notifications and alerts for users
    """

    __tablename__ = "notification"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    business_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("business.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Notification content
    type: Mapped[NotificationType] = mapped_column(
        SQLEnum(NotificationType), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)

    # Related entity
    entity_type: Mapped[str | None] = mapped_column(String(50), nullable=True)  # invoice, payment, etc
    entity_id: Mapped[uuid.UUID | None] = mapped_column(nullable=True, index=True)

    # Action link
    action_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Read status
    is_read: Mapped[bool] = mapped_column(default=False, nullable=False, index=True)

    # Notification channel preferences
    send_email: Mapped[bool] = mapped_column(default=False, nullable=False)
    send_sms: Mapped[bool] = mapped_column(default=False, nullable=False)
    send_push: Mapped[bool] = mapped_column(default=True, nullable=False)

    # Relationships
    business: Mapped["Business"] = relationship("Business", back_populates="notifications")
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id])

    def __repr__(self) -> str:
        return f"<Notification {self.title}>"
