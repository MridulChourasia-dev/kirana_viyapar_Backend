from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.middleware.auth import get_current_user_context, TokenData
from app.schemas.payment import (
    PaymentCreate, PaymentResponse, PaymentListResponse, CustomerBalanceResponse,
)
from app.services.payment_service import PaymentService

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post("/", response_model=PaymentResponse, status_code=201)
async def create_payment(
    payload: PaymentCreate,
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """Record a payment against an invoice and update invoice/customer balances."""
    return await PaymentService.create(user.tenant_id, payload, user.user_id, db)


@router.get("/invoice/{invoice_id}", response_model=PaymentListResponse)
async def list_payments_for_invoice(
    invoice_id: str,
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    return await PaymentService.list_by_invoice(user.tenant_id, invoice_id, db)


@router.get("/customer/{customer_id}", response_model=CustomerBalanceResponse)
async def customer_balance(
    customer_id: str,
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    return await PaymentService.customer_balance(user.tenant_id, customer_id, db)
