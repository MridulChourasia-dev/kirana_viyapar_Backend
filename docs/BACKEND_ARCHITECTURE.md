# Backend Architecture Documentation

## Project Overview

**Viyapar** is a comprehensive SaaS billing and inventory management system designed for small businesses. The backend is built with FastAPI, a modern, fast Python web framework for building APIs.

## Technology Stack

- **Framework**: FastAPI 0.104+
- **Database**: PostgreSQL 15 with async SQLAlchemy
- **Caching**: Redis 7
- **Authentication**: JWT (JSON Web Tokens)
- **ORM**: SQLAlchemy 2.0 with async support
- **Database Migrations**: Alembic
- **Validation**: Pydantic v2
- **API Documentation**: Swagger/OpenAPI + ReDoc

## Architecture Overview

```
backend/
├── app/
│   ├── api/                    # API endpoints
│   │   └── v1/
│   │       ├── auth.py        # Authentication routes
│   │       ├── customers.py   # Customer management
│   │       ├── products.py    # Product management
│   │       ├── inventory.py   # Inventory control
│   │       ├── invoices.py    # Invoice management
│   │       ├── payments.py    # Payment tracking
│   │       ├── reports.py     # Business reports
│   │       └── router.py      # Route aggregator
│   ├── models/                # SQLAlchemy ORM models
│   │   ├── business.py        # Business/Tenant model
│   │   ├── user.py            # User model
│   │   ├── customer.py        # Customer model
│   │   ├── category.py        # Product category
│   │   ├── product.py         # Product model
│   │   ├── invoice.py         # Invoice & line items
│   │   ├── payment.py         # Payment model
│   │   └── stock_movement.py  # Inventory audit log
│   ├── schemas/               # Pydantic request/response schemas
│   │   ├── auth.py            # Auth schemas
│   │   ├── customer.py        # Customer schemas
│   │   ├── product.py         # Product schemas
│   │   ├── invoice.py         # Invoice schemas
│   │   ├── payment.py         # Payment schemas
│   │   └── reports.py         # Report schemas
│   ├── services/              # Business logic layer
│   │   ├── auth_service.py    # Auth logic
│   │   ├── customer_service.py
│   │   ├── product_service.py
│   │   ├── invoice_service.py
│   │   ├── payment_service.py
│   │   └── report_service.py
│   ├── core/                  # Core configuration
│   │   ├── config.py          # Settings management
│   │   └── security.py        # JWT & password utilities
│   ├── db/                    # Database configuration
│   │   ├── base_class.py      # Base SQLAlchemy model
│   │   ├── session.py         # Database session management
│   │   └── __init__.py
│   ├── middleware/            # Custom middleware
│   │   └── auth.py            # Authentication middleware
│   ├── utils/                 # Utility functions
│   │   └── decorators.py      # Custom decorators
│   └── main.py                # Application entry point
├── alembic/                   # Database migrations
├── Dockerfile                 # Docker image definition
├── requirements.txt           # Python dependencies
└── .env.example              # Environment template
```

## Multi-Tenancy Design

The system implements **strict database-level multi-tenancy**:

- Every table (except `user` and `business`) includes `business_id` foreign key
- Database constraints ensure users can only access their business data
- Row-level security via business_id filtering in services

## Core Entities

### 1. **Business** (Tenant)
```
- Core entity representing a business account
- Fields: name, email, phone, address, GSTIN, PAN
- One business has many users, customers, products, invoices
```

### 2. **User**
```
- Represents employees/staff within a business
- Roles: OWNER, ADMIN, STAFF
- JWT-based authentication
- Each user belongs to exactly one business
```

### 3. **Customer**
```
- Represents clients/customers
- Fields: name, phone, email, GST number, addresses
- Tracks outstanding balance
- Multi-address support (billing/shipping)
```

### 4. **Product**
```
- Inventory items
- Fields: SKU, HSN code, price, tax rate, stock quantity
- Belongs to category
- Tracks sale/purchase prices
```

### 5. **Invoice**
```
- Sales invoice with line items
- States: DRAFT, SENT, PAID, PARTIALLY_PAID, OVERDUE, CANCELLED
- Supports GST calculations (CGST, SGST, IGST)
- Line-item wise tax and discount
```

### 6. **Payment**
```
- Payment transaction against invoice
- Methods: CASH, UPI, BANK_TRANSFER, CHEQUE, CARD
- Tracks payment history and balance changes
- Supports partial payments
```

### 7. **StockMovement** (Audit Log)
```
- Complete inventory audit trail
- Types: STOCK_IN, STOCK_OUT, ADJUSTMENT, RETURN, DAMAGE
- Tracks quantity changes and cost
- Linked to source transaction (invoice, PO)
```

## API Endpoints

### Authentication
```
POST   /api/v1/auth/register      - User registration
POST   /api/v1/auth/login         - User login
POST   /api/v1/auth/refresh       - Refresh access token
POST   /api/v1/auth/logout        - User logout
```

### Customers
```
GET    /api/v1/customers          - List customers
POST   /api/v1/customers          - Create customer
GET    /api/v1/customers/{id}     - Get customer details
PUT    /api/v1/customers/{id}     - Update customer
DELETE /api/v1/customers/{id}     - Delete customer
```

### Products
```
GET    /api/v1/products           - List products
POST   /api/v1/products           - Create product
GET    /api/v1/products/{id}      - Get product details
PUT    /api/v1/products/{id}      - Update product
DELETE /api/v1/products/{id}      - Delete product
GET    /api/v1/products/low-stock - Low stock alerts
```

### Invoices
```
GET    /api/v1/invoices           - List invoices
POST   /api/v1/invoices           - Create invoice
GET    /api/v1/invoices/{id}      - Get invoice details
PUT    /api/v1/invoices/{id}      - Update invoice
DELETE /api/v1/invoices/{id}      - Cancel invoice
POST   /api/v1/invoices/{id}/send - Send invoice
```

### Payments
```
GET    /api/v1/payments           - List payments
POST   /api/v1/payments           - Record payment
GET    /api/v1/payments/{id}      - Get payment details
```

### Reports
```
GET    /api/v1/reports/sales      - Sales report
GET    /api/v1/reports/revenue    - Revenue report
GET    /api/v1/reports/inventory  - Inventory report
GET    /api/v1/reports/debtors    - Debtor report
```

## API Documentation

### Swagger UI
```
http://localhost:8000/api/v1/docs
```

### ReDoc
```
http://localhost:8000/api/v1/redoc
```

## Database Schema

### Key Design Patterns

**1. Timestamps**
- `created_at`: Automatic server timestamp (UTC)
- `updated_at`: Automatic on insert and update

**2. UUIDs**
- All primary keys are UUID v4
- Better for distributed systems and merging databases

**3. Foreign Keys**
- CASCADE DELETE for related records
- SET NULL for optional references

**4. Indexes**
- Business ID indexed for fast tenant isolation
- Email/phone indexed for lookups
- SKU indexed for product search

**5. Constraints**
- Unique constraints with business_id for tenant isolation
- NOT NULL constraints for required fields
- Check constraints for valid ranges

## Environment Setup

### Prerequisites
```
- Python 3.11+
- PostgreSQL 15+
- Redis 7+ (optional)
- Docker & Docker Compose (optional)
```

### Installation

**1. Clone Repository**
```bash
git clone <repository-url>
cd viyapar_application
```

**2. Create Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

**3. Install Dependencies**
```bash
pip install -r backend/requirements.txt
```

**4. Configure Environment**
```bash
cp backend/.env.example backend/.env
# Edit .env with your database credentials
```

**5. Run Migrations**
```bash
cd backend
alembic upgrade head
```

**6. Start Development Server**
```bash
uvicorn app.main:app --reload
```

Server runs at: http://localhost:8000

## Docker Deployment

### Build and Run
```bash
docker-compose up -d
```

### Access
- API: http://localhost:8000
- PostgreSQL: localhost:5432
- Redis: localhost:6379

## Security Features

1. **JWT Authentication**
   - Access tokens (short-lived, 30 min default)
   - Refresh tokens (long-lived, 7 days default)
   - Token validation on all protected routes

2. **Password Security**
   - Bcrypt hashing with salt
   - Minimum 8 character requirement

3. **CORS Configuration**
   - Configurable allowed origins
   - Credentials support

4. **Database Security**
   - Row-level business_id isolation
   - Prepared statements (automatic via SQLAlchemy)
   - No SQL injection vulnerabilities

5. **Rate Limiting** (Can be added)
   - Configurable per endpoint
   - User-based throttling

## Development Workflow

### Adding a New Endpoint

1. **Create Model** (if needed)
   ```python
   # app/models/new_entity.py
   class NewEntity(Base):
       __tablename__ = "new_entity"
       # ... fields
   ```

2. **Create Schemas**
   ```python
   # app/schemas/new_entity.py
   class NewEntityCreate(BaseModel):
       # ... fields
   ```

3. **Implement Service**
   ```python
   # app/services/new_entity_service.py
   class NewEntityService:
       async def create(self, db, entity_data):
           # ... service logic
   ```

4. **Create Routes**
   ```python
   # app/api/v1/new_entity.py
   @router.post("/new-entities")
   async def create_new_entity(data: NewEntityCreate, ...):
       # ... route logic
   ```

5. **Register Router**
   ```python
   # app/api/v1/router.py
   app.include_router(new_entity_router, prefix="/new-entities", tags=["New Entity"])
   ```

### Running Tests

```bash
pytest backend/tests/
pytest backend/tests/ -v  # Verbose
pytest backend/tests/ --cov=app  # With coverage
```

## Performance Optimization

1. **Database**
   - Connection pooling (20 connections default)
   - Pre-ping to detect dead connections
   - Indexed queries for fast lookups

2. **Caching** (Optional)
   - Redis for session caching
   - Response caching for reports
   - Cache invalidation strategies

3. **Async Operations**
   - Full async/await support
   - Non-blocking database operations
   - Concurrent request handling

## Monitoring & Logging

### Log Levels
- DEBUG: Detailed information for development
- INFO: General informational messages
- WARNING: Warning messages for potential issues
- ERROR: Error messages for failures

### Health Check
```bash
curl http://localhost:8000/health
```

Response:
```json
{"status": "healthy", "version": "1.0.0"}
```

## Deployment Checklist

- [ ] Set strong JWT_SECRET_KEY in production
- [ ] Configure CORS_ORIGINS for frontend domain
- [ ] Use strong database passwords
- [ ] Enable HTTPS/SSL in reverse proxy
- [ ] Configure backup strategy for database
- [ ] Setup monitoring and alerting
- [ ] Enable database audit logging
- [ ] Configure rate limiting
- [ ] Review and update security headers
- [ ] Load test the application

## Common Issues & Solutions

### PostgreSQL Connection Error
```
Solution: Check DATABASE_URL in .env, ensure PostgreSQL is running
```

### Migration Conflicts
```
Solution: alembic upgrade head, if issues: alembic upgrade --sql head
```

### Port Already in Use
```console
Solution: lsof -i :8000 && kill -9 <PID>
Or use different port: uvicorn app.main:app --port 8001
```

## Contributing

1. Follow PEP 8 code style
2. Use type hints for all functions
3. Add docstrings to all modules/functions
4. Write tests for new features
5. Run `black` and `flake8` before committing

## License

Proprietary - Viyapar SaaS Platform
