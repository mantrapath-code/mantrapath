#!/bin/bash

# MantraPath Integrated Backend Startup
# This script sets up the virtual environment and starts the backend services

set -e  # Exit on any error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

echo "🚀 MantraPath Backend Integrated Startup"
echo "========================================"
echo "Project Root: $PROJECT_ROOT"
echo "Backend Dir: $BACKEND_DIR"
echo ""

# Step 1: Setup virtual environment
print_status "Setting up virtual environment..."
if [ ! -f "$SCRIPT_DIR/setup-venv.sh" ]; then
    print_error "setup-venv.sh not found in scripts directory"
    exit 1
fi

# Run the venv setup script
chmod +x "$SCRIPT_DIR/setup-venv.sh"
"$SCRIPT_DIR/setup-venv.sh"

# Step 2: Check if Docker should be used or Python directly
USE_DOCKER=false
FORCE_PYTHON=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --docker|-d)
            USE_DOCKER=true
            shift
            ;;
        --python|-p)
            FORCE_PYTHON=true
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --docker, -d    Use Docker for backend services"
            echo "  --python, -p    Force Python mode (no Docker)"
            echo "  --help, -h      Show this help message"
            echo ""
            exit 0
            ;;
        *)
            print_warning "Unknown option: $1"
            shift
            ;;
    esac
done

# Step 3: Determine startup method
if [ "$FORCE_PYTHON" = true ]; then
    USE_DOCKER=false
    print_status "Forced Python mode - will not use Docker"
elif [ "$USE_DOCKER" = true ]; then
    print_status "Docker mode requested"
    # Check if Docker is available
    if ! command -v docker >/dev/null 2>&1; then
        print_warning "Docker not found, falling back to Python mode"
        USE_DOCKER=false
    elif ! docker info >/dev/null 2>&1; then
        print_warning "Docker not running, falling back to Python mode"
        USE_DOCKER=false
    fi
else
    # Auto-detect: prefer Python if venv exists, Docker as fallback
    if [ -d "$PROJECT_ROOT/venv" ]; then
        print_status "Virtual environment found, using Python mode"
        USE_DOCKER=false
    elif command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1; then
        print_status "Docker available, using Docker mode"
        USE_DOCKER=true
    else
        print_error "Neither virtual environment nor Docker available"
        echo "Please run: $SCRIPT_DIR/setup-venv.sh"
        echo "Or install and start Docker"
        exit 1
    fi
fi

# Step 4: Start services based on chosen method
if [ "$USE_DOCKER" = true ]; then
    print_status "Starting services with Docker..."
    cd "$BACKEND_DIR"
    
    if [ ! -f "docker-compose.yml" ]; then
        print_error "docker-compose.yml not found in backend directory"
        exit 1
    fi
    
    # Stop any existing containers
    print_status "Stopping existing containers..."
    docker-compose down 2>/dev/null || true
    
    # Build and start services
    print_status "Building and starting Docker services..."
    docker-compose up --build -d
    
    # Wait for services to be ready
    print_status "Waiting for services to initialize..."
    sleep 10
    
    print_success "Docker services started!"
    echo ""
    echo "📍 Service Endpoints:"
    echo "   🌐 API Gateway: http://localhost:8000"
    echo "   🔐 Auth Service: http://localhost:8001"
    echo "   😊 Mood Service: http://localhost:8003"
    echo ""
    echo "🔍 Health Checks:"
    echo "   curl http://localhost:8000/health"
    echo ""
    echo "🛑 To stop: cd backend && docker-compose down"
    
else
    print_status "Starting services with Python..."
    
    # Activate virtual environment
    if [ ! -d "$PROJECT_ROOT/venv" ]; then
        print_error "Virtual environment not found. Running setup..."
        "$SCRIPT_DIR/setup-venv.sh"
    fi
    
    source "$PROJECT_ROOT/venv/bin/activate"
    
    # Set environment variables
    export PYTHONPATH="$BACKEND_DIR/shared:$PYTHONPATH"
    export DATABASE_URL="sqlite:///$BACKEND_DIR/mantrapath.db"
    export JWT_SECRET_KEY="dev-secret-key-change-in-production"
    
    # Create database directory
    mkdir -p "$BACKEND_DIR/database"
    
    print_success "Python environment activated"
    echo "  Python: $(which python)"
    echo "  PYTHONPATH: $PYTHONPATH"
    echo ""
    
    # Start services in background
    cd "$BACKEND_DIR"
    
    print_status "Starting Python services..."
    
    # Start API Gateway
    echo "🌐 Starting API Gateway on port 8000..."
    python -m services.api_gateway.main &
    GATEWAY_PID=$!
    sleep 2
    
    # Start Auth Service
    echo "🔐 Starting Auth Service on port 8001..."
    python -m services.auth_service.main &
    AUTH_PID=$!
    sleep 2
    
    # Start Mood Service
    echo "😊 Starting Mood Service on port 8003..."
    python -m services.mood_service.main &
    MOOD_PID=$!
    sleep 2
    
    print_success "Python services started!"
    echo ""
    echo "📍 Service Endpoints:"
    echo "   🌐 API Gateway: http://localhost:8000"
    echo "   🔐 Auth Service: http://localhost:8001" 
    echo "   😊 Mood Service: http://localhost:8003"
    echo ""
    echo "🔍 Health Check:"
    echo "   curl http://localhost:8000/health"
    echo ""
    echo "Press Ctrl+C to stop all services..."
    
    # Wait for interrupt and cleanup
    cleanup() {
        echo ""
        print_status "Stopping services..."
        kill $GATEWAY_PID $AUTH_PID $MOOD_PID 2>/dev/null || true
        print_success "Services stopped"
        exit 0
    }
    
    trap cleanup INT TERM
    wait
fi
