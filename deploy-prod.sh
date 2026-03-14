#!/bin/bash
# ============================================================================
# Viyapar Production Deployment Guide
# ============================================================================
# This script provides a reference for deploying Viyapar with Docker Compose
# in a production environment.
# ============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Viyapar Production Deployment Checklist${NC}"
echo -e "${GREEN}========================================${NC}\n"

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${RED}✗ .env file not found!${NC}"
    echo -e "${YELLOW}  Please copy .env.prod.example to .env and update with your values${NC}"
    exit 1
fi

echo -e "${GREEN}✓ .env file found${NC}\n"

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"

if ! command -v docker &> /dev/null; then
    echo -e "${RED}✗ Docker not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Docker is installed${NC}"

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}✗ Docker Compose not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Docker Compose is installed${NC}\n"

# Create SSL directory if it doesn't exist
if [ ! -d "nginx/ssl" ]; then
    echo -e "${YELLOW}Creating SSL directory...${NC}"
    mkdir -p nginx/ssl
    echo -e "${GREEN}✓ SSL directory created${NC}\n"
fi

# Check for SSL certificates
if [ ! -f "nginx/ssl/cert.pem" ] || [ ! -f "nginx/ssl/key.pem" ]; then
    echo -e "${RED}⚠ SSL certificates not found!${NC}"
    echo -e "${YELLOW}  You need to provide:${NC}"
    echo -e "${YELLOW}    - nginx/ssl/cert.pem (certificate)${NC}"
    echo -e "${YELLOW}    - nginx/ssl/key.pem (private key)${NC}"
    echo -e "${YELLOW}    - nginx/ssl/chain.pem (certificate chain)${NC}"
    echo -e "${YELLOW}    - nginx/ssl/dhparam.pem (DHE parameters)${NC}\n"
    
    echo -e "${YELLOW}To generate self-signed certificates:${NC}"
    echo "  openssl req -x509 -newkey rsa:4096 -keyout nginx/ssl/key.pem -out nginx/ssl/cert.pem -days 365 -nodes"
    echo "  cp nginx/ssl/cert.pem nginx/ssl/chain.pem"
    echo "  openssl dhparam -out nginx/ssl/dhparam.pem 2048"
    echo ""
fi

# Check for /etc/nginx/ssl in production
if [ ! -f "nginx/ssl/dhparam.pem" ]; then
    echo -e "${YELLOW}Generating DH parameters (this may take a few minutes)...${NC}"
    openssl dhparam -out nginx/ssl/dhparam.pem 2048
    echo -e "${GREEN}✓ DH parameters generated${NC}\n"
fi

echo -e "${GREEN}✓ SSL certificates configured${NC}\n"

# Dry-run docker-compose
echo -e "${YELLOW}Validating docker-compose configuration...${NC}"
if docker-compose -f docker-compose.prod.yml config > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Docker Compose configuration is valid${NC}\n"
else
    echo -e "${RED}✗ Docker Compose configuration is invalid${NC}"
    exit 1
fi

# Display deployment info
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment Information${NC}"
echo -e "${GREEN}========================================${NC}\n"

echo "Services to be started:"
echo "  • PostgreSQL Database (postgres:5432)"
echo "  • Redis Cache (redis:6379)"
echo "  • FastAPI Backend (backend:8000)"
echo "  • Celery Worker (background tasks)"
echo "  • Celery Scheduler (scheduled tasks)"
echo "  • Nginx Reverse Proxy (HTTP/HTTPS)\n"

echo -e "${YELLOW}To start the production deployment, run:${NC}"
echo "  docker-compose -f docker-compose.prod.yml up -d\n"

echo -e "${YELLOW}To view logs:${NC}"
echo "  docker-compose -f docker-compose.prod.yml logs -f [service-name]\n"

echo -e "${YELLOW}To stop all services:${NC}"
echo "  docker-compose -f docker-compose.prod.yml down\n"

echo -e "${YELLOW}To backup the database:${NC}"
echo "  docker-compose -f docker-compose.prod.yml exec postgres pg_dump -U \$POSTGRES_USER -d \$POSTGRES_DB > backup.sql\n"

echo -e "${YELLOW}To restore from backup:${NC}"
echo "  docker-compose -f docker-compose.prod.yml exec -T postgres psql -U \$POSTGRES_USER -d \$POSTGRES_DB < backup.sql\n"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Ready for deployment!${NC}"
echo -e "${GREEN}========================================${NC}\n"
