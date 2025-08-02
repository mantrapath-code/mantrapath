#!/bin/bash

# MantraPath Development Environment - Logs Script
# View logs from all running services

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

echo -e "${BLUE}📋 MantraPath Development Logs${NC}"
echo ""

# Function to check if service is running on port
service_running() {
    lsof -i ":$1" >/dev/null 2>&1
}

# Function to show Docker logs
show_docker_logs() {
    if [ -f "$BACKEND_DIR/docker-compose.yml" ]; then
        echo -e "${CYAN}=== Docker Services Logs ===${NC}"
        cd "$BACKEND_DIR"
        
        # Check which compose command is available
        if command -v docker-compose >/dev/null 2>&1; then
            DOCKER_COMPOSE_CMD="docker-compose"
        elif docker compose version >/dev/null 2>&1; then
            DOCKER_COMPOSE_CMD="docker compose"
        else
            echo -e "${YELLOW}⚠️  Docker Compose not found${NC}"
            return
        fi
        
        # Show logs for running containers
        echo -e "${BLUE}📊 PostgreSQL logs:${NC}"
        $DOCKER_COMPOSE_CMD logs --tail=20 postgres 2>/dev/null || echo -e "${YELLOW}PostgreSQL not running${NC}"
        
        echo ""
        echo -e "${BLUE}📊 Redis logs:${NC}"
        $DOCKER_COMPOSE_CMD logs --tail=20 redis 2>/dev/null || echo -e "${YELLOW}Redis not running${NC}"
        
        echo ""
    fi
}

# Function to show service status
show_service_status() {
    echo -e "${CYAN}=== Service Status ===${NC}"
    
    # Check each service port
    declare -A SERVICES=(
        [3000]="Frontend"
        [5173]="Frontend (Vite)"
        [8000]="API Gateway"
        [8001]="Auth Service"
        [8002]="Profile Service"
        [8003]="Mood Service"
        [8004]="Community Service"
        [8005]="Content Service"
        [8006]="Media Service"
        [8007]="Notification Service"
        [8008]="Chatbot Service"
        [8009]="ML Service"
        [5432]="PostgreSQL"
        [6379]="Redis"
    )
    
    for port in "${!SERVICES[@]}"; do
        service="${SERVICES[$port]}"
        if service_running $port; then
            echo -e "${GREEN}✅ $service${NC} - localhost:$port"
        else
            echo -e "${RED}❌ $service${NC} - localhost:$port (not running)"
        fi
    done
    echo ""
}

# Function to tail logs from specific service
tail_service_logs() {
    local service=$1
    case $service in
        "frontend"|"fe")
            if service_running 3000 || service_running 5173; then
                echo -e "${BLUE}📊 Following Frontend logs (Ctrl+C to stop):${NC}"
                # Frontend logs are typically in terminal where npm run dev is running
                # We'll show recent system logs for Node.js processes
                tail -f /dev/null  # Placeholder - in real scenario you'd tail actual log files
            else
                echo -e "${RED}❌ Frontend is not running${NC}"
            fi
            ;;
        "backend"|"be"|"mood")
            if service_running 8003; then
                echo -e "${BLUE}📊 Following Mood Service logs (Ctrl+C to stop):${NC}"
                # In a real scenario, you'd tail the actual log file
                # For now, we'll monitor the process
                echo -e "${YELLOW}Mood Service is running on port 8003${NC}"
                echo -e "${CYAN}API Health: http://localhost:8003/health${NC}"
                echo -e "${CYAN}API Docs: http://localhost:8003/docs${NC}"
            else
                echo -e "${RED}❌ Mood Service is not running${NC}"
            fi
            ;;
        "docker"|"db"|"redis")
            show_docker_logs
            ;;
        *)
            echo -e "${RED}❌ Unknown service: $service${NC}"
            echo -e "${YELLOW}Available services: frontend, backend, docker${NC}"
            ;;
    esac
}

# Function to show live monitoring
live_monitoring() {
    echo -e "${BLUE}📊 Live Service Monitoring (Press Ctrl+C to stop)${NC}"
    echo -e "${CYAN}Refreshing every 5 seconds...${NC}"
    echo ""
    
    while true; do
        clear
        echo -e "${BLUE}📋 MantraPath Development Logs - Live Monitoring${NC}"
        echo -e "${CYAN}$(date)${NC}"
        echo ""
        
        show_service_status
        
        # Show recent Docker logs if available
        if [ -f "$BACKEND_DIR/docker-compose.yml" ]; then
            cd "$BACKEND_DIR"
            if command -v docker-compose >/dev/null 2>&1; then
                DOCKER_COMPOSE_CMD="docker-compose"
            elif docker compose version >/dev/null 2>&1; then
                DOCKER_COMPOSE_CMD="docker compose"
            fi
            
            if [ -n "$DOCKER_COMPOSE_CMD" ]; then
                echo -e "${CYAN}=== Recent Docker Activity ===${NC}"
                $DOCKER_COMPOSE_CMD logs --tail=5 --no-log-prefix 2>/dev/null | head -20 || echo -e "${YELLOW}No recent Docker activity${NC}"
                echo ""
            fi
        fi
        
        echo -e "${CYAN}Next refresh in 5 seconds... (Ctrl+C to stop)${NC}"
        sleep 5
    done
}

# Function to show help
show_help() {
    echo -e "${CYAN}=== MantraPath Logs Help ===${NC}"
    echo ""
    echo -e "${YELLOW}Usage:${NC}"
    echo -e "  ./scripts/logs.sh [command] [service]"
    echo ""
    echo -e "${YELLOW}Commands:${NC}"
    echo -e "  ${GREEN}status${NC}     - Show current service status"
    echo -e "  ${GREEN}docker${NC}     - Show Docker container logs"
    echo -e "  ${GREEN}tail${NC}       - Follow logs for specific service"
    echo -e "  ${GREEN}live${NC}       - Live monitoring of all services"
    echo -e "  ${GREEN}help${NC}       - Show this help message"
    echo ""
    echo -e "${YELLOW}Services (for tail command):${NC}"
    echo -e "  ${GREEN}frontend${NC}   - Frontend development server"
    echo -e "  ${GREEN}backend${NC}    - Backend services (mood service)"
    echo -e "  ${GREEN}docker${NC}     - Docker services (postgres, redis)"
    echo ""
    echo -e "${YELLOW}Examples:${NC}"
    echo -e "  ./scripts/logs.sh status"
    echo -e "  ./scripts/logs.sh docker"
    echo -e "  ./scripts/logs.sh tail frontend"
    echo -e "  ./scripts/logs.sh live"
    echo ""
}

# Parse command line arguments
case "${1:-status}" in
    "status"|"st")
        show_service_status
        ;;
    "docker"|"db")
        show_docker_logs
        ;;
    "tail"|"follow"|"f")
        if [ -z "$2" ]; then
            echo -e "${RED}❌ Please specify a service to tail${NC}"
            echo -e "${YELLOW}Available services: frontend, backend, docker${NC}"
            exit 1
        fi
        tail_service_logs "$2"
        ;;
    "live"|"monitor"|"watch")
        live_monitoring
        ;;
    "help"|"--help"|"-h")
        show_help
        ;;
    *)
        echo -e "${RED}❌ Unknown command: $1${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac
