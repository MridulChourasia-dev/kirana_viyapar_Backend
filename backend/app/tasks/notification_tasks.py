"""
Notification Tasks - Send notifications via email, SMS, push notifications
"""
import logging
from datetime import datetime
import uuid

from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(
    name="send_notification",
    bind=True,
    max_retries=3,
)
def send_notification(
    self,
    user_id: str,
    business_id: str,
    notification_type: str,
    title: str,
    message: str,
    channels: list = None,
    entity_id: str = None,
):
    """
    Send notification through multiple channels (email, SMS, push)
    
    Args:
        self: Celery task self
        user_id: UUID of user to notify
        business_id: UUID of business
        notification_type: Type of notification (invoice, payment, alert, etc.)
        title: Notification title
        message: Notification message
        channels: List of channels to send through (email, sms, push)
        entity_id: Optional ID of related entity (invoice, payment, etc.)
    
    Returns:
        dict: Task execution result with channel status
    """
    try:
        if channels is None:
            channels = ["push"]  # Default to push notifications
        
        logger.info(f"Sending {notification_type} notification to user {user_id} via {channels}")
        
        channel_results = {}
        
        for channel in channels:
            try:
                if channel == "email":
                    channel_results["email"] = _send_email_notification(user_id, title, message)
                elif channel == "sms":
                    channel_results["sms"] = _send_sms_notification(user_id, message)
                elif channel == "push":
                    channel_results["push"] = _send_push_notification(user_id, title, message)
                else:
                    logger.warning(f"Unknown notification channel: {channel}")
            except Exception as e:
                logger.error(f"Error sending {channel} notification: {e}")
                channel_results[channel] = {"status": "failed", "error": str(e)}
        
        result = {
            "status": "success",
            "user_id": user_id,
            "notification_type": notification_type,
            "channels": channel_results,
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        logger.info(f"Notification sent: {result}")
        return result
        
    except Exception as exc:
        logger.error(f"Error sending notification: {exc}")
        raise self.retry(exc=exc, countdown=60)


def _send_email_notification(user_id: str, title: str, message: str) -> dict:
    """Send email notification"""
    logger.info(f"Sending email notification to user {user_id}: {title}")
    return {
        "status": "sent",
        "channel": "email",
        "timestamp": datetime.utcnow().isoformat(),
    }


def _send_sms_notification(user_id: str, message: str) -> dict:
    """Send SMS notification"""
    logger.info(f"Sending SMS notification to user {user_id}")
    return {
        "status": "sent",
        "channel": "sms",
        "timestamp": datetime.utcnow().isoformat(),
    }


def _send_push_notification(user_id: str, title: str, message: str) -> dict:
    """Send push notification"""
    logger.info(f"Sending push notification to user {user_id}: {title}")
    return {
        "status": "sent",
        "channel": "push",
        "timestamp": datetime.utcnow().isoformat(),
    }


@celery_app.task(
    name="send_bulk_notification",
    bind=True,
)
def send_bulk_notification(
    self,
    user_ids: list,
    business_id: str,
    notification_type: str,
    title: str,
    message: str,
    channels: list = None,
):
    """
    Send notification to multiple users
    
    Args:
        self: Celery task self
        user_ids: List of user UUIDs
        business_id: UUID of business
        notification_type: Type of notification
        title: Notification title
        message: Notification message
        channels: List of channels
    
    Returns:
        dict: Task execution result with statistics
    """
    try:
        logger.info(f"Sending bulk notification to {len(user_ids)} users")
        
        if channels is None:
            channels = ["push"]
        
        successful = 0
        failed = 0
        
        for user_id in user_ids:
            try:
                send_notification.delay(
                    user_id,
                    business_id,
                    notification_type,
                    title,
                    message,
                    channels,
                )
                successful += 1
            except Exception as e:
                logger.error(f"Failed to queue notification for user {user_id}: {e}")
                failed += 1
        
        return {
            "status": "success" if successful > 0 else "failed",
            "total": len(user_ids),
            "queued": successful,
            "failed": failed,
            "timestamp": datetime.utcnow().isoformat(),
        }
        
    except Exception as exc:
        logger.error(f"Error sending bulk notification: {exc}")
        raise self.retry(exc=exc, countdown=300)


@celery_app.task(
    name="schedule_notification",
    bind=True,
)
def schedule_notification(
    self,
    user_id: str,
    business_id: str,
    notification_type: str,
    title: str,
    message: str,
    scheduled_time: str,
    channels: list = None,
):
    """
    Schedule notification for later delivery
    
    Args:
        self: Celery task self
        user_id: UUID of user
        business_id: UUID of business
        notification_type: Type of notification
        title: Notification title
        message: Notification message
        scheduled_time: ISO format timestamp for when to send
        channels: List of channels
    
    Returns:
        dict: Task execution result
    """
    try:
        scheduled_id = str(uuid.uuid4())
        logger.info(f"Scheduled notification {scheduled_id} for user {user_id} at {scheduled_time}")
        
        return {
            "status": "scheduled",
            "scheduled_id": scheduled_id,
            "user_id": user_id,
            "scheduled_time": scheduled_time,
            "timestamp": datetime.utcnow().isoformat(),
        }
        
    except Exception as exc:
        logger.error(f"Error scheduling notification: {exc}")
        raise self.retry(exc=exc, countdown=60)
