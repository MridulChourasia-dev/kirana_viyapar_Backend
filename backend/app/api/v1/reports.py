from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.middleware.auth import get_current_user_context, TokenData
from app.schemas.reports import SalesReport, PnLReport, InventoryReport
from app.services.report_service import ReportService

# ─────────────────────────────────────────
# Reports Router
# ─────────────────────────────────────────

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/sales", response_model=SalesReport)
async def sales_report(
    months: int = Query(12, ge=1, le=36, description="Number of past months to analyse"),
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """
    Sales report – revenue KPIs, monthly trend, top customers & products.
    """
    return await ReportService.sales_report(user.tenant_id, db, months)


@router.get("/pnl", response_model=PnLReport)
async def pnl_report(
    months: int = Query(12, ge=1, le=36, description="Number of past months to analyse"),
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """
    Profit & Loss report – gross profit, COGS, tax collected, monthly P&L table.
    """
    return await ReportService.pnl_report(user.tenant_id, db, months)


@router.get("/inventory", response_model=InventoryReport)
async def inventory_report(
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """
    Inventory report – stock KPIs, low-stock alerts, category breakdown, fast movers.
    """
    return await ReportService.inventory_report(user.tenant_id, db)
