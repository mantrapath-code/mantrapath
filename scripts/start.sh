#!/bin/bash

# MantraPath Development Environment - Main Start Script
# Starts all services with proper dependency management

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

# Service status tracking
FRONTEND_PID=""

echo -e "${BLUE}🚀 MantraPath Development Environment${NC}"
echo -e "${CYAN}Starting all services with dependency management...${NC}"
echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if port is in use
port_in_use() {
    lsof -i ":$1" >/dev/null 2>&1
}

# Function to check if port is in use
port_in_use() {
    lsof -i ":$1" >/dev/null 2>&1
}

# Function to wait for port to be available
wait_for_port() {
    local port=$1
    local service=$2
    local max_attempts=30
    local attempt=0
    
    echo -e "${YELLOW}⏳ Waiting for $service on port $port...${NC}"
    
    while [ $attempt -lt $max_attempts ]; do
        if port_in_use $port; then
            echo -e "${GREEN}✅ $service is ready on port $port${NC}"
            return 0
        fi
        sleep 2
        attempt=$((attempt + 1))
        echo -n "."
    done
    
    echo -e "${RED}❌ $service failed to start on port $port${NC}"
    return 1
}

# Function to check service health
check_service_health() {
    local url=$1
    local service=$2
    local max_attempts=15
    local attempt=0
    
    echo -e "${YELLOW}🔍 Checking $service health at $url...${NC}"
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -s "$url" >/dev/null 2>&1; then
            echo -e "${GREEN}✅ $service is healthy${NC}"
            return 0
        fi
        sleep 2
        attempt=$((attempt + 1))
        echo -n "."
    done
    
    echo -e "${YELLOW}⚠️  $service health check timeout (service may still be starting)${NC}"
    return 1
}

# Function to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}🧹 Cleaning up services...${NC}"
    
        # Kill background processes
    if [ -n "$FRONTEND_PID" ] && kill -0 "$FRONTEND_PID" 2>/dev/null; then
        kill "$FRONTEND_PID" 2>/dev/null || true
    fi
    
    # Stop Docker services if running
    if [ -f "$BACKEND_DIR/docker-compose.yml" ]; then
        echo -e "${BLUE}🐳 Stopping Docker services...${NC}"
        cd "$BACKEND_DIR"
        docker-compose down 2>/dev/null || true
    fi
    
    echo -e "${GREEN}✅ Cleanup completed${NC}"
    exit 0
}

# Set up cleanup trap
trap cleanup EXIT INT TERM

# Check prerequisites
echo -e "${BLUE}🔍 Checking prerequisites...${NC}"

if ! command_exists node; then
    echo -e "${RED}❌ Node.js is not installed${NC}"
    echo -e "${YELLOW}Please install Node.js from https://nodejs.org/${NC}"
    exit 1
fi

if ! command_exists python3; then
    echo -e "${RED}❌ Python 3 is not installed${NC}"
    echo -e "${YELLOW}Please install Python 3${NC}"
    exit 1
fi

if ! command_exists docker; then
    echo -e "${RED}❌ Docker is not installed${NC}"
    echo -e "${YELLOW}Please install Docker from https://docker.com/${NC}"
    exit 1
fi

if ! command_exists docker-compose; then
    if ! docker compose version >/dev/null 2>&1; then
        echo -e "${RED}❌ Docker Compose is not available${NC}"
        echo -e "${YELLOW}Please install Docker Compose${NC}"
        exit 1
    else
        # Use 'docker compose' instead of 'docker-compose'
        DOCKER_COMPOSE_CMD="docker compose"
    fi
else
    DOCKER_COMPOSE_CMD="docker-compose"
fi

echo -e "${GREEN}✅ All prerequisites met${NC}"

# Check environment files
echo -e "${BLUE}🔧 Checking environment configuration...${NC}"

if [ ! -f "$BACKEND_DIR/.env" ] || [ ! -f "$FRONTEND_DIR/.env" ]; then
    echo -e "${YELLOW}⚠️  Environment files missing${NC}"
    echo -e "${BLUE}Running environment setup...${NC}"
    chmod +x "$SCRIPT_DIR/dev/setup-env.sh"
    "$SCRIPT_DIR/dev/setup-env.sh"
fi

echo -e "${GREEN}✅ Environment configuration ready${NC}"

# Start infrastructure services (Database & Redis)
echo -e "${PURPLE}🐳 Starting infrastructure services...${NC}"
cd "$BACKEND_DIR"

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running${NC}"
    echo -e "${YELLOW}Please start Docker and try again${NC}"
    exit 1
fi

# Start only database and redis first
$DOCKER_COMPOSE_CMD up -d postgres redis

# Wait for database and redis
wait_for_port 5432 "PostgreSQL"
wait_for_port 6379 "Redis"

# Initialize database if needed
echo -e "${BLUE}🗄️  Initializing database...${NC}"
sleep 3

# Start all backend services with Docker Compose
echo -e "${PURPLE}🔧 Starting all backend services...${NC}"
$DOCKER_COMPOSE_CMD up -d

# Wait for main services to be ready
wait_for_port 8000 "API Gateway"
wait_for_port 8001 "Auth Service" 
wait_for_port 8003 "Mood Service"

# Check health of main services
check_service_health "http://localhost:8000/health" "API Gateway"
check_service_health "http://localhost:8003/health" "Mood Service"

# Start frontend
echo -e "${PURPLE}🎨 Starting frontend...${NC}"
cd "$FRONTEND_DIR"

# Install frontend dependencies if needed
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}📦 Installing frontend dependencies...${NC}"
    npm install
fi

# Start frontend development server
echo -e "${BLUE}🌐 Starting frontend development server...${NC}"
npm run dev &
FRONTEND_PID=$!

# Wait for frontend (Vite usually starts on 5173, but could be 3000)
if wait_for_port 5173 "Frontend (port 5173)"; then
    echo -e "${GREEN}✅ Frontend started on port 5173${NC}"
elif wait_for_port 3000 "Frontend (port 3000)"; then
    echo -e "${GREEN}✅ Frontend started on port 3000${NC}"
else
    echo -e "${YELLOW}⚠️  Frontend may be starting, check manually${NC}"
fi

# Display status
echo ""
echo -e "${GREEN}🎉 All services started successfully!${NC}"
echo ""
echo -e "${CYAN}=== Service Status ===${NC}"
echo -e "${GREEN}✅ PostgreSQL${NC}     - localhost:5432"
echo -e "${GREEN}✅ Redis${NC}          - localhost:6379"
echo -e "${GREEN}✅ API Gateway${NC}    - http://localhost:8000"
echo -e "${GREEN}✅ Auth Service${NC}   - http://localhost:8001"
echo -e "${GREEN}✅ Mood Service${NC}   - http://localhost:8003"
if port_in_use 5173; then
    echo -e "${GREEN}✅ Frontend${NC}       - http://localhost:5173"
elif port_in_use 3000; then
    echo -e "${GREEN}✅ Frontend${NC}       - http://localhost:3000"
fi
echo ""
echo -e "${CYAN}=== Quick Links ===${NC}"
if port_in_use 5173; then
    echo -e "${BLUE}🌐 Application:${NC}    http://localhost:5173"
elif port_in_use 3000; then
    echo -e "${BLUE}🌐 Application:${NC}    http://localhost:3000"
fi
echo -e "${BLUE}📊 API Gateway:${NC}    http://localhost:8000/docs"
echo -e "${BLUE}🧠 Mood Service:${NC}   http://localhost:8003/docs"
echo -e "${BLUE}🔍 Health Check:${NC}    http://localhost:8000/health"
echo ""
echo -e "${CYAN}=== Useful Commands ===${NC}"
echo -e "${YELLOW}View Logs:${NC}        ./scripts/logs.sh"
echo -e "${YELLOW}Stop Services:${NC}    ./scripts/stop.sh or Ctrl+C"
echo -e "${YELLOW}Restart:${NC}          ./scripts/restart.sh"
echo ""
echo -e "${BLUE}💡 The application is now running in development mode${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"

# Keep script running and show live logs
echo -e "${CYAN}📋 Live service status (Press Ctrl+C to stop):${NC}"
echo ""

# Monitor services
while true; do
    sleep 5
    
    # Check if services are still running
    if [ -n "$MOOD_SERVICE_PID" ] && ! kill -0 "$MOOD_SERVICE_PID" 2>/dev/null; then
        echo -e "${RED}❌ Mood Service (PID: $MOOD_SERVICE_PID) has stopped${NC}"
        MOOD_SERVICE_PID=""
    fi
    
    if [ -n "$FRONTEND_PID" ] && ! kill -0 "$FRONTEND_PID" 2>/dev/null; then
        echo -e "${RED}❌ Frontend (PID: $FRONTEND_PID) has stopped${NC}"
        FRONTEND_PID=""
    fi
    
    # Show brief status every 30 seconds
    if [ $(($(date +%s) % 30)) -eq 0 ]; then
        running_count=0
        if [ -n "$MOOD_SERVICE_PID" ]; then running_count=$((running_count + 1)); fi
        if [ -n "$FRONTEND_PID" ]; then running_count=$((running_count + 1)); fi
        echo -e "${CYAN}⏰ $(date '+%H:%M:%S') - Services: $running_count running${NC}"
    fi
done
