from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.middleware.auth import get_current_user_context, TokenData
from app.schemas.invoice import (
    InvoiceCreate, InvoiceUpdate,
    InvoiceResponse, InvoiceListResponse, InvoiceSummary,
)
from app.services.invoice_service import InvoiceService

# ─────────────────────────────────────────
# Invoice Router
# ─────────────────────────────────────────

router = APIRouter(prefix="/invoices", tags=["Invoices"])


@router.get("/summary", response_model=InvoiceSummary)
async def invoice_summary(
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """Get invoice KPIs: total revenue, outstanding, counts."""
    return await InvoiceService.get_summary(user.tenant_id, db)


@router.post("/", response_model=InvoiceResponse, status_code=201)
async def create_invoice(
    payload: InvoiceCreate,
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """Create a new invoice with line items and GST calculation."""
    return await InvoiceService.create(user.tenant_id, payload, user.user_id, db)


@router.get("/", response_model=InvoiceListResponse)
async def list_invoices(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: str | None = Query(None, max_length=100, description="Search by invoice number or customer name"),
    status: str | None = Query(None, description="draft|sent|paid|partially_paid|overdue|cancelled"),
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """List invoices with pagination, search, and status filter."""
    return await InvoiceService.list(user.tenant_id, db, page, per_page, search, status)


@router.get("/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice(
    invoice_id: str,
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """Get a single invoice with all line items and GST breakdown."""
    return await InvoiceService.get_by_id(user.tenant_id, invoice_id, db)


@router.patch("/{invoice_id}", response_model=InvoiceResponse)
async def update_invoice(
    invoice_id: str,
    payload: InvoiceUpdate,
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """Update invoice status, payment amount, due date, notes."""
    return await InvoiceService.update(user.tenant_id, invoice_id, payload, db)


@router.delete("/{invoice_id}", status_code=204)
async def cancel_invoice(
    invoice_id: str,
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """Cancel an invoice (sets status to 'cancelled')."""
    await InvoiceService.delete(user.tenant_id, invoice_id, db)
