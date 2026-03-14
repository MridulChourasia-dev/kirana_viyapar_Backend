"""
Expense and ExpenseCategory models for business expenses
"""
import uuid
from datetime import date

from sqlalchemy import ForeignKey, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class ExpenseCategory(Base):
    """
    ExpenseCategory model - categories for business expenses
    """

    __tablename__ = "expense_category"
    __table_args__ = (UniqueConstraint("business_id", "name", name="uq_business_expense_category_name"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    business_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("business.id", ondelete="CASCADE"), nullable=False, index=True
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    business: Mapped["Business"] = relationship("Business")
    expenses: Mapped[list["Expense"]] = relationship(
        "Expense", back_populates="category", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<ExpenseCategory {self.name}>"


class Expense(Base):
    """
    Expense model - records business expenses (utilities, rent, salaries, etc.)
    """

    __tablename__ = "expense"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    business_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("business.id", ondelete="CASCADE"), nullable=False, index=True
    )
    category_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("expense_category.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    vendor_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("vendor.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # Expense details
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    expense_date: Mapped[date] = mapped_column(nullable=False, index=True)

    # Payment method
    payment_method: Mapped[str] = mapped_column(String(50), nullable=False)  # cash, check, transfer, card
    reference: Mapped[str | None] = mapped_column(String(100), nullable=True)  # cheque no, UTR, etc

    # Tax (if applicable)
    tax_amount: Mapped[float] = mapped_column(Numeric(14, 2), default=0.00, nullable=False)
    has_gst: Mapped[bool] = mapped_column(default=False, nullable=False)

    # Notes
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    business: Mapped["Business"] = relationship("Business")
    category: Mapped["ExpenseCategory"] = relationship("ExpenseCategory", back_populates="expenses")
    vendor: Mapped["Vendor | None"] = relationship("Vendor")

    def __repr__(self) -> str:
        return f"<Expense {self.description} ₹{self.amount}>"
