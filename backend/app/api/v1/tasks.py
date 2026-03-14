"""
Task Management Routes - Async task orchestration endpoints
"""
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.middleware.auth import get_current_user_context, TokenData
from app.schemas.tasks import (
    SendInvoiceEmailRequest,
    GenerateInvoicePdfRequest,
    SendNotificationRequest,
    GenerateSalesReportRequest,
    GenerateInventoryReportRequest,
    TaskStatusResponse,
    TaskResultResponse,
    BulkTaskResponse,
)
from app.tasks import email_tasks, pdf_tasks, notification_tasks, report_tasks
from app.workers.celery_app import celery_app
from app.core.openapi_docs import RESPONSES_ACTION, RESPONSES_READ

# ─────────────────────────────────────────
# Task Router - Async Task Management
# ─────────────────────────────────────────

router = APIRouter(prefix="/tasks", tags=["Background Tasks"])


# ─── Email Tasks ───


@router.post(
    "/send-invoice-email",
    response_model=TaskResultResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Send Invoice Email",
    description="Queue task to send invoice email to recipient",
    responses=RESPONSES_ACTION,
)
async def send_invoice_email_task(
    payload: SendInvoiceEmailRequest,
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """
    Queue email sending task for invoice.
    
    Args:
    - **invoice_id**: Invoice ID to send
    - **recipient_email**: Email address of recipient
    
    Returns:
    - **task_id**: Background task ID to check status
    - **status**: Initially 'queued'
    """
    task = email_tasks.send_invoice_email.delay(
        str(payload.invoice_id),
        payload.recipient_email,
        business_id=str(user.tenant_id),
    )
    
    return {
        "task_id": task.id,
        "status": "queued",
        "result": None,
        "timestamp": datetime.utcnow(),
    }


@router.post(
    "/send-reminder-email",
    response_model=TaskResultResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Send Reminder Email",
    description="Queue task to send payment reminder email",
    responses=RESPONSES_ACTION,
)
async def send_reminder_email_task(
    invoice_id: uuid.UUID,
    recipient_email: str = Query(..., min_length=5, description="Recipient email address"),
    reminder_type: str = Query("overdue", description="Type of reminder: overdue|due_soon|first_reminder"),
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """Queue payment reminder email task."""
    task = email_tasks.send_reminder_email.delay(
        str(invoice_id),
        recipient_email,
        reminder_type=reminder_type,
    )
    
    return {
        "task_id": task.id,
        "status": "queued",
        "result": None,
        "timestamp": datetime.utcnow(),
    }


# ─── PDF Tasks ───


@router.post(
    "/generate-invoice-pdf",
    response_model=TaskResultResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Generate Invoice PDF",
    description="Queue task to generate invoice PDF file",
    responses=RESPONSES_ACTION,
)
async def generate_invoice_pdf_task(
    payload: GenerateInvoicePdfRequest,
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """Queue PDF generation task for invoice."""
    task = pdf_tasks.generate_invoice_pdf.delay(
        str(payload.invoice_id),
        business_id=str(user.tenant_id),
        save_path=payload.save_path,
    )
    
    return {
        "task_id": task.id,
        "status": "queued",
        "result": None,
        "timestamp": datetime.utcnow(),
    }


@router.post(
    "/generate-batch-pdf",
    response_model=TaskResultResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Generate Batch PDFs",
    description="Queue task to generate PDFs for multiple invoices",
    responses=RESPONSES_ACTION,
)
async def generate_batch_pdf_task(
    invoice_ids: list[uuid.UUID],
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """Queue batch PDF generation task for multiple invoices."""
    task = pdf_tasks.generate_batch_pdf.delay(
        [str(inv_id) for inv_id in invoice_ids],
        business_id=str(user.tenant_id),
    )
    
    return {
        "task_id": task.id,
        "status": "queued",
        "result": None,
        "timestamp": datetime.utcnow(),
    }


# ─── Notification Tasks ───


@router.post(
    "/send-notification",
    response_model=TaskResultResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Send Notification",
    description="Queue task to send notification to user",
    responses=RESPONSES_ACTION,
)
async def send_notification_task(
    payload: SendNotificationRequest,
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """
    Queue notification sending task.
    
    Args:
    - **user_id**: Recipient user ID
    - **notification_type**: Type of notification (alert|info|success|warning)
    - **title**: Notification title
    - **message**: Notification message
    - **channels**: Delivery channels (push|email|in_app)
    - **entity_id**: Related entity ID (invoice, customer, etc.)
    """
    task = notification_tasks.send_notification.delay(
        str(payload.user_id),
        str(user.tenant_id),
        payload.notification_type,
        payload.title,
        payload.message,
        channels=payload.channels,
        entity_id=str(payload.entity_id) if payload.entity_id else None,
    )
    
    return {
        "task_id": task.id,
        "status": "queued",
        "result": None,
        "timestamp": datetime.utcnow(),
    }


@router.post(
    "/send-bulk-notification",
    response_model=BulkTaskResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Send Bulk Notification",
    description="Queue task to send notification to multiple users",
    responses=RESPONSES_ACTION,
)
async def send_bulk_notification_task(
    user_ids: list[uuid.UUID],
    notification_type: str = Query(..., description="Notification type"),
    title: str = Query(..., description="Notification title"),
    message: str = Query(..., description="Notification message"),
    channels: list[str] = Query(None, description="Delivery channels (push|email|in_app)"),
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """Queue bulk notification task for multiple recipients."""
    if channels is None:
        channels = ["push"]
    
    task = notification_tasks.send_bulk_notification.delay(
        [str(uid) for uid in user_ids],
        str(user.tenant_id),
        notification_type,
        title,
        message,
        channels=channels,
    )
    
    return {
        "task_ids": [task.id],
        "status": "queued",
        "total_tasks": len(user_ids),
        "timestamp": datetime.utcnow(),
    }


# ─── Report Tasks ───


@router.post(
    "/generate-sales-report",
    response_model=TaskResultResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Generate Sales Report",
    description="Queue task to generate sales report",
    responses=RESPONSES_ACTION,
)
async def generate_sales_report_task(
    payload: GenerateSalesReportRequest,
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """Queue sales report generation task."""
    task = report_tasks.generate_sales_report.delay(
        str(user.tenant_id),
        payload.start_date,
        payload.end_date,
        report_format=payload.report_format,
        email_to=payload.email_to,
    )
    
    return {
        "task_id": task.id,
        "status": "queued",
        "result": None,
        "timestamp": datetime.utcnow(),
    }


@router.post(
    "/generate-inventory-report",
    response_model=TaskResultResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Generate Inventory Report",
    description="Queue task to generate inventory report",
    responses=RESPONSES_ACTION,
)
async def generate_inventory_report_task(
    payload: GenerateInventoryReportRequest,
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """Queue inventory report generation task."""
    task = report_tasks.generate_inventory_report.delay(
        str(user.tenant_id),
        report_format=payload.report_format,
        low_stock_threshold=payload.low_stock_threshold,
    )
    
    return {
        "task_id": task.id,
        "status": "queued",
        "result": None,
        "timestamp": datetime.utcnow(),
    }


@router.post(
    "/generate-customer-report",
    response_model=TaskResultResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Generate Customer Report",
    description="Queue task to generate customer analysis report",
    responses=RESPONSES_ACTION,
)
async def generate_customer_report_task(
    report_format: str = Query("pdf", description="Output format: pdf|csv|json"),
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """Queue customer report generation task."""
    task = report_tasks.generate_customer_report.delay(
        str(user.tenant_id),
        report_format=report_format,
    )
    
    return {
        "task_id": task.id,
        "status": "queued",
        "result": None,
        "timestamp": datetime.utcnow(),
    }


@router.post(
    "/generate-financial-report",
    response_model=TaskResultResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Generate Financial Report",
    description="Queue task to generate financial P&L report",
    responses=RESPONSES_ACTION,
)
async def generate_financial_report_task(
    start_date: str = Query(..., description="Report start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="Report end date (YYYY-MM-DD)"),
    report_format: str = Query("pdf", description="Output format: pdf|csv|json"),
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """Queue financial report generation task."""
    task = report_tasks.generate_financial_report.delay(
        str(user.tenant_id),
        start_date,
        end_date,
        report_format=report_format,
    )
    
    return {
        "task_id": task.id,
        "status": "queued",
        "result": None,
        "timestamp": datetime.utcnow(),
    }


# ─── Task Status ───


@router.get(
    "/{task_id}",
    response_model=TaskStatusResponse,
    summary="Get Task Status",
    description="Get the status and result of a background task",
    responses=RESPONSES_READ,
)
async def get_task_status(
    task_id: str,
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """
    Get task execution status and result.
    
    Returns:
    - **task_id**: Task identifier
    - **status**: Task state (pending|started|success|failure|revoked)
    - **result**: Result data if completed successfully
    - **error**: Error message if task failed
    """
    task = celery_app.AsyncResult(task_id)
    
    return {
        "task_id": task_id,
        "status": task.status,
        "result": task.result if task.status == "SUCCESS" else None,
        "error": str(task.info) if task.status == "FAILURE" else None,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }


@router.get(
    "/{task_id}/result",
    summary="Get Task Result",
    description="Get the result of a completed background task",
    responses=RESPONSES_READ,
)
async def get_task_result(
    task_id: str,
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """Get task result once completed (pending/processing/success/failed)."""
    task = celery_app.AsyncResult(task_id)
    
    if task.status == "PENDING":
        return {"status": "pending", "task_id": task_id}
    elif task.status == "STARTED":
        return {"status": "processing", "task_id": task_id}
    elif task.status == "SUCCESS":
        return {"status": "success", "result": task.result}
    elif task.status == "FAILURE":
        return {"status": "failed", "error": str(task.info)}
    else:
        return {"status": task.status, "task_id": task_id}


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Cancel Task",
    description="Cancel a pending or running background task",
    responses=RESPONSES_ACTION,
)
async def cancel_task(
    task_id: str,
    user: TokenData = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """Cancel a task by ID."""
    celery_app.control.revoke(task_id, terminate=True)
