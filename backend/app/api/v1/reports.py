from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.middleware.auth import get_current_user_context, TokenData
from app.schemas.reports import SalesReport, PnLReport, InventoryReport
from app.services.report_service import ReportService
from app.core.openapi_docs import RESPONSES_ACTION

# ─────────────────────────────────────────
# Reports Router
# ─────────────────────────────────────────

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get(
    "/sales",
    response_model=SalesReport,
    summary="Sales Report",
    description="Get sales KPIs with monthly trend and top performers",
    responses=RESPONSES_ACTION,
)
async def sales_report(
    months: int = Query(12, ge=1, le=36, description="Number of past months to analyze"),
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """
    Get sales analysis report with KPIs and trends.
    
    Query Parameters:
    - **months**: Analysis period in months (1-36, default 12)
    
    Returns:
    - **period**: Report period
    - **total_revenue**: Total sales revenue
    - **invoice_count**: Number of invoices
    - **monthly_trend**: Revenue by month
    - **top_customers**: Highest spending customers
    - **top_products**: Best selling products
    - **average_transaction**: Average invoice value
    """
    return await ReportService.sales_report(user.tenant_id, db, months)


@router.get(
    "/pnl",
    response_model=PnLReport,
    summary="Profit & Loss Report",
    description="Get P&L analysis with COGS, taxes, and profitability",
    responses=RESPONSES_ACTION,
)
async def pnl_report(
    months: int = Query(12, ge=1, le=36, description="Number of past months to analyze"),
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """
    Get profit and loss analysis for specified period.
    
    Query Parameters:
    - **months**: Analysis period in months (1-36, default 12)
    
    Returns:
    - **period**: Report period
    - **total_revenue**: Total revenue
    - **total_cogs**: Cost of goods sold
    - **gross_profit**: Gross profit amount and %
    - **expenses**: Operating expenses
    - **tax_collected**: GST collected
    - **net_profit**: Net profit/loss
    - **monthly_breakdown**: P&L by month
    """
    return await ReportService.pnl_report(user.tenant_id, db, months)


@router.get(
    "/inventory",
    response_model=InventoryReport,
    summary="Inventory Report",
    description="Get inventory metrics with stock levels and movement analysis",
    responses=RESPONSES_ACTION,
)
async def inventory_report(
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """
    Get comprehensive inventory analysis report.
    
    Returns:
    - **total_items**: Count of products
    - **total_value**: Total inventory value at cost
    - **total_valued_at**: Inventory value at selling price
    - **low_stock_count**: Products below reorder threshold
    - **category_breakdown**: Inventory value by category
    - **fast_movers**: Top selling products
    - **slow_movers**: Slow moving inventory
    - **movement_summary**: Stock in/out summary
    """
    return await ReportService.inventory_report(user.tenant_id, db)
