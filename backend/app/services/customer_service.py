import math
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from fastapi import HTTPException, status

from app.models.customer import Customer
from app.schemas.customer import (
    CustomerCreate, CustomerUpdate, CustomerResponse, CustomerListResponse,
)

# ─────────────────────────────────────────
# Customer Service – Business Logic
# ─────────────────────────────────────────

class CustomerService:

    @staticmethod
    async def create(tenant_id: str, payload: CustomerCreate, db: AsyncSession) -> CustomerResponse:
        customer = Customer(business_id=tenant_id, **payload.model_dump())
        db.add(customer)
        await db.commit()
        await db.refresh(customer)
        return CustomerService._to_response(customer)

    @staticmethod
    async def list(
        tenant_id: str,
        db: AsyncSession,
        page: int = 1,
        per_page: int = 20,
        search: str | None = None,
    ) -> CustomerListResponse:
        query = select(Customer).where(Customer.business_id == tenant_id)

        # Search by name, phone, or email
        if search:
            search_filter = f"%{search}%"
            query = query.where(
                or_(
                    Customer.name.ilike(search_filter),
                    Customer.phone.ilike(search_filter),
                    Customer.email.ilike(search_filter),
                )
            )

        # Total count
        count_query = select(func.count()).select_from(query.subquery())
        total = (await db.execute(count_query)).scalar() or 0
        total_pages = math.ceil(total / per_page) if total > 0 else 1

        # Paginate
        query = query.order_by(Customer.name.asc())
        query = query.offset((page - 1) * per_page).limit(per_page)
        result = await db.execute(query)
        customers = result.scalars().all()

        return CustomerListResponse(
            data=[CustomerService._to_response(c) for c in customers],
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages,
        )

    @staticmethod
    async def get_by_id(tenant_id: str, customer_id: str, db: AsyncSession) -> CustomerResponse:
        customer = await CustomerService._get_or_404(tenant_id, customer_id, db)
        return CustomerService._to_response(customer)

    @staticmethod
    async def update(
        tenant_id: str, customer_id: str, payload: CustomerUpdate, db: AsyncSession
    ) -> CustomerResponse:
        customer = await CustomerService._get_or_404(tenant_id, customer_id, db)

        update_data = payload.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(customer, field, value)

        await db.commit()
        await db.refresh(customer)
        return CustomerService._to_response(customer)

    @staticmethod
    async def delete(tenant_id: str, customer_id: str, db: AsyncSession) -> None:
        customer = await CustomerService._get_or_404(tenant_id, customer_id, db)
        await db.delete(customer)
        await db.commit()

    # ─── Helpers ───

    @staticmethod
    async def _get_or_404(tenant_id: str, customer_id: str, db: AsyncSession) -> Customer:
        result = await db.execute(
            select(Customer).where(
                Customer.id == customer_id,
                Customer.business_id == tenant_id,
            )
        )
        customer = result.scalar_one_or_none()
        if not customer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
        return customer

    @staticmethod
    def _to_response(customer: Customer) -> CustomerResponse:
        return CustomerResponse(
            id=str(customer.id),
            business_id=customer.business_id,
            name=customer.name,
            phone=customer.phone,
            email=customer.email,
            gstin=customer.gstin,
            billing_address=customer.billing_address,
            shipping_address=customer.shipping_address,
            city=customer.city,
            state=customer.state,
            country=customer.country,
            pincode=customer.pincode,
            balance=float(customer.balance),
            notes=customer.notes,
            created_at=customer.created_at,
            updated_at=customer.updated_at,
        )
