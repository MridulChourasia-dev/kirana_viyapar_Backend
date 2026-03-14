"""
Stock movement model - inventory audit log
"""
import enum
import uuid

from sqlalchemy import Enum as SQLEnum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class MovementType(str, enum.Enum):
    """Stock movement types"""

    STOCK_IN = "stock_in"
    STOCK_OUT = "stock_out"
    ADJUSTMENT = "adjustment"
    RETURN = "return"
    DAMAGE = "damage"


class MovementReason(str, enum.Enum):
    """Reason for stock movement"""

    PURCHASE = "purchase"
    SALE = "sale"
    MANUAL = "manual"
    RETURN_IN = "return_in"
    RETURN_OUT = "return_out"
    DAMAGE = "damage"
    OPENING_STOCK = "opening_stock"
    CORRECTION = "correction"


class StockMovement(Base):
    """
    Stock movement model - complete audit log of inventory changes.
    Each row represents a single transaction affecting stock quantity.
    """

    __tablename__ = "stock_movement"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    business_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("business.id", ondelete="CASCADE"), nullable=False, index=True
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("product.id", ondelete="CASCADE"), nullable=False, index=True
    )

    movement_type: Mapped[MovementType] = mapped_column(
        SQLEnum(MovementType), nullable=False
    )
    reason: Mapped[MovementReason] = mapped_column(
        SQLEnum(MovementReason), default=MovementReason.MANUAL, nullable=False
    )

    quantity: Mapped[int] = mapped_column(Integer, nullable=False)  # Always positive
    stock_before: Mapped[int] = mapped_column(Integer, nullable=False)
    stock_after: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_cost: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)

    # Optional tracking
    reference_id: Mapped[str | None] = mapped_column(String(100), nullable=True)  # Invoice ID, PO ID
    performed_by: Mapped[uuid.UUID | None] = mapped_column(nullable=True)  # User ID
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    business: Mapped["Business"] = relationship("Business", back_populates="stock_movements")
    product: Mapped["Product"] = relationship("Product", back_populates="stock_movements")

    def __repr__(self) -> str:
        return f"<StockMovement {self.movement_type} qty={self.quantity}>"
