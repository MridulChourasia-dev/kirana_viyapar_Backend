import math
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.models.product import Product
from app.models.stock_movement import StockMovement, MovementType, MovementReason
from app.schemas.inventory import (
    StockInRequest, StockOutRequest, StockAdjustmentRequest,
    StockMovementResponse, StockMovementListResponse,
    LowStockItem, InventoryDashboard,
)

# ─────────────────────────────────────────
# Inventory Service
# ─────────────────────────────────────────

class InventoryService:

    # ─── Stock In ───

    @staticmethod
    async def stock_in(
        tenant_id: str, payload: StockInRequest, user_id: str, db: AsyncSession
    ) -> StockMovementResponse:
        product = await InventoryService._get_product(tenant_id, payload.product_id, db)

        stock_before = product.stock_quantity
        stock_after = stock_before + payload.quantity
        product.stock_quantity = stock_after

        movement = StockMovement(
            business_id=tenant_id,
            product_id=product.id,
            movement_type=MovementType.STOCK_IN,
            reason=payload.reason,
            quantity=payload.quantity,
            stock_before=stock_before,
            stock_after=stock_after,
            unit_cost=payload.unit_cost,
            reference_id=payload.reference_id,
            notes=payload.notes,
            performed_by=user_id,
        )
        db.add(movement)
        await db.commit()
        await db.refresh(movement)

        return InventoryService._to_response(movement, product.name)

    # ─── Stock Out ───

    @staticmethod
    async def stock_out(
        tenant_id: str, payload: StockOutRequest, user_id: str, db: AsyncSession
    ) -> StockMovementResponse:
        product = await InventoryService._get_product(tenant_id, payload.product_id, db)

        if product.stock_quantity < payload.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock. Available: {product.stock_quantity}, Requested: {payload.quantity}",
            )

        stock_before = product.stock_quantity
        stock_after = stock_before - payload.quantity
        product.stock_quantity = stock_after

        movement = StockMovement(
            business_id=tenant_id,
            product_id=product.id,
            movement_type=MovementType.STOCK_OUT,
            reason=payload.reason,
            quantity=payload.quantity,
            stock_before=stock_before,
            stock_after=stock_after,
            reference_id=payload.reference_id,
            notes=payload.notes,
            performed_by=user_id,
        )
        db.add(movement)
        await db.commit()
        await db.refresh(movement)

        return InventoryService._to_response(movement, product.name)

    # ─── Stock Adjustment ───

    @staticmethod
    async def adjust_stock(
        tenant_id: str, payload: StockAdjustmentRequest, user_id: str, db: AsyncSession
    ) -> StockMovementResponse:
        product = await InventoryService._get_product(tenant_id, payload.product_id, db)

        stock_before = product.stock_quantity
        stock_after = payload.new_quantity
        quantity_diff = abs(stock_after - stock_before)
        product.stock_quantity = stock_after

        movement_type = MovementType.ADJUSTMENT

        movement = StockMovement(
            business_id=tenant_id,
            product_id=product.id,
            movement_type=movement_type,
            reason=payload.reason,
            quantity=quantity_diff,
            stock_before=stock_before,
            stock_after=stock_after,
            notes=payload.notes,
            performed_by=user_id,
        )
        db.add(movement)
        await db.commit()
        await db.refresh(movement)

        return InventoryService._to_response(movement, product.name)

    # ─── Movement History ───

    @staticmethod
    async def get_history(
        tenant_id: str,
        db: AsyncSession,
        product_id: str | None = None,
        movement_type: str | None = None,
        page: int = 1,
        per_page: int = 20,
    ) -> StockMovementListResponse:
        query = (
            select(StockMovement)
            .options(selectinload(StockMovement.product))
            .where(StockMovement.business_id == tenant_id)
        )

        if product_id:
            query = query.where(StockMovement.product_id == product_id)
        if movement_type:
            query = query.where(StockMovement.movement_type == movement_type)

        # Total count
        count_q = select(func.count()).select_from(query.subquery())
        total = (await db.execute(count_q)).scalar() or 0
        total_pages = math.ceil(total / per_page) if total > 0 else 1

        # Paginate (newest first)
        query = query.order_by(StockMovement.created_at.desc())
        query = query.offset((page - 1) * per_page).limit(per_page)
        result = await db.execute(query)
        movements = result.scalars().all()

        return StockMovementListResponse(
            data=[InventoryService._to_response(m, m.product.name) for m in movements],
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages,
        )

    # ─── Low Stock Alerts ───

    @staticmethod
    async def get_low_stock(tenant_id: str, db: AsyncSession) -> list[LowStockItem]:
        from app.models.category import Category

        query = (
            select(Product)
            .outerjoin(Category, Product.category_id == Category.id)
            .where(
                Product.tenant_id == tenant_id,
                Product.is_active == True,
                Product.stock_quantity <= Product.low_stock_alert,
            )
            .order_by(Product.stock_quantity.asc())
        )
        result = await db.execute(query)
        products = result.scalars().all()

        items = []
        for p in products:
            cat_name = None
            if p.category:
                cat_name = p.category.name
            items.append(LowStockItem(
                product_id=str(p.id),
                product_name=p.name,
                sku=p.sku,
                current_stock=p.stock_quantity,
                low_stock_alert=p.low_stock_alert,
                unit=p.unit.value if hasattr(p.unit, "value") else p.unit,
                category_name=cat_name,
            ))
        return items

    # ─── Dashboard ───

    @staticmethod
    async def get_dashboard(tenant_id: str, db: AsyncSession) -> InventoryDashboard:
        # Totals
        total_q = select(func.count()).where(Product.business_id == tenant_id, Product.is_active == True)
        total_products = (await db.execute(total_q)).scalar() or 0

        # Stock value (sum of stock_quantity * purchase_price)
        value_q = select(
            func.sum(Product.stock_quantity * Product.purchase_price)
        ).where(Product.business_id == tenant_id, Product.is_active == True)
        total_stock_value = float((await db.execute(value_q)).scalar() or 0)

        # Low stock count
        low_q = select(func.count()).where(
            Product.tenant_id == tenant_id,
            Product.is_active == True,
            Product.stock_quantity <= Product.low_stock_alert,
            Product.stock_quantity > 0,
        )
        low_stock_count = (await db.execute(low_q)).scalar() or 0

        # Out of stock count
        oos_q = select(func.count()).where(
            Product.tenant_id == tenant_id,
            Product.is_active == True,
            Product.stock_quantity == 0,
        )
        out_of_stock_count = (await db.execute(oos_q)).scalar() or 0

        # Low stock items
        low_stock_items = await InventoryService.get_low_stock(tenant_id, db)

        # Recent 10 movements
        recent_q = (
            select(StockMovement)
            .options(selectinload(StockMovement.product))
            .where(StockMovement.business_id == tenant_id)
            .order_by(StockMovement.created_at.desc())
            .limit(10)
        )
        recent = (await db.execute(recent_q)).scalars().all()
        recent_movements = [InventoryService._to_response(m, m.product.name) for m in recent]

        return InventoryDashboard(
            total_products=total_products,
            total_stock_value=total_stock_value,
            low_stock_count=low_stock_count,
            out_of_stock_count=out_of_stock_count,
            low_stock_items=low_stock_items,
            recent_movements=recent_movements,
        )

    # ─── Helpers ───

    @staticmethod
    async def _get_product(tenant_id: str, product_id: str, db: AsyncSession) -> Product:
        result = await db.execute(
            select(Product).where(Product.id == product_id, Product.business_id == tenant_id)
        )
        product = result.scalar_one_or_none()
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        return product

    @staticmethod
    def _to_response(movement: StockMovement, product_name: str) -> StockMovementResponse:
        return StockMovementResponse(
            id=str(movement.id),
            product_id=str(movement.product_id),
            product_name=product_name,
            movement_type=movement.movement_type.value,
            reason=movement.reason.value if hasattr(movement.reason, "value") else movement.reason,
            quantity=movement.quantity,
            stock_before=movement.stock_before,
            stock_after=movement.stock_after,
            unit_cost=float(movement.unit_cost) if movement.unit_cost else None,
            reference_id=movement.reference_id,
            notes=movement.notes,
            performed_by=str(movement.performed_by) if movement.performed_by else None,
            created_at=movement.created_at,
        )
