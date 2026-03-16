# Viyapar Backend - Billing & Inventory SaaS

A production-ready FastAPI backend for a multi-tenant SaaS billing and inventory management system.

## ✨ Key Features

✅ **Multi-Tenant Architecture** - Complete data isolation per business
✅ **JWT Authentication** - Secure access with refresh tokens
✅ **PostgreSQL Database** - ACID compliance with async support
✅ **RESTful API** - Clean, well-documented endpoints
✅ **Swagger Documentation** - Interactive API exploration
✅ **Pydantic Validation** - Automatic request/response validation
✅ **Alembic Migrations** - Version-controlled database changes
✅ **Error Handling** - Comprehensive error responses
✅ **CORS Configuration** - Frontend-friendly cross-origin support
✅ **Docker Ready** - One-command deployment

## 🚀 Quick Start

### Using Docker (Recommended)
```bash
docker-compose up -d
```

### Manual Setup
```bash
python -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
cd backend && alembic upgrade head
uvicorn app.main:app --reload
```

**Access**:
- API Docs: http://localhost:8000/api/v1/docs
- ReDoc: http://localhost:8000/api/v1/redoc
- Health: http://localhost:8000/health

## 📚 Documentation

Complete documentation is available in the `docs/` folder:

- **[Development Guide](./docs/development-guide.md)** - Setup, installation, project structure, and common workflows
- **[Architecture](./docs/BACKEND_ARCHITECTURE.md)** - Design patterns, clean architecture, and system design
- **[API Reference](./docs/API_REFERENCE.md)** - Complete endpoint documentation with examples
- **[Database Schema](./docs/DATABASE_SCHEMA.md)** - Data model, tables, and relationships
- **[Deployment Guide](./docs/DEPLOYMENT_GUIDE.md)** - Production deployment, Docker, Kubernetes
- **[Offline Sync Architecture](./docs/offline-sync-architecture.md)** - Mobile offline-first design
- **[Offline Sync Setup](./docs/offline-sync-setup.md)** - Implementing offline capabilities
- **[Reporting System](./docs/reporting-system.md)** - Business analytics and reporting features

## 🏗️ Architecture

### Core Components

**Models** - SQLAlchemy ORM models with relationships
- Business, User, Customer, Product, Category
- Invoice, InvoiceItem, Payment
- StockMovement (audit log)

**Schemas** - Pydantic validation models
- Request schemas for incoming data
- Response schemas for API output
- Type hints and automatic documentation

**Services** - Business logic layer
- AuthService - JWT generation and validation
- CustomerService - Customer management
- ProductService - Inventory management
- InvoiceService - Invoice creation and tracking
- PaymentService - Payment recording
- ReportService - Business analytics

**API Routes** - Endpoint handlers
- Authentication (/auth/*)
- Customers (/customers/*)
- Products (/products/*)
- Invoices (/invoices/*)
- Payments (/payments/*)
- Reports (/reports/*)

## 🔐 Security

- **JWT Tokens** - Secure stateless authentication
- **Password Hashing** - Bcrypt with salts
- **Row-Level Security** - business_id filtering
- **CORS** - Configurable origins
- **SQL Injection Prevention** - Parameterized queries
- **Rate Limiting** - Configurable per endpoint

## 📊 Database

### Multi-Tenant Design
Every table includes `business_id` for strict tenant isolation:
```python
class Product(Base):
    business_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("business.id", ondelete="CASCADE")
    )
```

### Key Tables
- `business` - Tenant/business account
- `user` - Business users/employees
- `customer` - Customer records
- `product` - Product inventory
- `invoice` - Sales invoices
- `invoice_item` - Line items
- `payment` - Payment transactions
- `stock_movement` - Inventory audit log

### Indexes & Constraints
- Unique constraints with business_id for tenant isolation
- Indexes on frequently queried fields
- CASCADE deletes for related data cleanup

## 📡 API Endpoints

### Authentication
```
POST   /auth/register      - User registration
POST   /auth/login         - User login
POST   /auth/refresh       - Refresh access token
POST   /auth/logout        - User logout
```

### Customers
```
GET    /customers          - List customers
POST   /customers          - Create customer
GET    /customers/{id}     - Get customer
PUT    /customers/{id}     - Update customer
DELETE /customers/{id}     - Delete customer
```

### Products
```
GET    /products           - List products
POST   /products           - Create product
GET    /products/{id}      - Get product
PUT    /products/{id}      - Update product
DELETE /products/{id}      - Delete product
GET    /products/low-stock - Low stock items
```

### Invoices
```
GET    /invoices           - List invoices
POST   /invoices           - Create invoice
GET    /invoices/{id}      - Get invoice
POST   /invoices/{id}/send - Send invoice
POST   /invoices/{id}/payment - Record payment
```

### Reports
```
GET    /reports/sales      - Sales analytics
GET    /reports/revenue    - Revenue tracking
GET    /reports/inventory  - Inventory valuation
GET    /reports/debtors    - Debtor analysis
```

## 🔧 Configuration

### Environment Variables

```env
# Database
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=viyapar

# Security
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application
DEBUG=true
PROJECT_NAME=Viyapar

# Redis (optional)
REDIS_URL=redis://localhost:6379
ENABLE_CACHING=false

# CORS
CORS_ORIGINS=["http://localhost:3000"]
```

## 📦 Dependencies

### Core
- **FastAPI** 0.104+ - Web framework
- **SQLAlchemy** 2.0+ - ORM
- **Pydantic** 2.0+ - Validation
- **Alembic** - Migrations
- **python-jose** - JWT handling
- **passlib** - Password hashing
- **psycopg2** - PostgreSQL driver
- **asyncpg** - Async PostgreSQL

### Optional
- **redis** - Caching
- **pytest** - Testing
- **black** - Code formatting
- **flake8** - Linting

See `backend/requirements.txt` for exact versions.

## 🧪 Testing

```bash
# Run all tests
pytest backend/tests/

# Run with coverage
pytest backend/tests/ --cov=app

# Run specific test
pytest backend/tests/test_auth.py -v

# Run and stop on first failure
pytest backend/tests/ -x
```

## 🐳 Docker

### Build
```bash
docker build -f backend/Dockerfile -t viyapar-backend:latest .
```

### Run
```bash
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql+asyncpg://user:pass@postgres/viyapar \
  viyapar-backend:latest
```

### Docker Compose
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

## 📈 Performance

### Optimizations
- **Connection Pooling** - 20 connections default
- **Index Strategy** - Optimized for query patterns
- **Async/Await** - Non-blocking operations
- **Query Optimization** - Eager loading where beneficial
- **Caching** - Optional Redis caching

### Monitoring
```bash
# Health check
curl http://localhost:8000/health

# API metrics (when implemented)
GET /api/v1/metrics

# Database query logging
# Set DATABASE_ECHO=true in .env
```

## 🚢 Deployment

### Production Checklist
- [ ] Change JWT_SECRET_KEY
- [ ] Set DEBUG=false
- [ ] Configure HTTPS/SSL
- [ ] Setup database backups
- [ ] Enable logging
- [ ] Configure rate limiting
- [ ] Setup monitoring/alerting
- [ ] Test all endpoints
- [ ] Load test the system

### Deployment Options

**Docker Swarm**
```bash
docker service create --name backend viyapar-backend:latest
```

**Kubernetes**
```bash
kubectl apply -f backend/k8s/deployment.yaml
```

**Heroku**
```bash
git push heroku main
```

**AWS ECS/Fargate** (See infrastructure/terraform/)

## 📝 Code Style

- **Python** - PEP 8
- **Type Hints** - Full type coverage
- **Docstrings** - Google format
- **Code Format** - Black
- **Linting** - Flake8

## 🐛 Troubleshooting

**PostgreSQL Connection Error**
```bash
# Check if PostgreSQL is running
pg_isready -h localhost -p 5432

# Create database if missing
createdb -U postgres viyapar
```

**Port Already in Use**
```bash
lsof -i :8000
kill -9 <PID>
```

**Migration Issues**
```bash
alembic downgrade -1
alembic upgrade head
```

**Token Invalid**
- Ensure JWT_SECRET_KEY is set
- Check token hasn't expired (30 min default)
- Verify header format: `Authorization: Bearer <token>`

## 🤝 Contributing

1. Follow PEP 8 code style
2. Add type hints to all functions
3. Write tests for new features
4. Update documentation
5. Run `black` and `flake8` before committing

## 📞 Support

- Documentation: See links above
- Issues: GitHub Issues
- FastAPI Help: https://fastapi.tiangolo.com/
- SQLAlchemy: https://docs.sqlalchemy.org/

## 📄 License

Proprietary - Viyapar SaaS Platform

---

**Ready to Deploy?** Check out [BACKEND_SETUP_GUIDE.md](./BACKEND_SETUP_GUIDE.md)

**Want to Understand the Design?** Read [BACKEND_ARCHITECTURE.md](./docs/BACKEND_ARCHITECTURE.md)

**Building an Endpoint?** See [API_REFERENCE.md](./docs/API_REFERENCE.md)

def generate_unique_email(prefix: str = "customer") -> str:
    """Generate truly unique email"""
    ts = int(time.time() * 1000)
    uid = uuid.uuid4().hex[:16]
    return f"{prefix}.{ts}.{uid}@example.com"

def generate_unique_sku() -> str:
    """Generate truly unique SKU"""
    return f"SKU-{uuid.uuid4().hex[:20].upper()}"
