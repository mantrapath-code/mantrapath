#!/bin/bash

# Single Service Build Script
# Usage: ./build-single-service.sh <service_name>

set -e

if [ $# -eq 0 ]; then
    echo "Usage: $0 <service_name>"
    echo "Example: $0 models_service"
    exit 1
fi

SERVICE_NAME=$1
# Use env vars for registry configuration (do NOT hardcode secrets)
REGISTRY_URL="${VULTR_REGISTRY:-blr.vultrcr.com/mantrapath}"
REGISTRY_USERNAME="${VULTR_REGISTRY_USERNAME:-}"
REGISTRY_PASSWORD="${VULTR_REGISTRY_PASSWORD:-}"
SERVICES_DIR="/home/sachin/mantrapath/backend/services"
SERVICE_PATH="$SERVICES_DIR/$SERVICE_NAME"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Check if service exists
if [ ! -d "$SERVICE_PATH" ]; then
    log_error "Service directory not found: $SERVICE_PATH"
    exit 1
fi

if [ ! -f "$SERVICE_PATH/Dockerfile" ]; then
    log_error "Dockerfile not found in: $SERVICE_PATH"
    exit 1
fi

if [ -z "$REGISTRY_USERNAME" ] || [ -z "$REGISTRY_PASSWORD" ]; then
    log_error "Missing VULTR_REGISTRY_USERNAME or VULTR_REGISTRY_PASSWORD env vars"
    exit 1
fi

log_info "Building service: $SERVICE_NAME"
log_info "Service path: $SERVICE_PATH"

# Login to registry
log_info "Logging into registry..."
echo "$REGISTRY_PASSWORD" | docker login "https://$REGISTRY_URL" --username "$REGISTRY_USERNAME" --password-stdin

# Get commit SHA
COMMIT_SHA=$(git rev-parse --short HEAD 2>/dev/null || date +%Y%m%d-%H%M%S)

# Build image
log_info "Building Docker image..."
BACKEND_DIR="$(dirname "$SERVICES_DIR")"
docker build -f "$SERVICE_PATH/Dockerfile" -t "temp-$SERVICE_NAME:latest" "$BACKEND_DIR"

# Tag images
log_info "Tagging images..."
docker tag "temp-$SERVICE_NAME:latest" "$REGISTRY_URL/mantrapath-$SERVICE_NAME:latest"
docker tag "temp-$SERVICE_NAME:latest" "$REGISTRY_URL/mantrapath-$SERVICE_NAME:$COMMIT_SHA"

# Push images
log_info "Pushing images..."
docker push "$REGISTRY_URL/mantrapath-$SERVICE_NAME:latest"
docker push "$REGISTRY_URL/mantrapath-$SERVICE_NAME:$COMMIT_SHA"

# Cleanup
docker rmi "temp-$SERVICE_NAME:latest" > /dev/null 2>&1 || true

log_success "Successfully built and pushed $SERVICE_NAME!"
log_info "Images pushed:"
log_info "  - $REGISTRY_URL/mantrapath-$SERVICE_NAME:latest"
log_info "  - $REGISTRY_URL/mantrapath-$SERVICE_NAME:$COMMIT_SHA"
