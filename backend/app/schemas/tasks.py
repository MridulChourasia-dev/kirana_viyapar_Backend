"""
Task Management Schemas - Pydantic models for async tasks
"""
import uuid
from datetime import datetime
from typing import Optional, Any

from pydantic import BaseModel, ConfigDict, Field


class TaskStatusResponse(BaseModel):
    """Task status response"""

    model_config = ConfigDict(from_attributes=True)

    task_id: str
    status: str  # PENDING, STARTED, SUCCESS, FAILURE, RETRY
    result: Optional[Any] = None
    error: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class SendInvoiceEmailRequest(BaseModel):
    """Request to send invoice email"""

    invoice_id: uuid.UUID
    recipient_email: str = Field(..., min_length=5)


class GenerateInvoicePdfRequest(BaseModel):
    """Request to generate invoice PDF"""

    invoice_id: uuid.UUID
    save_path: Optional[str] = None


class SendNotificationRequest(BaseModel):
    """Request to send notification"""

    user_id: uuid.UUID
    notification_type: str = Field(..., min_length=1, max_length=50)
    title: str = Field(..., min_length=1, max_length=255)
    message: str = Field(..., min_length=1)
    channels: list[str] = Field(default=["push"])
    entity_id: Optional[uuid.UUID] = None


class GenerateSalesReportRequest(BaseModel):
    """Request to generate sales report"""

    start_date: str = Field(..., description="ISO format date")
    end_date: str = Field(..., description="ISO format date")
    report_format: str = Field("pdf", description="pdf, csv, or json")
    email_to: Optional[str] = None


class GenerateInventoryReportRequest(BaseModel):
    """Request to generate inventory report"""

    report_format: str = Field("pdf", description="pdf, csv, or json")
    low_stock_threshold: int = Field(10, ge=1, le=1000)


class TaskResultResponse(BaseModel):
    """Task result response"""

    model_config = ConfigDict(from_attributes=True)

    task_id: str
    status: str
    result: Optional[Any] = None
    error: Optional[str] = None
    timestamp: datetime


class BulkTaskResponse(BaseModel):
    """Response for bulk task operations"""

    model_config = ConfigDict(from_attributes=True)

    task_ids: list[str]
    status: str
    total_tasks: int
    timestamp: datetime


class TaskQueueStatusResponse(BaseModel):
    """Celery queue status"""

    model_config = ConfigDict(from_attributes=True)

    active_tasks: int
    pending_tasks: int
    scheduled_tasks: int
    failed_tasks: int
    worker_count: int
    queues: dict
    timestamp: datetime
