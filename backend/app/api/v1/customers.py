from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.middleware.auth import get_current_user_context, TokenData
from app.schemas.customer import (
    CustomerCreate, CustomerUpdate, CustomerResponse, CustomerListResponse,
)
from app.services.customer_service import CustomerService

# ─────────────────────────────────────────
# Customer Router
# ─────────────────────────────────────────

router = APIRouter(prefix="/customers", tags=["Customers"])

@router.post("/", response_model=CustomerResponse, status_code=201)
async def create_customer(
    payload: CustomerCreate,
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """Create a new customer for the current tenant."""
    return await CustomerService.create(user.tenant_id, payload, db)

@router.get("/", response_model=CustomerListResponse)
async def list_customers(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: str | None = Query(None, max_length=100),
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """List customers with pagination and search."""
    return await CustomerService.list(user.tenant_id, db, page, per_page, search)

@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(
    customer_id: str,
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """Get a single customer by ID."""
    return await CustomerService.get_by_id(user.tenant_id, customer_id, db)

@router.patch("/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    customer_id: str,
    payload: CustomerUpdate,
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """Partially update a customer."""
    return await CustomerService.update(user.tenant_id, customer_id, payload, db)

@router.delete("/{customer_id}", status_code=204)
async def delete_customer(
    customer_id: str,
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """Delete a customer."""
    await CustomerService.delete(user.tenant_id, customer_id, db)
