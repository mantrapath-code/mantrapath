#!/bin/bash

# Sprint 2 Backend Services Startup Script
# MantraPath V3 - Live Intelligence Coordination

set -e

echo "🚀 Starting MantraPath Sprint 2 Backend Services"
echo "Theme: Live Intelligence Coordination"
echo "================================================"

# Color codes for output
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

# Check prerequisites
print_status "Checking prerequisites..."

if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

print_success "Prerequisites check passed"

# Navigate to backend directory
cd "$(dirname "$0")"
print_status "Working directory: $(pwd)"

# Stop any existing services
print_status "Stopping existing services..."
docker-compose down --remove-orphans

# Build services
print_status "Building services..."
docker-compose build --parallel

# Start infrastructure services first
print_status "Starting infrastructure services..."
docker-compose up -d postgres redis nats

# Wait for infrastructure to be ready
print_status "Waiting for infrastructure services to be ready..."
for i in {1..30}; do
    if docker-compose exec -T postgres pg_isready -U postgres >/dev/null 2>&1 && \
       docker-compose exec -T redis redis-cli ping >/dev/null 2>&1 && \
       curl -s http://localhost:8222/healthz >/dev/null 2>&1; then
        print_success "Infrastructure services are ready"
        break
    fi
    
    if [ $i -eq 30 ]; then
        print_error "Infrastructure services failed to start within 30 seconds"
        docker-compose logs postgres redis nats
        exit 1
    fi
    
    echo -n "."
    sleep 1
done

# Start Sprint 2 AI services
print_status "Starting Sprint 2 AI services..."
docker-compose up -d ai-event-processor voice-event-processor

# Wait for AI services to be ready
print_status "Waiting for AI services to be ready..."
for i in {1..60}; do
    if curl -s http://localhost:8014/health >/dev/null 2>&1 && \
       curl -s http://localhost:8015/health >/dev/null 2>&1; then
        print_success "AI services are ready"
        break
    fi
    
    if [ $i -eq 60 ]; then
        print_warning "AI services taking longer than expected, checking logs..."
        docker-compose logs --tail=20 ai-event-processor voice-event-processor
    fi
    
    echo -n "."
    sleep 1
done

# Start remaining services
print_status "Starting remaining services..."
docker-compose up -d

# Verify all services
print_status "Verifying service health..."

services=(
    "postgres:5432"
    "redis:6379" 
    "nats:8222"
    "ai-event-processor:8014"
    "voice-event-processor:8015"
    "api-gateway:8000"
)

failed_services=()

for service in "${services[@]}"; do
    service_name=$(echo $service | cut -d: -f1)
    port=$(echo $service | cut -d: -f2)
    
    if curl -s "http://localhost:$port/health" >/dev/null 2>&1 || \
       ([ "$service_name" = "postgres" ] && docker-compose exec -T postgres pg_isready -U postgres >/dev/null 2>&1) || \
       ([ "$service_name" = "redis" ] && docker-compose exec -T redis redis-cli ping >/dev/null 2>&1) || \
       ([ "$service_name" = "nats" ] && curl -s "http://localhost:8222/healthz" >/dev/null 2>&1); then
        print_success "$service_name is healthy"
    else
        print_error "$service_name is not responding"
        failed_services+=("$service_name")
    fi
done

# Sprint 2 specific tests
print_status "Running Sprint 2 verification tests..."

# Test AI Event Processing
print_status "Testing AI Event Processing..."
ai_test_result=$(curl -s -X POST http://localhost:8014/api/v1/analyze/emotion \
    -H "Content-Type: application/json" \
    -d '{"text": "I am feeling great today!", "language": "en", "user_id": "test_user"}' | \
    python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('emotion', 'error'))" 2>/dev/null || echo "error")

if [ "$ai_test_result" != "error" ]; then
    print_success "AI Event Processing test passed (detected emotion: $ai_test_result)"
else
    print_warning "AI Event Processing test failed"
    failed_services+=("ai-event-processor-functionality")
fi

# Test Voice Event Processing readiness
print_status "Testing Voice Event Processing readiness..."
voice_test_result=$(curl -s http://localhost:8015/health/ready | \
    python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('status', 'error'))" 2>/dev/null || echo "error")

if [ "$voice_test_result" = "ready" ]; then
    print_success "Voice Event Processing readiness test passed"
else
    print_warning "Voice Event Processing readiness test failed"
    failed_services+=("voice-event-processor-readiness")
fi

# Display final status
echo ""
echo "================================================"

if [ ${#failed_services[@]} -eq 0 ]; then
    print_success "🎉 Sprint 2 Backend Services started successfully!"
    echo ""
    echo "📊 Service Status:"
    echo "   AI Event Processor:     http://localhost:8014"
    echo "   Voice Event Processor:  http://localhost:8015"
    echo "   API Gateway:           http://localhost:8000"
    echo "   NATS Monitoring:       http://localhost:8222"
    echo ""
    echo "🧪 Test Commands:"
    echo "   AI Emotion Analysis:   curl -X POST http://localhost:8014/api/v1/analyze/emotion -H 'Content-Type: application/json' -d '{\"text\": \"I am happy\", \"language\": \"en\", \"user_id\": \"test\"}'"
    echo "   AI Metrics:           curl http://localhost:8014/api/v1/metrics"
    echo "   Voice Metrics:        curl http://localhost:8015/api/v1/metrics"
    echo ""
    echo "📋 Next Steps:"
    echo "   1. Run integration tests: cd tests && python -m pytest integration/sprint2/"
    echo "   2. Monitor logs: docker-compose logs -f ai-event-processor voice-event-processor"
    echo "   3. Access services via API Gateway at http://localhost:8000"
    echo ""
    echo "✅ Sprint 2 'Live Intelligence Coordination' is operational!"
    
else
    print_error "❌ Some services failed to start properly:"
    for service in "${failed_services[@]}"; do
        echo "   - $service"
    done
    echo ""
    echo "🔧 Troubleshooting:"
    echo "   Check logs: docker-compose logs [service-name]"
    echo "   Restart services: docker-compose restart [service-name]" 
    echo "   Full restart: docker-compose down && ./start-sprint2.sh"
    exit 1
fi

echo "================================================"
