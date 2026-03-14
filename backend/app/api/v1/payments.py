from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.middleware.auth import get_current_user_context, TokenData
from app.schemas.payment import (
    PaymentCreate, PaymentResponse, PaymentListResponse, CustomerBalanceResponse,
)
from app.services.payment_service import PaymentService
from app.core.openapi_docs import (
    RESPONSES_CREATE, RESPONSES_READ, RESPONSES_LIST
)

# ─────────────────────────────────────────
# Payment Router
# ─────────────────────────────────────────

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post(
    "/",
    response_model=PaymentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Record Payment",
    description="Record a payment against an invoice and update balances",
    responses=RESPONSES_CREATE,
)
async def create_payment(
    payload: PaymentCreate,
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """
    Record a payment against an invoice.
    
    Args:
    - **invoice_id**: Invoice ID to record payment for
    - **amount**: Payment amount
    - **payment_method**: Method used (cash|cheque|bank_transfer|credit_card|upi)
    - **reference_number**: Bank reference or cheque number
    - **notes**: Payment notes
    
    Returns:
    - **payment_id**: Unique payment identifier
    - **invoice_id**: Associated invoice
    - **amount**: Recorded payment amount
    - **status**: Payment status (completed|failed|pending)
    """
    return await PaymentService.create(user.tenant_id, payload, user.user_id, db)


@router.get(
    "/invoice/{invoice_id}",
    response_model=PaymentListResponse,
    summary="List Payments for Invoice",
    description="Get all payments made against a specific invoice",
    responses=RESPONSES_LIST,
)
async def list_payments_for_invoice(
    invoice_id: str,
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all payment records for an invoice.
    
    Returns:
    - **payments**: Array of payment records with dates and amounts
    - **total_paid**: Total payment amount recorded
    - **balance**: Remaining balance on invoice
    """
    return await PaymentService.list_by_invoice(user.tenant_id, invoice_id, db)


@router.get(
    "/",
    response_model=PaymentListResponse,
    summary="List Payments",
    description="Compatibility endpoint to list all payments for current business",
    responses=RESPONSES_LIST,
)
async def list_payments(
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """List all payments for the tenant."""
    return await PaymentService.list_all(user.tenant_id, db)


@router.get(
    "/{payment_id}",
    response_model=PaymentResponse,
    summary="Get Payment Details",
    description="Compatibility endpoint to fetch payment by ID",
    responses=RESPONSES_READ,
)
async def get_payment(
    payment_id: str,
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """Get a single payment by ID."""
    return await PaymentService.get_by_id(user.tenant_id, payment_id, db)


@router.get(
    "/customer/{customer_id}",
    response_model=CustomerBalanceResponse,
    summary="Customer Online Balance",
    description="Get customer's outstanding balance and payment summary",
    responses=RESPONSES_READ,
)
async def customer_balance(
    customer_id: str,
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """
    Get customer's outstanding balance and payment summary.
    
    Returns:
    - **customer_id**: Customer identifier
    - **total_outstanding**: Total amount due from customer
    - **overdue**: Amount past due date
    - **payment_summary**: Array of payments grouped by date
    """
    return await PaymentService.customer_balance(user.tenant_id, customer_id, db)
