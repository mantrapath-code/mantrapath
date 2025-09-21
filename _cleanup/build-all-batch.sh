#!/bin/bash

# Build All Services in Batches
# This script builds all services in small batches to avoid timeout issues

set -e

SCRIPT_DIR="/home/sachin/mantrapath"
BUILD_SCRIPT="$SCRIPT_DIR/build-single-service.sh"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }

# All services to build
SERVICES=(
    "auth_service"
    "chatbot_service" 
    "content_service"
    "profile_service"
    "notification_service"
    "phi3_agent"
    "mood_service"
    "memory_service"
    "ml_service"
    "deployment_api"
    "community_service"
    "api_gateway"
    "action_orchestrator"
    "ai_context_store"
    "ai_event_processor"
    "media_service"
    "proactive_assistance_engine"
    "voice_event_processor"
    "voice_service"
    "translation_service"
    "models_service"
)

log_info "Starting batch build of ${#SERVICES[@]} services"
echo "========================================"

SUCCESS_COUNT=0
FAILED_COUNT=0
FAILED_SERVICES=()

for service in "${SERVICES[@]}"; do
    echo ""
    log_info "Building service: $service"
    echo "----------------------------------------"
    
    if $BUILD_SCRIPT "$service"; then
        log_success "✓ $service completed successfully"
        ((SUCCESS_COUNT++))
    else
        log_error "✗ $service failed to build"
        ((FAILED_COUNT++))
        FAILED_SERVICES+=("$service")
    fi
    
    # Brief pause between builds
    sleep 2
done

echo ""
echo "========================================"
log_info "Build Summary:"
log_success "Successful builds: $SUCCESS_COUNT"

if [ $FAILED_COUNT -gt 0 ]; then
    log_error "Failed builds: $FAILED_COUNT"
    log_error "Failed services:"
    for failed_service in "${FAILED_SERVICES[@]}"; do
        echo "  - $failed_service"
    done
    echo ""
    log_warning "You can retry failed services individually:"
    for failed_service in "${FAILED_SERVICES[@]}"; do
        echo "  ./build-single-service.sh $failed_service"
    done
fi

echo ""
if [ $FAILED_COUNT -eq 0 ]; then
    log_success "🎉 All $SUCCESS_COUNT services built and pushed successfully!"
    exit 0
else
    log_error "⚠️  $FAILED_COUNT out of ${#SERVICES[@]} services failed to build"
    exit 1
fi

