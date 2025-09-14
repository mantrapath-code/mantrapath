#!/bin/bash

# MantraPath Server Startup Script
# This script starts the complete MantraPath application on a server

set -e

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

# Get server IP
get_server_ip() {
    SERVER_IP=$(hostname -I | awk '{print $1}')
    if [ -z "$SERVER_IP" ]; then
        SERVER_IP="localhost"
    fi
    echo "$SERVER_IP"
}

# Check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    print_success "Docker is running"
}

# Check if Ollama is running
check_ollama() {
    if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        print_warning "Ollama is not running. Starting Ollama..."
        ollama serve &
        sleep 10
        if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
            print_success "Ollama started successfully"
        else
            print_error "Failed to start Ollama. Please start it manually: ollama serve"
            exit 1
        fi
    else
        print_success "Ollama is running"
    fi
}

# Check if .env file exists and update with server IP
check_env() {
    if [ ! -f ".env" ]; then
        print_warning ".env file not found. Creating from template..."
        create_env_file
    else
        print_success ".env file found"
    fi
    
    # Update server IP in .env
    SERVER_IP=$(get_server_ip)
    print_status "Updating configuration for server IP: $SERVER_IP"
    
    # Update API Gateway URL
    sed -i "s|VITE_API_GATEWAY_URL=.*|VITE_API_GATEWAY_URL=http://$SERVER_IP:8000|g" .env
    sed -i "s|APP_URL=.*|APP_URL=http://$SERVER_IP:5173|g" .env
    
    print_success "Configuration updated for server deployment"
}

# Create environment file
create_env_file() {
    cat > .env << 'EOF'
# MantraPath Environment Configuration
ENVIRONMENT=production
DEBUG=false
TAG=latest

# Database Configuration
POSTGRES_DB=mantrapath
POSTGRES_USER=mantrapath
POSTGRES_PASSWORD=mantrapath123
POSTGRES_PORT=5432
DATABASE_URL=postgresql://mantrapath:mantrapath123@postgres:5432/mantrapath

# Redis Configuration
REDIS_PORT=6379
REDIS_URL=redis://redis:6379

# API Gateway Configuration
API_GATEWAY_PORT=8000
API_GATEWAY_WEBSOCKET_PORT=8080
API_GATEWAY_METRICS_PORT=9090

# Frontend Configuration
FRONTEND_PORT=5173
VITE_FRONTEND_PORT=5173
VITE_API_GATEWAY_URL=http://SERVER_IP:8000

# Service Ports
AUTH_SERVICE_PORT=8001
PROFILE_SERVICE_PORT=8002
MOOD_SERVICE_PORT=8003
CHATBOT_SERVICE_PORT=8004
CONTENT_SERVICE_PORT=8005
COMMUNITY_SERVICE_PORT=8006
NOTIFICATION_SERVICE_PORT=8007
ML_SERVICE_PORT=8008
TRANSLATION_SERVICE_PORT=8010
VOICE_SERVICE_PORT=8011
ACTION_ORCHESTRATOR_PORT=8012
AI_CONTEXT_STORE_PORT=8013
AI_EVENT_PROCESSOR_PORT=8014
VOICE_EVENT_PROCESSOR_PORT=8015
PHI4_AGENT_PORT=8016
MEMORY_SERVICE_PORT=8017
PROACTIVE_ASSISTANCE_PORT=8018
MEDIA_SERVICE_PORT=8021

# Models Service Configuration
MODELS_SERVICE_INTERNAL_PORT=8080
MODELS_SERVICE_EXTERNAL_PORT=8081

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production-please

# SMTP Configuration (for email notifications)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=your-email@gmail.com

# Application URL
APP_URL=http://SERVER_IP:5173

# External API Keys (optional)
OPENAI_API_KEY=your-openai-api-key-here

# Models Service Configuration
MODELS_PRELOAD_LIST=whisper_base,vosk_hi_small
MODELS_PRELOAD_BACKGROUND=true
MODELS_SERVICE_SKIP_DEFAULTS=false
EOF
    
    # Replace SERVER_IP placeholder
    SERVER_IP=$(get_server_ip)
    sed -i "s/SERVER_IP/$SERVER_IP/g" .env
}

# Function to show service URLs
show_urls() {
    SERVER_IP=$(get_server_ip)
    echo ""
    echo "=========================================="
    echo "🚀 MantraPath Server Application Started!"
    echo "=========================================="
    echo ""
    echo "📱 Frontend (React App):"
    echo "   http://$SERVER_IP:5173"
    echo ""
    echo "🔧 Backend Services:"
    echo "   API Gateway:        http://$SERVER_IP:8000"
    echo "   WebSocket:          ws://$SERVER_IP:8080"
    echo "   API Documentation:  http://$SERVER_IP:8000/docs"
    echo "   ReDoc:              http://$SERVER_IP:8000/redoc"
    echo ""
    echo "🗄️  Database & Cache:"
    echo "   PostgreSQL:         localhost:5432"
    echo "   Redis:              localhost:6379"
    echo "   NATS:               localhost:4222"
    echo ""
    echo "🤖 AI Services:"
    echo "   Models Service:     http://$SERVER_IP:8081"
    echo "   Voice Service:      http://$SERVER_IP:8011"
    echo "   Translation:        http://$SERVER_IP:8010"
    echo ""
    echo "📊 Monitoring:"
    echo "   NATS Monitoring:    http://$SERVER_IP:8222"
    echo "   API Metrics:        http://$SERVER_IP:9090"
    echo ""
    echo "=========================================="
    echo "💡 Team Access: Share these URLs with your team"
    echo "   Server IP: $SERVER_IP"
    echo "=========================================="
    echo ""
}

# Main execution
main() {
    echo "🚀 Starting MantraPath Server Application..."
    echo ""
    
    # Pre-flight checks
    check_docker
    check_ollama
    check_env
    
    # Load environment variables
    source .env
    
    print_status "Starting Docker Compose services..."
    
    # Start services
    docker compose up -d --build
    
    # Wait for services to be ready
    print_status "Waiting for services to start..."
    sleep 15
    
    # Check if services are running
    if docker compose ps | grep -q "Up"; then
        print_success "Services started successfully!"
        show_urls
        
        echo ""
        print_status "To view logs: docker compose logs -f"
        print_status "To stop services: docker compose down"
        print_status "To restart: docker compose restart"
        echo ""
        
        # Show logs for a few seconds
        print_status "Showing recent logs (press Ctrl+C to stop viewing logs):"
        docker compose logs --tail=20 -f
    else
        print_error "Failed to start services. Check logs with: docker compose logs"
        exit 1
    fi
}

# Handle script interruption
trap 'echo -e "\n${YELLOW}Script interrupted. Services are still running.${NC}"; exit 0' INT

# Run main function
main "$@"
