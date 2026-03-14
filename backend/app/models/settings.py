"""
Settings model - configurable business and application settings
"""
import uuid

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class Settings(Base):
    """
    Settings model - stores configurable settings for business and application
    Key-value pairs for flexible configuration
    """

    __tablename__ = "settings"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    business_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("business.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Setting key and value
    key: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)

    # Category for grouping related settings
    category: Mapped[str] = mapped_column(
        String(100), 
        nullable=False, 
        index=True
    )  # billing, inventory, email, tax, etc.

    # Metadata
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    data_type: Mapped[str] = mapped_column(String(50), default="string", nullable=False)  # string, int, bool, json

    # Relationships
    business: Mapped["Business"] = relationship("Business", back_populates="settings")

    def __repr__(self) -> str:
        return f"<Settings {self.category}:{self.key}>"
