from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.middleware.auth import get_current_user_context, TokenData
from app.schemas.inventory import (
    StockInRequest, StockOutRequest, StockAdjustmentRequest,
    StockMovementResponse, StockMovementListResponse,
    LowStockItem, InventoryDashboard,
)
from app.services.inventory_service import InventoryService

# ─────────────────────────────────────────
# Inventory Router
# ─────────────────────────────────────────

router = APIRouter(prefix="/inventory", tags=["Inventory"])

@router.get("/dashboard", response_model=InventoryDashboard)
async def inventory_dashboard(
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """Get inventory dashboard: totals, stock value, low stock alerts, recent movements."""
    return await InventoryService.get_dashboard(user.tenant_id, db)

@router.post("/stock-in", response_model=StockMovementResponse, status_code=201)
async def stock_in(
    payload: StockInRequest,
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """Add stock to a product (purchase, return, opening stock)."""
    return await InventoryService.stock_in(user.tenant_id, payload, user.user_id, db)

@router.post("/stock-out", response_model=StockMovementResponse, status_code=201)
async def stock_out(
    payload: StockOutRequest,
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """Remove stock from a product (sale, damage, return out)."""
    return await InventoryService.stock_out(user.tenant_id, payload, user.user_id, db)

@router.post("/adjust", response_model=StockMovementResponse, status_code=201)
async def adjust_stock(
    payload: StockAdjustmentRequest,
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """Adjust stock to a new quantity (physical count correction)."""
    return await InventoryService.adjust_stock(user.tenant_id, payload, user.user_id, db)

@router.get("/history", response_model=StockMovementListResponse)
async def movement_history(
    product_id: str | None = Query(None),
    movement_type: str | None = Query(None, description="stock_in, stock_out, adjustment, return, damage"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """Get stock movement history with optional product and type filters."""
    return await InventoryService.get_history(user.tenant_id, db, product_id, movement_type, page, per_page)

@router.get("/low-stock", response_model=list[LowStockItem])
async def low_stock_alerts(
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """Get all products at or below their low stock threshold."""
    return await InventoryService.get_low_stock(user.tenant_id, db)
