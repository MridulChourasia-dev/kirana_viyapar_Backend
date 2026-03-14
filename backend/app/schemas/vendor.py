"""
Vendor schemas for purchase supplier management
"""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class VendorCreateRequest(BaseModel):
    """Vendor creation request"""

    name: str = Field(..., min_length=2, max_length=255)
    phone: str | None = Field(None, max_length=20)
    email: str | None = None
    website: str | None = None
    billing_address: str | None = None
    shipping_address: str | None = None
    city: str | None = None
    state: str | None = None
    country: str | None = None
    pincode: str | None = None
    gstin: str | None = Field(None, max_length=15)
    pan: str | None = Field(None, max_length=10)
    bank_account: str | None = None
    bank_name: str | None = None
    ifsc_code: str | None = None
    credit_limit: float = 0.00
    credit_period_days: int = 0
    notes: str | None = None


class VendorUpdateRequest(BaseModel):
    """Vendor update request"""

    name: str | None = None
    phone: str | None = None
    email: str | None = None
    website: str | None = None
    billing_address: str | None = None
    shipping_address: str | None = None
    city: str | None = None
    state: str | None = None
    country: str | None = None
    pincode: str | None = None
    gstin: str | None = None
    pan: str | None = None
    bank_account: str | None = None
    bank_name: str | None = None
    ifsc_code: str | None = None
    credit_limit: float | None = None
    credit_period_days: int | None = None
    is_active: bool | None = None
    notes: str | None = None


class VendorResponse(BaseModel):
    """Vendor response schema"""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    business_id: uuid.UUID
    name: str
    phone: str | None
    email: str | None
    website: str | None
    billing_address: str | None
    shipping_address: str | None
    city: str | None
    state: str | None
    country: str | None
    pincode: str | None
    gstin: str | None
    pan: str | None
    bank_account: str | None
    bank_name: str | None
    ifsc_code: str | None
    credit_limit: float
    credit_period_days: int
    is_active: bool
    notes: str | None
    created_at: datetime
    updated_at: datetime


class VendorListResponse(BaseModel):
    """Vendor list response"""

    model_config = ConfigDict(from_attributes=True)

    data: list
    total: int
    page: int
    per_page: int
    total_pages: int


class VendorMinimalResponse(BaseModel):
    """Minimal vendor response for relationships"""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    email: str | None
    phone: str | None


# Aliases for backward compatibility
VendorCreate = VendorCreateRequest
VendorUpdate = VendorUpdateRequest
