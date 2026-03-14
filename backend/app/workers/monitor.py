"""
Celery Monitoring and Management Utilities
"""
import logging
from typing import Optional
from datetime import datetime

from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


class CeleryMonitor:
    """
    Monitor and manage Celery tasks and workers
    """

    @staticmethod
    def get_active_tasks() -> list[dict]:
        """Get all active tasks"""
        try:
            inspect = celery_app.control.inspect()
            active = inspect.active()
            if active:
                tasks = []
                for worker, task_list in active.items():
                    for task in task_list:
                        tasks.append({
                            "worker": worker,
                            "task_id": task["id"],
                            "task_name": task["name"],
                            "args": task.get("args", []),
                            "kwargs": task.get("kwargs", {}),
                        })
                return tasks
            return []
        except Exception as e:
            logger.error(f"Error getting active tasks: {e}")
            return []

    @staticmethod
    def get_scheduled_tasks() -> list[dict]:
        """Get all scheduled tasks"""
        try:
            inspect = celery_app.control.inspect()
            scheduled = inspect.scheduled()
            if scheduled:
                tasks = []
                for worker, task_list in scheduled.items():
                    for task in task_list:
                        tasks.append({
                            "worker": worker,
                            "task_id": task["request"]["id"],
                            "task_name": task["request"]["name"],
                            "eta": task.get("eta"),
                        })
                return tasks
            return []
        except Exception as e:
            logger.error(f"Error getting scheduled tasks: {e}")
            return []

    @staticmethod
    def get_reserved_tasks() -> list[dict]:
        """Get all reserved tasks"""
        try:
            inspect = celery_app.control.inspect()
            reserved = inspect.reserved()
            if reserved:
                tasks = []
                for worker, task_list in reserved.items():
                    for task in task_list:
                        tasks.append({
                            "worker": worker,
                            "task_id": task["id"],
                            "task_name": task["name"],
                        })
                return tasks
            return []
        except Exception as e:
            logger.error(f"Error getting reserved tasks: {e}")
            return []

    @staticmethod
    def get_workers() -> list[dict]:
        """Get information about all workers"""
        try:
            inspect = celery_app.control.inspect()
            stats = inspect.stats()
            if stats:
                workers = []
                for worker_name, info in stats.items():
                    workers.append({
                        "name": worker_name,
                        "pool": info.get("pool", {}).get("implementation", "N/A"),
                        "concurrency": info.get("pool", {}).get("max-concurrency", 0),
                        "completed_tasks": info.get("total", 0),
                    })
                return workers
            return []
        except Exception as e:
            logger.error(f"Error getting workers: {e}")
            return []

    @staticmethod
    def get_queue_status() -> dict:
        """Get queue status"""
        try:
            active = CeleryMonitor.get_active_tasks()
            scheduled = CeleryMonitor.get_scheduled_tasks()
            reserved = CeleryMonitor.get_reserved_tasks()
            
            return {
                "active_tasks": len(active),
                "scheduled_tasks": len(scheduled),
                "reserved_tasks": len(reserved),
                "workers": len(CeleryMonitor.get_workers()),
                "timestamp": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            logger.error(f"Error getting queue status: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }

    @staticmethod
    def get_task_status(task_id: str) -> dict:
        """Get status of a specific task"""
        try:
            task = celery_app.AsyncResult(task_id)
            
            result = {
                "task_id": task_id,
                "status": task.status,
                "timestamp": datetime.utcnow().isoformat(),
            }
            
            if task.status == "SUCCESS":
                result["result"] = task.result
            elif task.status == "FAILURE":
                result["error"] = str(task.info)
                result["traceback"] = task.traceback
            elif task.status in ["RETRY", "STARTED"]:
                result["info"] = str(task.info)
            
            return result
        except Exception as e:
            logger.error(f"Error getting task status: {e}")
            return {
                "task_id": task_id,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }

    @staticmethod
    def cancel_task(task_id: str, terminate: bool = False) -> dict:
        """Cancel a task"""
        try:
            celery_app.control.revoke(task_id, terminate=terminate)
            logger.info(f"Task {task_id} revoked (terminate={terminate})")
            return {
                "task_id": task_id,
                "status": "revoked",
                "timestamp": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            logger.error(f"Error canceling task: {e}")
            return {
                "task_id": task_id,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }

    @staticmethod
    def purge_queue(queue_name: str) -> dict:
        """Purge all tasks in a queue"""
        try:
            celery_app.control.purge()
            logger.warning(f"Queue {queue_name} purged")
            return {
                "queue": queue_name,
                "status": "purged",
                "timestamp": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            logger.error(f"Error purging queue: {e}")
            return {
                "queue": queue_name,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }

    @staticmethod
    def get_queue_metrics() -> dict:
        """Get detailed queue metrics"""
        try:
            inspect = celery_app.control.inspect()
            
            # Get queue information
            active_queues = inspect.active_queues()
            
            queues = {}
            if active_queues:
                for worker, queue_list in active_queues.items():
                    for queue in queue_list:
                        queue_name = queue.get("name")
                        if queue_name not in queues:
                            queues[queue_name] = {
                                "name": queue_name,
                                "workers": [],
                                "exchange": queue.get("exchange", {}),
                                "routing_key": queue.get("routing_key"),
                            }
                        queues[queue_name]["workers"].append(worker)
            
            return {
                "queues": queues,
                "queue_count": len(queues),
                "timestamp": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            logger.error(f"Error getting queue metrics: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }
