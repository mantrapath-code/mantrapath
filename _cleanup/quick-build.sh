#!/bin/bash

# Quick Build Script - Non-interactive version for automation
# This script builds and pushes all services without user prompts

set -e

# Configuration
REGISTRY_URL="blr.vultrcr.com/mantrapath"
REGISTRY_USERNAME="e9b950f6-81b8-4433-bb62-844d3f44b6bb"
REGISTRY_PASSWORD="D5w5WAevjZQhcUrEQPcuuA6qgCTXzTfLHtYJ"
SERVICES_DIR="/home/sachin/mantrapath/backend/services"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Login to registry
echo "$REGISTRY_PASSWORD" | docker login "$REGISTRY_URL" --username "$REGISTRY_USERNAME" --password-stdin

# Get commit SHA
COMMIT_SHA=$(git rev-parse --short HEAD 2>/dev/null || date +%Y%m%d-%H%M%S)

# Build and push all services
BACKEND_DIR="$(dirname "$SERVICES_DIR")"
cd "$SERVICES_DIR"
SUCCESS_COUNT=0
TOTAL_COUNT=0

for service_dir in */; do
    service_name=${service_dir%/}
    
    if [ -f "$service_dir/Dockerfile" ]; then
        ((TOTAL_COUNT++))
        log_info "Building $service_name..."
        
        # Build and tag (use backend directory as context)
        if docker build -f "$SERVICES_DIR/$service_dir/Dockerfile" -t "temp-$service_name:latest" "$BACKEND_DIR" && \
           docker tag "temp-$service_name:latest" "$REGISTRY_URL/mantrapath-$service_name:latest" && \
           docker tag "temp-$service_name:latest" "$REGISTRY_URL/mantrapath-$service_name:$COMMIT_SHA" && \
           docker push "$REGISTRY_URL/mantrapath-$service_name:latest" && \
           docker push "$REGISTRY_URL/mantrapath-$service_name:$COMMIT_SHA"; then
            
            log_success "✓ $service_name"
            ((SUCCESS_COUNT++))
            docker rmi "temp-$service_name:latest" > /dev/null 2>&1 || true
        else
            log_error "✗ $service_name"
        fi
    fi
done

log_info "Build Summary: $SUCCESS_COUNT/$TOTAL_COUNT services successful"

if [ $SUCCESS_COUNT -eq $TOTAL_COUNT ]; then
    log_success "All services built and pushed successfully!"
    exit 0
else
    log_error "Some services failed to build"
    exit 1
fi
