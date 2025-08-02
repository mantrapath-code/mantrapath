#!/bin/bash

# MantraPath Project Startup Script
# Quick and easy way to start the entire MantraPath project

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}🌟 MantraPath Project Startup${NC}"
echo "============================="
echo ""

# Function to check if Docker is available and running
check_docker() {
    if ! command -v docker >/dev/null 2>&1; then
        return 1
    fi
    
    if ! docker info >/dev/null 2>&1; then
        return 1
    fi
    
    return 0
}

# Function to start backend with Docker Compose
start_backend_docker() {
    echo -e "${BLUE}🐳 Starting backend with Docker Compose...${NC}"
    
    cd "$PROJECT_ROOT/backend"
    
    # Stop any existing containers
    echo "� Stopping existing containers..."
    docker-compose down >/dev/null 2>&1 || true
    
    # Build and start services
    echo "🔨 Building and starting services..."
    docker-compose up --build -d
    
    # Wait for services to initialize
    echo "⏳ Waiting for services to initialize..."
    sleep 15
    
    # Check if backend is running
    local retries=0
    local max_retries=10
    
    while [ $retries -lt $max_retries ]; do
        if curl -s http://localhost:8000/health >/dev/null 2>&1; then
            echo -e "${GREEN}✅ Backend is running at http://localhost:8000${NC}"
            return 0
        fi
        
        echo "⏳ Backend still starting... (attempt $((retries + 1))/$max_retries)"
        sleep 3
        retries=$((retries + 1))
    done
    
    echo -e "${YELLOW}⚠️  Backend may still be starting up...${NC}"
    return 1
}

# Function to start backend with Python (fallback)
start_backend_python() {
    echo -e "${BLUE}🐍 Starting backend with Python (fallback mode)...${NC}"
    "$PROJECT_ROOT/scripts/start-backend-integrated.sh" --python &
    BACKEND_PID=$!
    
    # Wait for backend to be ready
    echo "⏳ Waiting for backend to start..."
    sleep 10
    
    # Check if backend is running
    if curl -s http://localhost:8000/health >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Backend is running at http://localhost:8000${NC}"
    else
        echo -e "${YELLOW}⚠️  Backend may still be starting up...${NC}"
    fi
}

# Function to start backend (auto-detect best method)
start_backend() {
    local force_mode="$1"
    
    if [ "$force_mode" = "--docker" ]; then
        if check_docker; then
            start_backend_docker
        else
            echo -e "${YELLOW}⚠️  Docker not available, falling back to Python mode${NC}"
            start_backend_python
        fi
    elif [ "$force_mode" = "--python" ]; then
        start_backend_python
    else
        # Auto-detect: prefer Docker, fallback to Python
        if check_docker; then
            echo -e "${BLUE}🐳 Docker detected, using Docker Compose...${NC}"
            start_backend_docker
        else
            echo -e "${YELLOW}⚠️  Docker not available, using Python mode...${NC}"
            start_backend_python
        fi
    fi
}

# Function to start frontend
start_frontend() {
    echo -e "${BLUE}🎨 Starting frontend...${NC}"
    cd "$PROJECT_ROOT/frontend"
    
    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        echo "📦 Installing frontend dependencies..."
        npm install
    fi
    
    echo "🚀 Starting frontend development server..."
    npm run dev &
    FRONTEND_PID=$!
    
    echo -e "${GREEN}✅ Frontend starting at http://localhost:5173${NC}"
}

# Parse command line arguments
START_BACKEND=true
START_FRONTEND=true
BACKEND_MODE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --backend-only|-b)
            START_FRONTEND=false
            shift
            ;;
        --frontend-only|-f)
            START_BACKEND=false
            shift
            ;;
        --docker|-d)
            BACKEND_MODE="--docker"
            shift
            ;;
        --python|-p)
            BACKEND_MODE="--python"
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "MantraPath Project Startup - Docker First Approach"
            echo ""
            echo "Options:"
            echo "  --backend-only, -b   Start only backend services"
            echo "  --frontend-only, -f  Start only frontend"
            echo "  --docker, -d         Force Docker Compose mode for backend"
            echo "  --python, -p         Force Python development mode for backend"
            echo "  --help, -h           Show this help message"
            echo ""
            echo "Default Behavior:"
            echo "  - Uses Docker Compose if Docker is available and running"
            echo "  - Falls back to Python mode if Docker is not available"
            echo "  - Starts both backend and frontend by default"
            echo ""
            echo "Examples:"
            echo "  $0                   # Auto-detect best backend mode, start both"
            echo "  $0 --backend-only    # Start only backend (auto-detect mode)"
            echo "  $0 --docker          # Force Docker backend + frontend"
            echo "  $0 --python          # Force Python backend + frontend"
            echo "  $0 --frontend-only   # Start only frontend (for external backend)"
            echo ""
            echo "Docker Requirements:"
            echo "  - Docker Desktop must be installed and running"
            echo "  - Services will be available on localhost:8000"
            echo ""
            echo "Python Fallback:"
            echo "  - Uses virtual environment in ./venv"
            echo "  - Runs services directly with uvicorn"
            echo "  - Good for development and debugging"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Start services
if [ "$START_BACKEND" = true ]; then
    start_backend $BACKEND_MODE
fi

if [ "$START_FRONTEND" = true ]; then
    start_frontend
fi

# Show status and wait
echo ""
echo -e "${GREEN}🎉 MantraPath is starting up!${NC}"
echo ""
echo "📍 Available Services:"

if [ "$START_BACKEND" = true ]; then
    echo "   🔧 Backend API: http://localhost:8000"
    echo "   🔍 Health Check: curl http://localhost:8000/health"
    if check_docker && [ "$BACKEND_MODE" != "--python" ]; then
        echo "   🐳 Running with Docker Compose"
        echo "   📊 Container Status: docker-compose ps (from backend/)"
    else
        echo "   🐍 Running with Python (development mode)"
    fi
fi

if [ "$START_FRONTEND" = true ]; then
    echo "   🎨 Frontend: http://localhost:5173"
fi

echo ""
echo "📝 Useful Commands:"
echo "   🛑 Stop all: Press Ctrl+C"
echo "   🔧 Backend only: $0 --backend-only"
echo "   🎨 Frontend only: $0 --frontend-only"
if check_docker; then
    echo "   🐳 Force Docker: $0 --docker"
    echo "   🐍 Force Python: $0 --python"
    echo "   📊 Check containers: cd backend && docker-compose ps"
    echo "   📋 View logs: cd backend && docker-compose logs -f"
fi
echo ""

if [ "$START_BACKEND" = true ] && [ "$START_FRONTEND" = true ]; then
    echo "Press Ctrl+C to stop all services..."
    
    cleanup() {
        echo ""
        echo "🛑 Stopping all services..."
        
        # Stop Docker containers if they're running
        if check_docker; then
            echo "🐳 Stopping Docker containers..."
            cd "$PROJECT_ROOT/backend"
            docker-compose down >/dev/null 2>&1 || true
        fi
        
        # Stop Python backend processes
        if [ ! -z "$BACKEND_PID" ]; then
            kill $BACKEND_PID 2>/dev/null || true
        fi
        
        # Stop frontend process
        if [ ! -z "$FRONTEND_PID" ]; then
            kill $FRONTEND_PID 2>/dev/null || true
        fi
        
        # Kill any remaining processes
        pkill -f "uvicorn.*main:app" 2>/dev/null || true
        pkill -f "npm run dev" 2>/dev/null || true
        
        echo "✅ All services stopped"
        exit 0
    }
    
    trap cleanup INT TERM
    wait
fi
