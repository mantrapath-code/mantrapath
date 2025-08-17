#!/bin/bash
# MantraPath - Unified Development Launcher
# This script replaces all the old individual start scripts

set -e

# Get script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

# Load environment variables
if [ -f "$PROJECT_ROOT/backend/.env" ]; then
    set -a # automatically export all variables
    source "$PROJECT_ROOT/backend/.env"
    set +a
else
    # Set defaults
    DOMAIN=${DOMAIN:-localhost}
    PROTOCOL=${PROTOCOL:-http}
    FRONTEND_PORT=${FRONTEND_PORT:-5173}
    API_GATEWAY_PORT=${API_GATEWAY_PORT:-8000}
fi

# Construct URLs from environment variables
FRONTEND_URL="${PROTOCOL}://${DOMAIN}:${FRONTEND_PORT}"
API_GATEWAY_URL="${PROTOCOL}://${DOMAIN}:${API_GATEWAY_PORT}"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_header() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════╗"
    echo "║            MantraPath                ║"
    echo "║     Development Environment         ║"
    echo "╚══════════════════════════════════════╝"
    echo -e "${NC}"
}

print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

show_menu() {
    echo ""
    echo "Select what you want to start:"
    echo ""
    echo "1) 🚀 Full Stack (Backend + Frontend) - Recommended"
    echo "2) 🐳 Backend Services Only (Docker)"
    echo "3) 💻 Frontend Only"
    echo "4) 📊 View Service Status"
    echo "5) 📝 View Logs"
    echo "6) 🛑 Stop All Services"
    echo "7) ❓ Help & Documentation"
    echo "8) 🏗️  First Time Setup"
    echo ""
    echo "0) Exit"
    echo ""
}

check_requirements() {
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker Desktop."
        exit 1
    fi
    
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker Desktop."
        exit 1
    fi
    
    # Check Node.js for frontend
    if ! command -v node &> /dev/null; then
        print_warning "Node.js is not installed. Frontend development will not be available."
    fi
}

start_backend() {
    print_info "Starting backend services with Docker Compose..."
    cd "$PROJECT_ROOT/backend"
    
    # Check if .env exists
    if [ ! -f ".env" ]; then
        print_info "Creating .env file..."
        bash setup-env.sh
    fi
    
    docker-compose up -d --build
    print_info "Backend services started successfully!"
    
    # Wait a bit for services to initialize
    sleep 5
    
    # Show service status
    echo ""
    print_info "Service Status:"
    docker-compose ps
    
    echo ""
    print_info "API Gateway: $API_GATEWAY_URL"
    print_info "Health Check: $API_GATEWAY_URL/health"
}

start_frontend() {
    print_info "Starting frontend development server..."
    cd "$PROJECT_ROOT/frontend"
    
    if [ ! -d "node_modules" ]; then
        print_info "Installing frontend dependencies..."
        npm install
    fi
    
    print_info "Frontend starting at: $FRONTEND_URL"
    npm run dev
}

start_full_stack() {
    print_info "Starting full MantraPath development environment..."
    
    # Start backend in background
    start_backend
    
    echo ""
    print_info "Backend is running. Starting frontend..."
    sleep 2
    
    # Start frontend (this will block)
    start_frontend
}

view_status() {
    print_info "Checking service status..."
    cd "$PROJECT_ROOT/backend"
    
    if [ ! -f "docker-compose.yml" ]; then
        print_error "Docker Compose file not found!"
        return 1
    fi
    
    echo ""
    echo "Docker Services:"
    docker-compose ps
    
    echo ""
    echo "Service Health Checks:"
    
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
        "8010:Translation Service"
        "8011:Voice Service"
        "8012:Action Orchestrator"
        "8013:AI Context Store"
        "8014:AI Event Processor"
        "8015:Voice Event Processor"
        "8080:Models Service"
        "5432:PostgreSQL"
        "6379:Redis"
        "4222:NATS Client"
        "8222:NATS Monitor"
    )
    
    for service in "${services[@]}"; do
        port=$(echo $service | cut -d: -f1)
        name=$(echo $service | cut -d: -f2)
        
        # Special handling for different service types
        case $port in
            5432)
                # PostgreSQL - check if port is open
                if nc -z localhost $port 2>/dev/null; then
                    echo -e "  ${GREEN}✅${NC} $name (port $port)"
                else
                    echo -e "  ${RED}❌${NC} $name (port $port)"
                fi
                ;;
            6379)
                # Redis - check if port is open
                if nc -z localhost $port 2>/dev/null; then
                    echo -e "  ${GREEN}✅${NC} $name (port $port)"
                else
                    echo -e "  ${RED}❌${NC} $name (port $port)"
                fi
                ;;
            4222)
                # NATS Client - check if port is open
                if nc -z localhost $port 2>/dev/null; then
                    echo -e "  ${GREEN}✅${NC} $name (port $port)"
                else
                    echo -e "  ${RED}❌${NC} $name (port $port)"
                fi
                ;;
            8222)
                # NATS Monitor - has special healthz endpoint
                if curl -s -f "${PROTOCOL}://${DOMAIN}:$port/healthz" >/dev/null 2>&1; then
                    echo -e "  ${GREEN}✅${NC} $name (port $port)"
                else
                    echo -e "  ${RED}❌${NC} $name (port $port)"
                fi
                ;;
            *)
                # Regular services with /health endpoint
                if curl -s -f "${PROTOCOL}://${DOMAIN}:$port/health" >/dev/null 2>&1; then
                    echo -e "  ${GREEN}✅${NC} $name (port $port)"
                else
                    echo -e "  ${RED}❌${NC} $name (port $port)"
                fi
                ;;
        esac
    done
}

view_logs() {
    cd "$PROJECT_ROOT/backend"
    
    echo "Available services:"
    docker-compose config --services
    echo ""
    
    read -p "Enter service name (or press Enter for all): " service_name
    
    if [ -z "$service_name" ]; then
        docker-compose logs -f
    else
        docker-compose logs -f "$service_name"
    fi
}

stop_services() {
    print_info "Stopping all services..."
    cd "$PROJECT_ROOT/backend"
    docker-compose down
    print_info "All services stopped."
}

show_help() {
    echo ""
    echo "MantraPath Development Guide"
    echo "============================"
    echo ""
    echo "🚀 Quick Start:"
    echo "   1. Run './start.sh' and choose option 8 (First Time Setup)"
    echo "   2. Then choose option 1 (Full Stack) to start development"
    echo ""
    echo "📁 Project Structure:"
    echo "   • backend/     - All microservices (Docker containers)"
    echo "   • frontend/    - React/TypeScript frontend"
    echo "   • scripts/     - Development scripts"
    echo ""
    echo "🐳 Docker Services:"
    echo "   • PostgreSQL   - Main database (port 5432)"
    echo "   • Redis        - Cache and sessions (port 6379)"
    echo "   • API Gateway  - $API_GATEWAY_URL"
    echo "   • Auth Service - ${PROTOCOL}://${DOMAIN}:8001"
    echo "   • Community    - ${PROTOCOL}://${DOMAIN}:8006"
    echo "   • [... and more]"
    echo ""
    echo "💻 Frontend:"
    echo "   • Development server: $FRONTEND_URL"
    echo "   • Built with Vite + React + TypeScript"
    echo ""
    echo "🔧 Useful Commands:"
    echo "   • View logs: ./start.sh → option 5"
    echo "   • Check status: ./start.sh → option 4"
    echo "   • Stop services: ./start.sh → option 6"
    echo ""
    echo "📚 Documentation: docs/ directory"
    echo ""
}

first_time_setup() {
    print_info "Starting first-time setup for MantraPath..."
    
    # Check requirements
    check_requirements
    
    # Setup backend
    print_info "Setting up backend environment..."
    cd "$PROJECT_ROOT/backend"
    
    if [ ! -f ".env" ]; then
        bash setup-env.sh
    fi
    
    # Start backend services
    print_info "Building and starting backend services..."
    docker-compose up -d --build
    
    # Wait for services to be ready
    print_info "Waiting for services to initialize..."
    sleep 15
    
    # Setup frontend
    print_info "Setting up frontend dependencies..."
    cd "$PROJECT_ROOT/frontend"
    npm install
    
    print_info ""
    print_info "✅ Setup complete!"
    print_info ""
    print_info "🚀 You can now:"
    print_info "   • Start full development: ./start.sh → option 1"
    print_info "   • View service status: ./start.sh → option 4"
    print_info "   • Access the app: $FRONTEND_URL (after starting frontend)"
    print_info ""
}

# Main script execution
main() {
    print_header
    
    if [ $# -eq 0 ]; then
        # Interactive mode
        while true; do
            show_menu
            read -p "Enter your choice [0-8]: " choice
            
            case $choice in
                1)
                    check_requirements
                    start_full_stack
                    break
                    ;;
                2)
                    check_requirements
                    start_backend
                    break
                    ;;
                3)
                    start_frontend
                    break
                    ;;
                4)
                    view_status
                    echo ""
                    read -p "Press Enter to continue..."
                    ;;
                5)
                    view_logs
                    break
                    ;;
                6)
                    stop_services
                    echo ""
                    read -p "Press Enter to continue..."
                    ;;
                7)
                    show_help
                    echo ""
                    read -p "Press Enter to continue..."
                    ;;
                8)
                    first_time_setup
                    echo ""
                    read -p "Press Enter to continue..."
                    ;;
                0)
                    print_info "Goodbye!"
                    exit 0
                    ;;
                *)
                    print_error "Invalid option. Please try again."
                    ;;
            esac
        done
    else
        # Command line mode
        case "$1" in
            "backend")
                check_requirements
                start_backend
                ;;
            "frontend")
                start_frontend
                ;;
            "full"|"all")
                check_requirements
                start_full_stack
                ;;
            "status")
                view_status
                ;;
            "logs")
                view_logs
                ;;
            "stop")
                stop_services
                ;;
            "setup")
                first_time_setup
                ;;
            "help"|"-h"|"--help")
                show_help
                ;;
            *)
                echo "Usage: $0 [backend|frontend|full|status|logs|stop|setup|help]"
                echo "Or run without arguments for interactive menu."
                exit 1
                ;;
        esac
    fi
}

# Run main function
main "$@"
