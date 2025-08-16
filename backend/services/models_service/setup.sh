#!/bin/bash

# Models Service Setup Script
# This script sets up the self-hosted TTS/STT models service for MantraPath

set -e  # Exit on any error

echo "🚀 Setting up MantraPath Models Service..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed and running
check_docker() {
    print_status "Checking Docker installation..."
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker first."
        exit 1
    fi
    
    print_success "Docker is installed and running"
}

# Check if Docker Compose is available
check_docker_compose() {
    print_status "Checking Docker Compose..."
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose is not available. Please install Docker Compose."
        exit 1
    fi
    print_success "Docker Compose is available"
}

# Check available ports
check_ports() {
    print_status "Checking required ports..."
    
    # Check if port 8085 is available
    if lsof -i :8085 >/dev/null 2>&1; then
        print_warning "Port 8085 is already in use."
        print_warning "Current process using port 8085:"
        lsof -i :8085
    else
        print_success "Port 8085 is available for models service"
    fi
    
    # Check if port 6385 is available  
    if lsof -i :6385 >/dev/null 2>&1; then
        print_warning "Port 6385 is already in use."
        print_warning "Current process using port 6385:"
        lsof -i :6385
    else
        print_success "Port 6385 is available for Redis"
    fi
}

# Check system resources
check_resources() {
    print_status "Checking system resources..."
    
    # Check available disk space (need at least 5GB for basic models)
    available_space=$(df -h . | awk 'NR==2 {print $4}' | sed 's/G.*//')
    if [ "${available_space}" -lt 5 ] 2>/dev/null; then
        print_warning "Available disk space may be limited. Consider cleaning up for larger models."
    else
        print_success "Sufficient disk space available"
    fi
}

# Build and start services
build_and_start() {
    print_status "Building Docker images..."
    if docker-compose build; then
        print_success "Docker images built successfully"
    else
        print_error "Failed to build Docker images"
        exit 1
    fi
    
    print_status "Starting services..."
    if docker-compose up -d; then
        print_success "Services started successfully"
    else
        print_error "Failed to start services"
        exit 1
    fi
}

# Wait for services to be healthy
wait_for_health() {
    print_status "Waiting for services to be healthy..."
    
    max_attempts=30
    attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -s http://localhost:8085/health >/dev/null 2>&1; then
            print_success "Models service is healthy"
            break
        fi
        
        attempt=$((attempt + 1))
        echo -n "."
        sleep 2
    done
    
    if [ $attempt -eq $max_attempts ]; then
        print_error "Services did not become healthy within expected time"
        echo "Check logs with: docker-compose logs"
        exit 1
    fi
}

# Test basic functionality
test_functionality() {
    print_status "Testing basic functionality..."
    
    # Test health endpoint
    if curl -s http://localhost:8085/health | grep -q "healthy"; then
        print_success "Health endpoint working"
    else
        print_error "Health endpoint not responding correctly"
        return 1
    fi
    
    # Test models list endpoint
    if curl -s http://localhost:8085/models/available >/dev/null 2>&1; then
        print_success "Models list endpoint working"
    else
        print_error "Models list endpoint not responding"
        return 1
    fi
    
    # Test STT languages endpoint
    if curl -s http://localhost:8085/api/v1/stt/languages >/dev/null 2>&1; then
        print_success "STT languages endpoint working"
    else
        print_error "STT languages endpoint not responding"
        return 1
    fi
}

# Show service information
show_info() {
    echo ""
    echo "🎉 MantraPath Models Service Setup Complete!"
    echo ""
    echo "📍 Service URLs:"
    echo "   • API Documentation: http://localhost:8085/docs"
    echo "   • Health Check: http://localhost:8085/health"
    echo "   • Available Models: http://localhost:8085/models/available"
    echo ""
    echo "🔧 Management Commands:"
    echo "   • Check status: docker-compose ps"
    echo "   • View logs: docker-compose logs -f models-service"
    echo "   • Stop services: docker-compose down"
    echo "   • Restart services: docker-compose restart"
    echo ""
    echo "🌐 Supported Languages:"
    echo "   • Hindi (hi), Bengali (bn), Telugu (te), Tamil (ta)"
    echo "   • English (en), Spanish (es), French (fr), German (de)"
    echo ""
    echo "💡 Quick Test:"
    echo "   curl -s http://localhost:8085/health | python3 -m json.tool"
    echo ""
}

# Main execution
main() {
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║              MantraPath Models Service Setup                 ║"
    echo "║                 Self-Hosted TTS/STT Service                  ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""
    
    # Change to the script directory
    cd "$(dirname "$0")"
    
    # Run all checks
    check_docker
    check_docker_compose
    check_ports
    check_resources
    
    echo ""
    print_status "All checks passed. Starting setup..."
    echo ""
    
    # Build and start
    build_and_start
    
    # Wait for health
    wait_for_health
    
    # Test functionality
    if test_functionality; then
        print_success "All tests passed"
    else
        print_warning "Some tests failed, but basic service is running"
    fi
    
    # Show final information
    show_info
}

# Handle command line arguments
case "${1:-}" in
    --help|-h)
        echo "MantraPath Models Service Setup Script"
        echo ""
        echo "Usage: $0 [options]"
        echo ""
        echo "Options:"
        echo "  --help, -h        Show this help message"
        echo "  --check-only      Only run system checks"
        echo ""
        exit 0
        ;;
    --check-only)
        check_docker
        check_docker_compose
        check_ports
        check_resources
        print_success "All checks completed"
        exit 0
        ;;
    *)
        main "$@"
        ;;
esac
