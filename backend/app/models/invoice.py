"""
Invoice and invoice item models for billing
"""
import enum
import uuid
from datetime import date

from sqlalchemy import Boolean, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class InvoiceStatus(str, enum.Enum):
    """Invoice status enumeration"""

    DRAFT = "draft"
    SENT = "sent"
    PAID = "paid"
    PARTIALLY_PAID = "partially_paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class PaymentMode(str, enum.Enum):
    """Payment mode enumeration"""

    CASH = "cash"
    UPI = "upi"
    BANK_TRANSFER = "bank_transfer"
    CHEQUE = "cheque"
    CREDIT = "credit"
    OTHER = "other"


class Invoice(Base):
    """
    Invoice model - represents a sales invoice
    """

    __tablename__ = "invoice"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    business_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("business.id", ondelete="CASCADE"), nullable=False, index=True
    )
    customer_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("customer.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # Invoice Number (auto-generated, e.g. INV-2026-0001)
    invoice_number: Mapped[str] = mapped_column(String(30), nullable=False, index=True)

    # Customer snapshot (preserves data at invoice time)
    customer_name: Mapped[str] = mapped_column(String(255), nullable=False)
    customer_phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    customer_gstin: Mapped[str | None] = mapped_column(String(15), nullable=True)
    billing_address: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Status & Dates
    status: Mapped[str] = mapped_column(String(50), default=InvoiceStatus.DRAFT.value, nullable=False)
    invoice_date: Mapped[date] = mapped_column(nullable=False)
    due_date: Mapped[date | None] = mapped_column(nullable=True)

    # Financials (all stored as rupees with 2dp)
    subtotal: Mapped[float] = mapped_column(Numeric(14, 2), default=0.00, nullable=False)
    total_cgst: Mapped[float] = mapped_column(Numeric(14, 2), default=0.00, nullable=False)
    total_sgst: Mapped[float] = mapped_column(Numeric(14, 2), default=0.00, nullable=False)
    total_igst: Mapped[float] = mapped_column(Numeric(14, 2), default=0.00, nullable=False)
    total_tax: Mapped[float] = mapped_column(Numeric(14, 2), default=0.00, nullable=False)
    discount_amount: Mapped[float] = mapped_column(Numeric(14, 2), default=0.00, nullable=False)
    grand_total: Mapped[float] = mapped_column(Numeric(14, 2), default=0.00, nullable=False)
    amount_paid: Mapped[float] = mapped_column(Numeric(14, 2), default=0.00, nullable=False)
    amount_due: Mapped[float] = mapped_column(Numeric(14, 2), default=0.00, nullable=False)

    # GST type flag
    is_igst: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Payment
    payment_mode: Mapped[str] = mapped_column(String(50), default=PaymentMode.CASH.value, nullable=False)

    # Notes
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    terms: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    business: Mapped["Business"] = relationship("Business", back_populates="invoices")
    customer: Mapped["Customer | None"] = relationship("Customer", back_populates="invoices")
    items: Mapped[list["InvoiceItem"]] = relationship(
        "InvoiceItem", back_populates="invoice", cascade="all, delete-orphan"
    )
    payments: Mapped[list["Payment"]] = relationship(
        "Payment", back_populates="invoice", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Invoice {self.invoice_number}>"


class InvoiceItem(Base):
    """
    Invoice line item model - represents a product row in an invoice
    """

    __tablename__ = "invoice_item"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    invoice_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("invoice.id", ondelete="CASCADE"), nullable=False, index=True
    )
    product_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("product.id", ondelete="SET NULL"), nullable=True
    )

    # Snapshot fields (preserves data in case product is edited/deleted)
    product_name: Mapped[str] = mapped_column(String(255), nullable=False)
    hsn_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    unit: Mapped[str | None] = mapped_column(String(20), nullable=True)

    quantity: Mapped[float] = mapped_column(Numeric(12, 3), nullable=False)
    unit_price: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    tax_rate: Mapped[float] = mapped_column(Numeric(5, 2), default=0.00, nullable=False)
    discount_pct: Mapped[float] = mapped_column(Numeric(5, 2), default=0.00, nullable=False)

    # Computed fields (stored for audit trail)
    line_subtotal: Mapped[float] = mapped_column(Numeric(14, 2), default=0.00, nullable=False)
    line_discount: Mapped[float] = mapped_column(Numeric(14, 2), default=0.00, nullable=False)
    taxable_amount: Mapped[float] = mapped_column(Numeric(14, 2), default=0.00, nullable=False)
    line_cgst: Mapped[float] = mapped_column(Numeric(14, 2), default=0.00, nullable=False)
    line_sgst: Mapped[float] = mapped_column(Numeric(14, 2), default=0.00, nullable=False)
    line_igst: Mapped[float] = mapped_column(Numeric(14, 2), default=0.00, nullable=False)
    line_total: Mapped[float] = mapped_column(Numeric(14, 2), default=0.00, nullable=False)

    # Relationships
    invoice: Mapped["Invoice"] = relationship("Invoice", back_populates="items")
    product: Mapped["Product | None"] = relationship("Product", back_populates="invoice_items")

    def __repr__(self) -> str:
        return f"<InvoiceItem {self.product_name} x{self.quantity}>"
