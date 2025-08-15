#!/bin/bash

# MantraPath Development Environment - Status Script
# Quick status check for all services

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

echo -e "${BLUE}📊 MantraPath Development Environment Status${NC}"
echo -e "${CYAN}$(date)${NC}"
echo ""

# Function to check if port is in use
port_in_use() {
    lsof -i ":$1" >/dev/null 2>&1
}

# Function to check HTTP endpoint
check_endpoint() {
    local url=$1
    local timeout=3
    
    if curl -s --max-time $timeout "$url" >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Function to get process info for port
get_port_process() {
    local port=$1
    local pid=$(lsof -ti ":$port" 2>/dev/null | head -1)
    
    if [ -n "$pid" ]; then
        local cmd=$(ps -p "$pid" -o command= 2>/dev/null | cut -c1-50)
        echo "PID: $pid - $cmd"
    else
        echo "Not running"
    fi
}

# Check Docker services
echo -e "${CYAN}=== Infrastructure Services ===${NC}"

if port_in_use 5432; then
    echo -e "${GREEN}✅ PostgreSQL${NC}     - localhost:5432 ($(get_port_process 5432))"
else
    echo -e "${RED}❌ PostgreSQL${NC}     - localhost:5432 (not running)"
fi

if port_in_use 6379; then
    echo -e "${GREEN}✅ Redis${NC}          - localhost:6379 ($(get_port_process 6379))"
else
    echo -e "${RED}❌ Redis${NC}          - localhost:6379 (not running)"
fi

echo ""

# Check Backend Services
echo -e "${CYAN}=== Backend Services ===${NC}"

# Backend service ports and names
check_backend_service() {
    local port=$1
    local service=$2
    
    if port_in_use $port; then
        # Check if service responds to health check
        health_status=""
        if check_endpoint "http://localhost:$port/health"; then
            health_status=" ${GREEN}(healthy)${NC}"
        elif check_endpoint "http://localhost:$port/"; then
            health_status=" ${YELLOW}(responding)${NC}"
        else
            health_status=" ${RED}(not responding)${NC}"
        fi
        
        echo -e "${GREEN}✅ $service${NC} - localhost:$port$health_status"
    else
        echo -e "${RED}❌ $service${NC} - localhost:$port (not running)"
    fi
}

# Check all backend services
check_backend_service 8000 "API Gateway"
check_backend_service 8001 "Auth Service"
check_backend_service 8002 "Profile Service"
check_backend_service 8003 "Mood Service"
check_backend_service 8004 "Community Service"
check_backend_service 8005 "Content Service"
check_backend_service 8006 "Media Service"
check_backend_service 8007 "Notification Service"
check_backend_service 8008 "Chatbot Service"
check_backend_service 8009 "ML Service"

echo ""

# Check Frontend Services
echo -e "${CYAN}=== Frontend Services ===${NC}"

# Fix hardcoded references - use environment variables when available
if port_in_use ${FRONTEND_PORT:-3000}; then
    echo "✅ Frontend detected"
    if check_endpoint "${PROTOCOL:-http}://${DOMAIN:-localhost}:${FRONTEND_PORT:-3000}"; then
        health_status=" ${GREEN}(responding)${NC}"
    else
        health_status=" ${RED}(not responding)${NC}"
    fi
    echo -e "${GREEN}✅ Frontend${NC}       - ${DOMAIN:-localhost}:${FRONTEND_PORT:-3000}$health_status"
elif port_in_use 5173; then
    health_status=""
    if check_endpoint "http://localhost:5173"; then
        health_status=" ${GREEN}(responding)${NC}"
    else
        health_status=" ${RED}(not responding)${NC}"
    fi
    echo -e "${GREEN}✅ Frontend (Vite)${NC} - localhost:5173$health_status"
else
    echo -e "${RED}❌ Frontend${NC}       - localhost:3000/5173 (not running)"
fi

echo ""

# Check environment files
echo -e "${CYAN}=== Configuration ===${NC}"

if [ -f "$BACKEND_DIR/.env" ]; then
    echo -e "${GREEN}✅ Backend .env${NC}   - $BACKEND_DIR/.env"
else
    echo -e "${RED}❌ Backend .env${NC}   - $BACKEND_DIR/.env (missing)"
fi

if [ -f "$FRONTEND_DIR/.env" ]; then
    echo -e "${GREEN}✅ Frontend .env${NC}  - $FRONTEND_DIR/.env"
else
    echo -e "${RED}❌ Frontend .env${NC}  - $FRONTEND_DIR/.env (missing)"
fi

# Check dependencies
echo ""
echo -e "${CYAN}=== Dependencies ===${NC}"

if [ -d "$BACKEND_DIR/venv311" ] || [ -d "$BACKEND_DIR/venv" ]; then
    echo -e "${GREEN}✅ Python venv${NC}    - Backend virtual environment exists"
else
    echo -e "${RED}❌ Python venv${NC}    - Backend virtual environment missing"
fi

if [ -d "$FRONTEND_DIR/node_modules" ]; then
    echo -e "${GREEN}✅ Node modules${NC}   - Frontend dependencies installed"
else
    echo -e "${RED}❌ Node modules${NC}   - Frontend dependencies missing"
fi

# Docker status
echo ""
echo -e "${CYAN}=== Docker Status ===${NC}"

if command -v docker >/dev/null 2>&1; then
    if docker info >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Docker${NC}         - Running"
        
        # Check docker-compose
        if [ -f "$BACKEND_DIR/docker-compose.yml" ]; then
            cd "$BACKEND_DIR"
            if command -v docker-compose >/dev/null 2>&1; then
                DOCKER_COMPOSE_CMD="docker-compose"
            elif docker compose version >/dev/null 2>&1; then
                DOCKER_COMPOSE_CMD="docker compose"
            fi
            
            if [ -n "$DOCKER_COMPOSE_CMD" ]; then
                running_containers=$($DOCKER_COMPOSE_CMD ps --services --filter "status=running" 2>/dev/null | wc -l | tr -d ' ')
                total_containers=$($DOCKER_COMPOSE_CMD ps --services 2>/dev/null | wc -l | tr -d ' ')
                echo -e "${BLUE}📊 Containers${NC}     - $running_containers/$total_containers running"
            fi
        fi
    else
        echo -e "${RED}❌ Docker${NC}         - Not running"
    fi
else
    echo -e "${RED}❌ Docker${NC}         - Not installed"
fi

# Summary
echo ""
echo -e "${CYAN}=== Quick Summary ===${NC}"

# Count running services
running_backend=0
total_backend=10

# Count backend services manually
if port_in_use 8000; then running_backend=$((running_backend + 1)); fi
if port_in_use 8001; then running_backend=$((running_backend + 1)); fi
if port_in_use 8002; then running_backend=$((running_backend + 1)); fi
if port_in_use 8003; then running_backend=$((running_backend + 1)); fi
if port_in_use 8004; then running_backend=$((running_backend + 1)); fi
if port_in_use 8005; then running_backend=$((running_backend + 1)); fi
if port_in_use 8006; then running_backend=$((running_backend + 1)); fi
if port_in_use 8007; then running_backend=$((running_backend + 1)); fi
if port_in_use 8008; then running_backend=$((running_backend + 1)); fi
if port_in_use 8009; then running_backend=$((running_backend + 1)); fi

running_infrastructure=0
total_infrastructure=2

if port_in_use 5432; then
    running_infrastructure=$((running_infrastructure + 1))
fi

if port_in_use 6379; then
    running_infrastructure=$((running_infrastructure + 1))
fi

running_frontend=0
total_frontend=1

if port_in_use 3000 || port_in_use 5173; then
    running_frontend=1
fi

echo -e "${BLUE}🏗️  Infrastructure:${NC} $running_infrastructure/$total_infrastructure services"
echo -e "${BLUE}🔧 Backend:${NC}        $running_backend/$total_backend services"
echo -e "${BLUE}🎨 Frontend:${NC}       $running_frontend/$total_frontend services"

total_running=$((running_infrastructure + running_backend + running_frontend))
total_services=$((total_infrastructure + total_backend + total_frontend))

if [ $total_running -eq $total_services ]; then
    echo -e "${GREEN}🎉 All systems operational!${NC}"
elif [ $total_running -gt 0 ]; then
    echo -e "${YELLOW}⚠️  Partial system running${NC}"
else
    echo -e "${RED}🛑 No services running${NC}"
fi

echo ""
echo -e "${CYAN}=== Quick Links ===${NC}"
if port_in_use 3000; then
    echo -e "${BLUE}🌐 Application:${NC}    http://localhost:3000"
elif port_in_use 5173; then
    echo -e "${BLUE}🌐 Application:${NC}    http://localhost:5173"
fi

if port_in_use 8003; then
    echo -e "${BLUE}📊 API Docs:${NC}       http://localhost:8003/docs"
    echo -e "${BLUE}🔍 API Health:${NC}     http://localhost:8003/health"
fi

echo ""
echo -e "${CYAN}=== Available Commands ===${NC}"
echo -e "${YELLOW}Start:${NC}             ./scripts/start.sh"
echo -e "${YELLOW}Stop:${NC}              ./scripts/stop.sh"
echo -e "${YELLOW}Restart:${NC}           ./scripts/restart.sh"
echo -e "${YELLOW}Logs:${NC}              ./scripts/logs.sh"
echo -e "${YELLOW}Setup Environment:${NC} ./scripts/setup-env.sh"
echo ""
