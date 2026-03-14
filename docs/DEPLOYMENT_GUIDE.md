# Deployment Guide

## Table of Contents

1. [Environment Setup](#environment-setup)
2. [Development Setup](#development-setup)
3. [Production Deployment](#production-deployment)
4. [Docker Deployment](#docker-deployment)
5. [Database Migrations](#database-migrations)
6. [Monitoring & Maintenance](#monitoring--maintenance)
7. [Troubleshooting](#troubleshooting)

---

## Environment Setup

### System Requirements

- **OS**: Linux (Ubuntu 20.04+), macOS, or Windows WSL2
- **Python**: 3.9 or higher
- **PostgreSQL**: 12 or higher
- **Redis**: 6.0 or higher (optional for development)
- **Docker**: Latest stable (for containerized deployment)

### Install Python Dependencies

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the backend directory:

```bash
# API Configuration
API_V1_STR=/api/v1
PROJECT_NAME=Viyapar - Billing & Inventory System
VERSION=1.0.0
DEBUG=False

# Database Configuration
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=viyapar

# Redis Configuration (Optional)
REDIS_URL=redis://localhost:6379/0
ENABLE_CACHING=False

# Security Configuration
JWT_SECRET_KEY=your_secret_key_change_in_production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Server Configuration
DEBUG=False
CORS_ORIGINS=["http://localhost:3000","http://localhost:8080"]

# Email Configuration (Optional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# AWS S3 Configuration (Optional)
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_S3_BUCKET=viyapar-bucket
AWS_REGION=us-east-1
```

### Generate JWT Secret Key

```python
import secrets
print(secrets.token_urlsafe(32))
```

---

## Development Setup

### 1. Initialize Database

```bash
# Create PostgreSQL database
createdb viyapar
createuser viyapar_user --password

# Run migrations
cd backend
alembic upgrade head
```

### 2. Start PostgreSQL (if using local installation)

```bash
# macOS (if installed via homebrew)
brew services start postgresql

# Linux
sudo systemctl start postgresql

# Or use Docker
docker run -d \
  --name postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=viyapar \
  -p 5432:5432 \
  postgres:14-alpine
```

### 3. Start Redis (Optional)

```bash
# macOS
brew services start redis

# Or use Docker
docker run -d \
  --name redis \
  -p 6379:6379 \
  redis:7-alpine
```

### 4. Run Development Server

```bash
# From backend directory
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Server will be available at:
- API: `http://localhost:8000`
- Swagger Docs: `http://localhost:8000/api/v1/docs`
- ReDoc: `http://localhost:8000/api/v1/redoc`

### 5. (Optional) Start Celery Worker

```bash
# In a new terminal
cd backend
celery -A app.workers.celery_app worker --loglevel=info

# Monitor with Flower
celery -A app.workers.celery_app flower --port=5555
# Access at: http://localhost:5555
```

---

## Production Deployment

### Prerequisites

1. AWS Account (or other cloud provider)
2. PostgreSQL database (RDS recommended)
3. Redis cluster (ElastiCache recommended)
4. S3 bucket for file storage
5. Load balancer (ALB/NLB)
6. SSL certificate

### 1. Server Preparation

#### Option A: Traditional VPS Deployment

```bash
# SSH into your server
ssh ubuntu@your_server_ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and system dependencies
sudo apt install -y python3.11 python3-pip python3-venv git nginx supervisor

# Clone repository
git clone https://github.com/your-org/viyapar.git
cd viyapar/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
nano .env  # Edit with production secrets
```

#### Option B: Docker/Container Deployment

```bash
# Build Docker image
docker build -t viyapar-backend:latest .

# Push to registry
docker tag viyapar-backend:latest your-registry/viyapar-backend:latest
docker push your-registry/viyapar-backend:latest
```

### 2. Database Setup

#### RDS PostgreSQL

```bash
# Via AWS CLI
aws rds create-db-instance \
  --db-instance-identifier viyapar-prod \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username postgres \
  --master-user-password your_secure_password \
  --allocated-storage 100 \
  --storage-type gp2

# Run migrations
export DATABASE_URL=postgresql://postgres:password@your-rds-endpoint:5432/viyapar
cd backend
alembic upgrade head
```

#### ElastiCache Redis

```bash
aws elasticache create-cache-cluster \
  --cache-cluster-id viyapar-redis \
  --cache-node-type cache.t3.micro \
  --engine redis \
  --num-cache-nodes 1
```

### 3. FastAPI Server Configuration

#### Using Gunicorn + Supervisor

```bash
# Install gunicorn
pip install gunicorn

# Create supervisor configuration
sudo nano /etc/supervisor/conf.d/viyapar.conf
```

**Content:**
```ini
[program:viyapar]
directory=/home/ubuntu/viyapar/backend
command=/home/ubuntu/viyapar/backend/venv/bin/gunicorn \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 127.0.0.1:8000 \
  app.main:app
user=ubuntu
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/viyapar/gunicorn.log
```

```bash
# Create log directory
mkdir -p /var/log/viyapar
sudo chown ubuntu:ubuntu /var/log/viyapar

# Start supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start viyapar
```

#### Using Systemd

**Create `/etc/systemd/system/viyapar.service`:**

```ini
[Unit]
Description=Viyapar Backend API
After=network.target

[Service]
Type=notify
User=ubuntu
WorkingDirectory=/home/ubuntu/viyapar/backend
ExecStart=/home/ubuntu/viyapar/backend/venv/bin/gunicorn \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 127.0.0.1:8000 \
  app.main:app
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable viyapar
sudo systemctl start viyapar
sudo systemctl status viyapar
```

### 4. Nginx Reverse Proxy

**Create `/etc/nginx/sites-available/viyapar`:**

```nginx
upstream viyapar_backend {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name api.viyapar.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.viyapar.com;
    
    # SSL Certificate
    ssl_certificate /etc/letsencrypt/live/api.viyapar.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.viyapar.com/privkey.pem;
    
    # SSL Configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # Security Headers
    add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;
    add_header X-Content-Type-Options \"nosniff\" always;
    add_header X-Frame-Options \"SAMEORIGIN\" always;
    add_header X-XSS-Protection \"1; mode=block\" always;
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=100r/s;
    limit_req zone=api_limit burst=200 nodelay;
    
    # Logging
    access_log /var/log/nginx/viyapar_access.log;
    error_log /var/log/nginx/viyapar_error.log;
    
    # Proxy configuration
    location / {
        proxy_pass http://viyapar_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 60s;
        proxy_connect_timeout 60s;
    }
    
    # WebSocket support
    location ~ ^/ws {
        proxy_pass http://viyapar_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection \"upgrade\";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/viyapar /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 5. SSL Certificate (Let's Encrypt)

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot certonly --nginx -d api.viyapar.com

# Auto-renew
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

### 6. Celery Workers for Background Tasks

**Create `/etc/systemd/system/viyapar-celery.service`:**

```ini
[Unit]
Description=Viyapar Celery Worker
After=network.target

[Service]
Type=forking
User=ubuntu
WorkingDirectory=/home/ubuntu/viyapar/backend
ExecStart=/home/ubuntu/viyapar/backend/venv/bin/celery -A app.workers.celery_app worker \
  --loglevel=info \
  --concurrency=4 \
  --logfile=/var/log/viyapar/celery.log
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

---

## Docker Deployment

### Docker Compose (Development)

**Create `docker-compose.yml`:**

```yaml
version: '3.8'

services:
  db:
    image: postgres:14-alpine
    environment:
      POSTGRES_USER: viyapar_user
      POSTGRES_PASSWORD: viyapar_password
      POSTGRES_DB: viyapar
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U viyapar_user"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build: ./backend
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    ports:
      - "8000:8000\"\n    environment:\n      DATABASE_URL: postgresql+asyncpg://viyapar_user:viyapar_password@db:5432/viyapar\n      REDIS_URL: redis://redis:6379\n    volumes:\n      - ./backend:/app\n    depends_on:\n      db:\n        condition: service_healthy\n      redis:\n        condition: service_healthy\n\n  celery:\n    build: ./backend\n    command: celery -A app.workers.celery_app worker --loglevel=info\n    environment:\n      DATABASE_URL: postgresql+asyncpg://viyapar_user:viyapar_password@db:5432/viyapar\n      REDIS_URL: redis://redis:6379\n    depends_on:\n      - db\n      - redis\n\nvolumes:\n  postgres_data:\n```\n\n```bash\n# Start services\ndocker-compose up -d\n\n# Run migrations\ndocker-compose exec backend alembic upgrade head\n\n# View logs\ndocker-compose logs -f backend\n\n# Stop services\ndocker-compose down\n```\n\n### Production Docker Deployment\n\n**Dockerfile:**\n\n```dockerfile\nFROM python:3.11-slim\n\nWORKDIR /app\n\n# Install system dependencies\nRUN apt-get update && apt-get install -y \\\n    gcc \\\n    postgresql-client \\\n    && rm -rf /var/lib/apt/lists/*\n\n# Copy requirements\nCOPY requirements.txt .\n\n# Install Python dependencies\nRUN pip install --no-cache-dir -r requirements.txt\n\n# Copy application code\nCOPY app /app/app\nCOPY alembic /app/alembic\nCOPY alembic.ini /app/\n\n# Run migrations and start server\nCMD [\"sh\", \"-c\", \"alembic upgrade head && gunicorn --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 app.main:app\"]\n```\n\n```bash\n# Build image\ndocker build -t viyapar-backend:1.0.0 .\n\n# Push to registry\ndocker tag viyapar-backend:1.0.0 your-registry/viyapar-backend:1.0.0\ndocker push your-registry/viyapar-backend:1.0.0\n\n# Deploy\ndocker run -d \\\n  -e DATABASE_URL=postgresql+asyncpg://user:pass@host/db \\\n  -e REDIS_URL=redis://redis-host:6379 \\\n  -e JWT_SECRET_KEY=your_secret \\\n  -p 8000:8000 \\\n  your-registry/viyapar-backend:1.0.0\n```\n\n---\n\n## Database Migrations\n\n### Creating Migrations\n\n```bash\n# Auto-generate migration from model changes\ncd backend\nalembic revision --autogenerate -m \"Add user preferences table\"\n\n# Edit the migration file (alembic/versions/xxxxx_message.py)\n# Review changes and adjust if needed\n```\n\n### Applying Migrations\n\n```bash\n# Apply all pending migrations\nalembic upgrade head\n\n# Apply specific number of migrations\nalembic upgrade +2\n\n# Apply to specific revision\nalembic upgrade ae1027a6acf\n```\n\n### Rollback Migrations\n\n```bash\n# Rollback one revision\nalembic downgrade -1\n\n# Rollback to specific revision\nalembic downgrade ae1027a6acf\n```\n\n---\n\n## Monitoring & Maintenance\n\n### Application Monitoring\n\n```bash\n# Check service status\nsudo systemctl status viyapar\n\n# View logs\nsudo journalctl -u viyapar -f\n\n# Check disk usage\ndf -h\n\n# Check memory usage\nfree -h\n```\n\n### Database Maintenance\n\n```bash\n# Connect to database\npsql -h your-host -U postgres -d viyapar\n\n# Analyze query performance\nEXPLAIN ANALYZE SELECT * FROM invoice WHERE business_id = '...';\n\n# Vacuum (cleanup)\nVACUUM;\n\n# Reindex\nREINDEX DATABASE viyapar;\n```\n\n### Backup Strategy\n\n```bash\n# Manual backup\npg_dump -h your-host -U postgres viyapar > backup_$(date +%Y%m%d_%H%M%S).sql\n\n# Automated backup (cron job)\n# Add to crontab: 0 2 * * * pg_dump -h your-host -U postgres viyapar > /backups/viyapar_$(date +\\%Y\\%m\\%d).sql\n```\n\n### Monitoring Tools\n\n- **Prometheus + Grafana**: Metrics collection and visualization\n- **Sentry**: Error tracking and monitoring\n- **NewRelic**: Application performance monitoring\n- **Datadog**: Infrastructure and application monitoring\n\n---\n\n## Troubleshooting\n\n### Common Issues\n\n#### 1. Database Connection Errors\n\n```bash\n# Check connection string\necho $DATABASE_URL\n\n# Test connection\npsql -h your-host -U postgres -c \"SELECT 1;\"\n\n# Check PostgreSQL service\nsudo systemctl status postgresql\n```\n\n#### 2. High Memory Usage\n\n```bash\n# Check Python process memory\nps aux | grep python\n\n# Restart service\nsudo systemctl restart viyapar\n\n# Optimize Gunicorn workers\n# Recommended: workers = (2 × CPU cores) + 1\n```\n\n#### 3. Slow Database Queries\n\n```sql\n-- Check long-running queries\nSELECT pid, query, query_start FROM pg_stat_activity \nWHERE query_start < NOW() - INTERVAL '5 minutes';\n\n-- Analyze query plan\nEXPLAIN ANALYZE SELECT ... FROM table WHERE condition;\n```\n\n#### 4. Celery Tasks Not Processing\n\n```bash\n# Restart Celery worker\nsudo systemctl restart viyapar-celery\n\n# Check queue\ncelery -A app.workers.celery_app inspect active\n\n# Purge queue (clear stuck tasks)\ncelery -A app.workers.celery_app purge\n```\n\n#### 5. SSL Certificate Issues\n\n```bash\n# Check certificate expiry\necho | openssl s_client -servername api.viyapar.com -connect api.viyapar.com:443 2>/dev/null | openssl x509 -noout -dates\n\n# Renew certificate\nsudo certbot renew\n```\n\n### Log Files\n\n- **Application**: `/var/log/viyapar/gunicorn.log`\n- **Celery**: `/var/log/viyapar/celery.log`\n- **Nginx**: `/var/log/nginx/viyapar_access.log`, `/var/log/nginx/viyapar_error.log`\n- **System**: `sudo journalctl -u viyapar`\n\n---\n\n## Performance Tuning\n\n### Gunicorn Configuration\n\n```bash\n# Optimal settings for production\ngunicorn \\\n  --workers 8 \\\n  --worker-class uvicorn.workers.UvicornWorker \\\n  --worker-connections 1000 \\\n  --max-requests 10000 \\\n  --max-requests-jitter 1000 \\\n  --timeout 60 \\\n  app.main:app\n```\n\n### Database Connection Pooling\n\n```python\n# In app/db/session.py\nengine = create_async_engine(\n    settings.ASYNC_DATABASE_URL,\n    echo=False,\n    pool_size=20,\n    max_overflow=10,\n    pool_pre_ping=True,  # Check connections before use\n    pool_recycle=3600,   # Recycle connections every hour\n)\n```\n\n### Nginx Optimization\n\n```nginx\n# In nginx.conf\nworker_processes auto;\nworker_connections 2048;\n\n# Enable gzip compression\ngzip on;\ngzip_types text/plain text/css text/xml text/javascript \n           application/x-javascript application/json \n           application/javascript application/xml+rss;\ngzip_min_length 1000;\n```\n\n---\n\n## Scaling Strategy\n\n### Horizontal Scaling\n\n1. **Load Balancer**: AWS ALB or Nginx\n2. **Multiple Instances**: Run multiple Gunicorn processes\n3. **Shared Database**: Use managed RDS\n4. **Shared Cache**: Use managed ElastiCache\n5. **Shared Storage**: Use S3 for file uploads\n\n### Kubernetes Deployment\n\n```yaml\napiVersion: apps/v1\nkind: Deployment\nmetadata:\n  name: viyapar-backend\nspec:\n  replicas: 3\n  selector:\n    matchLabels:\n      app: viyapar-backend\n  template:\n    metadata:\n      labels:\n        app: viyapar-backend\n    spec:\n      containers:\n      - name: backend\n        image: your-registry/viyapar-backend:latest\n        ports:\n        - containerPort: 8000\n        env:\n        - name: DATABASE_URL\n          valueFrom:\n            secretKeyRef:\n              name: viyapar-secrets\n              key: database-url\n        resources:\n          requests:\n            memory: \"256Mi\"\n            cpu: \"250m\"\n          limits:\n            memory: \"512Mi\"\n            cpu: \"500m\"\n```\n\n---\n\n## Support\n\nFor deployment assistance:\n- Documentation: https://docs.viyapar.com\n- Email: devops@viyapar.com\n- Community: https://discord.gg/viyapar\n