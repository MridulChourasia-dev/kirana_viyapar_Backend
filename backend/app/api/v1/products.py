from fastapi import APIRouter, Depends, Query, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.middleware.auth import get_current_user_context, TokenData
from app.schemas.product import (
    ProductCreate, ProductUpdate, ProductResponse, ProductListResponse,
    CategoryCreate, CategoryUpdate, CategoryResponse,
)
from app.services.product_service import ProductService, CategoryService
from app.core.openapi_docs import (
    RESPONSES_CREATE, RESPONSES_READ, RESPONSES_LIST, RESPONSES_UPDATE, RESPONSES_DELETE, RESPONSES_ACTION
)

# ─────────────────────────────────────────
# Product Router
# ─────────────────────────────────────────

router = APIRouter(tags=["Products"])

# ─── Products ─────────────────────────────

@router.post(
    "/products/",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Product",
    description="Create a new product in the catalog",
    responses=RESPONSES_CREATE,
)
async def create_product(
    payload: ProductCreate,
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new product.
    
    Args:
    - **name**: Product name
    - **sku**: Stock keeping unit (unique identifier)
    - **price**: Selling price
    - **cost**: Cost price
    - **category_id**: Product category
    - **description**: Product description
    - **is_active**: Whether product is available for sale
    """
    return await ProductService.create(user.tenant_id, payload, db)

@router.get(
    "/products/",
    response_model=ProductListResponse,
    summary="List Products",
    description="Get paginated list of products with search and category filter",
    responses=RESPONSES_LIST,
)
async def list_products(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    search: str | None = Query(None, max_length=100, description="Search by name or SKU"),
    category_id: str | None = Query(None, description="Filter by category"),
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """
    List products with pagination, search, and category filter.
    
    Query Parameters:
    - **page**: Page number (1-indexed)
    - **per_page**: Items per page (1-100)
    - **search**: Search term
    - **category_id**: Category ID to filter
    """
    return await ProductService.list(user.tenant_id, db, page, per_page, search, category_id)

@router.get(
    "/products/low-stock",
    response_model=ProductListResponse,
    summary="Low Stock Products",
    description="List products where stock quantity is less than or equal to low stock threshold",
    responses=RESPONSES_LIST,
)
async def list_low_stock_products(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """Compatibility endpoint for API reference low-stock route."""
    products = await ProductService.list(user.tenant_id, db, page=1, per_page=10000)
    low_stock = [p for p in products.data if p.stock_quantity <= p.low_stock_alert]
    start = (page - 1) * per_page
    end = start + per_page
    page_data = low_stock[start:end]
    total = len(low_stock)
    total_pages = (total + per_page - 1) // per_page if total > 0 else 1
    return ProductListResponse(data=page_data, total=total, page=page, per_page=per_page, total_pages=total_pages)

@router.get(
    "/products/{product_id}",
    response_model=ProductResponse,
    summary="Get Product Details",
    description="Retrieve a single product with full details",
    responses=RESPONSES_READ,
)
async def get_product(
    product_id: str,
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """Get a single product by ID."""
    return await ProductService.get_by_id(user.tenant_id, product_id, db)

@router.patch(
    "/products/{product_id}",
    response_model=ProductResponse,
    summary="Update Product",
    description="Partially update product information",
    responses=RESPONSES_UPDATE,
)
async def update_product(
    product_id: str,
    payload: ProductUpdate,
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """Partially update a product."""
    return await ProductService.update(user.tenant_id, product_id, payload, db)


@router.put(
    "/products/{product_id}",
    response_model=ProductResponse,
    summary="Update Product (PUT Alias)",
    description="Compatibility alias for full product update via PUT",
    responses=RESPONSES_UPDATE,
)
async def update_product_put(
    product_id: str,
    payload: ProductUpdate,
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """Compatibility alias for clients using PUT instead of PATCH."""
    return await ProductService.update(user.tenant_id, product_id, payload, db)

@router.delete(
    "/products/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Product",
    description="Delete a product from catalog",
    responses=RESPONSES_DELETE,
)
async def delete_product(
    product_id: str,
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """Delete a product."""
    await ProductService.delete(user.tenant_id, product_id, db)

@router.post(
    "/products/{product_id}/image",
    response_model=ProductResponse,
    summary="Upload Product Image",
    description="Upload or replace product image (max 5 MB, jpg/png/webp)",
    responses=RESPONSES_ACTION,
)
async def upload_product_image(
    product_id: str,
    file: UploadFile = File(...),
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """Upload or replace a product image (max 5 MB, jpg/png/webp)."""
    return await ProductService.upload_image(user.tenant_id, product_id, file, db)


# ─── Categories ───────────────────────────

@router.post(
    "/categories/",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Product Category",
    description="Create a new product category",
    responses=RESPONSES_CREATE,
)
async def create_category(
    payload: CategoryCreate,
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """Create a new product category."""
    return await CategoryService.create(user.tenant_id, payload, db)

@router.get(
    "/categories/",
    response_model=list[CategoryResponse],
    summary="List Product Categories",
    description="Get all product categories",
    responses=RESPONSES_LIST,
)
async def list_categories(
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """List all categories for the tenant."""
    return await CategoryService.list(user.tenant_id, db)

@router.patch(
    "/categories/{category_id}",
    response_model=CategoryResponse,
    summary="Update Product Category",
    description="Update category information",
    responses=RESPONSES_UPDATE,
)
async def update_category(
    category_id: str,
    payload: CategoryUpdate,
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """Update a category."""
    return await CategoryService.update(user.tenant_id, category_id, payload, db)

@router.delete(
    "/categories/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Product Category",
    description="Delete a category. Products become uncategorized.",
    responses=RESPONSES_DELETE,
)
async def delete_category(
    category_id: str,
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """Delete a category. Products in this category will become uncategorized."""
    await CategoryService.delete(user.tenant_id, category_id, db)
