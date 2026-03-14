from pydantic import BaseModel, Field
from datetime import datetime

# ─────────────────────────────────────────
# Category Schemas
# ─────────────────────────────────────────

class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, examples=["Electronics"])
    description: str | None = Field(None, max_length=500)

class CategoryUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None

class CategoryResponse(BaseModel):
    id: str
    name: str
    description: str | None
    created_at: datetime

    class Config:
        from_attributes = True

# ─────────────────────────────────────────
# Product Schemas
# ─────────────────────────────────────────

class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, examples=["Wireless Mouse"])
    sku: str | None = Field(None, max_length=50, examples=["WM-001"])
    hsn_code: str | None = Field(None, max_length=20, examples=["8471"])
    description: str | None = None
    sale_price: float = Field(0.00, ge=0, examples=[599.00])
    purchase_price: float = Field(0.00, ge=0, examples=[350.00])
    tax_rate: float = Field(0.00, ge=0, le=100, examples=[18.00])
    stock_quantity: int = Field(0, ge=0, examples=[100])
    low_stock_alert: int = Field(10, ge=0, examples=[10])
    unit: str = Field("piece", examples=["piece"])
    category_id: str | None = None
    is_active: bool = True

class ProductUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    sku: str | None = None
    hsn_code: str | None = None
    description: str | None = None
    sale_price: float | None = Field(None, ge=0)
    purchase_price: float | None = Field(None, ge=0)
    tax_rate: float | None = Field(None, ge=0, le=100)
    stock_quantity: int | None = Field(None, ge=0)
    low_stock_alert: int | None = Field(None, ge=0)
    unit: str | None = None
    category_id: str | None = None
    is_active: bool | None = None

class ProductResponse(BaseModel):
    id: str
    name: str
    sku: str | None
    hsn_code: str | None
    description: str | None
    sale_price: float
    purchase_price: float
    tax_rate: float
    stock_quantity: int
    low_stock_alert: int
    unit: str
    image_url: str | None
    is_active: bool
    category_id: str | None
    category_name: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ProductListResponse(BaseModel):
    data: list[ProductResponse]
    total: int
    page: int
    per_page: int
    total_pages: int
