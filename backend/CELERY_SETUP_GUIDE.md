# Background Task Processing with Celery

## Overview

This backend uses **Celery** with **Redis** for asynchronous background task processing. This enables long-running operations like generating PDFs, sending emails, and creating reports without blocking API responses.

## Architecture

```
FastAPI Endpoint
    ↓
   Task Queue (Redis)
    ↓
   Celery Workers (Multiple)
    ↓
   Task Results (Redis)
    ↓
   Task Status API
```

## Setup

### 1. Install Dependencies

```bash
# All dependencies in requirements.txt
pip install -r requirements.txt

# Or specific packages
pip install celery[redis]
pip install redis
pip install flower  # Optional: task monitoring UI
```

### 2. Configure Redis

**Linux/Mac:**
```bash
# Install Redis
brew install redis  # macOS
sudo apt-get install redis-server  # Ubuntu

# Start Redis
redis-server
```

**Windows:**
```bash
# Using WSL or Docker
docker run -d -p 6379:6379 redis:latest
```

### 3. Environment Setup

Copy `.env.example` to `.env` and configure:

```env
# Redis
REDIS_URL=redis://localhost:6379/0

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Worker Configuration
CELERYD_CONCURRENCY=4
CELERYD_PREFETCH_MULTIPLIER=1
```

## Starting Workers

### Option 1: Python Script

```bash
python -m app.workers.run_worker
```

Or for specific queue:
```bash
python -m app.workers.run_worker email
```

### Option 2: Bash Script (Linux/Mac)

```bash
./start_worker.sh          # All queues
./start_worker.sh email    # Email queue only
./start_worker.sh pdf      # PDF queue only
./start_worker.sh reports  # Reports queue only
```

### Option 3: Batch Script (Windows)

```cmd
start_worker.bat
start_worker.bat email
```

### Option 4: Direct Celery Command

```bash
# All queues (default)
celery -A app.workers.celery_app worker --loglevel=info

# Specific queue
celery -A app.workers.celery_app worker --queues=email,pdf --loglevel=info

# With auto-reload
celery -A app.workers.celery_app worker -l info -f worker.log
```

## Task Queue Routing

Tasks are automatically routed to specific queues:

| Queue | Tasks |
|-------|-------|
| `default` | Generic tasks |
| `email` | Email sending tasks |
| `pdf` | PDF generation tasks |
| `reports` | Report generation tasks |

### Run Multiple Workers

For production, run multiple workers processing different queues:

```bash
# Terminal 1: Email queue
celery -A app.workers.celery_app worker --queues=email --loglevel=info

# Terminal 2: PDF queue
celery -A app.workers.celery_app worker --queues=pdf --loglevel=info

# Terminal 3: Reports queue
celery -A app.workers.celery_app worker --queues=reports --loglevel=info

# Terminal 4: Default queue
celery -A app.workers.celery_app worker --queues=default --loglevel=info
```

## Using Background Tasks

### 1. Queue a Task

All tasks are triggered via REST API endpoints:

```bash
# Send invoice email
curl -X POST http://localhost:8000/api/v1/tasks/send-invoice-email \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "invoice_id": "123e4567-e89b-12d3-a456-426614174000",
    "recipient_email": "customer@example.com"
  }'

# Response (HTTP 202 Accepted)
{
  "task_id": "abc123def456",
  "status": "queued",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### 2. Get Task Status

```bash
curl http://localhost:8000/api/v1/tasks/abc123def456 \
  -H "Authorization: Bearer YOUR_TOKEN"

# Response
{
  "task_id": "abc123def456",
  "status": "SUCCESS",
  "result": {
    "email_sent": true,
    "recipient": "customer@example.com"
  },
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:35:00Z"
}
```

### 3. Cancel a Task

```bash
curl -X DELETE http://localhost:8000/api/v1/tasks/abc123def456 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Available Tasks

### Email Tasks

```
POST /tasks/send-invoice-email
POST /tasks/send-reminder-email
POST /tasks/send-bulk-notification
```

### PDF Tasks

```
POST /tasks/generate-invoice-pdf
POST /tasks/generate-batch-pdf
```

### Notification Tasks

```
POST /tasks/send-notification
POST /tasks/send-bulk-notification
```

### Report Tasks

```
POST /tasks/generate-sales-report
POST /tasks/generate-inventory-report
POST /tasks/generate-customer-report
POST /tasks/generate-financial-report
```

## Task Status Endpoints

```
GET /tasks/{task_id}              # Get task status
GET /tasks/{task_id}/result       # Get result when completed
DELETE /tasks/{task_id}           # Cancel task
```

## Monitoring

### Using Flower (Web UI)

Flower provides a web interface for monitoring tasks:

```bash
# Start Flower
celery -A app.workers.celery_app flower

# Open browser
http://localhost:5555
```

Features:
- Real-time task monitoring
- Worker pool status
- Task history
- Rate limiting
- Task routing visualization

### Using Celery Events

```bash
# Monitor events in terminal
celery -A app.workers.celery_app events

# With purge before starting
celery -A app.workers.celery_app purge
celery -A app.workers.celery_app events
```

### Programmatic Monitoring

Use `/tasks/monitor` endpoints for programmatic access (if implemented):

```python
from app.workers.monitor import CeleryMonitor

# Get active tasks
active = CeleryMonitor.get_active_tasks()

# Get worker status
workers = CeleryMonitor.get_workers()

# Get queue status
status = CeleryMonitor.get_queue_status()

# Get task status
task_status = CeleryMonitor.get_task_status(task_id)

# Cancel task
CeleryMonitor.cancel_task(task_id)
```

## Task Life Cycle

```
1. PENDING   → Task queued, waiting for worker
2. STARTED   → Worker accepted and started task
3. RETRY     → Task failed, retrying (if configured)
4. SUCCESS   → Task completed successfully
5. FAILURE   → Task failed permanently
```

## Retry Configuration

Tasks have built-in retry logic:

- **Email tasks**: max_retries=3, countdown=300s (5 min)
- **PDF tasks**: max_retries=2, countdown=60s (1 min)
- **Notification tasks**: max_retries=3, countdown=60s
- **Report tasks**: No automatic retries

## Time Limits

All tasks have time limits:

- **Soft limit**: 25 minutes (warning logged)
- **Hard limit**: 30 minutes (task killed)

Configure in `.env`:
```env
CELERY_TASK_SOFT_TIME_LIMIT=1500    # 25 min
CELERY_TASK_HARD_TIME_LIMIT=1800    # 30 min
```

## Docker Integration

### docker-compose.yml

```yaml
version: '3.8'

services:
  redis:
    image: redis:latest
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - redis

  celery_worker:
    build: .
    command: celery -A app.workers.celery_app worker --loglevel=info
    environment:
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - redis

  flower:
    build: .
    command: celery -A app.workers.celery_app flower
    ports:
      - "5555:5555"
    environment:
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - redis

volumes:
  redis_data:
```

## Troubleshooting

### No Tasks Being Processed

1. Check Redis connection:
   ```bash
   redis-cli ping
   # Should output: PONG
   ```

2. Verify worker is running:
   ```bash
   celery -A app.workers.celery_app inspect active
   ```

3. Check logs:
   ```bash
   celery -A app.workers.celery_app worker -l debug
   ```

### Task Timeout

Increase soft/hard limits in `.env`:
```env
CELERY_TASK_SOFT_TIME_LIMIT=3000    # 50 min
CELERY_TASK_HARD_TIME_LIMIT=3300    # 55 min
```

### Worker Won't Start

```bash
# Check Redis
redis-cli
> PING

# Check Celery config
python -c "from app.workers.celery_app import celery_app; print(celery_app.conf)"

# Run with debug
celery -A app.workers.celery_app worker -l debug
```

### Results Not Being Stored

Verify Redis backend:
```bash
redis-cli
> SELECT 0
> KEYS *
```

## Best Practices

1. **Task Idempotency**: Tasks should be safe to retry
2. **Task Dependency**: Don't create chains without testing
3. **Error Handling**: Always handle task failures gracefully
4. **Logging**: Log task progress for debugging
5. **Timeouts**: Set appropriate time limits
6. **Concurrency**: Tune concurrency for your hardware
7. **Monitoring**: Regularly monitor task queue health

## Performance Tuning

```env
# Increase concurrency for high throughput
CELERYD_CONCURRENCY=8

# Decrease prefetch for long-running tasks
CELERYD_PREFETCH_MULTIPLIER=1

# Max tasks per child process
CELERYD_MAX_TASKS_PER_CHILD=1000

# Task time limits
CELERY_TASK_SOFT_TIME_LIMIT=1500
CELERY_TASK_HARD_TIME_LIMIT=1800
```

## References

- [Celery Documentation](https://docs.celeryproject.io/)
- [Redis Documentation](https://redis.io/documentation)
- [FastAPI Background Tasks](https://fastapi.tiangolo.com/tutorial/background-tasks/)
- [Flower Documentation](https://flower.readthedocs.io/)
