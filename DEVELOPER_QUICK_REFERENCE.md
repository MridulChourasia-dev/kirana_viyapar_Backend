# Backend Quick Reference Card

## 🚀 Start Development

```bash
# Setup
python -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
cd backend && alembic upgrade head

# Run
uvicorn app.main:app --reload

# Access
http://localhost:8000/api/v1/docs
```

## 📁 Project Structure Quick Reference

```
backend/
├── app/main.py                  ← Start here
├── core/config.py               ← Settings
├── db/session.py                ← DB connection
├── models/                      ← ORM models
├── schemas/                     ← Pydantic validation
├── services/                    ← Business logic (TODO)
├── api/v1/                      ← Routes (TODO)
└── middleware/                  ← Custom middleware
```

## 🔑 Key Files & Their Purpose

| File | Purpose | Status |
|------|---------|--------|
| `app/main.py` | FastAPI app setup | ✅ Done |
| `app/core/config.py` | Read from .env | ✅ Done |
| `app/db/session.py` | DB connection pool | ✅ Done |
| `app/models/*.py` | Database schema | ✅ Done |
| `app/schemas/*.py` | Request/response validation | ✅ Done |
| `app/services/*.py` | Business logic | ⏳ TODO |
| `app/api/v1/*.py` | URL routes | ⏳ TODO |

## 🏗️ Adding a New Endpoint

### 1. Ensure Model Exists
```python
# app/models/my_entity.py
class MyEntity(Base):
    __tablename__ = "my_entity"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    business_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("business.id"))
    name: Mapped[str] = mapped_column(String(255))
```

### 2. Create Schemas
```python
# app/schemas/my_entity.py
class MyEntityCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)

class MyEntityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    name: str
```

### 3. Create Service
```python
# app/services/my_entity_service.py
class MyEntityService:
    @staticmethod
    async def create(db: AsyncSession, business_id: uuid.UUID, data: MyEntityCreateRequest):
        db_entity = MyEntity(**data.dict(), business_id=business_id)
        db.add(db_entity)
        await db.commit()
        await db.refresh(db_entity)
        return db_entity
```

### 4. Create Routes
```python
# app/api/v1/my_entity.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db

router = APIRouter(prefix="/my-entities", tags=["My Entity"])

@router.post("/", response_model=MyEntityResponse, status_code=201)
async def create_my_entity(
    data: MyEntityCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    entity = await MyEntityService.create(db, business_id, data)
    return entity

@router.get("/{entity_id}", response_model=MyEntityResponse)
async def get_my_entity(entity_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    entity = await db.get(MyEntity, entity_id)
    return entity
```

### 5. Register Router
```python
# app/api/v1/router.py
from app.api.v1 import my_entity

api_router = APIRouter()
api_router.include_router(my_entity.router)
```

## 🗄️ Database Commands

```bash
# Create migration
alembic revision --autogenerate -m "Add entity table"

# Apply migrations
alembic upgrade head

# Show current migration
alembic current

# Rollback one step
alembic downgrade -1

# Create database
createdb -U postgres viyapar

# Backup database
pg_dump -U postgres viyapar > backup.sql

# Restore database
psql -U postgres viyapar < backup.sql
```

## 🔒 Environment Variables

```env
# Database
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=viyapar

# JWT
JWT_SECRET_KEY=change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# App
DEBUG=true
PROJECT_NAME=Viyapar

# CORS
CORS_ORIGINS=["http://localhost:3000"]
```

## 🧪 Testing Patterns

### Test Authentication
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'
```

### Test Protected Endpoint
```bash
curl http://localhost:8000/api/v1/customers \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

### Test POST
```bash
curl -X POST http://localhost:8000/api/v1/customers \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"name": "Customer Name", "phone": "+919876543210"}'
```

## 🐛 Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `connection refused` | PostgreSQL not running | `systemctl start postgresql` |
| `database does not exist` | DB not created | `createdb viyapar` |
| `Port 8000 in use` | Another process | `lsof -i :8000` then kill |
| `Import error` | Missing module | `pip install -r requirements.txt` |
| `Token invalid` | Wrong secret or expired | Check JWT_SECRET_KEY, token age |

## 📊 Database Schema Quick View

```
business
├── users (many)
├── customers (many)
├── products (many)
│   └── stock_movements (many)
├── categories (many)
└── invoices (many)
    ├── invoice_items (many)
    └── payments (many)
```

## 🔄 Data Flow Example

```
API Request (POST /customers)
    ↓
Router (app/api/v1/customers.py)
    ↓
Service (app/services/customer_service.py)
    ↓
Model (app/models/customer.py - SQLAlchemy)
    ↓
Database (PostgreSQL)
    ↓
Response (app/schemas/customer.py - Pydantic)
    ↓
API Response (JSON)
```

## 🎯 Multi-Tenancy Pattern

```python
# Every endpoint must filter by business_id from JWT token

@router.get("/customers")
async def list_customers(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # IMPORTANT: Filter by business_id
    stmt = select(Customer).where(Customer.business_id == current_user.business_id)
    result = await db.execute(stmt)
    return result.scalars().all()
```

## 📚 Documentation Links

| Document | Purpose |
|----------|---------|
| [BACKEND_SETUP_GUIDE.md](../BACKEND_SETUP_GUIDE.md) | How to install & run |
| [BACKEND_ARCHITECTURE.md](../docs/BACKEND_ARCHITECTURE.md) | Design & architecture |
| [API_REFERENCE.md](../docs/API_REFERENCE.md) | All endpoints |
| [BACKEND_README.md](../BACKEND_README.md) | Overview |

## ⚡ Performance Tips

```python
# ✅ DO: Use async
async def get_customers(db: AsyncSession):
    result = await db.execute(query)

# ❌ DON'T: Use sync
def get_customers(db: Session):
    result = db.execute(query)

# ✅ DO: Add indexes
class Product(Base):
    name: Mapped[str] = mapped_column(String, index=True)

# ✅ DO: Use connection pooling (already configured)
# ❌ DON'T: Create new connections per request
```

## 🆘 Need Help?

1. Check documentation links above
2. Search error message in docs
3. Review similar endpoint in codebase
4. Check FastAPI docs: https://fastapi.tiangolo.com/
5. Check SQLAlchemy docs: https://docs.sqlalchemy.org/

---

**Keep it simple. Follow the patterns. Document as you go.** ✅
