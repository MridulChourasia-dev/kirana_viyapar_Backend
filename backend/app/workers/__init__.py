"""
Celery Workers - Background task processing and job orchestration

This module provides the Celery application instance and worker management.
Tasks are defined in the app.tasks module.
"""
from app.workers.celery_app import celery_app

__all__ = ["celery_app"]
