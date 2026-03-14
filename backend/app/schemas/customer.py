"""
Customer schemas
"""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CustomerCreateRequest(BaseModel):
    """Customer creation request"""

    name: str = Field(..., min_length=2, max_length=255)
    phone: str | None = Field(None, max_length=20)
    email: str | None = None
    gstin: str | None = Field(None, max_length=15)
    city: str | None = None
    state: str | None = None
    country: str | None = None
    pincode: str | None = None
    billing_address: str | None = None
    shipping_address: str | None = None
    notes: str | None = None


class CustomerUpdateRequest(BaseModel):
    """Customer update request"""

    name: str | None = None
    phone: str | None = None
    email: str | None = None
    gstin: str | None = None
    city: str | None = None
    state: str | None = None
    country: str | None = None
    pincode: str | None = None
    billing_address: str | None = None
    shipping_address: str | None = None
    notes: str | None = None


class CustomerResponse(BaseModel):
    """Customer response schema"""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    business_id: uuid.UUID
    name: str
    phone: str | None
    email: str | None
    gstin: str | None
    city: str | None
    state: str | None
    country: str | None
    pincode: str | None
    billing_address: str | None
    shipping_address: str | None
    balance: float
    notes: str | None
    created_at: datetime
    updated_at: datetime


class CustomerListResponse(BaseModel):
    """Customer list item response"""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    phone: str | None
    email: str | None
    city: str | None
    balance: float


# Aliases for backward compatibility
CustomerCreate = CustomerCreateRequest
CustomerUpdate = CustomerUpdateRequest
