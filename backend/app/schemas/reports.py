from pydantic import BaseModel
from typing import List, Optional


# ─────────────────────────────────────────
# Shared
# ─────────────────────────────────────────

class MonthlyDataPoint(BaseModel):
    month: str          # "2026-01"
    label: str          # "Jan 2026"
    value: float


# ─────────────────────────────────────────
# Sales Report
# ─────────────────────────────────────────

class TopCustomer(BaseModel):
    customer_name: str
    invoice_count: int
    total_revenue: float


class TopProduct(BaseModel):
    product_name: str
    quantity_sold: float
    total_revenue: float


class SalesReport(BaseModel):
    # KPIs
    total_revenue: float
    total_invoices: int
    paid_invoices: int
    outstanding_amount: float
    average_invoice_value: float
    collection_rate: float          # paid / total revenue %

    # Breakdown by status
    draft_amount: float
    sent_amount: float
    paid_amount: float
    partially_paid_amount: float
    overdue_amount: float
    cancelled_amount: float

    # Time series
    monthly_revenue: List[MonthlyDataPoint]

    # Leaderboards
    top_customers: List[TopCustomer]
    top_products: List[TopProduct]

    # Period info
    period_months: int


# ─────────────────────────────────────────
# Profit & Loss Report
# ─────────────────────────────────────────

class MonthlyPnL(BaseModel):
    month: str
    label: str
    revenue: float
    cogs: float                     # purchase_price * qty sold
    gross_profit: float
    gross_margin_pct: float


class PnLReport(BaseModel):
    # Totals
    total_revenue: float
    total_cogs: float
    gross_profit: float
    gross_margin_pct: float

    # Tax collected
    total_cgst_collected: float
    total_sgst_collected: float
    total_igst_collected: float
    total_tax_collected: float

    # Discounts given
    total_discounts: float

    # Time series
    monthly_pnl: List[MonthlyPnL]

    # Period info
    period_months: int


# ─────────────────────────────────────────
# Inventory Report
# ─────────────────────────────────────────

class CategoryStock(BaseModel):
    category_name: str
    product_count: int
    total_stock: int
    stock_value: float              # stock_quantity * purchase_price


class LowStockProduct(BaseModel):
    product_name: str
    sku: Optional[str]
    stock_quantity: int
    low_stock_alert: int
    category_name: Optional[str]


class FastMovingProduct(BaseModel):
    product_name: str
    sku: Optional[str]
    total_sold: float
    stock_quantity: int


class InventoryReport(BaseModel):
    # KPIs
    total_products: int
    active_products: int
    low_stock_count: int
    out_of_stock_count: int
    total_stock_value: float        # sum(stock_qty * purchase_price)
    total_retail_value: float       # sum(stock_qty * sale_price)

    # Breakdown
    by_category: List[CategoryStock]
    low_stock_products: List[LowStockProduct]
    fast_moving_products: List[FastMovingProduct]

    # Stock movement this month
    stock_in_this_month: int
    stock_out_this_month: int
