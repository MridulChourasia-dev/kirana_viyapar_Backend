"""
Vendor Service - Business logic for vendor management
"""
import math
import uuid

from fastapi import HTTPException, status
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.vendor import Vendor
from app.schemas.vendor import (
    VendorCreate,
    VendorUpdate,
    VendorResponse,
    VendorListResponse,
)


class VendorService:
    """Service for vendor CRUD operations"""

    @staticmethod
    async def create(
        tenant_id: uuid.UUID, payload: VendorCreate, db: AsyncSession
    ) -> VendorResponse:
        """Create a new vendor"""
        vendor = Vendor(business_id=tenant_id, **payload.model_dump())
        db.add(vendor)
        await db.commit()
        await db.refresh(vendor)
        return VendorService._to_response(vendor)

    @staticmethod
    async def list(
        tenant_id: uuid.UUID,
        db: AsyncSession,
        page: int = 1,
        per_page: int = 20,
        search: str | None = None,
        is_active: bool | None = None,
    ) -> VendorListResponse:
        """List vendors with pagination and filters"""
        query = select(Vendor).where(Vendor.business_id == tenant_id)

        # Search by name, phone, or email
        if search:
            search_filter = f"%{search}%"
            query = query.where(
                or_(
                    Vendor.name.ilike(search_filter),
                    Vendor.phone.ilike(search_filter),
                    Vendor.email.ilike(search_filter),
                )
            )

        # Filter by active status
        if is_active is not None:
            query = query.where(Vendor.is_active == is_active)

        # Total count
        count_query = select(func.count()).select_from(query.subquery())
        total = (await db.execute(count_query)).scalar() or 0
        total_pages = math.ceil(total / per_page) if total > 0 else 1

        # Paginate
        query = query.order_by(Vendor.name.asc())
        query = query.offset((page - 1) * per_page).limit(per_page)
        result = await db.execute(query)
        vendors = result.scalars().all()

        return VendorListResponse(
            data=[VendorService._to_response(v) for v in vendors],
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages,
        )

    @staticmethod
    async def get_by_id(
        tenant_id: uuid.UUID, vendor_id: uuid.UUID, db: AsyncSession
    ) -> VendorResponse:
        """Get vendor by ID"""
        vendor = await VendorService._get_or_404(tenant_id, vendor_id, db)
        return VendorService._to_response(vendor)

    @staticmethod
    async def update(
        tenant_id: uuid.UUID,
        vendor_id: uuid.UUID,
        payload: VendorUpdate,
        db: AsyncSession,
    ) -> VendorResponse:
        """Update vendor"""
        vendor = await VendorService._get_or_404(tenant_id, vendor_id, db)

        update_data = payload.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(vendor, field, value)

        await db.commit()
        await db.refresh(vendor)
        return VendorService._to_response(vendor)

    @staticmethod
    async def delete(tenant_id: uuid.UUID, vendor_id: uuid.UUID, db: AsyncSession) -> None:
        """Delete vendor"""
        vendor = await VendorService._get_or_404(tenant_id, vendor_id, db)
        await db.delete(vendor)
        await db.commit()

    # ─── Helpers ───

    @staticmethod
    async def _get_or_404(
        tenant_id: uuid.UUID, vendor_id: uuid.UUID, db: AsyncSession
    ) -> Vendor:
        """Get vendor or raise 404"""
        result = await db.execute(
            select(Vendor).where(
                Vendor.id == vendor_id,
                Vendor.business_id == tenant_id,
            )
        )
        vendor = result.scalar_one_or_none()
        if not vendor:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vendor not found")
        return vendor

    @staticmethod
    def _to_response(vendor: Vendor) -> VendorResponse:
        """Convert vendor model to response"""
        return VendorResponse.model_validate(vendor)
