#!/usr/bin/env python
"""
Celery Worker Startup Script
Usage: python -m workers.run_worker [queue_name]
"""
import logging
import sys
import os
from app.workers.celery_app import celery_app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Start Celery worker"""
    queue = sys.argv[1] if len(sys.argv) > 1 else None
    
    argv = [
        'worker',
        '--loglevel=info',
        '--concurrency=4',
        '--prefetch-multiplier=1',
    ]
    
    if queue:
        logger.info(f"Starting Celery worker for queue: {queue}")
        argv.extend([f'--queues={queue}'])
    else:
        logger.info("Starting Celery worker for all queues")
    
    try:
        celery_app.worker_main(argv)
    except KeyboardInterrupt:
        logger.info("Celery worker shutdown")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Celery worker error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
