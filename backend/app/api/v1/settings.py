"""
Settings API routes for application settings
"""
import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.middleware.auth import get_current_user_context, TokenData
from app.schemas.settings import (
    SettingCreate,
    SettingUpdate,
    SettingResponse,
    SettingListResponse,
    SettingByCategoryResponse,
)
from app.services.settings_service import SettingsService
from app.core.openapi_docs import (
    RESPONSES_CREATE, RESPONSES_READ, RESPONSES_LIST, RESPONSES_UPDATE, RESPONSES_DELETE
)

# ─────────────────────────────────────────
# Settings Router
# ─────────────────────────────────────────

router = APIRouter(prefix="/settings", tags=["Settings"])


@router.post(
    "/",
    response_model=SettingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Setting",
    description="Create a new application setting",
    responses=RESPONSES_CREATE,
)
async def create_setting(
    payload: SettingCreate,
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new application setting.
    
    Args:
    - **key**: Setting key (e.g., business_name, timezone, currency)
    - **category**: Setting category (e.g., business, display, tax)
    - **value**: Setting value (string, number, boolean, or JSON)
    - **description**: Optional description
    - **is_public**: Whether setting is accessible externally
    """
    return await SettingsService.create(user.tenant_id, payload, db)


@router.get(
    "/",
    response_model=SettingListResponse,
    summary="List Settings",
    description="Get all settings with optional category filtering",
    responses=RESPONSES_LIST,
)
async def list_settings(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    category: str | None = Query(None, description="Filter by category"),
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """
    List all settings with pagination and category filtering.
    
    Query Parameters:
    - **page**: Page number
    - **per_page**: Items per page
    - **category**: Filter by category (e.g., business, display)
    """
    return await SettingsService.list_all(user.tenant_id, db, page, per_page, category)


@router.get(
    "/categories/{category}",
    response_model=SettingByCategoryResponse,
    summary="List Settings by Category",
    description="Get all settings in a specific category",
    responses=RESPONSES_READ,
)
async def list_settings_by_category(
    category: str,
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all settings grouped by category.
    
    Returns:
    - **category**: Category name
    - **settings**: Array of settings in this category
    """
    return await SettingsService.list_by_category(user.tenant_id, category, db)


@router.get(
    "/by-key/{key}",
    response_model=SettingResponse,
    summary="Get Setting by Key",
    description="Retrieve a specific setting by key and category",
    responses=RESPONSES_READ,
)
async def get_setting_by_key(
    key: str,
    category: str = Query(..., description="Setting category"),
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """
    Get setting by key and category.
    
    Query Parameters:
    - **category**: Required - Setting category
    """
    return await SettingsService.get_by_key(user.tenant_id, key, category, db)


@router.get(
    "/{setting_id}",
    response_model=SettingResponse,
    summary="Get Setting",
    description="Retrieve a specific setting by ID",
    responses=RESPONSES_READ,
)
async def get_setting(
    setting_id: uuid.UUID,
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """Get a setting by ID with all details."""
    return await SettingsService.get_by_id(user.tenant_id, setting_id, db)


@router.patch(
    "/{setting_id}",
    response_model=SettingResponse,
    summary="Update Setting",
    description="Update a setting value by ID",
    responses=RESPONSES_UPDATE,
)
async def update_setting(
    setting_id: uuid.UUID,
    payload: SettingUpdate,
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """Update a setting's value, description, or visibility."""
    return await SettingsService.update(user.tenant_id, setting_id, payload, db)


@router.patch(
    "/by-key/{key}",
    response_model=SettingResponse,
    summary="Update Setting by Key",
    description="Update a setting value using key and category",
    responses=RESPONSES_UPDATE,
)
async def update_setting_by_key(
    key: str,
    payload: SettingUpdate,
    category: str = Query(..., description="Setting category"),
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """
    Update setting by key and category.
    
    Query Parameters:
    - **category**: Required - Setting category
    """
    return await SettingsService.update_by_key(user.tenant_id, key, category, payload, db)


@router.delete(
    "/{setting_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Setting",
    description="Delete a setting by ID",
    responses=RESPONSES_DELETE,
)
async def delete_setting(
    setting_id: uuid.UUID,
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """Delete a setting by ID."""
    await SettingsService.delete(user.tenant_id, setting_id, db)


@router.delete(
    "/by-key/{key}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Setting by Key",
    description="Delete a setting by key and category",
    responses=RESPONSES_DELETE,
)
async def delete_setting_by_key(
    key: str,
    category: str = Query(..., description="Setting category"),
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """Delete setting by key and category."""
    await SettingsService.delete_by_key(user.tenant_id, key, category, db)
