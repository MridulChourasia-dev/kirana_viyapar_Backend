from fastapi import APIRouter, Depends, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.middleware.auth import get_current_user_context, TokenData
from app.schemas.product import (
    ProductCreate, ProductUpdate, ProductResponse, ProductListResponse,
    CategoryCreate, CategoryUpdate, CategoryResponse,
)
from app.services.product_service import ProductService, CategoryService

# ─────────────────────────────────────────
# Product Router
# ─────────────────────────────────────────

router = APIRouter(tags=["Products"])

# ─── Products ─────────────────────────────

@router.post("/products/", response_model=ProductResponse, status_code=201)
async def create_product(
    payload: ProductCreate,
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """Create a new product."""
    return await ProductService.create(user.tenant_id, payload, db)

@router.get("/products/", response_model=ProductListResponse)
async def list_products(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: str | None = Query(None, max_length=100),
    category_id: str | None = Query(None),
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """List products with pagination, search, and category filter."""
    return await ProductService.list(user.tenant_id, db, page, per_page, search, category_id)

@router.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: str,
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """Get a single product."""
    return await ProductService.get_by_id(user.tenant_id, product_id, db)

@router.patch("/products/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: str,
    payload: ProductUpdate,
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """Partially update a product."""
    return await ProductService.update(user.tenant_id, product_id, payload, db)

@router.delete("/products/{product_id}", status_code=204)
async def delete_product(
    product_id: str,
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """Delete a product."""
    await ProductService.delete(user.tenant_id, product_id, db)

@router.post("/products/{product_id}/image", response_model=ProductResponse)
async def upload_product_image(
    product_id: str,
    file: UploadFile = File(...),
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """Upload or replace a product image (max 5 MB, jpg/png/webp)."""
    return await ProductService.upload_image(user.tenant_id, product_id, file, db)

# ─── Categories ───────────────────────────

@router.post("/categories/", response_model=CategoryResponse, status_code=201)
async def create_category(
    payload: CategoryCreate,
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """Create a new product category."""
    return await CategoryService.create(user.tenant_id, payload, db)

@router.get("/categories/", response_model=list[CategoryResponse])
async def list_categories(
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """List all categories for the tenant."""
    return await CategoryService.list(user.tenant_id, db)

@router.patch("/categories/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: str,
    payload: CategoryUpdate,
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """Update a category."""
    return await CategoryService.update(user.tenant_id, category_id, payload, db)

@router.delete("/categories/{category_id}", status_code=204)
async def delete_category(
    category_id: str,
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """Delete a category. Products in this category will become uncategorized."""
    await CategoryService.delete(user.tenant_id, category_id, db)
