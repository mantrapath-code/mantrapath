#!/bin/bash

# Enhanced Chatbot Voice Integration Deployment Script
# 
# This script deploys the enhanced chatbot service with voice integration,
# multi-language support, and platform awareness capabilities.
#
# Author: MantraPath Development Team
# Version: 1.0.0

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BACKEND_DIR="/Users/sachin/Desktop/mantrapath/backend"
ENHANCED_COMPOSE_FILE="docker-compose-enhanced-voice.yml"
TEST_SCRIPT="../scripts/test_enhanced_chatbot_voice.py"

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

# Function to check if service is healthy
check_service_health() {
    local service_name=$1
    local health_url=$2
    local max_attempts=30
    local attempt=1
    
    print_status "Checking health of $service_name..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f -s "$health_url" > /dev/null 2>&1; then
            print_success "$service_name is healthy"
            return 0
        fi
        
        echo -n "."
        sleep 2
        ((attempt++))
    done
    
    print_error "$service_name failed to become healthy after $max_attempts attempts"
    return 1
}

# Function to run tests
run_tests() {
    print_status "Running enhanced chatbot voice integration tests..."
    
    cd "$BACKEND_DIR"
    
    if python3 "$TEST_SCRIPT"; then
        print_success "All tests passed!"
        return 0
    else
        print_error "Some tests failed. Check the logs for details."
        return 1
    fi
}

# Main deployment process
main() {
    print_status "Starting Enhanced Chatbot Voice Integration Deployment"
    echo "============================================================"
    
    # Change to backend directory
    cd "$BACKEND_DIR"
    
    # Check if docker-compose is available
    if ! command -v docker-compose &> /dev/null; then
        print_error "docker-compose is not installed or not in PATH"
        exit 1
    fi
    
    # Check if enhanced compose file exists
    if [ ! -f "$ENHANCED_COMPOSE_FILE" ]; then
        print_error "Enhanced compose file not found: $ENHANCED_COMPOSE_FILE"
        exit 1
    fi
    
    # Stop any existing enhanced services
    print_status "Stopping any existing enhanced services..."
    docker-compose -f "$ENHANCED_COMPOSE_FILE" down --remove-orphans || true
    
    # Build enhanced services
    print_status "Building enhanced chatbot and voice event processor services..."
    docker-compose -f docker-compose.yml -f "$ENHANCED_COMPOSE_FILE" build chatbot-service-enhanced voice-event-processor-enhanced
    
    # Start core dependencies first
    print_status "Starting core dependencies..."
    docker-compose -f docker-compose.yml up -d postgres redis nats
    
    # Wait for core dependencies
    print_status "Waiting for core dependencies to be ready..."
    sleep 10
    
    # Start required services for enhanced chatbot
    print_status "Starting required services..."
    docker-compose -f docker-compose.yml up -d \
        voice-service \
        translation-service \
        mood-service \
        profile-service \
        content-service \
        community-service \
        memory-service \
        action-orchestrator \
        ai-context-store \
        ai-event-processor \
        models-service
    
    # Wait for services to start
    print_status "Waiting for services to initialize..."
    sleep 15
    
    # Start enhanced services
    print_status "Starting enhanced chatbot and voice event processor..."
    docker-compose -f docker-compose.yml -f "$ENHANCED_COMPOSE_FILE" up -d \
        chatbot-service-enhanced \
        voice-event-processor-enhanced
    
    # Wait for enhanced services to start
    print_status "Waiting for enhanced services to initialize..."
    sleep 20
    
    # Health checks
    print_status "Performing health checks..."
    
    services_to_check=(
        "chatbot-service-enhanced:http://localhost:8104/health"
        "voice-event-processor-enhanced:http://localhost:8115/health"
        "voice-service:http://localhost:8011/health"
        "translation-service:http://localhost:8010/health"
    )
    
    all_healthy=true
    for service_check in "${services_to_check[@]}"; do
        IFS=':' read -r service_name health_url <<< "$service_check"
        if ! check_service_health "$service_name" "$health_url"; then
            all_healthy=false
        fi
    done
    
    if [ "$all_healthy" = true ]; then
        print_success "All services are healthy!"
    else
        print_error "Some services are not healthy. Check docker logs for details."
        exit 1
    fi
    
    # Show service status
    print_status "Enhanced services status:"
    echo "============================================================"
    echo "Enhanced Chatbot Service:     http://localhost:8104"
    echo "Voice Event Processor:        http://localhost:8115"
    echo "Original Chatbot Service:     http://localhost:8004"
    echo "Voice Service:                http://localhost:8011"
    echo "Translation Service:          http://localhost:8010"
    echo "============================================================"
    
    # Run integration tests
    print_status "Running integration tests..."
    if run_tests; then
        print_success "Enhanced Chatbot Voice Integration deployed successfully!"
        echo ""
        echo "🎉 Your enhanced chatbot service is now running with:"
        echo "   ✅ Voice interaction support"
        echo "   ✅ Multi-language auto-detection"
        echo "   ✅ Platform awareness (mood, journal, community)"
        echo "   ✅ Cultural intelligence"
        echo "   ✅ Conversation memory"
        echo "   ✅ Crisis detection"
        echo ""
        echo "📋 API Endpoints:"
        echo "   POST /api/chat/voice   - Voice chat with audio upload"
        echo "   POST /api/chat/text    - Text chat with language support"
        echo "   GET  /api/chat/sessions - Get chat sessions"
        echo "   POST /api/language/detect - Detect text language"
        echo ""
        echo "🔧 For troubleshooting:"
        echo "   docker-compose -f docker-compose.yml -f $ENHANCED_COMPOSE_FILE logs chatbot-service-enhanced"
        echo "   docker-compose -f docker-compose.yml -f $ENHANCED_COMPOSE_FILE logs voice-event-processor-enhanced"
    else
        print_warning "Deployment completed but some tests failed. Services are running but may need attention."
    fi
}

# Script options
case "${1:-deploy}" in
    "deploy")
        main
        ;;
    "test")
        cd "$BACKEND_DIR"
        run_tests
        ;;
    "status")
        cd "$BACKEND_DIR"
        print_status "Enhanced services status:"
        docker-compose -f docker-compose.yml -f "$ENHANCED_COMPOSE_FILE" ps chatbot-service-enhanced voice-event-processor-enhanced
        ;;
    "logs")
        cd "$BACKEND_DIR"
        if [ -n "$2" ]; then
            docker-compose -f docker-compose.yml -f "$ENHANCED_COMPOSE_FILE" logs -f "$2"
        else
            docker-compose -f docker-compose.yml -f "$ENHANCED_COMPOSE_FILE" logs -f chatbot-service-enhanced voice-event-processor-enhanced
        fi
        ;;
    "stop")
        cd "$BACKEND_DIR"
        print_status "Stopping enhanced services..."
        docker-compose -f docker-compose.yml -f "$ENHANCED_COMPOSE_FILE" down chatbot-service-enhanced voice-event-processor-enhanced
        print_success "Enhanced services stopped"
        ;;
    "restart")
        cd "$BACKEND_DIR"
        print_status "Restarting enhanced services..."
        docker-compose -f docker-compose.yml -f "$ENHANCED_COMPOSE_FILE" restart chatbot-service-enhanced voice-event-processor-enhanced
        print_success "Enhanced services restarted"
        ;;
    "help")
        echo "Enhanced Chatbot Voice Integration Deployment Script"
        echo ""
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  deploy   - Deploy enhanced services (default)"
        echo "  test     - Run integration tests only"
        echo "  status   - Show service status"
        echo "  logs     - Show service logs (add service name for specific logs)"
        echo "  stop     - Stop enhanced services"
        echo "  restart  - Restart enhanced services"
        echo "  help     - Show this help message"
        echo ""
        echo "Examples:"
        echo "  $0 deploy                    # Deploy all enhanced services"
        echo "  $0 test                      # Run tests only"
        echo "  $0 logs                      # Show all enhanced service logs"
        echo "  $0 logs chatbot-service-enhanced  # Show specific service logs"
        ;;
    *)
        print_error "Unknown command: $1"
        echo "Use '$0 help' for usage information"
        exit 1
        ;;
esac
