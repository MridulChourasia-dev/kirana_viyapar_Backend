@echo off
REM Celery Worker Startup Script (Windows Batch)
REM Usage: start_worker.bat [queue_name]

echo Starting Celery Worker...

if "%1%"=="" (
    echo Starting worker for all queues...
    celery -A app.workers.celery_app worker ^
        --loglevel=info ^
        --concurrency=4 ^
        --prefetch-multiplier=1 ^
        --tasks-per-child=1000 ^
        -E
) else (
    echo Starting worker for queue: %1%
    celery -A app.workers.celery_app worker ^
        --loglevel=info ^
        --concurrency=4 ^
        --prefetch-multiplier=1 ^
        --queues=%1% ^
        --tasks-per-child=1000 ^
        -E
)
