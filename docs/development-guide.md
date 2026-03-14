# Development Guide

## Table of Contents
1. [Quick Start](#quick-start)
2. [Installation](#installation)
3. [Project Structure](#project-structure)
4. [Using Background Tasks](#using-background-tasks)
5. [Common Workflows](#common-workflows)
6. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Docker (Recommended for Development)
```bash
# Start all services
docker-compose up -d

# Run migrations
docker-compose exec backend alembic upgrade head

# Access API
http://localhost:8000/api/v1/docs
```

### Manual Setup (Local Development)
```bash
# Create environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r backend/requirements.txt

# Setup database
cd backend
alembic upgrade head

# Run server
uvicorn app.main:app --reload
```

**Access Points**:
- API Docs: http://localhost:8000/api/v1/docs
- ReDoc: http://localhost:8000/api/v1/redoc
- Health: http://localhost:8000/health

---

## Installation

### Prerequisites
- Python 3.11+
- PostgreSQL 15+
- Redis 7+ (optional, for caching)
- Docker & Docker Compose (optional)

### Step-by-Step Setup

**1. Create Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate
```

**2. Install Dependencies**
```bash
pip install -r backend/requirements.txt
```

**3. Create Environment File**
```bash
cp backend/.env.example backend/.env
```

**4. Configure Database Connection**
Edit `backend/.env`:
```env
# Database
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=viyapar

# JWT
JWT_SECRET_KEY=your-secret-key-min-32-chars

# Redis (optional)
REDIS_URL=redis://localhost:6379/0
```

**5. Run Migrations**
```bash
cd backend
alembic upgrade head
```

**6. Verify Setup**
```bash
# Start server
uvicorn app.main:app --reload

# In another terminal, test health endpoint
curl http://localhost:8000/health
```

---

## Project Structure

### Directory Layout
```
backend/
├── app/                           # Main application
│   ├── api/                      # API routes
│   │   └── v1/                   # API v1 endpoints
│   │       ├── auth.py           # Authentication routes
│   │       ├── customers.py      # Customer endpoints
│   │       ├── vendors.py        # Vendor endpoints
│   │       ├── products.py       # Product endpoints
│   │       ├── inventory.py      # Inventory endpoints
│   │       ├── invoices.py       # Invoice endpoints
│   │       ├── payments.py       # Payment endpoints
│   │       ├── expenses.py       # Expense endpoints
│   │       ├── reports.py        # Reports endpoints
│   │       ├── notifications.py  # Notification endpoints
│   │       ├── settings.py       # Settings endpoints
│   │       ├── tasks.py          # Background task endpoints
│   │       └── router.py         # Route aggregation
│   │
│   ├── models/                   # SQLAlchemy ORM models
│   │   ├── business.py           # Multi-tenant business model
│   │   ├── user.py               # User model
│   │   ├── product.py            # Product model
│   │   ├── customer.py           # Customer model
│   │   ├── invoice.py            # Invoice model
│   │   ├── payment.py            # Payment model
│   │   ├── expense.py            # Expense model
│   │   └── ...                   # Additional models
│   │
│   ├── schemas/                  # Pydantic validation models
│   │   ├── auth.py               # Auth schemas
│   │   ├── customer.py           # Customer request/response
│   │   ├── product.py            # Product schemas
│   │   └── ...                   # More schemas
│   │
│   ├── services/                 # Business logic layer
│   │   ├── auth_service.py       # Authentication logic
│   │   ├── customer_service.py   # Customer operations
│   │   ├── product_service.py    # Product operations
│   │   └── ...                   # More services
│   │
│   ├── tasks/                    # Celery background tasks
│   │   ├── email_tasks.py        # Email sending
│   │   ├── pdf_tasks.py          # PDF generation
│   │   ├── notification_tasks.py # Notifications
│   │   └── report_tasks.py       # Report generation
│   │
│   ├── workers/                  # Celery setup
│   │   ├── celery_app.py         # Celery configuration
│   │   ├── run_worker.py         # Worker startup
│   │   └── monitor.py            # Task monitoring
│   │
│   ├── utils/                    # Utility functions
│   ├── middleware/               # Custom middleware
│   ├── core/                     # Core configuration
│   │   ├── config.py             # Settings
│   │   ├── security.py           # JWT utilities
│   │   └── openapi_docs.py       # Swagger config
│   ├── db/                       # Database setup
│   │   ├── session.py            # Connection pool
│   │   └── base_class.py         # Base models
│   └── main.py                   # FastAPI entry point
│
├── alembic/                      # Database migrations
│   ├── versions/                 # Migration scripts
│   └── env.py                    # Alembic config
│
├── requirements.txt              # Python dependencies
├── Dockerfile                    # Container image
├── .env.example                  # Environment template
└── README.md                     # Project README
```

### Module Responsibilities

| Module | Purpose |
|--------|---------|
| **api/v1** | HTTP request handlers and routing |
| **models** | Database schema defined via SQLAlchemy ORM |
| **schemas** | Pydantic validation for requests/responses |
| **services** | Business logic and data operations |
| **tasks** | Async background tasks via Celery |
| **workers** | Celery app configuration and execution |
| **utils** | Shared utility functions |
| **core** | Application settings and security |
| **db** | Database connection and session management |

---

## Using Background Tasks

### Overview
Background tasks run asynchronously using Celery + Redis, perfect for:
- Sending emails without blocking requests
- Generating PDFs offline
- Creating reports
- Sending notifications
- Long-running operations

### Setting Up Tasks

#### Prerequisites
```bash
# Redis must be running
redis-cli ping
# Should return: PONG

# In another terminal, start Celery worker
celery -A app.workers.celery_app worker --loglevel=info
```

#### Task Categories

**1. Email Tasks** (`app/tasks/email_tasks.py`)
```python
from app.tasks import email_tasks

# Queue email for sending
email_tasks.send_invoice_email.delay(
    invoice_id="123-456",
    recipient_email="customer@example.com",
    business_id="biz-id"
)

# Send bulk emails
email_tasks.send_bulk_email.delay(
    recipients=["user1@ex.com", "user2@ex.com"],
    subject="Invoice Reminder",
    template="invoice_reminder",
    context={"days_overdue": 5}
)
```

**2. PDF Tasks** (`app/tasks/pdf_tasks.py`)
```python
from app.tasks import pdf_tasks

# Generate invoice PDF
pdf_tasks.generate_invoice_pdf.delay(
    invoice_id="inv-456",
    business_id="biz-id"
)

# Batch PDF generation
pdf_tasks.generate_batch_pdf.delay(
    invoice_ids=["inv-1", "inv-2", "inv-3"],
    business_id="biz-id"
)
```

**3. Notification Tasks** (`app/tasks/notification_tasks.py`)
```python
from app.tasks import notification_tasks

# Send notification
notification_tasks.send_notification.delay(
    user_id="user-123",
    business_id="biz-id",
    notification_type="invoice",
    title="Invoice Paid",
    message="Invoice has been marked as paid",
    channels=["email", "push"]
)
```

**4. Report Tasks** (`app/tasks/report_tasks.py`)
```python
from app.tasks import report_tasks

# Generate sales report
report_tasks.generate_sales_report.delay(
    business_id="biz-id",
    start_date="2025-01-01",
    end_date="2025-01-31",
    report_format="pdf",
    email_to="owner@business.com"
)
```

### Task API Endpoints

All tasks have REST endpoints for management:

```
GET    /api/v1/tasks/                    - List all tasks
GET    /api/v1/tasks/{task_id}          - Get task status
POST   /api/v1/tasks/send-email         - Queue email task
POST   /api/v1/tasks/generate-pdf       - Queue PDF task
POST   /api/v1/tasks/send-notification  - Queue notification
POST   /api/v1/tasks/generate-report    - Queue report task
```

### Monitoring Tasks

**Celery CLI**
```bash
# View active tasks
celery -A app.workers.celery_app inspect active

# View registered tasks
celery -A app.workers.celery_app inspect registered

# Purge all tasks
celery -A app.workers.celery_app purge
```

**Flower (Web UI)**
```bash
# Start Flower (if installed)
pip install flower
flower -A app.workers.celery_app --port=5555

# Access: http://localhost:5555
```

---

## Common Workflows

### Creating a New API Endpoint

**1. Define Model** (`models/new_entity.py`)
```python
from sqlalchemy import Column, String, UUID
from app.db.base_class import Base

class NewEntity(Base):
    __tablename__ = "new_entity"
    
    id = Column(UUID, primary_key=True)
    business_id = Column(UUID, ForeignKey("business.id"))
    name = Column(String(255))
```

**2. Create Schema** (`schemas/new_entity.py`)
```python
from pydantic import BaseModel

class NewEntityCreate(BaseModel):
    name: str

class NewEntityResponse(BaseModel):
    id: str
    name: str
```

**3. Write Service Logic** (`services/new_entity_service.py`)
```python
async def create_new_entity(db, business_id, entity_data):
    entity = NewEntity(**entity_data, business_id=business_id)
    db.add(entity)
    await db.commit()
    return entity
```

**4. Add Routes** (`api/v1/new_entity.py`)
```python
from fastapi import APIRouter, Depends

router = APIRouter(prefix="/new-entities", tags=["New Entity"])

@router.post("/", response_model=NewEntityResponse)
async def create_entity(data: NewEntityCreate, db = Depends(get_db)):
    return await new_entity_service.create_new_entity(db, data)
```

**5. Register Router** (`api/v1/router.py`)
```python
from app.api.v1.new_entity import router as new_entity_router
api_router.include_router(new_entity_router)
```

### Running Database Migrations

```bash
cd backend

# Create new migration
alembic revision --autogenerate -m "Add new_field to users"

# Apply pending migrations
alembic upgrade head

# Downgrade to previous
alembic downgrade -1

# View current state
alembic current
```

### Testing an Endpoint

**Using cURL**
```bash
# Create resource
curl -X POST http://localhost:8000/api/v1/customers \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "Acme Corp", "email": "contact@acme.com"}'

# List resources
curl -X GET http://localhost:8000/api/v1/customers \
  -H "Authorization: Bearer <token>"
```

**Using Python Requests**
```python
import requests

BASE_URL = "http://localhost:8000/api/v1"
headers = {"Authorization": f"Bearer {token}"}

response = requests.post(
    f"{BASE_URL}/customers",
    json={"name": "Acme Corp"},
    headers=headers
)

print(response.json())
```

### Code Style and Testing

**Format Code**
```bash
# Black code formatting
black backend/app/

# Flake8 linting
flake8 backend/app/

# Type checking
mypy backend/app/
```

**Run Tests**
```bash
# All tests
pytest backend/tests/

# Specific test file
pytest backend/tests/test_auth.py

# With coverage report
pytest backend/tests/ --cov=app --cov-report=html
```

---

## Troubleshooting

### Common Issues

**Problem**: Database connection refused
```
Solution:
1. Verify PostgreSQL is running: pg_isready -h localhost
2. Check credentials in .env
3. Ensure database exists: psql -l
```

**Problem**: Celery tasks not being processed
```
Solution:
1. Check Redis is running: redis-cli ping
2. Verify Celery worker is running
3. Check worker logs for errors
4. Purge queue: celery -A app.workers.celery_app purge
```

**Problem**: Migration conflicts
```
Solution:
1. Check migration history: alembic history
2. Downgrade to stable: alembic downgrade -1
3. Create new migration: alembic revision --autogenerate
```

**Problem**: Port already in use
```bash
# Find process using port 8000
lsof -i :8000
# Kill process
kill -9 <PID>
```

**Problem**: Import errors
```bash
# Verify Python path is correct
export PYTHONPATH="${PYTHONPATH}:/path/to/backend"

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

---

## Environment Variables Reference

```env
# Database
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=viyapar

# JWT
JWT_SECRET_KEY=change-this-to-secure-key-min-32-chars
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Redis (for caching)
REDIS_URL=redis://localhost:6379/0

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Application
DEBUG=true
PROJECT_NAME=Viyapar
VERSION=1.0.0
ENVIRONMENT=development

# CORS
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8000"]
```

---

## Getting Help

- **API Documentation**: Visit http://localhost:8000/api/v1/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **SQLAlchemy Guide**: https://docs.sqlalchemy.org/
- **PostgreSQL Help**: https://www.postgresql.org/docs/
- **Celery Guide**: https://docs.celeryproject.io/

---

**Last Updated**: March 14, 2026  
**Version**: 1.0.0
