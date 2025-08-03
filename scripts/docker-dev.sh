#!/bin/bash
# Docker-based development script for MantraPath
# Use this instead of the old individual service scripts

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is running
check_docker() {
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker Desktop."
        exit 1
    fi
}

# Start all services
start_services() {
    print_status "Starting MantraPath services with Docker Compose..."
    cd "$BACKEND_DIR"
    
    # Build and start all services
    docker-compose up -d --build
    
    print_status "Waiting for services to be ready..."
    sleep 10
    
    # Check service health
    check_services
}

# Stop all services
stop_services() {
    print_status "Stopping MantraPath services..."
    cd "$BACKEND_DIR"
    docker-compose down
    print_status "Services stopped."
}

# Restart all services
restart_services() {
    print_status "Restarting MantraPath services..."
    stop_services
    sleep 2
    start_services
}

# Check service status
check_services() {
    print_status "Checking service status..."
    
    services=(
        "8000:API Gateway"
        "8001:Auth Service"
        "8002:Profile Service"
        "8003:Mood Service"
        "8004:Chatbot Service"
        "8005:Content Service"
        "8006:Community Service"
        "8007:Notification Service"
        "8008:ML Service"
        "8009:Media Service"
    )
    
    for service in "${services[@]}"; do
        port=$(echo $service | cut -d: -f1)
        name=$(echo $service | cut -d: -f2)
        
        if curl -s -f "http://localhost:$port/health" >/dev/null 2>&1; then
            print_status "$name (port $port): ✅ Running"
        else
            print_warning "$name (port $port): ❌ Not responding"
        fi
    done
    
    # Check database
    if docker-compose exec -T postgres pg_isready -U mantrapath >/dev/null 2>&1; then
        print_status "PostgreSQL Database: ✅ Running"
    else
        print_warning "PostgreSQL Database: ❌ Not responding"
    fi
    
    # Check Redis
    if docker-compose exec -T redis redis-cli ping >/dev/null 2>&1; then
        print_status "Redis Cache: ✅ Running"
    else
        print_warning "Redis Cache: ❌ Not responding"
    fi
}

# View logs
view_logs() {
    cd "$BACKEND_DIR"
    if [ -n "$1" ]; then
        docker-compose logs -f "$1"
    else
        docker-compose logs -f
    fi
}

# Start frontend development server
start_frontend() {
    print_status "Starting frontend development server..."
    cd "$FRONTEND_DIR"
    
    if [ ! -d "node_modules" ]; then
        print_status "Installing frontend dependencies..."
        npm install
    fi
    
    npm run dev
}

# Quick setup for new developers
quick_setup() {
    print_status "Setting up MantraPath development environment..."
    
    check_docker
    
    # Create .env file if it doesn't exist
    if [ ! -f "$BACKEND_DIR/.env" ]; then
        print_status "Creating .env file..."
        cd "$BACKEND_DIR"
        bash setup-env.sh
    fi
    
    start_services
    
    print_status "✅ Setup complete!"
    print_status "Frontend will be available at: http://localhost:5173"
    print_status "Backend API will be available at: http://localhost:8000"
    print_status ""
    print_status "To start frontend: $0 frontend"
    print_status "To view logs: $0 logs [service-name]"
    print_status "To stop services: $0 stop"
}

# Show usage
usage() {
    echo "MantraPath Docker Development Script"
    echo ""
    echo "Usage: $0 {start|stop|restart|status|logs|frontend|setup}"
    echo ""
    echo "Commands:"
    echo "  setup     - Quick setup for new developers (recommended)"
    echo "  start     - Start all backend services"
    echo "  stop      - Stop all services"
    echo "  restart   - Restart all services"
    echo "  status    - Check service status"
    echo "  logs      - View logs (optionally specify service name)"
    echo "  frontend  - Start frontend development server"
    echo ""
    echo "Examples:"
    echo "  $0 setup              # First time setup"
    echo "  $0 start              # Start backend services"
    echo "  $0 logs community-service  # View specific service logs"
    echo "  $0 frontend           # Start frontend dev server"
}

# Main script logic
case "${1:-}" in
    "start")
        check_docker
        start_services
        ;;
    "stop")
        check_docker
        stop_services
        ;;
    "restart")
        check_docker
        restart_services
        ;;
    "status")
        check_docker
        check_services
        ;;
    "logs")
        check_docker
        view_logs "$2"
        ;;
    "frontend")
        start_frontend
        ;;
    "setup")
        quick_setup
        ;;
    *)
        usage
        exit 1
        ;;
esac
