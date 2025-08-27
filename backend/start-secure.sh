#!/bin/bash

# MantraPath Team Setup Script
# Sets up secure environment with ngrok tunneling for team access
# Only exposes API Gateway externally for maximum security

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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

print_header() {
    echo -e "${BLUE}"
    echo "=================================================="
    echo "🚀 MantraPath Secure Team Setup"
    echo "=================================================="
    echo -e "${NC}"
}

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check Docker Compose
    if ! docker compose version &> /dev/null; then
        print_error "Docker Compose is not available. Please install Docker Compose."
        exit 1
    fi
    
    # Check ngrok
    if ! command -v ngrok &> /dev/null; then
        print_error "ngrok is not installed. Please install ngrok first."
        echo "Visit: https://ngrok.com/download"
        exit 1
    fi
    
    # Check ngrok auth
    if ! ngrok config check &> /dev/null; then
        print_warning "ngrok auth token not configured."
        echo "Please run: ngrok config add-authtoken <your-token>"
        echo "Get your token from: https://dashboard.ngrok.com/get-started/your-authtoken"
        read -p "Press Enter after configuring ngrok auth token..."
    fi
    
    print_success "All prerequisites met!"
}

# Setup environment
setup_environment() {
    print_status "Setting up environment..."
    
    # Navigate to backend directory
    cd "$(dirname "$0")"
    
    # Check if .env exists
    if [ ! -f .env ]; then
        if [ -f .env.example ]; then
            print_status "Creating .env from .env.example..."
            cp .env.example .env
            print_warning "Please update .env with your actual values before proceeding."
            read -p "Press Enter after updating .env..."
        else
            print_error ".env file not found. Please create one."
            exit 1
        fi
    fi
    
    print_success "Environment configured!"
}

# Stop any running services
stop_services() {
    print_status "Stopping any running services..."
    
    # Stop regular docker-compose
    docker compose down --remove-orphans 2>/dev/null || true
    
    # Stop secure docker-compose
    docker compose -f docker-compose.secure.yml down --remove-orphans 2>/dev/null || true
    
    # Kill any ngrok processes
    pkill -f ngrok 2>/dev/null || true
    
    print_success "Services stopped!"
}

# Start secure services
start_services() {
    print_status "Starting secure services (internal ports only)..."
    
    # Build and start services using secure configuration
    docker compose -f docker-compose.secure.yml up --build -d
    
    print_status "Waiting for services to be healthy..."
    
    # Wait for API Gateway to be ready
    for i in {1..30}; do
        if curl -f http://localhost:8000/health >/dev/null 2>&1; then
            print_success "API Gateway is ready!"
            break
        fi
        if [ $i -eq 30 ]; then
            print_error "API Gateway failed to start within 60 seconds"
            print_status "Checking logs..."
            docker compose -f docker-compose.secure.yml logs api-gateway --tail 20
            exit 1
        fi
        sleep 2
    done
    
    print_success "Secure services started!"
}

# Start ngrok tunnels
start_ngrok() {
    print_status "Starting ngrok tunnels..."
    
    # Start ngrok with configuration file
    if [ -f ../ngrok.yml ]; then
        ngrok start --config ../ngrok.yml --all &
        NGROK_PID=$!
        print_status "ngrok started with PID: $NGROK_PID"
    else
        print_warning "ngrok.yml not found, starting manual tunnels..."
        # Start main API tunnel
        ngrok http 8000 --log=stdout &
        NGROK_PID=$!
    fi
    
    # Wait for ngrok to start
    sleep 5
    
    # Get tunnel information
    if curl -s http://localhost:4040/api/tunnels >/dev/null 2>&1; then
        print_success "ngrok tunnels started!"
        print_status "Getting tunnel URLs..."
        
        # Extract URLs from ngrok API
        TUNNEL_INFO=$(curl -s http://localhost:4040/api/tunnels)
        
        # Parse and display URLs
        echo -e "${GREEN}"
        echo "=================================================="
        echo "🌐 Your MantraPath Application URLs:"
        echo "=================================================="
        echo "$TUNNEL_INFO" | jq -r '.tunnels[] | "🔗 " + .name + ": " + .public_url'
        echo "=================================================="
        echo -e "${NC}"
        
        # Save URLs to file for team sharing
        echo "$TUNNEL_INFO" | jq -r '.tunnels[] | .name + "=" + .public_url' > .tunnel_urls
        print_success "URLs saved to .tunnel_urls file"
        
    else
        print_warning "Could not retrieve tunnel information automatically"
        print_status "Visit http://localhost:4040 to see ngrok dashboard"
    fi
}

# Display service status
show_status() {
    print_status "Service Status:"
    echo ""
    
    # Check Docker services
    echo "🐳 Docker Services:"
    docker compose -f docker-compose.secure.yml ps
    echo ""
    
    # Check API Gateway health
    echo "🏥 Health Checks:"
    if curl -s http://localhost:8000/health | jq . 2>/dev/null; then
        print_success "API Gateway: Healthy"
    else
        print_error "API Gateway: Unhealthy"
    fi
    echo ""
    
    # Show ngrok status
    if curl -s http://localhost:4040/api/tunnels >/dev/null 2>&1; then
        echo "🌐 ngrok Tunnels:"
        curl -s http://localhost:4040/api/tunnels | jq -r '.tunnels[] | "✅ " + .name + ": " + .public_url'
    else
        print_warning "ngrok not running or not accessible"
    fi
    echo ""
}

# Main execution
main() {
    print_header
    
    case "${1:-start}" in
        "start")
            check_prerequisites
            setup_environment
            stop_services
            start_services
            start_ngrok
            show_status
            
            print_success "🎉 MantraPath is now running securely!"
            print_status "Share the tunnel URLs with your team members"
            print_status "Only the API Gateway is exposed externally"
            print_status "All other services are secure and internal"
            ;;
            
        "stop")
            print_status "Stopping MantraPath..."
            stop_services
            pkill -f ngrok 2>/dev/null || true
            print_success "MantraPath stopped!"
            ;;
            
        "status")
            show_status
            ;;
            
        "restart")
            print_status "Restarting MantraPath..."
            stop_services
            start_services
            show_status
            ;;
            
        "logs")
            SERVICE=${2:-api-gateway}
            print_status "Showing logs for $SERVICE..."
            docker compose -f docker-compose.secure.yml logs $SERVICE --tail 50 -f
            ;;
            
        "help")
            echo "MantraPath Team Setup Script"
            echo ""
            echo "Usage: $0 [command]"
            echo ""
            echo "Commands:"
            echo "  start     Start secure services with ngrok (default)"
            echo "  stop      Stop all services and ngrok"
            echo "  status    Show service status and URLs"
            echo "  restart   Restart services"
            echo "  logs      Show service logs (specify service name)"
            echo "  help      Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0 start          # Start everything"
            echo "  $0 logs mood-service  # Show mood service logs"
            echo "  $0 status         # Check what's running"
            ;;
            
        *)
            print_error "Unknown command: $1"
            print_status "Run '$0 help' for usage information"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
