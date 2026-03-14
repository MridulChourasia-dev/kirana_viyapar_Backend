"""
Celery Application Configuration for background task processing
"""
import os
from celery import Celery

# Initialize Celery
celery_app = Celery(
    __name__,
    broker=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    backend=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
)

# Load config from environment
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    task_acks_late=True,
    worker_disable_rate_limits=False,
    worker_log_format="[%(asctime)s: %(levelname)s/%(processName)s] %(message)s",
    task_routes={
        "app.tasks.*": {"queue": "default"},
        "app.tasks.email_tasks.*": {"queue": "email"},
        "app.tasks.pdf_tasks.*": {"queue": "pdf"},
        "app.tasks.report_tasks.*": {"queue": "reports"},
    },
)

# Import tasks to register them
from app.tasks import email_tasks, pdf_tasks, notification_tasks, report_tasks  # noqa

__all__ = ["celery_app"]
