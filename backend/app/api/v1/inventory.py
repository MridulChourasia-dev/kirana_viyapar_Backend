from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.middleware.auth import get_current_user_context, TokenData
from app.schemas.inventory import (
    StockInRequest, StockOutRequest, StockAdjustmentRequest,
    StockMovementResponse, StockMovementListResponse,
    LowStockItem, InventoryDashboard,
)
from app.services.inventory_service import InventoryService
from app.core.openapi_docs import (
    RESPONSES_CREATE, RESPONSES_READ, RESPONSES_LIST, RESPONSES_ACTION
)

# ─────────────────────────────────────────
# Inventory Router
# ─────────────────────────────────────────

router = APIRouter(prefix="/inventory", tags=["Inventory"])


@router.get(
    "/dashboard",
    response_model=InventoryDashboard,
    summary="Inventory Dashboard",
    description="Get inventory overview with stock value and alerts",
    responses=RESPONSES_ACTION,
)
async def inventory_dashboard(
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """
    Get inventory dashboard with key metrics.
    
    Returns:
    - **total_items**: Count of products in inventory
    - **total_value**: Total inventory value at cost price
    - **stock_in**: Inbound stock this month
    - **stock_out**: Outbound stock this month
    - **low_stock_count**: Number of products below threshold
    """
    return await InventoryService.get_dashboard(user.tenant_id, db)


@router.post(
    "/stock-in",
    response_model=StockMovementResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add Stock",
    description="Record stock inbound movement (purchase, return, opening stock)",
    responses=RESPONSES_CREATE,
)
async def stock_in(
    payload: StockInRequest,
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """
    Add stock to a product.
    
    Args:
    - **product_id**: Product identifier
    - **quantity**: Quantity to add
    - **movement_type**: Type of inbound (stock_in|return|opening_stock|adjustment)
    - **reference**: Reference number (PO, invoice, etc.)
    - **notes**: Additional notes
    
    Returns:
    - **movement_id**: Unique movement record ID
    - **product_id**: Associated product
    - **quantity**: Quantity moved
    - **new_balance**: New stock quantity after movement
    """
    return await InventoryService.stock_in(user.tenant_id, payload, user.user_id, db)


@router.post(
    "/stock-out",
    response_model=StockMovementResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Remove Stock",
    description="Record stock outbound movement (sale, damage, return)",
    responses=RESPONSES_CREATE,
)
async def stock_out(
    payload: StockOutRequest,
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """
    Remove stock from a product.
    
    Args:
    - **product_id**: Product identifier
    - **quantity**: Quantity to remove
    - **movement_type**: Type of outbound (stock_out|damage|return|sale|waste)
    - **reference**: Reference number (invoice, RMA, etc.)
    - **notes**: Reason or additional details
    """
    return await InventoryService.stock_out(user.tenant_id, payload, user.user_id, db)


@router.post(
    "/adjust",
    response_model=StockMovementResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Adjust Stock",
    description="Correct stock to a physical count quantity",
    responses=RESPONSES_CREATE,
)
async def adjust_stock(
    payload: StockAdjustmentRequest,
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """
    Adjust stock quantity to match physical count.
    
    Args:
    - **product_id**: Product identifier
    - **new_quantity**: Corrected stock quantity
    - **reason**: Reason for adjustment (physical_count|inventory_check|correction)
    - **notes**: Detailed reason or audit notes
    """
    return await InventoryService.adjust_stock(user.tenant_id, payload, user.user_id, db)


@router.get(
    "/history",
    response_model=StockMovementListResponse,
    summary="Stock Movement History",
    description="Get stock movements with optional filtering",
    responses=RESPONSES_LIST,
)
async def movement_history(
    product_id: str | None = Query(None, description="Filter by product ID"),
    movement_type: str | None = Query(None, description="Filter by type: stock_in, stock_out, adjustment, return, damage"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """
    Get stock movement history with pagination and filters.
    
    Query Parameters:
    - **product_id**: Filter by specific product
    - **movement_type**: Filter by movement type
    - **page**: Page number
    - **per_page**: Items per page
    """
    return await InventoryService.get_history(user.tenant_id, db, product_id, movement_type, page, per_page)


@router.get(
    "/low-stock",
    response_model=list[LowStockItem],
    summary="Low Stock Alerts",
    description="Get all products at or below reorder threshold",
    responses=RESPONSES_READ,
)
async def low_stock_alerts(
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all products at or below low stock threshold.
    
    Returns:
    - **product_id**: Product identifier
    - **product_name**: Product name
    - **current_stock**: Current quantity
    - **low_stock_threshold**: Reorder point
    - **reorder_quantity**: Suggested purchase quantity
    """
    return await InventoryService.get_low_stock(user.tenant_id, db)
