"""
Notification schemas for user notifications and alerts
"""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class NotificationCreateRequest(BaseModel):
    """Notification creation request"""

    user_id: uuid.UUID
    type: str = Field(..., max_length=50)
    title: str = Field(..., min_length=1, max_length=255)
    message: str = Field(...)
    entity_type: str | None = Field(None, max_length=50)
    entity_id: uuid.UUID | None = None
    action_url: str | None = None
    send_email: bool = False
    send_sms: bool = False
    send_push: bool = True


class NotificationUpdateRequest(BaseModel):
    """Notification update request"""

    is_read: bool | None = None
    send_email: bool | None = None
    send_sms: bool | None = None
    send_push: bool | None = None


class NotificationResponse(BaseModel):
    """Notification response schema"""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    business_id: uuid.UUID
    user_id: uuid.UUID
    type: str
    title: str
    message: str
    entity_type: str | None
    entity_id: uuid.UUID | None
    action_url: str | None
    is_read: bool
    send_email: bool
    send_sms: bool
    send_push: bool
    created_at: datetime
    updated_at: datetime


class NotificationListResponse(BaseModel):
    """Notification list response"""

    model_config = ConfigDict(from_attributes=True)

    data: list

    total: int
    page: int
    per_page: int
    total_pages: int


class NotificationMinimalResponse(BaseModel):
    """Minimal notification response"""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    type: str
    title: str
    is_read: bool
    created_at: datetime


# Aliases for backward compatibility
NotificationCreate = NotificationCreateRequest
NotificationUpdate = NotificationUpdateRequest
