#!/bin/bash
# ============================================================================
# Health Check Script for Viyapar Services
# ============================================================================
# Monitors the health of all running services
# ============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

COMPOSE_FILE="${1:-docker-compose.prod.yml}"

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}Viyapar Services Health Check${NC}"
echo -e "${BLUE}================================================${NC}\n"

# Function to check container health
check_container() {
    local container=$1
    local service=$2
    
    if docker-compose -f "$COMPOSE_FILE" ps "$container" | grep -q "Up"; then
        echo -e "${GREEN}✓ $service is running${NC}"
        return 0
    else
        echo -e "${RED}✗ $service is NOT running${NC}"
        return 1
    fi
}

# Function to check container logs for errors
check_logs() {
    local container=$1
    local service=$2
    
    local errors=$(docker-compose -f "$COMPOSE_FILE" logs "$container" 2>&1 | grep -i "error" | wc -l)
    
    if [ "$errors" -gt 0 ]; then
        echo -e "${YELLOW}  ⚠ Found $errors errors in logs${NC}"
    else
        echo -e "${GREEN}  ✓ No errors in recent logs${NC}"
    fi
}

# Check all services
echo -e "${BLUE}Service Status:${NC}"
echo "────────────────────────────────────────────────"

check_container "viyapar-db-prod" "PostgreSQL Database" && check_logs "viyapar-db-prod" "PostgreSQL"
check_container "viyapar-redis-prod" "Redis Cache" && check_logs "viyapar-redis-prod" "Redis"
check_container "viyapar-backend-prod" "FastAPI Backend" && check_logs "viyapar-backend-prod" "FastAPI"
check_container "viyapar-celery-worker-prod" "Celery Worker" && check_logs "viyapar-celery-worker-prod" "Celery Worker"
check_container "viyapar-celery-scheduler-prod" "Celery Scheduler" && check_logs "viyapar-celery-scheduler-prod" "Celery Scheduler"
check_container "viyapar-nginx-prod" "Nginx Proxy" && check_logs "viyapar-nginx-prod" "Nginx"

echo ""
echo -e "${BLUE}Resource Usage:${NC}"
echo "────────────────────────────────────────────────"
docker-compose -f "$COMPOSE_FILE" stats --no-stream

echo ""
echo -e "${BLUE}Network Status:${NC}"
echo "────────────────────────────────────────────────"

# Check database connectivity
echo -n "PostgreSQL connectivity: "
if docker-compose -f "$COMPOSE_FILE" exec -T postgres pg_isready -h postgres -U "${POSTGRES_USER:-viyapar}" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ OK${NC}"
else
    echo -e "${RED}✗ FAILED${NC}"
fi

# Check Redis connectivity
echo -n "Redis connectivity: "
if docker-compose -f "$COMPOSE_FILE" exec -T redis redis-cli -a "${REDIS_PASSWORD:-changeme}" ping > /dev/null 2>&1; then
    echo -e "${GREEN}✓ OK${NC}"
else
    echo -e "${RED}✗ FAILED${NC}"
fi

# Check API health
echo -n "API health endpoint: "
if curl -s -k https://localhost/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ OK${NC}"
else
    echo -e "${RED}✗ FAILED${NC}"
fi

echo ""
echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}Health Check Complete${NC}"
echo -e "${BLUE}================================================${NC}"
