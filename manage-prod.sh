#!/bin/bash
# ============================================================================
# Viyapar Production Services Quick Reference
# ============================================================================
# Common commands for managing production services
# ============================================================================

# Define compose file
COMPOSE_FILE="docker-compose.prod.yml"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Display menu
show_menu() {
    clear
    echo -e "${GREEN}╔════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║   Viyapar Production Services Manager          ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "1. Show service status"
    echo "2. View all logs (real-time)"
    echo "3. View specific service logs"
    echo "4. Restart specific service"
    echo "5. Stop all services"
    echo "6. Start all services"
    echo "7. Health check all services"
    echo "8. View resource usage"
    echo "9. Backup database"
    echo "10. Database CLI access"
    echo "11. Run database migrations"
    echo "12. View Celery worker status"
    echo "13. Purge Celery queue"
    echo "14. Exit"
    echo ""
    read -p "Select option (1-14): " choice
}

# Service status
show_status() {
    echo -e "${YELLOW}Fetching service status...${NC}\n"
    docker-compose -f "$COMPOSE_FILE" ps
    read -p "Press Enter to continue..."
}

# View all logs
view_all_logs() {
    echo -e "${YELLOW}Displaying all service logs (Ctrl+C to exit)...${NC}\n"
    docker-compose -f "$COMPOSE_FILE" logs -f --tail=50
}

# View specific service logs
view_service_logs() {
    echo -e "${YELLOW}Available services:${NC}"
    echo "1. postgres"
    echo "2. redis"
    echo "3. backend"
    echo "4. celery-worker"
    echo "5. celery-scheduler"
    echo "6. nginx"
    read -p "Select service: " service
    
    case $service in
        1) service="postgres" ;;
        2) service="redis" ;;
        3) service="backend" ;;
        4) service="celery-worker" ;;
        5) service="celery-scheduler" ;;
        6) service="nginx" ;;
        *) service="backend" ;;
    esac
    
    echo -e "${YELLOW}Displaying logs for $service (Ctrl+C to exit)...${NC}\n"
    docker-compose -f "$COMPOSE_FILE" logs -f --tail=100 "$service"
}

# Restart service
restart_service() {
    echo -e "${YELLOW}Available services:${NC}"
    echo "1. postgresql"
    echo "2. redis"
    echo "3. backend"
    echo "4. celery-worker"
    echo "5. celery-scheduler"
    echo "6. nginx"
    read -p "Select service to restart (1-6): " service
    
    case $service in
        1) docker-compose -f "$COMPOSE_FILE" restart postgres ;;
        2) docker-compose -f "$COMPOSE_FILE" restart redis ;;
        3) docker-compose -f "$COMPOSE_FILE" restart backend ;;
        4) docker-compose -f "$COMPOSE_FILE" restart celery-worker ;;
        5) docker-compose -f "$COMPOSE_FILE" restart celery-scheduler ;;
        6) docker-compose -f "$COMPOSE_FILE" restart nginx ;;
        *) echo -e "${RED}Invalid selection${NC}" ;;
    esac
    
    echo -e "${GREEN}Service restart initiated${NC}"
    sleep 2
}

# Stop services
stop_services() {
    read -p "Are you sure you want to stop all services? (yes/no): " confirm
    if [ "$confirm" = "yes" ]; then
        echo -e "${YELLOW}Stopping all services...${NC}"
        docker-compose -f "$COMPOSE_FILE" stop
        echo -e "${GREEN}All services stopped${NC}"
    fi
    read -p "Press Enter to continue..."
}

# Start services
start_services() {
    echo -e "${YELLOW}Starting all services...${NC}"
    docker-compose -f "$COMPOSE_FILE" up -d
    echo -e "${GREEN}Starting services in background${NC}"
    sleep 5
    echo -e "${YELLOW}Waiting for services to be ready...${NC}"
    sleep 10
    show_status
}

# Health check
run_health_check() {
    echo -e "${YELLOW}Running health checks...${NC}\n"
    
    echo -e "${GREEN}PostgreSQL:${NC}"
    docker-compose -f "$COMPOSE_FILE" exec -T postgres pg_isready -h postgres && echo "  ✓ Ready" || echo "  ✗ Not ready"
    
    echo -e "${GREEN}Redis:${NC}"
    docker-compose -f "$COMPOSE_FILE" exec -T redis redis-cli ping > /dev/null && echo "  ✓ Ready" || echo "  ✗ Not ready"
    
    echo -e "${GREEN}Backend:${NC}"
    curl -s -k https://localhost/health > /dev/null && echo "  ✓ Ready" || echo "  ✗ Not ready"
    
    echo ""
    read -p "Press Enter to continue..."
}

# Resource usage
view_resources() {
    echo -e "${YELLOW}Container Resource Usage:${NC}\n"
    docker-compose -f "$COMPOSE_FILE" stats --no-stream
    read -p "Press Enter to continue..."
}

# Backup database
backup_db() {
    read -p "Enter backup filename (default: backup_$(date +%Y%m%d_%H%M%S).sql): " backup_file
    backup_file="${backup_file:-backup_$(date +%Y%m%d_%H%M%S).sql}"
    
    echo -e "${YELLOW}Backing up database to $backup_file...${NC}"
    
    mkdir -p ./backups
    
    if docker-compose -f "$COMPOSE_FILE" exec -T postgres pg_dump \
        -U "${POSTGRES_USER:-viyapar}" \
        -d "${POSTGRES_DB:-viyapar}" \
        > "./backups/$backup_file"; then
        echo -e "${GREEN}✓ Backup completed: ./backups/$backup_file${NC}"
        echo -e "  Size: $(du -h "./backups/$backup_file" | cut -f1)"
    else
        echo -e "${RED}✗ Backup failed${NC}"
    fi
    
    read -p "Press Enter to continue..."
}

# Database CLI
db_cli() {
    echo -e "${YELLOW}Connecting to PostgreSQL CLI...${NC}"
    docker-compose -f "$COMPOSE_FILE" exec postgres psql -U "${POSTGRES_USER:-viyapar}" -d "${POSTGRES_DB:-viyapar}"
}

# Run migrations
run_migrations() {
    echo -e "${YELLOW}Running database migrations...${NC}"
    docker-compose -f "$COMPOSE_FILE" exec backend alembic upgrade head
    echo -e "${GREEN}✓ Migrations completed${NC}"
    read -p "Press Enter to continue..."
}

# Celery status
celery_status() {
    echo -e "${YELLOW}Celery Worker Status:${NC}\n"
    docker-compose -f "$COMPOSE_FILE" exec celery-worker celery -A app.celery_app inspect active
    echo ""
    echo -e "${YELLOW}Celery Tasks Registered:${NC}\n"
    docker-compose -f "$COMPOSE_FILE" exec celery-worker celery -A app.celery_app inspect registered
    read -p "Press Enter to continue..."
}

# Purge queue
purge_queue() {
    read -p "Are you sure you want to purge the Celery queue? (yes/no): " confirm
    if [ "$confirm" = "yes" ]; then
        echo -e "${YELLOW}Purging Celery queue...${NC}"
        docker-compose -f "$COMPOSE_FILE" exec celery-worker celery -A app.celery_app purge
        echo -e "${GREEN}✓ Queue purged${NC}"
    fi
    read -p "Press Enter to continue..."
}

# Main loop
while true; do
    show_menu
    
    case $choice in
        1) show_status ;;
        2) view_all_logs ;;
        3) view_service_logs ;;
        4) restart_service ;;
        5) stop_services ;;
        6) start_services ;;
        7) run_health_check ;;
        8) view_resources ;;
        9) backup_db ;;
        10) db_cli ;;
        11) run_migrations ;;
        12) celery_status ;;
        13) purge_queue ;;
        14) exit 0 ;;
        *) echo -e "${RED}Invalid option${NC}"; sleep 2 ;;
    esac
done
