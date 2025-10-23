#!/bin/bash

# Development environment helper script
# Usage: ./dev.sh [command]

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

COMPOSE_FILES="-f docker-compose.base.yml -f docker-compose.dev.yml"

# Ensure .env exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}No .env file found. Creating from .env.example...${NC}"
    cp .env.example .env
    echo -e "${GREEN}.env file created. Please review and update with your settings.${NC}"
fi

# Export environment for development
export BUILD_TARGET=development
export ENVIRONMENT=development

case "$1" in
    up)
        echo -e "${GREEN}Starting development environment...${NC}"
        docker-compose $COMPOSE_FILES up
        ;;

    upd)
        echo -e "${GREEN}Starting development environment in detached mode...${NC}"
        docker-compose $COMPOSE_FILES up -d
        echo -e "${GREEN}Services started. Use './dev.sh logs' to view logs.${NC}"
        ;;

    build)
        echo -e "${GREEN}Building development images...${NC}"
        docker-compose $COMPOSE_FILES build
        ;;

    rebuild)
        echo -e "${GREEN}Rebuilding and starting development environment...${NC}"
        docker-compose $COMPOSE_FILES up --build
        ;;

    rebuild-deps)
        echo -e "${GREEN}Rebuilding images from scratch (no cache) to pick up new dependencies...${NC}"
        docker-compose $COMPOSE_FILES build --no-cache
        echo -e "${GREEN}Build complete. Use './dev.sh up' or './dev.sh upd' to start.${NC}"
        ;;

    down)
        echo -e "${YELLOW}Stopping development environment...${NC}"
        docker-compose $COMPOSE_FILES down
        ;;

    restart)
        echo -e "${YELLOW}Restarting development environment...${NC}"
        docker-compose $COMPOSE_FILES restart
        ;;

    logs)
        docker-compose $COMPOSE_FILES logs -f "${@:2}"
        ;;

    shell)
        echo -e "${GREEN}Opening shell in agent container...${NC}"
        docker-compose $COMPOSE_FILES exec agent /bin/bash
        ;;

    python)
        echo -e "${GREEN}Opening Python shell in agent container...${NC}"
        docker-compose $COMPOSE_FILES exec agent python
        ;;

    test)
        echo -e "${GREEN}Running tests in agent container...${NC}"
        docker-compose $COMPOSE_FILES exec agent pytest "${@:2}"
        ;;

    format)
        echo -e "${GREEN}Formatting code with black and ruff...${NC}"
        docker-compose $COMPOSE_FILES exec agent black src/
        docker-compose $COMPOSE_FILES exec agent ruff check --fix src/
        ;;

    run)
        echo -e "${GREEN}Running Python module in agent container...${NC}"
        docker-compose $COMPOSE_FILES exec agent python -m "${@:2}"
        ;;

    qdrant-ui)
        echo -e "${GREEN}Opening Qdrant UI in browser...${NC}"
        echo -e "${GREEN}Dashboard: http://localhost:6333/dashboard${NC}"
        if command -v open &> /dev/null; then
            open "http://localhost:6333/dashboard"
        elif command -v xdg-open &> /dev/null; then
            xdg-open "http://localhost:6333/dashboard"
        fi
        ;;

    jupyter)
        echo -e "${GREEN}Opening JupyterLab in browser...${NC}"
        echo -e "${GREEN}JupyterLab: http://localhost:8888${NC}"
        if command -v open &> /dev/null; then
            open "http://localhost:8888"
        elif command -v xdg-open &> /dev/null; then
            xdg-open "http://localhost:8888"
        fi
        ;;

    jupyter-logs)
        echo -e "${GREEN}Viewing JupyterLab logs...${NC}"
        docker-compose $COMPOSE_FILES logs -f jupyter
        ;;

    clean)
        echo -e "${RED}Removing all containers, volumes, and images...${NC}"
        read -p "Are you sure? This will delete all data. (y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            docker-compose $COMPOSE_FILES down -v --rmi all
            echo -e "${GREEN}Cleanup complete.${NC}"
        fi
        ;;

    status)
        echo -e "${GREEN}Container status:${NC}"
        docker-compose $COMPOSE_FILES ps
        ;;

    *)
        echo -e "${GREEN}Development Environment Helper${NC}"
        echo ""
        echo "Usage: ./dev.sh [command]"
        echo ""
        echo "Commands:"
        echo "  up           - Start services (foreground)"
        echo "  upd          - Start services (detached/background)"
        echo "  build        - Build images"
        echo "  rebuild      - Rebuild and start services"
        echo "  rebuild-deps - Rebuild images from scratch (use after adding dependencies)"
        echo "  down         - Stop services"
        echo "  restart      - Restart services"
        echo "  logs [svc]   - View logs (optionally for specific service)"
        echo "  shell        - Open bash shell in agent container"
        echo "  python       - Open Python REPL in agent container"
        echo "  run [module] - Run Python module (e.g., ./dev.sh run src.ingestion.index_dekkingen)"
        echo "  test [args]  - Run pytest in agent container"
        echo "  format       - Format code with black and ruff"
        echo "  qdrant-ui    - Open Qdrant dashboard in browser"
        echo "  jupyter      - Open JupyterLab in browser"
        echo "  jupyter-logs - View JupyterLab logs"
        echo "  status       - Show container status"
        echo "  clean        - Remove all containers, volumes, and images"
        echo ""
        echo "Examples:"
        echo "  ./dev.sh up            # Start in foreground"
        echo "  ./dev.sh logs agent    # View agent logs"
        echo "  ./dev.sh test -v       # Run tests with verbose output"
        echo "  ./dev.sh jupyter       # Open JupyterLab"
        ;;
esac
