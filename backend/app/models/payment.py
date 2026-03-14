"""
Payment model - payment records against invoices
"""
import enum
import uuid
from datetime import date

from sqlalchemy import Enum as SQLEnum, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class PaymentMethod(str, enum.Enum):
    """Payment method enumeration"""

    CASH = "cash"
    UPI = "upi"
    BANK_TRANSFER = "bank_transfer"
    CHEQUE = "cheque"
    CARD = "card"
    OTHER = "other"


class Payment(Base):
    """
    Payment model - represents a payment received against an invoice.
    Each row represents a single payment transaction.
    An invoice may have multiple partial payments over time.
    """

    __tablename__ = "payment"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    business_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("business.id", ondelete="CASCADE"), nullable=False, index=True
    )
    invoice_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("invoice.id", ondelete="CASCADE"), nullable=False, index=True
    )
    customer_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("customer.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # Snapshot data (for audit trail)
    customer_name: Mapped[str] = mapped_column(String(255), nullable=False)
    invoice_number: Mapped[str] = mapped_column(String(30), nullable=False)

    # Payment details
    amount: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    method: Mapped[PaymentMethod] = mapped_column(
        SQLEnum(PaymentMethod), default=PaymentMethod.CASH, nullable=False
    )
    payment_date: Mapped[date] = mapped_column(nullable=False)

    # Optional tracking
    reference: Mapped[str | None] = mapped_column(String(100), nullable=True)  # cheque no, UTR, etc.

    # Invoice state snapshot at payment time (for audit)
    invoice_total: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    balance_before: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    balance_after: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)

    # Optional notes
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    business: Mapped["Business"] = relationship("Business")
    invoice: Mapped["Invoice"] = relationship("Invoice", back_populates="payments")
    customer: Mapped["Customer | None"] = relationship("Customer")

    def __repr__(self) -> str:
        return f"<Payment INV-{self.invoice_number} ₹{self.amount}>"
