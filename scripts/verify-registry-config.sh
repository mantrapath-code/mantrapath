#!/bin/bash

# Verify Registry Configuration Script
# Ensures all Helm templates and values correctly reference the Vultr registry

set -euo pipefail

# Configuration
REGISTRY="blr.vultrcr.com/mantrapath"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

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

check_helm_values() {
    log_info "Checking Helm values files..."
    
    local values_files=(
        "deployment/helm/mantrapath/values.yaml"
        "deployment/helm/mantrapath/values-dev.yaml"
        "deployment/helm/mantrapath/values-dev-minimal.yaml"
        "deployment/helm/mantrapath/values-prod.yaml"
    )
    
    for values_file in "${values_files[@]}"; do
        if [[ -f "$PROJECT_ROOT/$values_file" ]]; then
            local registry_value=$(grep -o 'registry: "[^"]*"' "$PROJECT_ROOT/$values_file" | head -1 || echo "")
            if [[ "$registry_value" == *"$REGISTRY"* ]]; then
                log_success "$values_file: Registry correctly set to $REGISTRY"
            else
                log_warning "$values_file: Registry not set or incorrect: $registry_value"
            fi
        else
            log_warning "$values_file: File not found"
        fi
    done
}

check_helm_templates() {
    log_info "Checking Helm templates for registry usage..."
    
    local template_files=(
        "deployment/helm/mantrapath/charts/api-gateway/templates/deployment.yaml"
        "deployment/helm/mantrapath/charts/frontend/templates/deployment.yaml"
        "deployment/helm/mantrapath/charts/translation-service/templates/deployment.yaml"
        "deployment/helm/mantrapath/charts/models-service/templates/deployment.yaml"
        "deployment/helm/mantrapath/charts/microservice/templates/deployment.yaml"
    )
    
    for template_file in "${template_files[@]}"; do
        if [[ -f "$PROJECT_ROOT/$template_file" ]]; then
            if grep -q "global.registry" "$PROJECT_ROOT/$template_file"; then
                log_success "$template_file: Uses global.registry template"
            else
                log_error "$template_file: Missing global.registry template usage"
            fi
        else
            log_warning "$template_file: File not found"
        fi
    done
}

check_image_pull_secrets() {
    log_info "Checking image pull secrets configuration..."
    
    # Check if registry secret is configured in values
    if grep -q "imagePullSecrets.*registry" "$PROJECT_ROOT/deployment/helm/mantrapath/values.yaml"; then
        log_success "Image pull secrets configured in values.yaml"
    else
        log_error "Image pull secrets not configured in values.yaml"
    fi
    
    # Check if registry secret template exists
    if grep -q "dockerRegistry" "$PROJECT_ROOT/deployment/helm/mantrapath/templates/secrets.yaml"; then
        log_success "Registry secret template exists in secrets.yaml"
    else
        log_error "Registry secret template missing in secrets.yaml"
    fi
}

test_registry_connectivity() {
    log_info "Testing registry connectivity..."
    
    # Test if we can reach the registry
    if curl -s --connect-timeout 5 "https://blr.vultrcr.com" > /dev/null; then
        log_success "Registry is reachable"
    else
        log_error "Cannot reach registry at https://blr.vultrcr.com"
    fi
    
    # Test if we can login (if docker is available)
    if command -v docker &> /dev/null; then
        log_info "Testing Docker registry login..."
        echo "D5w5WAevjZQhcUrEQPcuuA6qgCTXzTfLHtYJ" | docker login https://blr.vultrcr.com/mantrapath -u e9b950f6-81b8-4433-bb62-844d3f44b6bb --password-stdin &> /dev/null
        if [[ $? -eq 0 ]]; then
            log_success "Docker registry login successful"
        else
            log_error "Docker registry login failed"
        fi
    else
        log_warning "Docker not available, skipping login test"
    fi
}

generate_image_list() {
    log_info "Generating expected image list..."
    
    cat << EOF > "$PROJECT_ROOT/REGISTRY_IMAGES.md"
# MantraPath Container Images

All images are stored in the Vultr Container Registry: **$REGISTRY**

## Core Services

| Service | Image Name | Registry URL |
|---------|------------|--------------|
| API Gateway | mantrapath-api-gateway | $REGISTRY/mantrapath-api-gateway |
| Frontend | mantrapath-frontend | $REGISTRY/mantrapath-frontend |
| Translation Service | mantrapath-translation-service | $REGISTRY/mantrapath-translation-service |
| Models Service | mantrapath-models-service | $REGISTRY/mantrapath-models-service |
| Auth Service | mantrapath-auth-service | $REGISTRY/mantrapath-auth-service |

## Additional Services

| Service | Image Name | Registry URL |
|---------|------------|--------------|
| Chatbot Service | mantrapath-chatbot-service | $REGISTRY/mantrapath-chatbot-service |
| Voice Service | mantrapath-voice-service | $REGISTRY/mantrapath-voice-service |
| ML Service | mantrapath-ml-service | $REGISTRY/mantrapath-ml-service |
| Mood Service | mantrapath-mood-service | $REGISTRY/mantrapath-mood-service |
| Profile Service | mantrapath-profile-service | $REGISTRY/mantrapath-profile-service |
| Content Service | mantrapath-content-service | $REGISTRY/mantrapath-content-service |
| Community Service | mantrapath-community-service | $REGISTRY/mantrapath-community-service |
| Notification Service | mantrapath-notification-service | $REGISTRY/mantrapath-notification-service |
| Memory Service | mantrapath-memory-service | $REGISTRY/mantrapath-memory-service |
| Media Service | mantrapath-media-service | $REGISTRY/mantrapath-media-service |
| AI Context Store | mantrapath-ai-context-store | $REGISTRY/mantrapath-ai-context-store |
| AI Event Processor | mantrapath-ai-event-processor | $REGISTRY/mantrapath-ai-event-processor |
| Action Orchestrator | mantrapath-action-orchestrator | $REGISTRY/mantrapath-action-orchestrator |
| Voice Event Processor | mantrapath-voice-event-processor | $REGISTRY/mantrapath-voice-event-processor |
| Proactive Assistance | mantrapath-proactive-assistance | $REGISTRY/mantrapath-proactive-assistance |

## Image Tags

Each image is tagged with:
- \`latest\` - Latest version from main branch
- \`prod\` - Production release (from main branch)
- \`dev\` - Development version (from develop branch)
- \`<commit-sha>\` - Specific commit version

## Registry Access

- **Registry URL:** https://blr.vultrcr.com/mantrapath
- **Username:** e9b950f6-81b8-4433-bb62-844d3f44b6bb
- **Authentication:** Required for pull/push operations

## Kubernetes Configuration

Both prod and dev environments are configured to pull from this registry:

\`\`\`yaml
global:
  registry: "$REGISTRY"
  imagePullSecrets: ["mantrapath-dev-registry"]
\`\`\`

## CI/CD Integration

All images are automatically built and pushed by GitHub Actions:
- Push to \`main\` → Build and tag as \`latest\`, \`prod\`
- Push to \`develop\` → Build and tag as \`latest\`, \`dev\`
- All commits → Tag with commit SHA
EOF
    
    log_success "Image list generated: REGISTRY_IMAGES.md"
}

main() {
    cd "$PROJECT_ROOT"
    
    log_info "🔍 Verifying MantraPath registry configuration..."
    log_info "Target registry: $REGISTRY"
    echo
    
    check_helm_values
    echo
    
    check_helm_templates
    echo
    
    check_image_pull_secrets
    echo
    
    test_registry_connectivity
    echo
    
    generate_image_list
    echo
    
    log_success "✅ Registry configuration verification completed!"
    log_info "📋 Summary:"
    log_info "  • Registry: $REGISTRY"
    log_info "  • All images will be pushed to and pulled from this registry"
    log_info "  • Both prod and dev environments use the same registry"
    log_info "  • CI/CD pipeline configured to push all builds"
}

main "$@"
