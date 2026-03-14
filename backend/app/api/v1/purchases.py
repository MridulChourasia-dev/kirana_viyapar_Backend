"""
Purchase API routes for purchase order management
"""
import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.middleware.auth import get_current_user_context, TokenData
from app.schemas.purchase import (
    PurchaseCreate,
    PurchaseUpdate,
    PurchaseResponse,
    PurchaseListResponse,
)
from app.services.purchase_service import PurchaseService
from app.core.openapi_docs import (
    RESPONSES_CREATE, RESPONSES_READ, RESPONSES_LIST, RESPONSES_UPDATE, RESPONSES_DELETE
)

# ─────────────────────────────────────────
# Purchase Router
# ─────────────────────────────────────────

router = APIRouter(prefix="/purchases", tags=["Purchases"])


@router.post(
    "/",
    response_model=PurchaseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Purchase Order",
    description="Create a new purchase order with line items",
    responses=RESPONSES_CREATE,
)
async def create_purchase(
    payload: PurchaseCreate,
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new purchase order.
    
    Args:
    - **vendor_id**: Supplier vendor ID
    - **po_date**: Purchase order date
    - **expected_delivery**: Expected delivery date
    - **items**: Array of purchase line items with product, quantity, unit_price
    - **notes**: Additional order notes
    
    Returns:
    - **po_id**: Auto-generated purchase order number
    - **vendor**: Vendor details
    - **items**: Line items with extended amounts
    - **total**: Order total with taxes
    """
    return await PurchaseService.create(user.tenant_id, payload, db)


@router.get(
    "/",
    response_model=PurchaseListResponse,
    summary="List Purchase Orders",
    description="Get purchase orders with pagination and status filtering",
    responses=RESPONSES_LIST,
)
async def list_purchases(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    status: str | None = Query(None, description="Filter by status: draft|sent|received|cancelled|partial"),
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """
    List purchase orders with pagination and filtering.
    
    Query Parameters:
    - **page**: Page number
    - **per_page**: Items per page
    - **status**: Filter by order status (draft, sent, received, etc.)
    """
    return await PurchaseService.list(user.tenant_id, db, page, per_page, status)


@router.get(
    "/{purchase_id}",
    response_model=PurchaseResponse,
    summary="Get Purchase Order",
    description="Retrieve a specific purchase order with all details",
    responses=RESPONSES_READ,
)
async def get_purchase(
    purchase_id: uuid.UUID,
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """Get purchase order details including vendor info and line items."""
    return await PurchaseService.get_by_id(user.tenant_id, purchase_id, db)


@router.patch(
    "/{purchase_id}",
    response_model=PurchaseResponse,
    summary="Update Purchase Order",
    description="Update PO status, dates, or line items",
    responses=RESPONSES_UPDATE,
)
async def update_purchase(
    purchase_id: uuid.UUID,
    payload: PurchaseUpdate,
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """Update purchase order terms, status, or expected delivery date."""
    return await PurchaseService.update(user.tenant_id, purchase_id, payload, db)


@router.delete(
    "/{purchase_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Purchase Order",
    description="Cancel or delete a purchase order",
    responses=RESPONSES_DELETE,
)
async def delete_purchase(
    purchase_id: uuid.UUID,
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """Delete or cancel a purchase order."""
    await PurchaseService.delete(user.tenant_id, purchase_id, db)
