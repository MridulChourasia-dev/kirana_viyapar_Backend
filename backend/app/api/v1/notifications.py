"""
Notification API routes for user notifications
"""
import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.middleware.auth import get_current_user_context, TokenData
from app.schemas.notification import (
    NotificationCreate,
    NotificationUpdate,
    NotificationResponse,
    NotificationListResponse,
)
from app.services.notification_service import NotificationService
from app.core.openapi_docs import (
    RESPONSES_CREATE, RESPONSES_READ, RESPONSES_LIST, RESPONSES_UPDATE, RESPONSES_DELETE, RESPONSES_ACTION
)

# ─────────────────────────────────────────
# Notification Router
# ─────────────────────────────────────────

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.post(
    "/",
    response_model=NotificationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Notification",
    description="Send a new notification to user",
    responses=RESPONSES_CREATE,
)
async def create_notification(
    payload: NotificationCreate,
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new notification.
    
    Args:
    - **title**: Notification title
    - **message**: Notification message body
    - **type**: Notification type (alert|info|success|warning)
    - **recipient_id**: User recipient ID
    - **related_data**: Optional contextual data (invoice ID, customer ID, etc.)
    """
    return await NotificationService.create(user.tenant_id, payload, db)


@router.get(
    "/",
    response_model=NotificationListResponse,
    summary="List Notifications",
    description="Get notifications for current user with read/unread filtering",
    responses=RESPONSES_LIST,
)
async def list_notifications(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    is_read: bool | None = Query(None, description="Filter by read status"),
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """
    List notifications for current user with optional read status filtering.
    
    Query Parameters:
    - **page**: Page number
    - **per_page**: Items per page
    - **is_read**: Filter by read status (true|false, optional)
    """
    return await NotificationService.list_for_user(user.tenant_id, user.id, db, page, per_page, is_read)


@router.post(
    "/mark-all-as-read",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Mark All as Read",
    description="Mark all notifications as read for current user",
    responses=RESPONSES_ACTION,
)
async def mark_all_as_read(
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """Mark all unread notifications as read."""
    await NotificationService.mark_all_as_read(user.tenant_id, user.id, db)


@router.get(
    "/{notification_id}",
    response_model=NotificationResponse,
    summary="Get Notification",
    description="Retrieve a specific notification by ID",
    responses=RESPONSES_READ,
)
async def get_notification(
    notification_id: uuid.UUID,
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """Get notification details by ID."""
    return await NotificationService.get_by_id(user.tenant_id, notification_id, db)


@router.patch(
    "/{notification_id}",
    response_model=NotificationResponse,
    summary="Update Notification",
    description="Update notification read status or other details",
    responses=RESPONSES_UPDATE,
)
async def update_notification(
    notification_id: uuid.UUID,
    payload: NotificationUpdate,
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """Update notification is_read status or other details."""
    return await NotificationService.update(user.tenant_id, notification_id, payload, db)


@router.post(
    "/{notification_id}/mark-as-read",
    response_model=NotificationResponse,
    summary="Mark as Read",
    description="Mark a specific notification as read",
    responses=RESPONSES_ACTION,
)
async def mark_as_read(
    notification_id: uuid.UUID,
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """Mark specific notification as read."""
    return await NotificationService.mark_as_read(user.tenant_id, notification_id, db)


@router.delete(
    "/{notification_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Notification",
    description="Delete a specific notification",
    responses=RESPONSES_DELETE,
)
async def delete_notification(
    notification_id: uuid.UUID,
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """Delete a notification."""
    await NotificationService.delete(user.tenant_id, notification_id, db)


@router.delete(
    "/delete-all",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete All Notifications",
    description="Delete all notifications for current user",
    responses=RESPONSES_DELETE,
)
async def delete_all_notifications(
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """Delete all notifications for current user."""
    await NotificationService.delete_all_for_user(user.tenant_id, user.id, db)
