#!/bin/bash
# ============================================================================
# Viyapar Production Deployment Script
# ============================================================================
# Automated deployment with safety checks and rollback capability
# ============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
COMPOSE_FILE="docker-compose.prod.yml"
BACKUP_DIR="./backups"
LOG_FILE="./deployment.log"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Functions
log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
    exit 1
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

# Pre-deployment checks
pre_deployment_checks() {
    log "Running pre-deployment checks..."

    # Check Docker
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed or not in PATH"
    fi
    log "✓ Docker found"

    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose is not installed or not in PATH"
    fi
    log "✓ Docker Compose found"

    # Check .env file
    if [ ! -f .env ]; then
        error ".env file not found! Copy .env.prod.example to .env"
    fi
    log "✓ .env file exists"

    # Validate Docker Compose file
    if ! docker-compose -f "$COMPOSE_FILE" config > /dev/null 2>&1; then
        error "Invalid docker-compose configuration"
    fi
    log "✓ Docker Compose configuration is valid"

    # Check SSL certificates
    if [ ! -f "nginx/ssl/cert.pem" ] || [ ! -f "nginx/ssl/key.pem" ]; then
        error "SSL certificates not found in nginx/ssl/"
    fi
    log "✓ SSL certificates found"

    # Check disk space (minimum 5GB)
    available_space=$(df /var/lib/docker | awk 'NR==2 {print $4}')
    if [ "$available_space" -lt 5242880 ]; then
        error "Insufficient disk space (need at least 5GB)"
    fi
    log "✓ Sufficient disk space available"

    log "✓ All pre-deployment checks passed"
}

# Backup database
backup_database() {
    log "Backing up database..."

    mkdir -p "$BACKUP_DIR"

    local backup_file="$BACKUP_DIR/viyapar_backup_$TIMESTAMP.sql"

    if docker-compose -f "$COMPOSE_FILE" exec -T postgres pg_dump \
        -U "${POSTGRES_USER:-viyapar}" \
        -d "${POSTGRES_DB:-viyapar}" \
        --no-password > "$backup_file" 2>/dev/null; then
        
        success "Database backed up to $backup_file"
        log "Backup size: $(du -h "$backup_file" | cut -f1)"
    else
        error "Failed to backup database"
    fi
}

# Pull latest images
pull_images() {
    log "Pulling latest images..."

    if docker-compose -f "$COMPOSE_FILE" pull; then
        success "Images pulled successfully"
    else
        error "Failed to pull images"
    fi
}

# Build images if needed
build_images() {
    log "Building Docker images..."

    if docker-compose -f "$COMPOSE_FILE" build; then
        success "Images built successfully"
    else
        error "Failed to build images"
    fi
}

# Stop running services
stop_services() {
    log "Stopping running services..."

    if docker-compose -f "$COMPOSE_FILE" stop; then
        success "Services stopped"
    else
        error "Failed to stop services"
    fi
}

# Start services
start_services() {
    log "Starting services..."

    if docker-compose -f "$COMPOSE_FILE" up -d; then
        success "Services started"
    else
        error "Failed to start services"
    fi
}

# Wait for services to be ready
wait_for_services() {
    log "Waiting for services to be ready..."

    local max_attempts=60
    local attempt=0

    while [ $attempt -lt $max_attempts ]; do
        if docker-compose -f "$COMPOSE_FILE" ps | grep -q "viyapar-backend-prod.*Up"; then
            if curl -s -k https://localhost/health > /dev/null 2>&1; then
                success "All services are ready"
                return 0
            fi
        fi

        attempt=$((attempt + 1))
        echo -n "."
        sleep 2
    done

    error "Services did not start within 2 minutes"
}

# Run health checks
run_health_checks() {
    log "Running health checks..."

    # Check database
    if docker-compose -f "$COMPOSE_FILE" exec -T postgres pg_isready -h postgres > /dev/null 2>&1; then
        log "✓ Database is healthy"
    else
        error "Database health check failed"
    fi

    # Check Redis
    if docker-compose -f "$COMPOSE_FILE" exec -T redis redis-cli ping > /dev/null 2>&1; then
        log "✓ Redis is healthy"
    else
        error "Redis health check failed"
    fi

    # Check API
    if curl -s -k https://localhost/health | grep -q "healthy"; then
        log "✓ API is healthy"
    else
        error "API health check failed"
    fi

    success "All health checks passed"
}

# Run migrations
run_migrations() {
    log "Running database migrations..."

    if docker-compose -f "$COMPOSE_FILE" exec -T backend alembic upgrade head; then
        success "Database migrations completed"
    else
        error "Database migrations failed"
    fi
}

# Display deployment summary
show_summary() {
    echo ""
    echo -e "${BLUE}================================================${NC}"
    echo -e "${GREEN}✓ Deployment Completed Successfully!${NC}"
    echo -e "${BLUE}================================================${NC}"
    echo ""
    echo "Services deployed:"
    echo "  • PostgreSQL Database"
    echo "  • Redis Cache"
    echo "  • FastAPI Backend"
    echo "  • Celery Worker"
    echo "  • Celery Scheduler"
    echo "  • Nginx Reverse Proxy"
    echo ""
    echo "Access your application:"
    echo "  API: https://api.viyapar.com"
    echo "  Frontend: https://app.viyapar.com"
    echo ""
    echo "Useful commands:"
    echo "  View logs: docker-compose -f $COMPOSE_FILE logs -f [service]"
    echo "  Stop services: docker-compose -f $COMPOSE_FILE stop"
    echo "  Restart service: docker-compose -f $COMPOSE_FILE restart [service]"
    echo "  View resources: docker-compose -f $COMPOSE_FILE stats"
    echo ""
    echo "Backup file: $BACKUP_DIR/viyapar_backup_$TIMESTAMP.sql"
    echo ""
}

# Main deployment flow
main() {
    log "Starting Viyapar Production Deployment"
    log "================================================"

    pre_deployment_checks
    backup_database
    pull_images
    build_images
    stop_services
    start_services
    wait_for_services
    run_migrations
    run_health_checks

    show_summary

    success "Deployment completed!"
}

# Run main function
main "$@"
