from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


# ─────────────────────────────────────────
# Item Schemas
# ─────────────────────────────────────────

class InvoiceItemCreate(BaseModel):
    product_id: Optional[str] = None
    product_name: str = Field(..., min_length=1, examples=["Ashirvaad Atta 5kg"])
    hsn_code: Optional[str] = Field(None, examples=["1101"])
    unit: Optional[str] = Field(None, examples=["bag"])
    quantity: float = Field(..., gt=0, examples=[2.0])
    unit_price: float = Field(..., ge=0, examples=[250.00])
    tax_rate: float = Field(0.0, ge=0, le=100, examples=[18.0])
    discount_pct: float = Field(0.0, ge=0, le=100, examples=[5.0])


class InvoiceItemResponse(BaseModel):
    id: str
    product_id: Optional[str]
    product_name: str
    hsn_code: Optional[str]
    unit: Optional[str]
    quantity: float
    unit_price: float
    tax_rate: float
    discount_pct: float
    line_subtotal: float
    line_discount: float
    taxable_amount: float
    line_cgst: float
    line_sgst: float
    line_igst: float
    line_total: float

    class Config:
        from_attributes = True


# ─────────────────────────────────────────
# Invoice Create / Update Schemas
# ─────────────────────────────────────────

class InvoiceCreate(BaseModel):
    customer_id: Optional[str] = None
    customer_name: str = Field(..., min_length=1, examples=["Ravi Traders"])
    customer_phone: Optional[str] = Field(None, examples=["9876543210"])
    customer_gst: Optional[str] = Field(None, examples=["27AAPFU0939F1ZV"])
    billing_address: Optional[str] = None

    invoice_date: str = Field(..., examples=["2026-03-13"])
    due_date: Optional[str] = Field(None, examples=["2026-03-27"])

    is_igst: bool = Field(False, description="True for inter-state (IGST), False for intra-state (CGST+SGST)")
    discount_amount: float = Field(0.0, ge=0, description="Invoice-level discount in ₹")
    payment_mode: str = Field("cash", examples=["cash"])
    notes: Optional[str] = None
    terms: Optional[str] = None

    items: list[InvoiceItemCreate] = Field(..., min_length=1)


class InvoiceUpdate(BaseModel):
    status: Optional[str] = None
    due_date: Optional[str] = None
    amount_paid: Optional[float] = Field(None, ge=0)
    payment_mode: Optional[str] = None
    notes: Optional[str] = None
    terms: Optional[str] = None


# ─────────────────────────────────────────
# Response Schemas
# ─────────────────────────────────────────

class InvoiceResponse(BaseModel):
    id: str
    invoice_number: str
    customer_id: Optional[str]
    customer_name: str
    customer_phone: Optional[str]
    customer_gst: Optional[str]
    billing_address: Optional[str]

    status: str
    invoice_date: str
    due_date: Optional[str]

    subtotal: float
    total_cgst: float
    total_sgst: float
    total_igst: float
    total_tax: float
    discount_amount: float
    grand_total: float
    amount_paid: float
    amount_due: float

    is_igst: bool
    payment_mode: str
    notes: Optional[str]
    terms: Optional[str]

    items: list[InvoiceItemResponse] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class InvoiceListItem(BaseModel):
    """Lightweight response for list views (no items)."""
    id: str
    invoice_number: str
    customer_name: str
    customer_phone: Optional[str]
    status: str
    invoice_date: str
    due_date: Optional[str]
    grand_total: float
    amount_paid: float
    amount_due: float
    created_at: datetime

    class Config:
        from_attributes = True


class InvoiceListResponse(BaseModel):
    data: list[InvoiceListItem]
    total: int
    page: int
    per_page: int
    total_pages: int


# ─────────────────────────────────────────
# Dashboard / Summary
# ─────────────────────────────────────────

class InvoiceSummary(BaseModel):
    total_invoices: int
    total_revenue: float
    total_outstanding: float
    total_paid: float
    draft_count: int
    overdue_count: int
