"""
Expense API routes for expense tracking
"""
import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.middleware.auth import get_current_user_context, TokenData
from app.schemas.expense import (
    ExpenseCreate,
    ExpenseUpdate,
    ExpenseResponse,
    ExpenseListResponse,
    ExpenseCategoryCreate,
    ExpenseCategoryUpdate,
    ExpenseCategoryResponse,
)
from app.services.expense_service import ExpenseService
from app.core.openapi_docs import (
    RESPONSES_CREATE, RESPONSES_READ, RESPONSES_LIST, RESPONSES_UPDATE, RESPONSES_DELETE
)

# ─────────────────────────────────────────
# Expense Router
# ─────────────────────────────────────────

router = APIRouter(prefix="/expenses", tags=["Expenses"])


# ─── Expense Categories ───


@router.post(
    "/categories",
    response_model=ExpenseCategoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Expense Category",
    description="Create a new expense category for organizing expenses",
    responses=RESPONSES_CREATE,
)
async def create_expense_category(
    payload: ExpenseCategoryCreate,
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new expense category.
    
    Args:
    - **name**: Category name (e.g., Utilities, Rent, Supplies)
    - **description**: Optional category description
    - **budget_limit**: Optional monthly budget threshold
    
    Returns:
    - **id**: Category identifier
    - **name**: Category name
    - **description**: Category description
    """
    return await ExpenseService.create_category(user.tenant_id, payload, db)


@router.get(
    "/categories",
    response_model=list[ExpenseCategoryResponse],
    summary="List Expense Categories",
    description="Get all expense categories for expense tracking",
    responses=RESPONSES_LIST,
)
async def list_expense_categories(
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """
    List all expense categories.
    
    Returns:
    - **categories**: Array of category objects with name and budget info
    """
    return await ExpenseService.list_categories(user.tenant_id, db)


@router.get(
    "/categories/{category_id}",
    response_model=ExpenseCategoryResponse,
    summary="Get Expense Category",
    description="Retrieve details of a specific expense category",
    responses=RESPONSES_READ,
)
async def get_expense_category(
    category_id: uuid.UUID,
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """Get expense category details by ID."""
    return await ExpenseService.get_category(user.tenant_id, category_id, db)


@router.patch(
    "/categories/{category_id}",
    response_model=ExpenseCategoryResponse,
    summary="Update Expense Category",
    description="Update expense category details",
    responses=RESPONSES_UPDATE,
)
async def update_expense_category(
    category_id: uuid.UUID,
    payload: ExpenseCategoryUpdate,
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """Update expense category name, description, or budget limit."""
    return await ExpenseService.update_category(user.tenant_id, category_id, payload, db)


@router.delete(
    "/categories/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Expense Category",
    description="Delete an expense category and reassign its expenses",
    responses=RESPONSES_DELETE,
)
async def delete_expense_category(
    category_id: uuid.UUID,
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """Delete an expense category (associated expenses will be untagged)."""
    await ExpenseService.delete_category(user.tenant_id, category_id, db)


# ─── Expenses ───


@router.post(
    "/",
    response_model=ExpenseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Expense",
    description="Record a new business expense",
    responses=RESPONSES_CREATE,
)
async def create_expense(
    payload: ExpenseCreate,
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new expense record.
    
    Args:
    - **category_id**: Expense category ID
    - **amount**: Expense amount
    - **description**: Detailed description
    - **date**: Expense date
    - **payment_method**: How paid (cash|cheque|card|bank_transfer)
    - **reference**: Receipt number or reference
    
    Returns:
    - **id**: Expense identifier
    - **amount**: Recorded amount
    - **date**: Expense date
    - **category**: Category name
    """
    return await ExpenseService.create_expense(user.tenant_id, payload, db)


@router.get(
    "/",
    response_model=ExpenseListResponse,
    summary="List Expenses",
    description="Get expenses with pagination and filtering",
    responses=RESPONSES_LIST,
)
async def list_expenses(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    category_id: uuid.UUID | None = Query(None, description="Filter by category"),
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """
    List expenses with optional category filtering.
    
    Query Parameters:
    - **page**: Page number
    - **per_page**: Items per page
    - **category_id**: Filter by category (optional)
    """
    return await ExpenseService.list_expenses(user.tenant_id, db, page, per_page, category_id)


@router.get(
    "/{expense_id}",
    response_model=ExpenseResponse,
    summary="Get Expense",
    description="Retrieve a specific expense record detail",
    responses=RESPONSES_READ,
)
async def get_expense(
    expense_id: uuid.UUID,
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """Get expense details by ID."""
    return await ExpenseService.get_expense(user.tenant_id, expense_id, db)


@router.patch(
    "/{expense_id}",
    response_model=ExpenseResponse,
    summary="Update Expense",
    description="Update expense amount, category, or other details",
    responses=RESPONSES_UPDATE,
)
async def update_expense(
    expense_id: uuid.UUID,
    payload: ExpenseUpdate,
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """Update expense amount, category, description, or payment method."""
    return await ExpenseService.update_expense(user.tenant_id, expense_id, payload, db)


@router.delete(
    "/{expense_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Expense",
    description="Remove an expense record",
    responses=RESPONSES_DELETE,
)
async def delete_expense(
    expense_id: uuid.UUID,
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """Delete an expense record."""
    await ExpenseService.delete_expense(user.tenant_id, expense_id, db)
