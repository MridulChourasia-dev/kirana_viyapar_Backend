"""
Purchase Service - Business logic for purchase orders
"""
import math
import uuid
from datetime import date, datetime

from fastapi import HTTPException, status
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.purchase import Purchase, PurchaseItem, PurchaseStatus
from app.models.vendor import Vendor
from app.schemas.purchase import (
    PurchaseCreate,
    PurchaseUpdate,
    PurchaseResponse,
    PurchaseListResponse,
)


class PurchaseService:
    """Service for purchase order management"""

    @staticmethod
    async def _generate_po_number(tenant_id: uuid.UUID, db: AsyncSession) -> str:
        """Generate unique purchase order number"""
        year = datetime.now().year
        query = select(func.count(Purchase.id)).where(
            and_(
                Purchase.business_id == tenant_id,
                func.extract("year", Purchase.po_date) == year,
            )
        )
        count = (await db.execute(query)).scalar() or 0
        po_number = f"PO-{year}-{str(count + 1).zfill(4)}"
        return po_number

    @staticmethod
    async def create(
        tenant_id: uuid.UUID, payload: PurchaseCreate, db: AsyncSession
    ) -> PurchaseResponse:
        """Create a new purchase order"""
        # Get vendor details
        vendor_result = await db.execute(
            select(Vendor).where(
                and_(
                    Vendor.id == payload.vendor_id,
                    Vendor.business_id == tenant_id,
                )
            )
        )
        vendor = vendor_result.scalar_one_or_none()
        if not vendor:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vendor not found")

        # Generate PO number
        po_number = await PurchaseService._generate_po_number(tenant_id, db)

        # Calculate totals
        subtotal = 0.0
        tax_amount = 0.0

        for item in payload.items:
            line_subtotal = item.unit_cost * item.quantity
            subtotal += line_subtotal
            tax_amount += line_subtotal * (item.tax_rate / 100)

        total = subtotal + tax_amount + payload.shipping_cost

        # Create purchase
        purchase = Purchase(
            business_id=tenant_id,
            vendor_id=payload.vendor_id,
            po_number=po_number,
            vendor_name=vendor.name,
            vendor_email=vendor.email,
            vendor_phone=vendor.phone,
            po_date=payload.po_date,
            delivery_date=payload.delivery_date,
            expected_delivery_date=payload.expected_delivery_date,
            subtotal=subtotal,
            tax_amount=tax_amount,
            shipping_cost=payload.shipping_cost,
            total=total,
            amount_due=total,
            notes=payload.notes,
            terms=payload.terms,
        )
        db.add(purchase)
        await db.flush()

        # Create items
        for item_data in payload.items:
            line_subtotal = item_data.unit_cost * item_data.quantity
            tax = line_subtotal * (item_data.tax_rate / 100)
            line_total = line_subtotal + tax

            item = PurchaseItem(
                business_id=tenant_id,
                purchase_id=purchase.id,
                product_id=item_data.product_id,
                description=item_data.description,
                quantity=item_data.quantity,
                unit=item_data.unit,
                unit_cost=item_data.unit_cost,
                tax_rate=item_data.tax_rate,
                tax_amount=tax,
                line_total=line_total,
            )
            db.add(item)

        await db.commit()
        await db.refresh(purchase)
        return await PurchaseService._to_response(purchase, db)

    @staticmethod
    async def list(
        tenant_id: uuid.UUID,
        db: AsyncSession,
        page: int = 1,
        per_page: int = 20,
        status: str | None = None,
    ) -> PurchaseListResponse:
        """List purchase orders with pagination"""
        query = select(Purchase).where(Purchase.business_id == tenant_id)

        if status:
            query = query.where(Purchase.status == status)

        # Total count
        count_query = select(func.count()).select_from(query.subquery())
        total = (await db.execute(count_query)).scalar() or 0
        total_pages = math.ceil(total / per_page) if total > 0 else 1

        # Paginate
        query = query.order_by(Purchase.po_date.desc())
        query = query.offset((page - 1) * per_page).limit(per_page)
        query = query.options(selectinload(Purchase.items))
        result = await db.execute(query)
        purchases = result.unique().scalars().all()

        return PurchaseListResponse(
            data=[await PurchaseService._to_response(p, db) for p in purchases],
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages,
        )

    @staticmethod
    async def get_by_id(
        tenant_id: uuid.UUID, purchase_id: uuid.UUID, db: AsyncSession
    ) -> PurchaseResponse:
        """Get purchase order by ID"""
        purchase = await PurchaseService._get_or_404(tenant_id, purchase_id, db)
        return await PurchaseService._to_response(purchase, db)

    @staticmethod
    async def update(
        tenant_id: uuid.UUID,
        purchase_id: uuid.UUID,
        payload: PurchaseUpdate,
        db: AsyncSession,
    ) -> PurchaseResponse:
        """Update purchase order"""
        purchase = await PurchaseService._get_or_404(tenant_id, purchase_id, db)

        update_data = payload.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(purchase, field, value)

        await db.commit()
        await db.refresh(purchase)
        return await PurchaseService._to_response(purchase, db)

    @staticmethod
    async def delete(tenant_id: uuid.UUID, purchase_id: uuid.UUID, db: AsyncSession) -> None:
        """Delete purchase order"""
        purchase = await PurchaseService._get_or_404(tenant_id, purchase_id, db)
        await db.delete(purchase)
        await db.commit()

    # ─── Helpers ───

    @staticmethod
    async def _get_or_404(
        tenant_id: uuid.UUID, purchase_id: uuid.UUID, db: AsyncSession
    ) -> Purchase:
        """Get purchase or raise 404"""
        result = await db.execute(
            select(Purchase)
            .where(
                Purchase.id == purchase_id,
                Purchase.business_id == tenant_id,
            )
            .options(selectinload(Purchase.items))
        )
        purchase = result.unique().scalar_one_or_none()
        if not purchase:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Purchase not found")
        return purchase

    @staticmethod
    async def _to_response(purchase: Purchase, db: AsyncSession) -> PurchaseResponse:
        """Convert purchase model to response"""
        return PurchaseResponse.model_validate(purchase)
