"""
Base Pydantic schemas used across all API responses
"""
import uuid
from datetime import datetime
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class BaseResponseSchema(BaseModel):
    """Base schema for all API responses"""

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class PaginationSchema(BaseModel):
    """Pagination schema for list endpoints"""

    total: int
    page: int
    per_page: int
    pages: int


class PaginatedResponseSchema(BaseModel, Generic[T]):
    """Generic paginated response schema"""

    data: list[T]
    pagination: PaginationSchema


class SuccessResponse(BaseModel):
    """Success response wrapper"""

    success: bool = True
    message: str | None = None
    data: dict | list | None = None


class ErrorResponse(BaseModel):
    """Error response wrapper"""

    success: bool = False
    error: str
    details: dict | None = None
