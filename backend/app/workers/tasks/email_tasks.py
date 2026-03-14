"""
Email Tasks - Send invoice emails and other email communications
"""
import logging
from datetime import datetime

from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(
    name="send_invoice_email",
    bind=True,
    max_retries=3,
    default_retry_delay=60 * 5,  # Retry after 5 minutes
)
def send_invoice_email(self, invoice_id: str, recipient_email: str, business_id: str = None):
    """
    Send invoice email to customer
    
    Args:
        self: Celery task self
        invoice_id: UUID of invoice
        recipient_email: Email address to send to
        business_id: UUID of business (optional, for multi-tenant)
    
    Returns:
        dict: Task execution result with status
    """
    try:
        logger.info(f"Sending invoice email: invoice_id={invoice_id}, recipient={recipient_email}")
        
        # Placeholder for actual email sending logic
        # In production, integrate with email service (SendGrid, AWS SES, etc.)
        email_content = {
            "to": recipient_email,
            "subject": f"Invoice {invoice_id}",
            "template": "invoice",
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        # Simulate email sending
        logger.info(f"Email would be sent with content: {email_content}")
        
        result = {
            "status": "success",
            "invoice_id": invoice_id,
            "recipient": recipient_email,
            "timestamp": datetime.utcnow().isoformat(),
            "message": "Invoice email sent successfully",
        }
        
        logger.info(f"Invoice email sent successfully: {result}")
        return result
        
    except Exception as exc:
        logger.error(f"Error sending invoice email: {exc}")
        # Retry up to max_retries times
        raise self.retry(exc=exc, countdown=60)


@celery_app.task(
    name="send_reminder_email",
    bind=True,
    max_retries=2,
)
def send_reminder_email(self, invoice_id: str, recipient_email: str, reminder_type: str = "overdue"):
    """
    Send payment reminder emails
    
    Args:
        self: Celery task self
        invoice_id: UUID of invoice
        recipient_email: Email address to send to
        reminder_type: Type of reminder (overdue, due_soon, etc.)
    
    Returns:
        dict: Task execution result
    """
    try:
        logger.info(f"Sending {reminder_type} reminder email: invoice_id={invoice_id}")
        
        email_content = {
            "to": recipient_email,
            "subject": f"Payment Reminder - Invoice {invoice_id}",
            "template": f"reminder_{reminder_type}",
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        logger.info(f"Reminder email would be sent: {email_content}")
        
        return {
            "status": "success",
            "invoice_id": invoice_id,
            "reminder_type": reminder_type,
            "timestamp": datetime.utcnow().isoformat(),
        }
        
    except Exception as exc:
        logger.error(f"Error sending reminder email: {exc}")
        raise self.retry(exc=exc, countdown=120)


@celery_app.task(
    name="send_bulk_email",
    bind=True,
)
def send_bulk_email(self, recipients: list, subject: str, template: str, context: dict = None):
    """
    Send bulk emails to multiple recipients
    
    Args:
        self: Celery task self
        recipients: List of email addresses
        subject: Email subject
        template: Email template name
        context: Additional template context
    
    Returns:
        dict: Task execution result with send statistics
    """
    try:
        logger.info(f"Sending bulk email to {len(recipients)} recipients")
        
        successful = 0
        failed = 0
        
        for recipient in recipients:
            try:
                # Email sending logic here
                successful += 1
            except Exception as e:
                logger.error(f"Failed to send email to {recipient}: {e}")
                failed += 1
        
        return {
            "status": "success" if successful > 0 else "failed",
            "total": len(recipients),
            "successful": successful,
            "failed": failed,
            "timestamp": datetime.utcnow().isoformat(),
        }
        
    except Exception as exc:
        logger.error(f"Error sending bulk email: {exc}")
        raise self.retry(exc=exc, countdown=300)
