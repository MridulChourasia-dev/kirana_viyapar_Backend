"""
Purchase schemas for purchase orders
"""
import uuid
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class PurchaseItemCreateRequest(BaseModel):
    """Purchase item creation request"""

    product_id: uuid.UUID | None = None
    description: str = Field(..., min_length=1, max_length=500)
    quantity: int = Field(..., gt=0)
    unit: str = Field("pc", max_length=50)
    unit_cost: float = Field(..., gt=0)
    tax_rate: float = Field(0.0, ge=0, le=100)


class PurchaseItemResponse(BaseModel):
    """Purchase item response schema"""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    product_id: uuid.UUID | None
    description: str
    quantity: int
    unit: str
    unit_cost: float
    tax_rate: float
    tax_amount: float
    line_total: float
    quantity_received: int
    quantity_invoiced: int


class PurchaseCreateRequest(BaseModel):
    """Purchase creation request"""

    vendor_id: uuid.UUID
    po_date: date
    delivery_date: date | None = None
    expected_delivery_date: date | None = None
    items: list[PurchaseItemCreateRequest]
    shipping_cost: float = 0.0
    notes: str | None = None
    terms: str | None = None


class PurchaseUpdateRequest(BaseModel):
    """Purchase update request"""

    vendor_id: uuid.UUID | None = None
    po_date: date | None = None
    delivery_date: date | None = None
    expected_delivery_date: date | None = None
    status: str | None = None
    amount_paid: float | None = None
    notes: str | None = None
    terms: str | None = None


class PurchaseResponse(BaseModel):
    """Purchase response schema"""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    business_id: uuid.UUID
    vendor_id: uuid.UUID
    po_number: str
    vendor_name: str
    vendor_email: str | None
    vendor_phone: str | None
    po_date: date
    delivery_date: date | None
    expected_delivery_date: date | None
    status: str
    subtotal: float
    tax_amount: float
    shipping_cost: float
    total: float
    amount_paid: float
    amount_due: float
    notes: str | None
    terms: str | None
    items: list[PurchaseItemResponse] = []
    created_at: datetime
    updated_at: datetime


class PurchaseListResponse(BaseModel):
    """Purchase list response"""

    model_config = ConfigDict(from_attributes=True)

    data: list

    total: int
    page: int
    per_page: int
    total_pages: int


class PurchaseMinimalResponse(BaseModel):
    """Minimal purchase response"""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    po_number: str
    vendor_name: str
    po_date: date
    status: str
    total: float


# Aliases for backward compatibility
PurchaseCreate = PurchaseCreateRequest
PurchaseUpdate = PurchaseUpdateRequest
PurchaseItemCreate = PurchaseItemCreateRequest
