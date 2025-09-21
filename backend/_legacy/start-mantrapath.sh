#!/bin/bash

# MantraPath Docker Compose Startup Script
# This script starts the complete MantraPath application with frontend and backend services

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

# Check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    print_success "Docker is running"
}

# Check if .env file exists
check_env() {
    if [ ! -f ".env" ]; then
        print_warning ".env file not found. Creating from template..."
        cat > .env << 'EOF'
# MantraPath Environment Configuration
ENVIRONMENT=development
DEBUG=true
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
VITE_API_GATEWAY_URL=http://139.84.213.185:8000

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
SMTP_USERNAME=hr@mantrapath
SMTP_PASSWORD=yihh wowx rvth fsuq
FROM_EMAIL=hr@mantrapathclear

# Application URL
APP_URL=http://139.84.213.185:5173

# Ollama Configuration
OLLAMA_BASE_URL=http://139.84.213.185:11434
OLLAMA_URL=http://139.84.213.185:11434

# External API Keys (optional)
OPENAI_API_KEY=your-openai-api-key-here

# Models Service Configuration
MODELS_PRELOAD_LIST=whisper_base,vosk_hi_small
MODELS_PRELOAD_BACKGROUND=true
MODELS_SERVICE_SKIP_DEFAULTS=false
EOF
        print_success ".env file created"
    else
        print_success ".env file found"
    fi
}

# Function to show service URLs
show_urls() {
    local server_ip=${1:-"139.84.213.185"}
    echo ""
    echo "=========================================="
    echo "🚀 MantraPath Application Started!"
    echo "=========================================="
    echo ""
    echo "📱 Frontend (React App):"
    echo "   http://$server_ip:5173"
    echo ""
    echo "🔧 Backend Services:"
    echo "   API Gateway:        http://$server_ip:8000"
    echo "   WebSocket:          ws://$server_ip:8080"
    echo "   API Documentation:  http://$server_ip:8000/docs"
    echo "   ReDoc:              http://$server_ip:8000/redoc"
    echo ""
    echo "🗄️  Database & Cache (Internal to Docker Network):"
    echo "   PostgreSQL:         postgres:5432"
    echo "   Redis:              redis:6379"
    echo "   NATS:               nats:4222"
    echo ""
    echo "🤖 AI Services:"
    echo "   Models Service:     http://$server_ip:8081"
    echo "   Voice Service:      http://$server_ip:8011"
    echo "   Translation:        http://$server_ip:8010"
    echo "   Ollama (Host):      http://$server_ip:11434"
    echo ""
    echo "📊 Monitoring:"
    echo "   NATS Monitoring:    http://$server_ip:8222"
    echo "   API Metrics:        http://$server_ip:9090"
    echo ""
    echo "=========================================="
    echo "💡 Team Access: Share the above URLs with team members for network access."
    echo "=========================================="
    echo ""
}

# Function to get local IP
get_local_ip() {
    if command -v ip > /dev/null 2>&1; then
        LOCAL_IP=$(ip route get 1.1.1.1 | awk '{print $7; exit}' 2>/dev/null)
    elif command -v hostname > /dev/null 2>&1; then
        LOCAL_IP=$(hostname -I | awk '{print $1}' 2>/dev/null)
    else
        LOCAL_IP="localhost"
    fi
    
    if [ -n "$LOCAL_IP" ] && [ "$LOCAL_IP" != "127.0.0.1" ]; then
        echo ""
        echo "🌐 Team Access URLs (Server IP: $LOCAL_IP):"
        echo "   Frontend:  http://$LOCAL_IP:5173"
        echo "   API:       http://$LOCAL_IP:8000"
        echo "   WebSocket: ws://$LOCAL_IP:8080"
        echo ""
    fi
}

# Main execution
main() {
    echo "🚀 Starting MantraPath Application..."
    echo ""
    
    # Pre-flight checks
    check_docker
    check_env
    
    # Get server IP
    SERVER_IP=$(hostname -I | awk '{print $1}' 2>/dev/null)
    if [ -z "$SERVER_IP" ]; then
        SERVER_IP="139.84.213.185"  # Fallback to known server IP
    fi
    
    print_status "Using server IP: $SERVER_IP"
    
    # Update .env file with server IP
    print_status "Updating configuration for server deployment..."
    sed -i "s|APP_URL=http://localhost:5173|APP_URL=http://$SERVER_IP:5173|g" .env
    sed -i "s|VITE_API_GATEWAY_URL=http://localhost:8000|VITE_API_GATEWAY_URL=http://$SERVER_IP:8000|g" .env
    sed -i "s|OLLAMA_BASE_URL=http://localhost:11434|OLLAMA_BASE_URL=http://$SERVER_IP:11434|g" .env
    sed -i "s|OLLAMA_URL=http://localhost:11434|OLLAMA_URL=http://$SERVER_IP:11434|g" .env
    
    # Load environment variables
    source .env
    
    # Export server IP for Docker Compose
    export APP_URL="http://$SERVER_IP:5173"
    export VITE_API_GATEWAY_URL="http://$SERVER_IP:8000"
    export OLLAMA_BASE_URL="http://$SERVER_IP:11434"
    export OLLAMA_URL="http://$SERVER_IP:11434"
    
    print_status "Starting Docker Compose services..."
    
    # Start services
    docker compose up -d --build
    
    # Wait for services to be ready
    print_status "Waiting for services to start..."
    sleep 10
    
    # Check if services are running
    if docker compose ps | grep -q "Up"; then
        print_success "Services started successfully!"
        show_urls "$SERVER_IP"
        get_local_ip
        
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
