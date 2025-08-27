#!/bin/bash

# MantraPath Service Manager
# Comprehensive script for managing all MantraPath services

set -e

# Get script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_header() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════╗"
    echo "║               MantraPath Service Manager                 ║"
    echo "║            Comprehensive Service Management              ║"
    echo "╚══════════════════════════════════════════════════════════╝"
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
    echo "Select an option:"
    echo ""
    echo "1) 🚀 Start All Services"
    echo "2) 🛑 Stop All Services"
    echo "3) 🔄 Restart All Services"
    echo "4) 📊 Service Status"
    echo "5) 🔍 Health Check"
    echo "6) 📝 View Logs"
    echo "7) 🧹 Clean & Reset"
    echo "8) 🔧 Service-specific Actions"
    echo "9) 📋 Environment Info"
    echo "10) 🆘 Emergency Stop"
    echo ""
    echo "0) Exit"
    echo ""
}

check_requirements() {
    print_info "Checking requirements..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker Desktop."
        exit 1
    fi
    
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker Desktop."
        exit 1
    fi
    
    # Check if we have access to project directories
    if [ ! -d "$BACKEND_DIR" ]; then
        print_error "Backend directory not found: $BACKEND_DIR"
        exit 1
    fi
    
    # Check for required files
    if [ ! -f "$BACKEND_DIR/docker-compose.yml" ]; then
        print_error "Docker Compose file not found: $BACKEND_DIR/docker-compose.yml"
        exit 1
    fi
    
    print_info "All requirements met ✅"
}

start_services() {
    print_info "Starting all MantraPath services..."
    cd "$BACKEND_DIR"
    
    # Create .env if it doesn't exist
    if [ ! -f ".env" ]; then
        print_info "Creating .env file..."
        if [ -f "setup-env.sh" ]; then
            bash setup-env.sh
        else
            print_warning ".env file missing and setup-env.sh not found"
        fi
    fi
    
    # Start services
    docker-compose up -d --build
    
    print_info "Waiting for services to initialize..."
    sleep 10
    
    print_info "Services started! Running health check..."
    python3 "$SCRIPT_DIR/quick_health_check_fixed.py"
}

stop_services() {
    print_info "Stopping all MantraPath services..."
    cd "$BACKEND_DIR"
    
    docker-compose down
    
    # Also stop any standalone containers
    docker ps --filter "name=mantrapath" --format "{{.Names}}" | xargs -r docker stop
    
    print_info "All services stopped ✅"
}

restart_services() {
    print_info "Restarting all MantraPath services..."
    stop_services
    sleep 3
    start_services
}

show_status() {
    print_info "Service Status:"
    cd "$BACKEND_DIR"
    
    echo ""
    echo "Docker Compose Services:"
    docker-compose ps
    
    echo ""
    echo "All MantraPath Containers:"
    docker ps --filter "name=mantrapath" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    
    echo ""
    echo "Resource Usage:"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}" $(docker ps --filter "name=mantrapath" --format "{{.Names}}") 2>/dev/null || echo "No running containers"
}

health_check() {
    print_info "Running comprehensive health check..."
    python3 "$SCRIPT_DIR/quick_health_check_fixed.py"
}

view_logs() {
    cd "$BACKEND_DIR"
    
    echo "Available services:"
    docker-compose config --services | sort
    echo ""
    
    read -p "Enter service name (or 'all' for all services): " service_name
    
    if [ "$service_name" = "all" ] || [ -z "$service_name" ]; then
        docker-compose logs -f --tail=100
    else
        docker-compose logs -f --tail=100 "$service_name"
    fi
}

clean_reset() {
    print_warning "This will stop all services and remove containers, networks, and unused images."
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Performing clean reset..."
        cd "$BACKEND_DIR"
        
        # Stop and remove everything
        docker-compose down -v --remove-orphans
        
        # Remove all MantraPath containers
        docker ps -a --filter "name=mantrapath" --format "{{.Names}}" | xargs -r docker rm
        
        # Clean up Docker system
        docker system prune -f
        
        print_info "Clean reset completed ✅"
    else
        print_info "Clean reset cancelled"
    fi
}

service_specific_actions() {
    echo ""
    echo "Service-specific actions:"
    echo "1) Restart specific service"
    echo "2) View specific service logs"
    echo "3) Execute command in service"
    echo "4) Scale service"
    echo ""
    
    read -p "Select action (1-4): " action
    
    case $action in
        1)
            cd "$BACKEND_DIR"
            echo "Available services:"
            docker-compose config --services | sort
            read -p "Enter service name to restart: " service_name
            docker-compose restart "$service_name"
            ;;
        2)
            view_logs
            ;;
        3)
            cd "$BACKEND_DIR"
            echo "Available services:"
            docker-compose config --services | sort
            read -p "Enter service name: " service_name
            read -p "Enter command to execute: " command
            docker-compose exec "$service_name" $command
            ;;
        4)
            cd "$BACKEND_DIR"
            echo "Available services:"
            docker-compose config --services | sort
            read -p "Enter service name: " service_name
            read -p "Enter number of instances: " instances
            docker-compose up -d --scale "$service_name=$instances"
            ;;
        *)
            print_error "Invalid option"
            ;;
    esac
}

show_environment_info() {
    print_info "Environment Information:"
    echo ""
    echo "🐳 Docker:"
    docker --version
    docker-compose --version
    echo ""
    echo "📁 Paths:"
    echo "   Project Root: $PROJECT_ROOT"
    echo "   Backend Dir:  $BACKEND_DIR"
    echo "   Scripts Dir:  $SCRIPT_DIR"
    echo ""
    echo "🌐 Network Status:"
    docker network ls | grep mantrapath || echo "   No MantraPath networks found"
    echo ""
    echo "💾 Volumes:"
    docker volume ls | grep mantrapath || echo "   No MantraPath volumes found"
    echo ""
    echo "🔧 Environment Variables:"
    if [ -f "$BACKEND_DIR/.env" ]; then
        echo "   .env file exists ✅"
        echo "   Environment variables loaded from: $BACKEND_DIR/.env"
    else
        echo "   .env file missing ❌"
    fi
}

emergency_stop() {
    print_warning "Emergency stop - forcefully stopping all containers..."
    
    # Stop all MantraPath containers
    docker ps --filter "name=mantrapath" --format "{{.Names}}" | xargs -r docker kill
    
    # Stop all containers defined in compose file
    cd "$BACKEND_DIR"
    docker-compose kill
    
    print_info "Emergency stop completed"
}

# Main script execution
main() {
    print_header
    check_requirements
    
    while true; do
        show_menu
        read -p "Enter your choice: " choice
        
        case $choice in
            1) start_services ;;
            2) stop_services ;;
            3) restart_services ;;
            4) show_status ;;
            5) health_check ;;
            6) view_logs ;;
            7) clean_reset ;;
            8) service_specific_actions ;;
            9) show_environment_info ;;
            10) emergency_stop ;;
            0) 
                print_info "Goodbye!"
                exit 0
                ;;
            *)
                print_error "Invalid option. Please try again."
                ;;
        esac
        
        echo ""
        read -p "Press Enter to continue..."
    done
}

# Check if script is being sourced or executed
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
