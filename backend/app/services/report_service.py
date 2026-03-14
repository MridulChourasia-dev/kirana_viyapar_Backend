"""
Report Service – aggregated SQL queries for Sales, P&L, and Inventory reports.
All queries are tenant-scoped via tenant_id.
"""

import uuid
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.reports import (
    SalesReport, MonthlyDataPoint, TopCustomer, TopProduct,
    PnLReport, MonthlyPnL,
    InventoryReport, CategoryStock, LowStockProduct, FastMovingProduct,
)


# ─────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────

def _month_label(ym: str) -> str:
    """Convert '2026-01' → 'Jan 2026'"""
    try:
        dt = datetime.strptime(ym, "%Y-%m")
        return dt.strftime("%b %Y")
    except Exception:
        return ym


def _build_month_series(rows: list[dict], value_key: str, months: int) -> list[MonthlyDataPoint]:
    """Fill gaps in monthly series so every month in [now-months+1 .. now] appears."""
    now = datetime.now(timezone.utc)
    month_map = {r["month"]: float(r[value_key] or 0) for r in rows}
    result = []
    for i in range(months - 1, -1, -1):
        dt = now - relativedelta(months=i)
        ym = dt.strftime("%Y-%m")
        result.append(MonthlyDataPoint(
            month=ym,
            label=_month_label(ym),
            value=month_map.get(ym, 0.0),
        ))
    return result


# ─────────────────────────────────────────
# Sales Report
# ─────────────────────────────────────────

class ReportService:

    @staticmethod
    async def sales_report(
        tenant_id: uuid.UUID,
        db: AsyncSession,
        months: int = 12,
    ) -> SalesReport:

        tid = str(tenant_id)
        since = datetime.now(timezone.utc) - relativedelta(months=months)
        since_str = since.strftime("%Y-%m-%d")

        # ── KPIs ──
        kpi_sql = text("""
            SELECT
                COUNT(*)                                                            AS total_invoices,
                COALESCE(SUM(grand_total), 0)                                       AS total_revenue,
                COALESCE(SUM(amount_paid), 0)                                       AS total_paid,
                COALESCE(SUM(amount_due), 0)                                        AS outstanding_amount,
                COALESCE(SUM(CASE WHEN status = 'paid' THEN 1 ELSE 0 END), 0)      AS paid_invoices,

                COALESCE(SUM(CASE WHEN status = 'draft'        THEN grand_total ELSE 0 END), 0) AS draft_amount,
                COALESCE(SUM(CASE WHEN status = 'sent'         THEN grand_total ELSE 0 END), 0) AS sent_amount,
                COALESCE(SUM(CASE WHEN status = 'paid'         THEN grand_total ELSE 0 END), 0) AS paid_amount,
                COALESCE(SUM(CASE WHEN status = 'partially_paid' THEN grand_total ELSE 0 END), 0) AS partially_paid_amount,
                COALESCE(SUM(CASE WHEN status = 'overdue'      THEN grand_total ELSE 0 END), 0) AS overdue_amount,
                COALESCE(SUM(CASE WHEN status = 'cancelled'    THEN grand_total ELSE 0 END), 0) AS cancelled_amount
            FROM invoices
            WHERE tenant_id = :tid
              AND status != 'cancelled'
              AND invoice_date >= :since
        """)
        kpi = (await db.execute(kpi_sql, {"tid": tid, "since": since_str})).mappings().one()

        total_revenue = float(kpi["total_revenue"] or 0)
        total_paid = float(kpi["total_paid"] or 0)
        avg_value = total_revenue / max(int(kpi["total_invoices"]), 1)
        collection_rate = (total_paid / total_revenue * 100) if total_revenue > 0 else 0.0

        # ── Monthly Revenue ──
        monthly_sql = text("""
            SELECT
                TO_CHAR(DATE_TRUNC('month', invoice_date::date), 'YYYY-MM') AS month,
                COALESCE(SUM(grand_total), 0)                                AS value
            FROM invoices
            WHERE tenant_id = :tid
              AND status != 'cancelled'
              AND invoice_date >= :since
            GROUP BY 1
            ORDER BY 1
        """)
        monthly_rows = (await db.execute(monthly_sql, {"tid": tid, "since": since_str})).mappings().all()
        monthly_revenue = _build_month_series(monthly_rows, "value", months)

        # ── Top Customers ──
        cust_sql = text("""
            SELECT
                customer_name,
                COUNT(*)                    AS invoice_count,
                COALESCE(SUM(grand_total), 0) AS total_revenue
            FROM invoices
            WHERE tenant_id = :tid
              AND status != 'cancelled'
              AND invoice_date >= :since
            GROUP BY customer_name
            ORDER BY total_revenue DESC
            LIMIT 10
        """)
        cust_rows = (await db.execute(cust_sql, {"tid": tid, "since": since_str})).mappings().all()
        top_customers = [
            TopCustomer(
                customer_name=r["customer_name"],
                invoice_count=int(r["invoice_count"]),
                total_revenue=float(r["total_revenue"]),
            )
            for r in cust_rows
        ]

        # ── Top Products ──
        prod_sql = text("""
            SELECT
                ii.product_name,
                COALESCE(SUM(ii.quantity), 0)         AS quantity_sold,
                COALESCE(SUM(ii.line_total), 0)        AS total_revenue
            FROM invoice_items ii
            JOIN invoices inv ON inv.id = ii.invoice_id
            WHERE inv.tenant_id = :tid
              AND inv.status != 'cancelled'
              AND inv.invoice_date >= :since
            GROUP BY ii.product_name
            ORDER BY total_revenue DESC
            LIMIT 10
        """)
        prod_rows = (await db.execute(prod_sql, {"tid": tid, "since": since_str})).mappings().all()
        top_products = [
            TopProduct(
                product_name=r["product_name"],
                quantity_sold=float(r["quantity_sold"]),
                total_revenue=float(r["total_revenue"]),
            )
            for r in prod_rows
        ]

        return SalesReport(
            total_revenue=total_revenue,
            total_invoices=int(kpi["total_invoices"]),
            paid_invoices=int(kpi["paid_invoices"]),
            outstanding_amount=float(kpi["outstanding_amount"] or 0),
            average_invoice_value=avg_value,
            collection_rate=collection_rate,
            draft_amount=float(kpi["draft_amount"]),
            sent_amount=float(kpi["sent_amount"]),
            paid_amount=float(kpi["paid_amount"]),
            partially_paid_amount=float(kpi["partially_paid_amount"]),
            overdue_amount=float(kpi["overdue_amount"]),
            cancelled_amount=float(kpi["cancelled_amount"]),
            monthly_revenue=monthly_revenue,
            top_customers=top_customers,
            top_products=top_products,
            period_months=months,
        )

    # ─────────────────────────────────────────
    # Profit & Loss Report
    # ─────────────────────────────────────────

    @staticmethod
    async def pnl_report(
        tenant_id: uuid.UUID,
        db: AsyncSession,
        months: int = 12,
    ) -> PnLReport:

        tid = str(tenant_id)
        since = datetime.now(timezone.utc) - relativedelta(months=months)
        since_str = since.strftime("%Y-%m-%d")

        # ── Totals ──
        totals_sql = text("""
            SELECT
                COALESCE(SUM(inv.grand_total), 0)        AS total_revenue,
                COALESCE(SUM(inv.total_cgst), 0)         AS total_cgst,
                COALESCE(SUM(inv.total_sgst), 0)         AS total_sgst,
                COALESCE(SUM(inv.total_igst), 0)         AS total_igst,
                COALESCE(SUM(inv.total_tax), 0)          AS total_tax,
                COALESCE(SUM(inv.discount_amount), 0)    AS total_discounts,
                COALESCE(SUM(
                    ii.quantity * COALESCE(p.purchase_price, 0)
                ), 0)                                    AS total_cogs
            FROM invoices inv
            JOIN invoice_items ii ON ii.invoice_id = inv.id
            LEFT JOIN products p  ON p.id = ii.product_id
            WHERE inv.tenant_id = :tid
              AND inv.status != 'cancelled'
              AND inv.invoice_date >= :since
        """)
        totals = (await db.execute(totals_sql, {"tid": tid, "since": since_str})).mappings().one()

        total_revenue = float(totals["total_revenue"] or 0)
        total_cogs = float(totals["total_cogs"] or 0)
        gross_profit = total_revenue - total_cogs
        gross_margin = (gross_profit / total_revenue * 100) if total_revenue > 0 else 0.0

        # ── Monthly P&L ──
        monthly_pnl_sql = text("""
            SELECT
                TO_CHAR(DATE_TRUNC('month', inv.invoice_date::date), 'YYYY-MM') AS month,
                COALESCE(SUM(inv.grand_total), 0)                               AS revenue,
                COALESCE(SUM(ii.quantity * COALESCE(p.purchase_price, 0)), 0)   AS cogs
            FROM invoices inv
            JOIN invoice_items ii ON ii.invoice_id = inv.id
            LEFT JOIN products p  ON p.id = ii.product_id
            WHERE inv.tenant_id = :tid
              AND inv.status != 'cancelled'
              AND inv.invoice_date >= :since
            GROUP BY 1
            ORDER BY 1
        """)
        monthly_rows = (await db.execute(monthly_pnl_sql, {"tid": tid, "since": since_str})).mappings().all()

        # Build complete month series
        now = datetime.now(timezone.utc)
        month_map = {
            r["month"]: {"revenue": float(r["revenue"] or 0), "cogs": float(r["cogs"] or 0)}
            for r in monthly_rows
        }
        monthly_pnl = []
        from dateutil.relativedelta import relativedelta as rd
        for i in range(months - 1, -1, -1):
            dt = now - rd(months=i)
            ym = dt.strftime("%Y-%m")
            rev = month_map.get(ym, {}).get("revenue", 0.0)
            cogs = month_map.get(ym, {}).get("cogs", 0.0)
            gp = rev - cogs
            gm = (gp / rev * 100) if rev > 0 else 0.0
            monthly_pnl.append(MonthlyPnL(
                month=ym,
                label=_month_label(ym),
                revenue=rev,
                cogs=cogs,
                gross_profit=gp,
                gross_margin_pct=gm,
            ))

        return PnLReport(
            total_revenue=total_revenue,
            total_cogs=total_cogs,
            gross_profit=gross_profit,
            gross_margin_pct=gross_margin,
            total_cgst_collected=float(totals["total_cgst"] or 0),
            total_sgst_collected=float(totals["total_sgst"] or 0),
            total_igst_collected=float(totals["total_igst"] or 0),
            total_tax_collected=float(totals["total_tax"] or 0),
            total_discounts=float(totals["total_discounts"] or 0),
            monthly_pnl=monthly_pnl,
            period_months=months,
        )

    # ─────────────────────────────────────────
    # Inventory Report
    # ─────────────────────────────────────────

    @staticmethod
    async def inventory_report(
        tenant_id: uuid.UUID,
        db: AsyncSession,
    ) -> InventoryReport:

        tid = str(tenant_id)

        # ── KPIs ──
        kpi_sql = text("""
            SELECT
                COUNT(*)                                                                  AS total_products,
                COALESCE(SUM(CASE WHEN is_active THEN 1 ELSE 0 END), 0)                  AS active_products,
                COALESCE(SUM(CASE WHEN stock_quantity <= low_stock_alert AND stock_quantity > 0 THEN 1 ELSE 0 END), 0)
                                                                                          AS low_stock_count,
                COALESCE(SUM(CASE WHEN stock_quantity = 0 THEN 1 ELSE 0 END), 0)         AS out_of_stock_count,
                COALESCE(SUM(stock_quantity * purchase_price), 0)                         AS total_stock_value,
                COALESCE(SUM(stock_quantity * sale_price), 0)                             AS total_retail_value
            FROM products
            WHERE tenant_id = :tid
        """)
        kpi = (await db.execute(kpi_sql, {"tid": tid})).mappings().one()

        # ── By Category ──
        cat_sql = text("""
            SELECT
                COALESCE(c.name, 'Uncategorised')          AS category_name,
                COUNT(p.id)                                AS product_count,
                COALESCE(SUM(p.stock_quantity), 0)         AS total_stock,
                COALESCE(SUM(p.stock_quantity * p.purchase_price), 0) AS stock_value
            FROM products p
            LEFT JOIN categories c ON c.id = p.category_id
            WHERE p.tenant_id = :tid
            GROUP BY COALESCE(c.name, 'Uncategorised')
            ORDER BY stock_value DESC
        """)
        cat_rows = (await db.execute(cat_sql, {"tid": tid})).mappings().all()
        by_category = [
            CategoryStock(
                category_name=r["category_name"],
                product_count=int(r["product_count"]),
                total_stock=int(r["total_stock"]),
                stock_value=float(r["stock_value"]),
            )
            for r in cat_rows
        ]

        # ── Low Stock ──
        low_sql = text("""
            SELECT
                p.name                                     AS product_name,
                p.sku,
                p.stock_quantity,
                p.low_stock_alert,
                COALESCE(c.name, 'Uncategorised')          AS category_name
            FROM products p
            LEFT JOIN categories c ON c.id = p.category_id
            WHERE p.tenant_id = :tid
              AND p.stock_quantity <= p.low_stock_alert
              AND p.is_active = TRUE
            ORDER BY p.stock_quantity ASC
            LIMIT 20
        """)
        low_rows = (await db.execute(low_sql, {"tid": tid})).mappings().all()
        low_stock_products = [
            LowStockProduct(
                product_name=r["product_name"],
                sku=r["sku"],
                stock_quantity=int(r["stock_quantity"]),
                low_stock_alert=int(r["low_stock_alert"]),
                category_name=r["category_name"],
            )
            for r in low_rows
        ]

        # ── Fast Moving ──
        fast_sql = text("""
            SELECT
                ii.product_name,
                p.sku,
                COALESCE(SUM(ii.quantity), 0)  AS total_sold,
                COALESCE(p.stock_quantity, 0)  AS stock_quantity
            FROM invoice_items ii
            JOIN invoices inv         ON inv.id = ii.invoice_id
            LEFT JOIN products p      ON p.id = ii.product_id
            WHERE inv.tenant_id = :tid
              AND inv.status != 'cancelled'
              AND inv.invoice_date >= :since
            GROUP BY ii.product_name, p.sku, p.stock_quantity
            ORDER BY total_sold DESC
            LIMIT 10
        """)
        since_30 = (datetime.now(timezone.utc) - relativedelta(months=3)).strftime("%Y-%m-%d")
        fast_rows = (await db.execute(fast_sql, {"tid": tid, "since": since_30})).mappings().all()
        fast_moving_products = [
            FastMovingProduct(
                product_name=r["product_name"],
                sku=r["sku"],
                total_sold=float(r["total_sold"]),
                stock_quantity=int(r["stock_quantity"]),
            )
            for r in fast_rows
        ]

        # ── Stock movements this month ──
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-01")
        movement_sql = text("""
            SELECT
                COALESCE(SUM(CASE WHEN movement_type = 'stock_in'  THEN quantity ELSE 0 END), 0) AS stock_in,
                COALESCE(SUM(CASE WHEN movement_type = 'stock_out' THEN quantity ELSE 0 END), 0) AS stock_out
            FROM stock_movements
            WHERE tenant_id = :tid
              AND created_at >= :since
        """)
        mov = (await db.execute(movement_sql, {"tid": tid, "since": now_str})).mappings().one()

        return InventoryReport(
            total_products=int(kpi["total_products"]),
            active_products=int(kpi["active_products"]),
            low_stock_count=int(kpi["low_stock_count"]),
            out_of_stock_count=int(kpi["out_of_stock_count"]),
            total_stock_value=float(kpi["total_stock_value"] or 0),
            total_retail_value=float(kpi["total_retail_value"] or 0),
            by_category=by_category,
            low_stock_products=low_stock_products,
            fast_moving_products=fast_moving_products,
            stock_in_this_month=int(mov["stock_in"]),
            stock_out_this_month=int(mov["stock_out"]),
        )
