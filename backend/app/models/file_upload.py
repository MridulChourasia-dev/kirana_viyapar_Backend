"""
FileUpload model - track uploaded files
"""
import uuid

from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class FileUpload(Base):
    """
    FileUpload model - tracks uploaded files (receipts, invoices, documents, images)
    """

    __tablename__ = "file_upload"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    business_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("business.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # File metadata
    original_filename: Mapped[str] = mapped_column(String(500), nullable=False)
    stored_filename: Mapped[str] = mapped_column(String(500), nullable=False, unique=True)

    # File info
    file_type: Mapped[str] = mapped_column(String(50), nullable=False)  # mime type
    file_size: Mapped[int] = mapped_column(nullable=False)  # bytes
    extension: Mapped[str] = mapped_column(String(10), nullable=False)  # .pdf, .jpg, etc

    # Storage location
    storage_path: Mapped[str] = mapped_column(String(500), nullable=False)  # local or S3 path
    storage_type: Mapped[str] = mapped_column(String(50), default="local", nullable=False)  # local, s3, etc

    # Access and expiry
    is_public: Mapped[bool] = mapped_column(default=False, nullable=False)
    expiry_days: Mapped[int | None] = mapped_column(nullable=True)  # auto-delete after X days

    # Related entity (optional)
    entity_type: Mapped[str | None] = mapped_column(String(50), nullable=True)  # invoice, product, etc
    entity_id: Mapped[uuid.UUID | None] = mapped_column(nullable=True, index=True)

    # Relationships
    business: Mapped["Business"] = relationship("Business")
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id])

    def __repr__(self) -> str:
        return f"<FileUpload {self.original_filename}>"
