"""
Product model - business products/inventory
"""
import uuid

from sqlalchemy import Boolean, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class Product(Base):
    """
    Product model - represents products in inventory
    """

    __tablename__ = "product"
    __table_args__ = (UniqueConstraint("business_id", "sku", name="uq_business_product_sku"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    business_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("business.id", ondelete="CASCADE"), nullable=False, index=True
    )
    category_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("category.id", ondelete="SET NULL"), nullable=True, index=True
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    sku: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    barcode: Mapped[str | None] = mapped_column(String(50), nullable=True)
    hsn_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Pricing
    sale_price: Mapped[float] = mapped_column(Numeric(12, 2), default=0.00, nullable=False)
    purchase_price: Mapped[float] = mapped_column(Numeric(12, 2), default=0.00, nullable=False)
    tax_rate: Mapped[float] = mapped_column(Numeric(5, 2), default=0.00, nullable=False)  # GST %

    # Inventory
    stock_quantity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    low_stock_alert: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    unit: Mapped[str] = mapped_column(String(50), default="piece", nullable=False)

    # Media
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    business: Mapped["Business"] = relationship("Business", back_populates="products")
    category: Mapped["Category | None"] = relationship("Category", back_populates="products")
    invoice_items: Mapped[list["InvoiceItem"]] = relationship(
        "InvoiceItem", back_populates="product", cascade="all, delete-orphan"
    )
    stock_movements: Mapped[list["StockMovement"]] = relationship(
        "StockMovement", back_populates="product", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Product {self.name} ({self.sku})>"
