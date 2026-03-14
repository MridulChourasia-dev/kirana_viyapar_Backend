"""
Expense schemas for business expense tracking
"""
import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class ExpenseCategoryCreateRequest(BaseModel):
    """Expense category creation request"""

    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None


class ExpenseCategoryUpdateRequest(BaseModel):
    """Expense category update request"""

    name: str | None = None
    description: str | None = None


class ExpenseCategoryResponse(BaseModel):
    """Expense category response schema"""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    business_id: uuid.UUID
    name: str
    description: str | None
    created_at: datetime
    updated_at: datetime


class ExpenseCreateRequest(BaseModel):
    """Expense creation request"""

    category_id: uuid.UUID
    vendor_id: uuid.UUID | None = None
    description: str = Field(..., min_length=1, max_length=500)
    amount: float = Field(..., gt=0)
    expense_date: date
    payment_method: str = Field(..., max_length=50)
    reference: str | None = Field(None, max_length=100)
    tax_amount: float = 0.0
    has_gst: bool = False
    notes: str | None = None


class ExpenseUpdateRequest(BaseModel):
    """Expense update request"""

    category_id: uuid.UUID | None = None
    vendor_id: uuid.UUID | None = None
    description: str | None = None
    amount: float | None = None
    expense_date: date | None = None
    payment_method: str | None = None
    reference: str | None = None
    tax_amount: float | None = None
    has_gst: bool | None = None
    notes: str | None = None


class ExpenseResponse(BaseModel):
    """Expense response schema"""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    business_id: uuid.UUID
    category_id: uuid.UUID
    vendor_id: uuid.UUID | None
    description: str
    amount: float
    expense_date: date
    payment_method: str
    reference: str | None
    tax_amount: float
    has_gst: bool
    notes: str | None
    created_at: datetime
    updated_at: datetime


class ExpenseListResponse(BaseModel):
    """Expense list response"""

    model_config = ConfigDict(from_attributes=True)

    data: list

    total: int
    page: int
    per_page: int
    total_pages: int


class ExpenseMinimalResponse(BaseModel):
    """Minimal expense response"""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    description: str
    amount: float
    expense_date: date
    payment_method: str


# Aliases for backward compatibility
ExpenseCategoryCreate = ExpenseCategoryCreateRequest
ExpenseCategoryUpdate = ExpenseCategoryUpdateRequest
ExpenseCreate = ExpenseCreateRequest
ExpenseUpdate = ExpenseUpdateRequest
