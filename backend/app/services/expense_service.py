"""
Expense Service - Business logic for expense tracking
"""
import math
import uuid

from fastapi import HTTPException, status
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.expense import Expense, ExpenseCategory
from app.schemas.expense import (
    ExpenseCreate,
    ExpenseUpdate,
    ExpenseResponse,
    ExpenseListResponse,
    ExpenseCategoryCreate,
    ExpenseCategoryUpdate,
    ExpenseCategoryResponse,
)


class ExpenseService:
    """Service for expense management"""

    @staticmethod
    async def create_category(
        tenant_id: uuid.UUID, payload: ExpenseCategoryCreate, db: AsyncSession
    ) -> ExpenseCategoryResponse:
        """Create expense category"""
        category = ExpenseCategory(business_id=tenant_id, **payload.model_dump())
        db.add(category)
        await db.commit()
        await db.refresh(category)
        return ExpenseService._category_to_response(category)

    @staticmethod
    async def get_category(
        tenant_id: uuid.UUID, category_id: uuid.UUID, db: AsyncSession
    ) -> ExpenseCategoryResponse:
        """Get expense category by ID"""
        category = await ExpenseService._get_category_or_404(tenant_id, category_id, db)
        return ExpenseService._category_to_response(category)

    @staticmethod
    async def list_categories(
        tenant_id: uuid.UUID, db: AsyncSession
    ) -> list[ExpenseCategoryResponse]:
        """List all expense categories"""
        result = await db.execute(
            select(ExpenseCategory)
            .where(ExpenseCategory.business_id == tenant_id)
            .order_by(ExpenseCategory.name.asc())
        )
        categories = result.scalars().all()
        return [ExpenseService._category_to_response(c) for c in categories]

    @staticmethod
    async def update_category(
        tenant_id: uuid.UUID,
        category_id: uuid.UUID,
        payload: ExpenseCategoryUpdate,
        db: AsyncSession,
    ) -> ExpenseCategoryResponse:
        """Update expense category"""
        category = await ExpenseService._get_category_or_404(tenant_id, category_id, db)

        update_data = payload.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(category, field, value)

        await db.commit()
        await db.refresh(category)
        return ExpenseService._category_to_response(category)

    @staticmethod
    async def delete_category(
        tenant_id: uuid.UUID, category_id: uuid.UUID, db: AsyncSession
    ) -> None:
        """Delete expense category"""
        category = await ExpenseService._get_category_or_404(tenant_id, category_id, db)
        await db.delete(category)
        await db.commit()

    @staticmethod
    async def create_expense(
        tenant_id: uuid.UUID, payload: ExpenseCreate, db: AsyncSession
    ) -> ExpenseResponse:
        """Create expense"""
        expense = Expense(business_id=tenant_id, **payload.model_dump())
        db.add(expense)
        await db.commit()
        await db.refresh(expense)
        return ExpenseService._to_response(expense)

    @staticmethod
    async def list_expenses(
        tenant_id: uuid.UUID,
        db: AsyncSession,
        page: int = 1,
        per_page: int = 20,
        category_id: uuid.UUID | None = None,
    ) -> ExpenseListResponse:
        """List expenses with pagination"""
        query = select(Expense).where(Expense.business_id == tenant_id)

        if category_id:
            query = query.where(Expense.category_id == category_id)

        # Total count
        count_query = select(func.count()).select_from(query.subquery())
        total = (await db.execute(count_query)).scalar() or 0
        total_pages = math.ceil(total / per_page) if total > 0 else 1

        # Paginate
        query = query.order_by(Expense.expense_date.desc())
        query = query.offset((page - 1) * per_page).limit(per_page)
        result = await db.execute(query)
        expenses = result.scalars().all()

        return ExpenseListResponse(
            data=[ExpenseService._to_response(e) for e in expenses],
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages,
        )

    @staticmethod
    async def get_expense(
        tenant_id: uuid.UUID, expense_id: uuid.UUID, db: AsyncSession
    ) -> ExpenseResponse:
        """Get expense by ID"""
        expense = await ExpenseService._get_or_404(tenant_id, expense_id, db)
        return ExpenseService._to_response(expense)

    @staticmethod
    async def update_expense(
        tenant_id: uuid.UUID,
        expense_id: uuid.UUID,
        payload: ExpenseUpdate,
        db: AsyncSession,
    ) -> ExpenseResponse:
        """Update expense"""
        expense = await ExpenseService._get_or_404(tenant_id, expense_id, db)

        update_data = payload.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(expense, field, value)

        await db.commit()
        await db.refresh(expense)
        return ExpenseService._to_response(expense)

    @staticmethod
    async def delete_expense(
        tenant_id: uuid.UUID, expense_id: uuid.UUID, db: AsyncSession
    ) -> None:
        """Delete expense"""
        expense = await ExpenseService._get_or_404(tenant_id, expense_id, db)
        await db.delete(expense)
        await db.commit()

    # ─── Helpers ───

    @staticmethod
    async def _get_category_or_404(
        tenant_id: uuid.UUID, category_id: uuid.UUID, db: AsyncSession
    ) -> ExpenseCategory:
        """Get category or raise 404"""
        result = await db.execute(
            select(ExpenseCategory).where(
                ExpenseCategory.id == category_id,
                ExpenseCategory.business_id == tenant_id,
            )
        )
        category = result.scalar_one_or_none()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Expense category not found"
            )
        return category

    @staticmethod
    async def _get_or_404(
        tenant_id: uuid.UUID, expense_id: uuid.UUID, db: AsyncSession
    ) -> Expense:
        """Get expense or raise 404"""
        result = await db.execute(
            select(Expense).where(
                Expense.id == expense_id,
                Expense.business_id == tenant_id,
            )
        )
        expense = result.scalar_one_or_none()
        if not expense:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")
        return expense

    @staticmethod
    def _category_to_response(category: ExpenseCategory) -> ExpenseCategoryResponse:
        """Convert category model to response"""
        return ExpenseCategoryResponse.model_validate(category)

    @staticmethod
    def _to_response(expense: Expense) -> ExpenseResponse:
        """Convert expense model to response"""
        return ExpenseResponse.model_validate(expense)
