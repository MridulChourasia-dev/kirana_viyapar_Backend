# Backend Setup & Quick Start Guide

## What You're Setting Up

A production-ready FastAPI backend for a SaaS billing & inventory management system. Includes:
- Multi-tenant architecture
- JWT authentication
- PostgreSQL database with Alembic migrations
- Redis caching (optional)
- Comprehensive REST API with Swagger documentation

## Quick Start (Docker - Recommended)

### Prerequisites
- Docker and Docker Compose installed
- 2GB RAM minimum
- Internet connection

### Steps

**1. Create .env file**
```bash
cp backend/.env.example .env
```

**2. Update .env (if needed)**
```bash
nano .env
```

Default values work for local development:
```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=viyapar
JWT_SECRET_KEY=your-secret-key-change-in-production
DEBUG=true
```

**3. Start services**
```bash
docker-compose up -d
```

**4. Run migrations**
```bash
docker exec viyapar-backend alembic upgrade head
```

**5. Verify**
```bash
curl http://localhost:8000/health
```

Response should be:
```json
{"status": "healthy", "version": "1.0.0"}
```

**6. Access API**
- Swagger Docs: http://localhost:8000/api/v1/docs
- API Base URL: http://localhost:8000/api/v1

Done! ✅

## Manual Setup (Local Development)

### Prerequisites
- Python 3.11+
- PostgreSQL 15+
- Redis 7+ (optional)
- pip/venv

### Step-by-Step

**1. Clone Repository**
```bash
cd viyapar_application
```

**2. Create Virtual Environment**
```bash
python -m venv venv

# Activate it
On Linux/Mac:
source venv/bin/activate

On Windows:
venv\Scripts\activate
```

**3. Install Dependencies**
```bash
pip install -r backend/requirements.txt
```

**4. Create .env File**
```bash
cp backend/.env.example backend/.env
```

**5. Edit .env with Your Database Details**
```
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=viyapar
```

**6. Run Database Migrations**
```bash
cd backend
alembic upgrade head
```

**7. Start Development Server**
```bash
uvicorn app.main:app --reload

# Default: http://localhost:8000
```

**8. Verify Installation**

Open browser to:
```
http://localhost:8000/health
http://localhost:8000/api/v1/docs
```

## Project Structure

```
backend/
├── app/
│   ├── api/v1/                 # API routes
│   ├── models/                 # Database models
│   ├── schemas/                # Request/response schemas  
│   ├── services/               # Business logic
│   ├── core/                   # Configuration
│   ├── db/                     # Database setup
│   ├── middleware/             # Custom middleware
│   └── main.py                 # Entry point
├── alembic/                    # Database migrations
├── Dockerfile                  # Container image
├── requirements.txt            # Python packages
├── .env.example                # Environment template
└── README.md                   # Documentation
```

## Common Tasks

### Run Migrations
```bash
cd backend
alembic upgrade head              # Apply all pending migrations
alembic current                   # Show current migration
alembic revision --autogenerate   # Generate new migration
```

### Create Database Dump
```bash
pg_dump -U postgres viyapar > backup.sql
```

### Restore Database
```bash
psql -U postgres viyapar < backup.sql
```

### Run Tests
```bash
pytest backend/tests/
pytest backend/tests/ -v --cov=app
```

### Format Code
```bash
black backend/app/
flake8 backend/app/
```

### Check Requirements
```bash
pip list  # Show installed packages
pip freeze > requirements.txt  # Update requirements
```

## Testing the APIs

### Using cURL

**Register User**
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Rahul Sharma",
    "email": "rahul@example.com",
    "password": "SecurePassword123",
    "phone": "+919876543210",
    "business_name": "Sharma Traders"
  }'
```

**Login**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "rahul@example.com",
    "password": "SecurePassword123"
  }'
```

**Create Customer**
```bash
curl -X POST http://localhost:8000/api/v1/customers \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Amit Patel",
    "phone": "+919876543210",
    "email": "amit@example.com",
    "city": "Mumbai"
  }'
```

### Using Swagger UI

1. Open http://localhost:8000/api/v1/docs
2. Click "Authorize" button
3. Enter access token
4. Try out endpoints directly from web UI

## Troubleshooting

### Issue: "connection refused" PostgreSQL error

**Solution:**
```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql

# Or start it
sudo systemctl start postgresql

# Or use Docker
docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=postgres postgres:15
```

### Issue: "Port 8000 already in use"

**Solution:**
```bash
# Find process using port
lsof -i :8000

# Kill it
kill -9 <PID>

# Or use different port
uvicorn app.main:app --port 8001
```

### Issue: "database 'viyapar' does not exist"

**Solution:**
```bash
# Create database
createdb -U postgres viyapar

# Or via psql
psql -U postgres
CREATE DATABASE viyapar;
```

### Issue: Migration conflicts

**Solution:**
```bash
cd backend
# Check migration status
alembic current

# If stuck, downgrade and retry
alembic downgrade -1
alembic upgrade head
```

### Issue: JWT token invalid

**Solution:**
1. Ensure JWT_SECRET_KEY is set in .env
2. Token may be expired (default 30 minutes)
3. Check Authorization header format: `Bearer <token>`

## Environment Variables

```env
# Database
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=viyapar

# Security
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Application
DEBUG=true
PROJECT_NAME=Viyapar - Billing & Inventory System

# Redis (Optional)
REDIS_URL=redis://localhost:6379/0
ENABLE_CACHING=false

# CORS
CORS_ORIGINS=["http://localhost", "http://localhost:3000"]
```

## Production Deployment

### Security Checklist
- [ ] Change JWT_SECRET_KEY to strong random value
- [ ] Set DEBUG=false
- [ ] Use environment-specific .env file
- [ ] Enable HTTPS/TLS
- [ ] Setup database backups
- [ ] Configure rate limiting
- [ ] Enable request logging
- [ ] Setup error tracking (Sentry)
- [ ] Configure CDN for static files
- [ ] Use strong database password

### Deployment Steps

1. **Build Docker Image**
   ```bash
   docker build -f backend/Dockerfile -t viyapar-backend:latest .
   docker push your-registry/viyapar-backend:latest
   ```

2. **Deploy to Server**
   ```bash
   # Using Docker Swarm
   docker service create --name backend viyapar-backend:latest

   # Using Kubernetes
   kubectl apply -f backend/k8s/deployment.yaml
   ```

3. **Setup SSL Certificate**
   ```bash
   # Using Let's Encrypt
   certbot certonly --standalone -d api.yourdomain.com
   ```

4. **Configure Reverse Proxy (Nginx)**
   ```nginx
   server {
       listen 443 ssl;
       server_name api.yourdomain.com;
       
       ssl_certificate /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem;
       ssl_certificate_key /etc/letsencrypt/live/api.yourdomain.com/privkey.pem;
       
       location / {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

## Documentation Links

- [Full Architecture Guide](./BACKEND_ARCHITECTURE.md)
- [API Reference](./API_REFERENCE.md)
- [Database Schema](./DATABASE_SCHEMA.md)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/)

## Support & Help

- First, check the troubleshooting section above
- Search existing issues in repository
- Check FastAPI documentation at https://fastapi.tiangolo.com/
- Review code comments and docstrings
- Check logs: `docker-compose logs backend`

## Next Steps

1. **Configure Frontend** - Point frontend to http://localhost:8000/api/v1
2. **Test APIs** - Use Swagger at http://localhost:8000/api/v1/docs
3. **Understand Models** - Review `backend/app/models/`
4. **Add Custom Logic** - Extend services in `backend/app/services/`
5. **Deploy** - Follow production deployment steps

Congratulations! Your Viyapar backend is ready! 🎉
