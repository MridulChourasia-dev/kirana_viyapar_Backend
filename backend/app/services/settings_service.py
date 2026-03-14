"""
Settings Service - Business logic for settings management
"""
import math
import uuid

from fastapi import HTTPException, status
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.settings import Settings
from app.schemas.settings import (
    SettingCreate,
    SettingUpdate,
    SettingResponse,
    SettingListResponse,
    SettingByCategoryResponse,
)


class SettingsService:
    """Service for settings management"""

    @staticmethod
    async def create(
        tenant_id: uuid.UUID, payload: SettingCreate, db: AsyncSession
    ) -> SettingResponse:
        """Create setting"""
        setting = Settings(business_id=tenant_id, **payload.model_dump())
        db.add(setting)
        await db.commit()
        await db.refresh(setting)
        return SettingsService._to_response(setting)

    @staticmethod
    async def list_all(
        tenant_id: uuid.UUID,
        db: AsyncSession,
        page: int = 1,
        per_page: int = 20,
        category: str | None = None,
    ) -> SettingListResponse:
        """List all settings with pagination"""
        query = select(Settings).where(Settings.business_id == tenant_id)

        if category:
            query = query.where(Settings.category == category)

        # Total count
        count_query = select(func.count()).select_from(query.subquery())
        total = (await db.execute(count_query)).scalar() or 0
        total_pages = math.ceil(total / per_page) if total > 0 else 1

        # Paginate
        query = query.order_by(Settings.category.asc(), Settings.key.asc())
        query = query.offset((page - 1) * per_page).limit(per_page)
        result = await db.execute(query)
        settings = result.scalars().all()

        return SettingListResponse(
            data=[SettingsService._to_response(s) for s in settings],
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages,
        )

    @staticmethod
    async def list_by_category(
        tenant_id: uuid.UUID, category: str, db: AsyncSession
    ) -> SettingByCategoryResponse:
        """List settings by category"""
        result = await db.execute(
            select(Settings)
            .where(
                and_(
                    Settings.business_id == tenant_id,
                    Settings.category == category,
                )
            )
            .order_by(Settings.key.asc())
        )
        settings = result.scalars().all()

        return SettingByCategoryResponse(
            category=category,
            settings=[SettingsService._to_response(s) for s in settings],
        )

    @staticmethod
    async def get_by_key(
        tenant_id: uuid.UUID, key: str, category: str, db: AsyncSession
    ) -> SettingResponse:
        """Get setting by key and category"""
        result = await db.execute(
            select(Settings).where(
                and_(
                    Settings.business_id == tenant_id,
                    Settings.key == key,
                    Settings.category == category,
                )
            )
        )
        setting = result.scalar_one_or_none()
        if not setting:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Setting not found"
            )
        return SettingsService._to_response(setting)

    @staticmethod
    async def get_by_id(
        tenant_id: uuid.UUID, setting_id: uuid.UUID, db: AsyncSession
    ) -> SettingResponse:
        """Get setting by ID"""
        setting = await SettingsService._get_or_404(tenant_id, setting_id, db)
        return SettingsService._to_response(setting)

    @staticmethod
    async def update(
        tenant_id: uuid.UUID,
        setting_id: uuid.UUID,
        payload: SettingUpdate,
        db: AsyncSession,
    ) -> SettingResponse:
        """Update setting"""
        setting = await SettingsService._get_or_404(tenant_id, setting_id, db)

        update_data = payload.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(setting, field, value)

        await db.commit()
        await db.refresh(setting)
        return SettingsService._to_response(setting)

    @staticmethod
    async def update_by_key(
        tenant_id: uuid.UUID,
        key: str,
        category: str,
        payload: SettingUpdate,
        db: AsyncSession,
    ) -> SettingResponse:
        """Update setting by key"""
        result = await db.execute(
            select(Settings).where(
                and_(
                    Settings.business_id == tenant_id,
                    Settings.key == key,
                    Settings.category == category,
                )
            )
        )
        setting = result.scalar_one_or_none()
        if not setting:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Setting not found"
            )

        update_data = payload.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(setting, field, value)

        await db.commit()
        await db.refresh(setting)
        return SettingsService._to_response(setting)

    @staticmethod
    async def delete(
        tenant_id: uuid.UUID, setting_id: uuid.UUID, db: AsyncSession
    ) -> None:
        """Delete setting"""
        setting = await SettingsService._get_or_404(tenant_id, setting_id, db)
        await db.delete(setting)
        await db.commit()

    @staticmethod
    async def delete_by_key(
        tenant_id: uuid.UUID, key: str, category: str, db: AsyncSession
    ) -> None:
        """Delete setting by key"""
        result = await db.execute(
            select(Settings).where(
                and_(
                    Settings.business_id == tenant_id,
                    Settings.key == key,
                    Settings.category == category,
                )
            )
        )
        setting = result.scalar_one_or_none()
        if not setting:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Setting not found"
            )
        await db.delete(setting)
        await db.commit()

    # ─── Helpers ───

    @staticmethod
    async def _get_or_404(
        tenant_id: uuid.UUID, setting_id: uuid.UUID, db: AsyncSession
    ) -> Settings:
        """Get setting or raise 404"""
        result = await db.execute(
            select(Settings).where(
                and_(
                    Settings.business_id == tenant_id,
                    Settings.id == setting_id,
                )
            )
        )
        setting = result.scalar_one_or_none()
        if not setting:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Setting not found"
            )
        return setting

    @staticmethod
    def _to_response(setting: Settings) -> SettingResponse:
        """Convert setting model to response"""
        return SettingResponse.model_validate(setting)
