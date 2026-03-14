"""
Vendor API routes for supplier management
"""
import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.middleware.auth import get_current_user_context, TokenData
from app.schemas.vendor import (
    VendorCreate,
    VendorUpdate,
    VendorResponse,
    VendorListResponse,
)
from app.services.vendor_service import VendorService
from app.core.openapi_docs import (
    RESPONSES_CREATE, RESPONSES_READ, RESPONSES_LIST, RESPONSES_UPDATE, RESPONSES_DELETE
)

# ─────────────────────────────────────────
# Vendor Router
# ─────────────────────────────────────────

router = APIRouter(prefix="/vendors", tags=["Vendors"])


@router.post(
    "/",
    response_model=VendorResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Vendor",
    description="Create a new vendor/supplier account",
    responses=RESPONSES_CREATE,
)
async def create_vendor(
    payload: VendorCreate,
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new vendor for the current business.
    
    Args:
    - **name**: Vendor company name (required)
    - **email**: Business email address
    - **phone**: Contact phone number
    - **address**: Business address
    - **is_active**: Whether vendor is available for purchases
    """
    return await VendorService.create(user.tenant_id, payload, db)


@router.get(
    "/",
    response_model=VendorListResponse,
    summary="List Vendors",
    description="Retrieve paginated list of vendors",
    responses=RESPONSES_LIST,
)
async def list_vendors(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    search: str | None = Query(None, max_length=100, description="Search by name, phone, or email"),
    is_active: bool | None = Query(None, description="Filter by active status"),
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """
    List vendors with pagination and search.
    
    Query Parameters:
    - **page**: Page number
    - **per_page**: Items per page
    - **search**: Search term (searches name, phone, email)
    - **is_active**: Filter by active/inactive status
    """
    return await VendorService.list(user.tenant_id, db, page, per_page, search, is_active)


@router.get(
    "/{vendor_id}",
    response_model=VendorResponse,
    summary="Get Vendor Details",
    description="Retrieve a specific vendor by ID",
    responses=RESPONSES_READ,
)
async def get_vendor(
    vendor_id: uuid.UUID,
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """Get a single vendor by ID."""
    return await VendorService.get_by_id(user.tenant_id, vendor_id, db)


@router.patch(
    "/{vendor_id}",
    response_model=VendorResponse,
    summary="Update Vendor",
    description="Update vendor contact and business details",
    responses=RESPONSES_UPDATE,
)
async def update_vendor(
    vendor_id: uuid.UUID,
    payload: VendorUpdate,
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """Update a vendor."""
    return await VendorService.update(user.tenant_id, vendor_id, payload, db)


@router.delete(
    "/{vendor_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Vendor",
    description="Delete a vendor from the system",
    responses=RESPONSES_DELETE,
)
async def delete_vendor(
    vendor_id: uuid.UUID,
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """Delete a vendor."""
    await VendorService.delete(user.tenant_id, vendor_id, db)
