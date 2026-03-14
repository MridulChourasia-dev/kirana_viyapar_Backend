from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.middleware.auth import get_current_user_context, TokenData
from app.schemas.invoice import (
    InvoiceCreate, InvoiceUpdate,
    InvoiceResponse, InvoiceListResponse, InvoiceSummary,
)
from app.services.invoice_service import InvoiceService
from app.core.openapi_docs import (
    RESPONSES_CREATE, RESPONSES_READ, RESPONSES_LIST, RESPONSES_UPDATE, RESPONSES_DELETE, RESPONSES_ACTION
)

# ─────────────────────────────────────────
# Invoice Router
# ─────────────────────────────────────────

router = APIRouter(prefix="/invoices", tags=["Invoices"])


@router.get(
    "/summary",
    response_model=InvoiceSummary,
    summary="Invoice Summary",
    description="Get key invoice metrics and KPIs",
    responses=RESPONSES_ACTION,
)
async def invoice_summary(
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """
    Get invoice KPIs: total revenue, outstanding, counts.
    
    Returns:
    - **total_revenue**: Sum of all paid invoices
    - **outstanding**: Total amount overdue
    - **total_invoices**: Count of invoices
    - **paid_invoices**: Count of fully paid invoices
    """
    return await InvoiceService.get_summary(user.tenant_id, db)


@router.post(
    "/",
    response_model=InvoiceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Invoice",
    description="Create a new invoice with line items and tax calculation",
    responses=RESPONSES_CREATE,
)
async def create_invoice(
    payload: InvoiceCreate,
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new invoice with line items and GST calculation.
    
    Args:
    - **customer_id**: ID of the customer
    - **issue_date**: Invoice issue date
    - **due_date**: Payment due date
    - **items**: Array of line items with product, quantity, price
    - **notes**: Additional notes for invoice
    """
    return await InvoiceService.create(user.tenant_id, payload, user.user_id, db)


@router.get(
    "/",
    response_model=InvoiceListResponse,
    summary="List Invoices",
    description="Retrieve paginated invoices with search and filtering",
    responses=RESPONSES_LIST,
)
async def list_invoices(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    search: str | None = Query(None, max_length=100, description="Search by invoice number or customer name"),
    status: str | None = Query(None, description="Filter by status: draft|sent|paid|partially_paid|overdue|cancelled"),
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """
    List invoices with pagination, search, and status filter.
    
    Query Parameters:
    - **page**: Page number
    - **per_page**: Items per page
    - **search**: Search by number or customer name
    - **status**: Filter by invoice status
    """
    return await InvoiceService.list(user.tenant_id, db, page, per_page, search, status)


@router.get(
    "/{invoice_id}",
    response_model=InvoiceResponse,
    summary="Get Invoice Details",
    description="Retrieve a single invoice with all line items",
    responses=RESPONSES_READ,
)
async def get_invoice(
    invoice_id: str,
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """Get a single invoice with all line items and GST breakdown."""
    return await InvoiceService.get_by_id(user.tenant_id, invoice_id, db)


@router.patch(
    "/{invoice_id}",
    response_model=InvoiceResponse,
    summary="Update Invoice",
    description="Update invoice status, payment, or details",
    responses=RESPONSES_UPDATE,
)
async def update_invoice(
    invoice_id: str,
    payload: InvoiceUpdate,
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """Update invoice status, payment amount, due date, notes."""
    return await InvoiceService.update(user.tenant_id, invoice_id, payload, db)


@router.delete(
    "/{invoice_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Cancel Invoice",
    description="Cancel an invoice (sets status to cancelled)",
    responses=RESPONSES_DELETE,
)
async def cancel_invoice(
    invoice_id: str,
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """Cancel an invoice (sets status to 'cancelled')."""
    await InvoiceService.delete(user.tenant_id, invoice_id, db)
