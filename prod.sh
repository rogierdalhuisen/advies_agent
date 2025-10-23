#!/bin/bash

# Production environment helper script
# Usage: ./prod.sh [command]

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

COMPOSE_FILES="-f docker-compose.base.yml -f docker-compose.prod.yml"

# Ensure .env exists
if [ ! -f .env ]; then
    echo -e "${RED}ERROR: No .env file found!${NC}"
    echo -e "${YELLOW}Please create .env from .env.example and configure for production.${NC}"
    exit 1
fi

# Export environment for production
export BUILD_TARGET=production
export ENVIRONMENT=production

case "$1" in
    up)
        echo -e "${GREEN}Starting production environment...${NC}"
        docker-compose $COMPOSE_FILES up -d
        echo -e "${GREEN}Services started. Use './prod.sh logs' to view logs.${NC}"
        echo -e "${YELLOW}Health checks may take up to 40 seconds to initialize.${NC}"
        ;;

    build)
        echo -e "${GREEN}Building production images...${NC}"
        docker-compose $COMPOSE_FILES build --no-cache
        ;;

    rebuild)
        echo -e "${GREEN}Rebuilding production environment...${NC}"
        docker-compose $COMPOSE_FILES up -d --build --no-cache
        echo -e "${GREEN}Services restarted.${NC}"
        ;;

    down)
        echo -e "${YELLOW}Stopping production environment...${NC}"
        read -p "Stop all services? (y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            docker-compose $COMPOSE_FILES down
            echo -e "${GREEN}Services stopped.${NC}"
        fi
        ;;

    restart)
        echo -e "${YELLOW}Restarting production environment...${NC}"
        docker-compose $COMPOSE_FILES restart
        echo -e "${GREEN}Services restarted.${NC}"
        ;;

    logs)
        docker-compose $COMPOSE_FILES logs -f --tail=100 "${@:2}"
        ;;

    status)
        echo -e "${GREEN}Container status:${NC}"
        docker-compose $COMPOSE_FILES ps
        echo ""
        echo -e "${GREEN}Health status:${NC}"
        docker-compose $COMPOSE_FILES ps --format json | python -c "
import sys, json
try:
    for line in sys.stdin:
        data = json.loads(line)
        name = data.get('Name', 'unknown')
        health = data.get('Health', 'N/A')
        state = data.get('State', 'unknown')
        print(f'{name}: {state} (health: {health})')
except: pass
" 2>/dev/null || docker-compose $COMPOSE_FILES ps
        ;;

    health)
        echo -e "${GREEN}Checking service health...${NC}"
        echo ""
        echo "Qdrant:"
        curl -s http://localhost:6333/healthz && echo -e " ${GREEN}✓${NC}" || echo -e " ${RED}✗${NC}"
        echo ""
        echo "Agent:"
        docker-compose $COMPOSE_FILES exec -T agent python -c "import sys; sys.exit(0)" && echo -e "${GREEN}✓${NC}" || echo -e "${RED}✗${NC}"
        ;;

    backup)
        echo -e "${GREEN}Creating backup of Qdrant data...${NC}"
        BACKUP_DIR="./backups/$(date +%Y%m%d_%H%M%S)"
        mkdir -p "$BACKUP_DIR"
        docker run --rm -v advies_agent_qdrant_storage:/data -v "$PWD/$BACKUP_DIR":/backup alpine tar czf /backup/qdrant_backup.tar.gz -C /data .
        docker run --rm -v advies_agent_agent_data:/data -v "$PWD/$BACKUP_DIR":/backup alpine tar czf /backup/agent_data_backup.tar.gz -C /data .
        echo -e "${GREEN}Backup created in $BACKUP_DIR${NC}"
        ;;

    restore)
        if [ -z "$2" ]; then
            echo -e "${RED}ERROR: Please specify backup directory${NC}"
            echo "Usage: ./prod.sh restore [backup_directory]"
            exit 1
        fi
        echo -e "${YELLOW}Restoring from backup: $2${NC}"
        read -p "This will overwrite current data. Continue? (y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            docker run --rm -v advies_agent_qdrant_storage:/data -v "$PWD/$2":/backup alpine tar xzf /backup/qdrant_backup.tar.gz -C /data
            docker run --rm -v advies_agent_agent_data:/data -v "$PWD/$2":/backup alpine tar xzf /backup/agent_data_backup.tar.gz -C /data
            echo -e "${GREEN}Restore complete. Restart services with './prod.sh restart'${NC}"
        fi
        ;;

    update)
        echo -e "${GREEN}Updating production environment...${NC}"
        echo -e "${YELLOW}This will rebuild images and restart services.${NC}"
        read -p "Continue? (y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            docker-compose $COMPOSE_FILES pull
            docker-compose $COMPOSE_FILES build --no-cache
            docker-compose $COMPOSE_FILES up -d --force-recreate
            echo -e "${GREEN}Update complete.${NC}"
        fi
        ;;

    shell)
        echo -e "${GREEN}Opening shell in agent container...${NC}"
        docker-compose $COMPOSE_FILES exec agent /bin/bash
        ;;

    clean-logs)
        echo -e "${YELLOW}Cleaning old logs...${NC}"
        docker-compose $COMPOSE_FILES exec agent find /app/logs -type f -name "*.log" -mtime +7 -delete
        echo -e "${GREEN}Logs older than 7 days removed.${NC}"
        ;;

    *)
        echo -e "${GREEN}Production Environment Helper${NC}"
        echo ""
        echo "Usage: ./prod.sh [command]"
        echo ""
        echo "Commands:"
        echo "  up          - Start production services"
        echo "  build       - Build production images (no cache)"
        echo "  rebuild     - Rebuild and restart services"
        echo "  down        - Stop services"
        echo "  restart     - Restart services"
        echo "  logs [svc]  - View logs (optionally for specific service)"
        echo "  status      - Show container and health status"
        echo "  health      - Check service health"
        echo "  backup      - Create backup of all data volumes"
        echo "  restore DIR - Restore from backup directory"
        echo "  update      - Pull updates and rebuild"
        echo "  shell       - Open bash shell in agent container"
        echo "  clean-logs  - Remove logs older than 7 days"
        echo ""
        echo "Examples:"
        echo "  ./prod.sh up                    # Start production"
        echo "  ./prod.sh logs agent            # View agent logs"
        echo "  ./prod.sh backup                # Create backup"
        echo "  ./prod.sh restore backups/...   # Restore from backup"
        ;;
esac
