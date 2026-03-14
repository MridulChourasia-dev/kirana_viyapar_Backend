"""
Purchase and PurchaseItem models for purchase orders
"""
import enum
import uuid
from datetime import date

from sqlalchemy import Enum as SQLEnum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class PurchaseStatus(str, enum.Enum):
    """Purchase order status enumeration"""

    DRAFT = "draft"
    SENT = "sent"
    CONFIRMED = "confirmed"
    RECEIVED = "received"
    INVOICED = "invoiced"
    PAID = "paid"
    CANCELLED = "cancelled"


class Purchase(Base):
    """
    Purchase model - represents purchase orders from vendors
    """

    __tablename__ = "purchase"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    business_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("business.id", ondelete="CASCADE"), nullable=False, index=True
    )
    vendor_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("vendor.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # PO Number (auto-generated, e.g. PO-2026-0001)
    po_number: Mapped[str] = mapped_column(String(30), nullable=False, index=True, unique=True)

    # Vendor snapshot at PO creation time
    vendor_name: Mapped[str] = mapped_column(String(255), nullable=False)
    vendor_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    vendor_phone: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # Dates
    po_date: Mapped[date] = mapped_column(nullable=False)
    delivery_date: Mapped[date | None] = mapped_column(nullable=True)
    expected_delivery_date: Mapped[date | None] = mapped_column(nullable=True)

    # Status & Tracking
    status: Mapped[PurchaseStatus] = mapped_column(
        SQLEnum(PurchaseStatus), default=PurchaseStatus.DRAFT, nullable=False
    )

    # Financials
    subtotal: Mapped[float] = mapped_column(Numeric(14, 2), default=0.00, nullable=False)
    tax_amount: Mapped[float] = mapped_column(Numeric(14, 2), default=0.00, nullable=False)
    shipping_cost: Mapped[float] = mapped_column(Numeric(14, 2), default=0.00, nullable=False)
    total: Mapped[float] = mapped_column(Numeric(14, 2), default=0.00, nullable=False)
    amount_paid: Mapped[float] = mapped_column(Numeric(14, 2), default=0.00, nullable=False)
    amount_due: Mapped[float] = mapped_column(Numeric(14, 2), default=0.00, nullable=False)

    # Notes & Terms
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    terms: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    business: Mapped["Business"] = relationship("Business", back_populates="purchases")
    vendor: Mapped["Vendor"] = relationship("Vendor", back_populates="purchases")
    items: Mapped[list["PurchaseItem"]] = relationship(
        "PurchaseItem", back_populates="purchase", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Purchase {self.po_number}>"


class PurchaseItem(Base):
    """
    PurchaseItem model - line items in a purchase order
    """

    __tablename__ = "purchase_item"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    business_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("business.id", ondelete="CASCADE"), nullable=False, index=True
    )
    purchase_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("purchase.id", ondelete="CASCADE"), nullable=False, index=True
    )
    product_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("product.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # Item details
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit: Mapped[str] = mapped_column(String(50), nullable=False)  # piece, kg, box, etc.
    unit_cost: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)

    # Taxes
    tax_rate: Mapped[float] = mapped_column(Numeric(5, 2), default=0.00, nullable=False)  # %
    tax_amount: Mapped[float] = mapped_column(Numeric(12, 2), default=0.00, nullable=False)

    # Totals
    line_total: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)  # qty * unit_cost + tax

    # Received & Invoiced tracking
    quantity_received: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    quantity_invoiced: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationships
    business: Mapped["Business"] = relationship("Business", back_populates="purchase_items")
    purchase: Mapped["Purchase"] = relationship("Purchase", back_populates="items")
    product: Mapped["Product | None"] = relationship("Product")

    def __repr__(self) -> str:
        return f"<PurchaseItem {self.description}>"
