from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.middleware.auth import get_current_user_context, TokenData
from app.schemas.customer import (
    CustomerCreate, CustomerUpdate, CustomerResponse, CustomerListResponse,
)
from app.services.customer_service import CustomerService
from app.core.openapi_docs import (
    RESPONSES_CREATE, RESPONSES_READ, RESPONSES_LIST, RESPONSES_UPDATE, RESPONSES_DELETE
)

# ─────────────────────────────────────────
# Customer Router
# ─────────────────────────────────────────

router = APIRouter(prefix="/customers", tags=["Customers"])

@router.post(
    "/",
    response_model=CustomerResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Customer",
    description="Create a new customer for the current business",
    responses=RESPONSES_CREATE,
)
async def create_customer(
    payload: CustomerCreate,
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new customer for the current tenant/business.
    
    Args:
    - **name**: Customer name (required)
    - **email**: Customer email address (optional)
    - **phone**: Customer phone number (optional)
    - **address**: Street address (optional)
    - **city**: City (optional)
    - **state**: State/Province (optional)
    - **postal_code**: Postal/ZIP code (optional)
    - **notes**: Additional notes about customer (optional)
    
    Returns: Created customer with ID and timestamp
    """
    return await CustomerService.create(user.tenant_id, payload, db)

@router.get(
    "/",
    response_model=CustomerListResponse,
    summary="List Customers",
    description="Retrieve paginated list of customers with optional search",
    responses=RESPONSES_LIST,
)
async def list_customers(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    search: str | None = Query(None, max_length=100, description="Search by name or email"),
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """
    List customers with pagination and search.
    
    Query Parameters:
    - **page**: Page number starting from 1
    - **per_page**: Number of items per page (1-100)
    - **search**: Optional search term for name/email
    
    Returns: Paginated list of customers with total count
    """
    return await CustomerService.list(user.tenant_id, db, page, per_page, search)

@router.get(
    "/{customer_id}",
    response_model=CustomerResponse,
    summary="Get Customer Details",
    description="Retrieve a single customer by ID",
    responses=RESPONSES_READ,
)
async def get_customer(
    customer_id: str = Path(..., description="Customer ID (UUID)"),
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """
    Get a single customer by ID.
    
    Args:
    - **customer_id**: UUID of the customer
    
    Returns: Customer object with all details
    """
    return await CustomerService.get_by_id(user.tenant_id, customer_id, db)

@router.patch(
    "/{customer_id}",
    response_model=CustomerResponse,
    summary="Update Customer",
    description="Partially update customer information",
    responses=RESPONSES_UPDATE,
)
async def update_customer(
    customer_id: str = Path(..., description="Customer ID (UUID)"),
    *,
    payload: CustomerUpdate,
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """
    Partially update a customer.
    
    Only provided fields will be updated. All fields are optional.
    
    Args:
    - **customer_id**: UUID of customer to update
    - **payload**: Fields to update
    
    Returns: Updated customer object
    """
    return await CustomerService.update(user.tenant_id, customer_id, payload, db)


@router.put(
    "/{customer_id}",
    response_model=CustomerResponse,
    summary="Update Customer (PUT Alias)",
    description="Compatibility alias for full customer update via PUT",
    responses=RESPONSES_UPDATE,
)
async def update_customer_put(
    customer_id: str = Path(..., description="Customer ID (UUID)"),
    *,
    payload: CustomerUpdate,
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """Compatibility alias for clients using PUT instead of PATCH."""
    return await CustomerService.update(user.tenant_id, customer_id, payload, db)

@router.delete(
    "/{customer_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Customer",
    description="Delete a customer",
    responses=RESPONSES_DELETE,
)
async def delete_customer(
    customer_id: str = Path(..., description="Customer ID (UUID)"),
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a customer.
    
    Args:
    - **customer_id**: UUID of customer to delete
    
    Returns: No content (204)
    """
    await CustomerService.delete(user.tenant_id, customer_id, db)
