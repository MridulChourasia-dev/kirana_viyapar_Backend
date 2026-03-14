import math
import uuid
import os
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status, UploadFile

from app.models.product import Product
from app.models.category import Category
from app.schemas.product import (
    ProductCreate, ProductUpdate, ProductResponse, ProductListResponse,
    CategoryCreate, CategoryUpdate, CategoryResponse,
)

# ─────────────────────────────────────────
# Upload directory (local dev – swap with S3 in prod)
# ─────────────────────────────────────────

UPLOAD_DIR = Path("uploads/products")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

# ─────────────────────────────────────────
# Product Service
# ─────────────────────────────────────────

class ProductService:

    @staticmethod
    async def create(tenant_id: str, payload: ProductCreate, db: AsyncSession) -> ProductResponse:
        product = Product(
            tenant_id=tenant_id,
            name=payload.name,
            sku=payload.sku,
            hsn_code=payload.hsn_code,
            description=payload.description,
            sale_price=payload.sale_price,
            purchase_price=payload.purchase_price,
            tax_rate=payload.tax_rate,
            stock_quantity=payload.stock_quantity,
            low_stock_alert=payload.low_stock_alert,
            unit=payload.unit,
            category_id=payload.category_id,
            is_active=payload.is_active,
        )
        db.add(product)
        await db.commit()
        await db.refresh(product, attribute_names=["category"])
        return ProductService._to_response(product)

    @staticmethod
    async def list(
        tenant_id: str,
        db: AsyncSession,
        page: int = 1,
        per_page: int = 20,
        search: str | None = None,
        category_id: str | None = None,
    ) -> ProductListResponse:
        query = (
            select(Product)
            .options(selectinload(Product.category))
            .where(Product.tenant_id == tenant_id)
        )

        if search:
            pattern = f"%{search}%"
            query = query.where(
                or_(
                    Product.name.ilike(pattern),
                    Product.sku.ilike(pattern),
                )
            )

        if category_id:
            query = query.where(Product.category_id == category_id)

        # Total
        count_q = select(func.count()).select_from(query.subquery())
        total = (await db.execute(count_q)).scalar() or 0
        total_pages = math.ceil(total / per_page) if total > 0 else 1

        # Paginate
        query = query.order_by(Product.name.asc())
        query = query.offset((page - 1) * per_page).limit(per_page)
        result = await db.execute(query)
        products = result.scalars().all()

        return ProductListResponse(
            data=[ProductService._to_response(p) for p in products],
            total=total, page=page, per_page=per_page, total_pages=total_pages,
        )

    @staticmethod
    async def get_by_id(tenant_id: str, product_id: str, db: AsyncSession) -> ProductResponse:
        product = await ProductService._get_or_404(tenant_id, product_id, db)
        return ProductService._to_response(product)

    @staticmethod
    async def update(
        tenant_id: str, product_id: str, payload: ProductUpdate, db: AsyncSession
    ) -> ProductResponse:
        product = await ProductService._get_or_404(tenant_id, product_id, db)
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(product, field, value)
        await db.commit()
        await db.refresh(product, attribute_names=["category"])
        return ProductService._to_response(product)

    @staticmethod
    async def delete(tenant_id: str, product_id: str, db: AsyncSession) -> None:
        product = await ProductService._get_or_404(tenant_id, product_id, db)
        await db.delete(product)
        await db.commit()

    # ─── Image Upload ───

    @staticmethod
    async def upload_image(
        tenant_id: str, product_id: str, file: UploadFile, db: AsyncSession
    ) -> ProductResponse:
        product = await ProductService._get_or_404(tenant_id, product_id, db)

        # Validate file
        ext = os.path.splitext(file.filename or "")[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type '{ext}' not allowed. Use: {', '.join(ALLOWED_EXTENSIONS)}",
            )

        content = await file.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File size exceeds 5 MB limit",
            )

        # Save file (local dev – replace with S3 in production)
        filename = f"{tenant_id}_{product_id}_{uuid.uuid4().hex[:8]}{ext}"
        filepath = UPLOAD_DIR / filename
        with open(filepath, "wb") as f:
            f.write(content)

        # Update product
        product.image_url = f"/uploads/products/{filename}"
        await db.commit()
        await db.refresh(product, attribute_names=["category"])
        return ProductService._to_response(product)

    # ─── Helpers ───

    @staticmethod
    async def _get_or_404(tenant_id: str, product_id: str, db: AsyncSession) -> Product:
        result = await db.execute(
            select(Product)
            .options(selectinload(Product.category))
            .where(Product.id == product_id, Product.tenant_id == tenant_id)
        )
        product = result.scalar_one_or_none()
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        return product

    @staticmethod
    def _to_response(product: Product) -> ProductResponse:
        return ProductResponse(
            id=str(product.id),
            name=product.name,
            sku=product.sku,
            hsn_code=product.hsn_code,
            description=product.description,
            sale_price=float(product.sale_price),
            purchase_price=float(product.purchase_price),
            tax_rate=float(product.tax_rate),
            stock_quantity=product.stock_quantity,
            low_stock_alert=product.low_stock_alert,
            unit=product.unit.value if hasattr(product.unit, "value") else product.unit,
            image_url=product.image_url,
            is_active=product.is_active,
            category_id=str(product.category_id) if product.category_id else None,
            category_name=product.category.name if product.category else None,
            created_at=product.created_at,
            updated_at=product.updated_at,
        )


# ─────────────────────────────────────────
# Category Service
# ─────────────────────────────────────────

class CategoryService:

    @staticmethod
    async def create(tenant_id: str, payload: CategoryCreate, db: AsyncSession) -> CategoryResponse:
        category = Category(tenant_id=tenant_id, name=payload.name, description=payload.description)
        db.add(category)
        await db.commit()
        await db.refresh(category)
        return CategoryService._to_response(category)

    @staticmethod
    async def list(tenant_id: str, db: AsyncSession) -> list[CategoryResponse]:
        result = await db.execute(
            select(Category)
            .where(Category.tenant_id == tenant_id)
            .order_by(Category.name.asc())
        )
        return [CategoryService._to_response(c) for c in result.scalars().all()]

    @staticmethod
    async def update(
        tenant_id: str, category_id: str, payload: CategoryUpdate, db: AsyncSession
    ) -> CategoryResponse:
        result = await db.execute(
            select(Category).where(Category.id == category_id, Category.tenant_id == tenant_id)
        )
        category = result.scalar_one_or_none()
        if not category:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(category, field, value)
        await db.commit()
        await db.refresh(category)
        return CategoryService._to_response(category)

    @staticmethod
    async def delete(tenant_id: str, category_id: str, db: AsyncSession) -> None:
        result = await db.execute(
            select(Category).where(Category.id == category_id, Category.tenant_id == tenant_id)
        )
        category = result.scalar_one_or_none()
        if not category:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
        await db.delete(category)
        await db.commit()

    @staticmethod
    def _to_response(category: Category) -> CategoryResponse:
        return CategoryResponse(
            id=str(category.id),
            name=category.name,
            description=category.description,
            created_at=category.created_at,
        )
