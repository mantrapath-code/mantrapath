#!/bin/bash

# MantraPath Development Environment - Stop Script
# Gracefully stops all running services

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

echo -e "${RED}🛑 MantraPath Development Environment - Stop${NC}"
echo -e "${CYAN}Gracefully stopping all services...${NC}"
echo ""

# Function to check if port is in use and get PID
get_port_pid() {
    lsof -ti ":$1" 2>/dev/null || echo ""
}

# Function to kill process by port
kill_by_port() {
    local port=$1
    local service_name=$2
    local pid=$(get_port_pid $port)
    
    if [ -n "$pid" ]; then
        echo -e "${YELLOW}🔄 Stopping $service_name (PID: $pid) on port $port...${NC}"
        kill -TERM "$pid" 2>/dev/null || true
        
        # Wait up to 10 seconds for graceful shutdown
        for i in {1..10}; do
            if ! kill -0 "$pid" 2>/dev/null; then
                echo -e "${GREEN}✅ $service_name stopped gracefully${NC}"
                return 0
            fi
            sleep 1
        done
        
        # Force kill if still running
        echo -e "${YELLOW}⚠️  Force stopping $service_name...${NC}"
        kill -KILL "$pid" 2>/dev/null || true
        echo -e "${GREEN}✅ $service_name force stopped${NC}"
    else
        echo -e "${BLUE}ℹ️  $service_name not running on port $port${NC}"
    fi
}

# Function to stop Docker services
stop_docker_services() {
    if [ -f "$BACKEND_DIR/docker-compose.yml" ]; then
        echo -e "${BLUE}🐳 Stopping Docker services...${NC}"
        cd "$BACKEND_DIR"
        
        # Check which compose command is available
        if command -v docker-compose >/dev/null 2>&1; then
            DOCKER_COMPOSE_CMD="docker-compose"
        elif docker compose version >/dev/null 2>&1; then
            DOCKER_COMPOSE_CMD="docker compose"
        else
            echo -e "${YELLOW}⚠️  Docker Compose not found, skipping Docker services${NC}"
            return
        fi
        
        # Stop all services
        $DOCKER_COMPOSE_CMD down 2>/dev/null || true
        echo -e "${GREEN}✅ Docker services stopped${NC}"
    else
        echo -e "${BLUE}ℹ️  No docker-compose.yml found, skipping Docker services${NC}"
    fi
}

# Function to cleanup Python processes
cleanup_python_processes() {
    echo -e "${YELLOW}🐍 Cleaning up Python backend processes...${NC}"
    
    # Find and kill Python processes running MantraPath services
    local python_pids=$(pgrep -f "python.*main.py" 2>/dev/null || echo "")
    
    if [ -n "$python_pids" ]; then
        for pid in $python_pids; do
            local cmd=$(ps -p "$pid" -o command= 2>/dev/null || echo "")
            if [[ "$cmd" == *"mood_service"* ]] || [[ "$cmd" == *"mantrapath"* ]]; then
                echo -e "${YELLOW}🔄 Stopping Python service (PID: $pid)...${NC}"
                kill -TERM "$pid" 2>/dev/null || true
                sleep 2
                if kill -0 "$pid" 2>/dev/null; then
                    kill -KILL "$pid" 2>/dev/null || true
                fi
                echo -e "${GREEN}✅ Python service stopped${NC}"
            fi
        done
    else
        echo -e "${BLUE}ℹ️  No Python backend processes found${NC}"
    fi
}

# Function to cleanup Node.js processes
cleanup_node_processes() {
    echo -e "${YELLOW}🟢 Cleaning up Node.js frontend processes...${NC}"
    
    # Find and kill Node.js processes running on our ports
    local node_pids=$(pgrep -f "node.*vite\|npm.*dev\|yarn.*dev" 2>/dev/null || echo "")
    
    if [ -n "$node_pids" ]; then
        for pid in $node_pids; do
            echo -e "${YELLOW}🔄 Stopping Node.js service (PID: $pid)...${NC}"
            kill -TERM "$pid" 2>/dev/null || true
            sleep 2
            if kill -0 "$pid" 2>/dev/null; then
                kill -KILL "$pid" 2>/dev/null || true
            fi
            echo -e "${GREEN}✅ Node.js service stopped${NC}"
        done
    else
        echo -e "${BLUE}ℹ️  No Node.js frontend processes found${NC}"
    fi
}

# Stop services by known ports
echo -e "${PURPLE}🔌 Stopping services by port...${NC}"

# Frontend (typically on port 3000 or 5173 for Vite)
kill_by_port 3000 "Frontend (port 3000)"
kill_by_port 5173 "Frontend (port 5173)"

# Backend services
kill_by_port 8000 "API Gateway"
kill_by_port 8001 "Auth Service"
kill_by_port 8002 "Profile Service"
kill_by_port 8003 "Mood Service"
kill_by_port 8004 "Community Service"
kill_by_port 8005 "Content Service"
kill_by_port 8006 "Media Service"
kill_by_port 8007 "Notification Service"
kill_by_port 8008 "Chatbot Service"
kill_by_port 8009 "ML Service"

# Stop process-based services
cleanup_python_processes
cleanup_node_processes

# Stop Docker services (Database, Redis, etc.)
stop_docker_services

# Additional cleanup for any remaining processes
echo -e "${PURPLE}🧹 Final cleanup...${NC}"

# Kill any remaining processes from our project
PROJECT_PROCESSES=$(pgrep -f "mantrapath\|mood.*service" 2>/dev/null || echo "")
if [ -n "$PROJECT_PROCESSES" ]; then
    echo -e "${YELLOW}🔄 Cleaning up remaining project processes...${NC}"
    for pid in $PROJECT_PROCESSES; do
        kill -TERM "$pid" 2>/dev/null || true
    done
    sleep 2
    for pid in $PROJECT_PROCESSES; do
        if kill -0 "$pid" 2>/dev/null; then
            kill -KILL "$pid" 2>/dev/null || true
        fi
    done
    echo -e "${GREEN}✅ Remaining processes cleaned up${NC}"
fi

# Check for any processes still using our ports
echo -e "${BLUE}🔍 Checking for remaining port usage...${NC}"
REMAINING_PORTS=""
for port in 3000 5173 8000 8001 8002 8003 8004 8005 8006 8007 8008 8009 5432 6379; do
    if lsof -i ":$port" >/dev/null 2>&1; then
        REMAINING_PORTS="$REMAINING_PORTS $port"
    fi
done

if [ -n "$REMAINING_PORTS" ]; then
    echo -e "${YELLOW}⚠️  Some ports still in use:$REMAINING_PORTS${NC}"
    echo -e "${CYAN}You may need to manually stop these processes${NC}"
else
    echo -e "${GREEN}✅ All MantraPath ports are now free${NC}"
fi

# Cleanup temporary files
echo -e "${BLUE}🗑️  Cleaning up temporary files...${NC}"
find "$PROJECT_ROOT" -name "*.pyc" -delete 2>/dev/null || true
find "$PROJECT_ROOT" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find "$PROJECT_ROOT" -name ".DS_Store" -delete 2>/dev/null || true

echo ""
echo -e "${GREEN}🎉 All MantraPath services stopped successfully!${NC}"
echo ""
echo -e "${CYAN}=== Summary ===${NC}"
echo -e "${GREEN}✅ Frontend stopped${NC}"
echo -e "${GREEN}✅ Backend services stopped${NC}"
echo -e "${GREEN}✅ Docker services stopped${NC}"
echo -e "${GREEN}✅ Temporary files cleaned${NC}"
echo ""
echo -e "${BLUE}💡 To start services again, run: ./scripts/start.sh${NC}"
echo ""
