from pydantic import BaseModel, Field
from datetime import datetime

# ─────────────────────────────────────────
# Stock Movement Schemas
# ─────────────────────────────────────────

class StockInRequest(BaseModel):
    product_id: str
    quantity: int = Field(..., gt=0, examples=[50])
    reason: str = Field("purchase", examples=["purchase"])
    unit_cost: float | None = Field(None, ge=0, examples=[350.00])
    reference_id: str | None = Field(None, examples=["PO-2026-001"])
    notes: str | None = None

class StockOutRequest(BaseModel):
    product_id: str
    quantity: int = Field(..., gt=0, examples=[10])
    reason: str = Field("sale", examples=["sale"])
    reference_id: str | None = Field(None, examples=["INV-2026-042"])
    notes: str | None = None

class StockAdjustmentRequest(BaseModel):
    product_id: str
    new_quantity: int = Field(..., ge=0, examples=[95])
    reason: str = Field("correction", examples=["correction"])
    notes: str | None = Field(None, examples=["Physical count mismatch"])

# ─────────────────────────────────────────
# Response Schemas
# ─────────────────────────────────────────

class StockMovementResponse(BaseModel):
    id: str
    product_id: str
    product_name: str
    movement_type: str
    reason: str
    quantity: int
    stock_before: int
    stock_after: int
    unit_cost: float | None
    reference_id: str | None
    notes: str | None
    performed_by: str | None
    created_at: datetime

    class Config:
        from_attributes = True

class StockMovementListResponse(BaseModel):
    data: list[StockMovementResponse]
    total: int
    page: int
    per_page: int
    total_pages: int

class LowStockItem(BaseModel):
    product_id: str
    product_name: str
    sku: str | None
    current_stock: int
    low_stock_alert: int
    unit: str
    category_name: str | None

class InventoryDashboard(BaseModel):
    total_products: int
    total_stock_value: float
    low_stock_count: int
    out_of_stock_count: int
    low_stock_items: list[LowStockItem]
    recent_movements: list[StockMovementResponse]
