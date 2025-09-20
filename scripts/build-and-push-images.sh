#!/bin/bash

# Build and Push Images to Vultr Registry
# This script builds and pushes MantraPath images following the exact process specified

set -euo pipefail

# Configuration
REGISTRY="blr.vultrcr.com/mantrapath"
USERNAME="e9b950f6-81b8-4433-bb62-844d3f44b6bb"
PASSWORD="D5w5WAevjZQhcUrEQPcuuA6qgCTXzTfLHtYJ"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Login to registry
login_to_registry() {
    log_info "Logging in to Vultr Container Registry..."
    echo "$PASSWORD" | docker login https://blr.vultrcr.com/mantrapath -u "$USERNAME" --password-stdin
    log_success "Successfully logged in to registry"
}

# Build, tag, and push image
build_and_push_image() {
    local service_name="$1"
    local dockerfile_path="$2"
    local build_context="$3"
    local image_name="$4"
    
    log_info "Building $service_name..."
    
    # Build the image
    cd "$build_context"
    docker build -f "$dockerfile_path" -t "temp-$image_name:latest" .
    
    # Tag with registry prefix
    docker tag "temp-$image_name:latest" "$REGISTRY/$image_name:latest"
    
    log_info "Pushing $image_name to registry..."
    
    # Push to registry
    docker push "$REGISTRY/$image_name:latest"
    
    # Clean up temp image
    docker rmi "temp-$image_name:latest" || true
    
    log_success "Successfully pushed $REGISTRY/$image_name:latest"
    
    # Return to project root
    cd - > /dev/null
}

# Test with hello-world first
test_registry() {
    log_info "Testing registry with hello-world image..."
    
    docker pull hello-world:latest
    docker tag hello-world:latest "$REGISTRY/hello-world:latest"
    docker push "$REGISTRY/hello-world:latest"
    
    log_success "Registry test successful!"
    
    # Clean up
    docker rmi hello-world:latest || true
    docker rmi "$REGISTRY/hello-world:latest" || true
}

# Main function
main() {
    local project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
    cd "$project_root"
    
    log_info "Starting build and push process..."
    log_info "Registry: $REGISTRY"
    
    # Login to registry
    login_to_registry
    
    # Test registry
    test_registry
    
    # Build and push core services
    log_info "Building and pushing core services..."
    
    # API Gateway
    build_and_push_image "API Gateway" "backend/services/api_gateway/Dockerfile" "backend" "mantrapath-api-gateway"
    
    # Frontend
    build_and_push_image "Frontend" "deployment/Dockerfile.frontend" "frontend" "mantrapath-frontend"
    
    # Translation Service
    build_and_push_image "Translation Service" "backend/services/translation_service/Dockerfile" "backend" "mantrapath-translation-service"
    
    # Models Service
    build_and_push_image "Models Service" "backend/services/models_service/Dockerfile" "backend" "mantrapath-models-service"
    
    # Auth Service
    build_and_push_image "Auth Service" "backend/services/auth_service/Dockerfile" "backend" "mantrapath-auth-service"
    
    log_success "All core images built and pushed successfully!"
    
    # Optional: Build all other services
    read -p "Build and push all other services? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "Building all services..."
        
        # Add all other services
        build_and_push_image "Chatbot Service" "backend/services/chatbot_service/Dockerfile" "backend" "mantrapath-chatbot-service"
        build_and_push_image "Voice Service" "backend/services/voice_service/Dockerfile" "backend" "mantrapath-voice-service"
        build_and_push_image "ML Service" "backend/services/ml_service/Dockerfile" "backend" "mantrapath-ml-service"
        build_and_push_image "Mood Service" "backend/services/mood_service/Dockerfile" "backend" "mantrapath-mood-service"
        build_and_push_image "Profile Service" "backend/services/profile_service/Dockerfile" "backend" "mantrapath-profile-service"
        build_and_push_image "Content Service" "backend/services/content_service/Dockerfile" "backend" "mantrapath-content-service"
        build_and_push_image "Community Service" "backend/services/community_service/Dockerfile" "backend" "mantrapath-community-service"
        build_and_push_image "Notification Service" "backend/services/notification_service/Dockerfile" "backend" "mantrapath-notification-service"
        build_and_push_image "Memory Service" "backend/services/memory_service/Dockerfile" "backend" "mantrapath-memory-service"
        build_and_push_image "Media Service" "backend/services/media_service/Dockerfile" "backend" "mantrapath-media-service"
        build_and_push_image "AI Context Store" "backend/services/ai_context_store/Dockerfile" "backend" "mantrapath-ai-context-store"
        build_and_push_image "AI Event Processor" "backend/services/ai_event_processor/Dockerfile" "backend" "mantrapath-ai-event-processor"
        build_and_push_image "Action Orchestrator" "backend/services/action_orchestrator/Dockerfile" "backend" "mantrapath-action-orchestrator"
        build_and_push_image "Voice Event Processor" "backend/services/voice_event_processor/Dockerfile" "backend" "mantrapath-voice-event-processor"
        build_and_push_image "Proactive Assistance" "backend/services/proactive_assistance_engine/Dockerfile" "backend" "mantrapath-proactive-assistance"
        
        log_success "All services built and pushed successfully!"
    fi
    
    log_info "Build and push process completed!"
    log_info "Images are available at: https://blr.vultrcr.com/mantrapath"
}

# Run main function
main "$@"
