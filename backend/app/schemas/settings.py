"""
Settings schemas for application and business configuration
"""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SettingCreateRequest(BaseModel):
    """Setting creation request"""

    key: str = Field(..., min_length=1, max_length=255)
    value: str = Field(...)
    category: str = Field(..., min_length=1, max_length=100)
    description: str | None = None
    data_type: str = "string"


class SettingUpdateRequest(BaseModel):
    """Setting update request"""

    value: str
    description: str | None = None
    data_type: str | None = None


class SettingResponse(BaseModel):
    """Setting response schema"""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    business_id: uuid.UUID
    key: str
    value: str
    category: str
    description: str | None
    data_type: str
    created_at: datetime
    updated_at: datetime


class SettingListResponse(BaseModel):
    """Setting list response"""

    model_config = ConfigDict(from_attributes=True)

    data: list

    total: int
    page: int
    per_page: int
    total_pages: int


class SettingByCategoryResponse(BaseModel):
    """Settings grouped by category"""

    model_config = ConfigDict(from_attributes=True)

    category: str
    settings: list[SettingResponse]


class SettingMinimalResponse(BaseModel):
    """Minimal setting response"""

    model_config = ConfigDict(from_attributes=True)

    key: str
    value: str
    category: str


# Aliases for backward compatibility
SettingCreate = SettingCreateRequest
SettingUpdate = SettingUpdateRequest
