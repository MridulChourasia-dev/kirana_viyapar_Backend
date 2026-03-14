"""
Notification Service - Business logic for notifications
"""
import math
import uuid

from fastapi import HTTPException, status
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification
from app.schemas.notification import (
    NotificationCreate,
    NotificationUpdate,
    NotificationResponse,
    NotificationListResponse,
)


class NotificationService:
    """Service for notification management"""

    @staticmethod
    async def create(
        tenant_id: uuid.UUID, payload: NotificationCreate, db: AsyncSession
    ) -> NotificationResponse:
        """Create notification"""
        notification = Notification(business_id=tenant_id, **payload.model_dump())
        db.add(notification)
        await db.commit()
        await db.refresh(notification)
        return NotificationService._to_response(notification)

    @staticmethod
    async def list_for_user(
        tenant_id: uuid.UUID,
        user_id: uuid.UUID,
        db: AsyncSession,
        page: int = 1,
        per_page: int = 20,
        is_read: bool | None = None,
    ) -> NotificationListResponse:
        """List notifications for user"""
        query = select(Notification).where(
            and_(
                Notification.business_id == tenant_id,
                Notification.user_id == user_id,
            )
        )

        if is_read is not None:
            query = query.where(Notification.is_read == is_read)

        # Total count
        count_query = select(func.count()).select_from(query.subquery())
        total = (await db.execute(count_query)).scalar() or 0
        total_pages = math.ceil(total / per_page) if total > 0 else 1

        # Paginate
        query = query.order_by(Notification.created_at.desc())
        query = query.offset((page - 1) * per_page).limit(per_page)
        result = await db.execute(query)
        notifications = result.scalars().all()

        return NotificationListResponse(
            data=[NotificationService._to_response(n) for n in notifications],
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages,
        )

    @staticmethod
    async def get_by_id(
        tenant_id: uuid.UUID, notification_id: uuid.UUID, db: AsyncSession
    ) -> NotificationResponse:
        """Get notification by ID"""
        notification = await NotificationService._get_or_404(tenant_id, notification_id, db)
        return NotificationService._to_response(notification)

    @staticmethod
    async def mark_as_read(
        tenant_id: uuid.UUID, notification_id: uuid.UUID, db: AsyncSession
    ) -> NotificationResponse:
        """Mark notification as read"""
        notification = await NotificationService._get_or_404(tenant_id, notification_id, db)
        notification.is_read = True
        await db.commit()
        await db.refresh(notification)
        return NotificationService._to_response(notification)

    @staticmethod
    async def mark_all_as_read(
        tenant_id: uuid.UUID, user_id: uuid.UUID, db: AsyncSession
    ) -> None:
        """Mark all notifications as read for user"""
        result = await db.execute(
            select(Notification).where(
                and_(
                    Notification.business_id == tenant_id,
                    Notification.user_id == user_id,
                    Notification.is_read == False,
                )
            )
        )
        notifications = result.scalars().all()
        for notification in notifications:
            notification.is_read = True
        await db.commit()

    @staticmethod
    async def update(
        tenant_id: uuid.UUID,
        notification_id: uuid.UUID,
        payload: NotificationUpdate,
        db: AsyncSession,
    ) -> NotificationResponse:
        """Update notification"""
        notification = await NotificationService._get_or_404(tenant_id, notification_id, db)

        update_data = payload.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(notification, field, value)

        await db.commit()
        await db.refresh(notification)
        return NotificationService._to_response(notification)

    @staticmethod
    async def delete(
        tenant_id: uuid.UUID, notification_id: uuid.UUID, db: AsyncSession
    ) -> None:
        """Delete notification"""
        notification = await NotificationService._get_or_404(tenant_id, notification_id, db)
        await db.delete(notification)
        await db.commit()

    @staticmethod
    async def delete_all_for_user(
        tenant_id: uuid.UUID, user_id: uuid.UUID, db: AsyncSession
    ) -> None:
        """Delete all notifications for user"""
        result = await db.execute(
            select(Notification).where(
                and_(
                    Notification.business_id == tenant_id,
                    Notification.user_id == user_id,
                )
            )
        )
        notifications = result.scalars().all()
        for notification in notifications:
            await db.delete(notification)
        await db.commit()

    # ─── Helpers ───

    @staticmethod
    async def _get_or_404(
        tenant_id: uuid.UUID, notification_id: uuid.UUID, db: AsyncSession
    ) -> Notification:
        """Get notification or raise 404"""
        result = await db.execute(
            select(Notification).where(
                Notification.id == notification_id,
                Notification.business_id == tenant_id,
            )
        )
        notification = result.scalar_one_or_none()
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found"
            )
        return notification

    @staticmethod
    def _to_response(notification: Notification) -> NotificationResponse:
        """Convert notification model to response"""
        return NotificationResponse.model_validate(notification)
