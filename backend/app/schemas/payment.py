from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


# ─────────────────────────────────────────
# Record a Payment
# ─────────────────────────────────────────

class PaymentCreate(BaseModel):
    invoice_id: str = Field(..., description="UUID of the invoice being paid")
    amount: float = Field(..., gt=0, description="Payment amount in ₹")
    method: str = Field("cash", examples=["cash", "upi", "bank_transfer", "cheque", "card", "other"])
    reference: Optional[str] = Field(None, max_length=100, examples=["UTR123456", "CHQ-001"])
    payment_date: str = Field(..., examples=["2026-03-13"], description="ISO date YYYY-MM-DD")
    notes: Optional[str] = Field(None, max_length=500)


# ─────────────────────────────────────────
# Payment Response
# ─────────────────────────────────────────

class PaymentResponse(BaseModel):
    id: str
    invoice_id: str
    customer_id: Optional[str]
    customer_name: str
    amount: float
    method: str
    reference: Optional[str]
    payment_date: str
    notes: Optional[str]

    invoice_number: str
    invoice_total: float
    balance_before: float
    balance_after: float

    created_at: datetime

    class Config:
        from_attributes = True


# ─────────────────────────────────────────
# Payment History (list)
# ─────────────────────────────────────────

class PaymentListResponse(BaseModel):
    data: List[PaymentResponse]
    total: int
    total_paid: float
    total_outstanding: float


# ─────────────────────────────────────────
# Customer Balance Summary
# ─────────────────────────────────────────

class CustomerInvoiceSummary(BaseModel):
    invoice_id: str
    invoice_number: str
    invoice_date: str
    due_date: Optional[str]
    status: str
    grand_total: float
    amount_paid: float
    amount_due: float


class CustomerBalanceResponse(BaseModel):
    customer_id: str
    customer_name: str
    phone: Optional[str]
    total_invoices: int
    total_billed: float
    total_paid: float
    total_outstanding: float
    overdue_amount: float
    last_payment_date: Optional[str]
    invoices: List[CustomerInvoiceSummary]
