#!/bin/bash
# Celery Worker Startup Script (Bash)
# Usage: ./start_worker.sh [queue_name]

echo "Starting Celery Worker..."

QUEUE=${1:-}

if [ -z "$QUEUE" ]; then
    echo "Starting worker for all queues..."
    celery -A app.workers.celery_app worker \
        --loglevel=info \
        --concurrency=4 \
        --prefetch-multiplier=1 \
        --tasks-per-child=1000 \
        -E
else
    echo "Starting worker for queue: $QUEUE"
    celery -A app.workers.celery_app worker \
        --loglevel=info \
        --concurrency=4 \
        --prefetch-multiplier=1 \
        --queues=$QUEUE \
        --tasks-per-child=1000 \
        -E
fi
