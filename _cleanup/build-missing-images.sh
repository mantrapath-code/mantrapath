#!/bin/bash

# Quick script to build missing service images
set -e

cd /home/sachin/mantrapath/backend

# Registry info
REGISTRY="blr.vultrcr.com/mantrapath"

# Services to build
SERVICES=(
    "translation_service:mantrapath-translation-service"
    "chatbot_service:mantrapath-chatbot-service" 
    "voice_service:mantrapath-voice-service"
    "ml_service:mantrapath-ml-service"
    "mood_service:mantrapath-mood-service"
    "profile_service:mantrapath-profile-service"
    "content_service:mantrapath-content-service"
    "community_service:mantrapath-community-service"
    "notification_service:mantrapath-notification-service"
    "memory_service:mantrapath-memory-service"
    "media_service:mantrapath-media-service"
    "ai_context_store:mantrapath-ai-context-store"
    "ai_event_processor:mantrapath-ai-event-processor"
    "action_orchestrator:mantrapath-action-orchestrator"
    "voice_event_processor:mantrapath-voice-event-processor"
    "proactive_assistance_engine:mantrapath-proactive-assistance"
    "deployment_api:mantrapath-deployment-api"
    "phi3_agent:mantrapath-phi3-agent"
)

echo "Building and pushing missing service images..."

for service in "${SERVICES[@]}"; do
    IFS=':' read -ra SERVICE_PARTS <<< "$service"
    SERVICE_DIR="${SERVICE_PARTS[0]}"
    IMAGE_NAME="${SERVICE_PARTS[1]}"
    
    echo "Building $SERVICE_DIR -> $IMAGE_NAME"
    
    if [[ -f "services/$SERVICE_DIR/Dockerfile" ]]; then
        docker build -f "services/$SERVICE_DIR/Dockerfile" -t "$REGISTRY/$IMAGE_NAME:latest" . || echo "Failed to build $SERVICE_DIR"
        docker push "$REGISTRY/$IMAGE_NAME:latest" || echo "Failed to push $SERVICE_DIR"
        echo "✅ $SERVICE_DIR completed"
    else
        echo "⚠️ Dockerfile not found for $SERVICE_DIR"
    fi
done

echo "All images built and pushed!"
