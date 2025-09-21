#!/bin/bash

# MantraPath Complete Service Deployment Script
# This script builds and deploys all MantraPath services to Kubernetes using Helm

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REGISTRY="blr.vultrcr.com/mantrapath"
REGISTRY_USERNAME="e9b950f6-81b8-4433-bb62-844d3f44b6bb"
NAMESPACE_DEV="mantrapath-dev"
NAMESPACE_PROD="mantrapath-prod"
HELM_CHART_PATH="../helm/mantrapath"
PROJECT_ROOT="../.."

# Default values
ENVIRONMENT="dev"
BUILD_IMAGES="true"
DEPLOY_HELM="true"
FORCE_REBUILD="false"
SELECTED_SERVICES=""

# Service definitions: name:dockerfile:context:image:port
declare -a ALL_SERVICES=(
    "api-gateway:backend/services/api_gateway/Dockerfile:backend:mantrapath-api-gateway:8000"
    "frontend:deployment/configs/Dockerfile.frontend:frontend:mantrapath-frontend:3000"
    "translation-service:backend/services/translation_service/Dockerfile:backend:mantrapath-translation-service:8010"
    "models-service:backend/services/models_service/Dockerfile:backend:mantrapath-models-service:8080"
    "auth-service:backend/services/auth_service/Dockerfile:backend:mantrapath-auth-service:8001"
    "chatbot-service:backend/services/chatbot_service/Dockerfile:backend:mantrapath-chatbot-service:8003"
    "voice-service:backend/services/voice_service/Dockerfile:backend:mantrapath-voice-service:8007"
    "ml-service:backend/services/ml_service/Dockerfile:backend:mantrapath-ml-service:8004"
    "mood-service:backend/services/mood_service/Dockerfile:backend:mantrapath-mood-service:8015"
    "profile-service:backend/services/profile_service/Dockerfile:backend:mantrapath-profile-service:8002"
    "content-service:backend/services/content_service/Dockerfile:backend:mantrapath-content-service:8009"
    "community-service:backend/services/community_service/Dockerfile:backend:mantrapath-community-service:8011"
    "notification-service:backend/services/notification_service/Dockerfile:backend:mantrapath-notification-service:8013"
    "memory-service:backend/services/memory_service/Dockerfile:backend:mantrapath-memory-service:8014"
    "media-service:backend/services/media_service/Dockerfile:backend:mantrapath-media-service:8012"
    "ai-context-store:backend/services/ai_context_store/Dockerfile:backend:mantrapath-ai-context-store:8005"
    "ai-event-processor:backend/services/ai_event_processor/Dockerfile:backend:mantrapath-ai-event-processor:8006"
    "action-orchestrator:backend/services/action_orchestrator/Dockerfile:backend:mantrapath-action-orchestrator:8016"
    "voice-event-processor:backend/services/voice_event_processor/Dockerfile:backend:mantrapath-voice-event-processor:8008"
    "proactive-assistance:backend/services/proactive_assistance_engine/Dockerfile:backend:mantrapath-proactive-assistance:8017"
    "deployment-api:backend/services/deployment_api/Dockerfile:backend:mantrapath-deployment-api:8086"
    "phi3-agent:backend/services/phi3_agent/Dockerfile:backend:mantrapath-phi3-agent:8018"
)

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

# Function to show usage
usage() {
    cat << EOF
MantraPath Complete Service Deployment Script

Usage: $0 [OPTIONS]

Options:
    -e, --environment ENV       Target environment (dev|prod) [default: dev]
    -s, --services SERVICES     Comma-separated list of services to deploy (empty for all)
    -b, --build-only           Only build images, don't deploy
    -d, --deploy-only          Only deploy, don't build images
    -f, --force-rebuild        Force rebuild all images
    -h, --help                 Show this help message

Services:
$(printf "    %s\n" "${ALL_SERVICES[@]}" | cut -d: -f1 | sort)

Examples:
    $0 -e dev                                    # Deploy all services to dev
    $0 -e prod -s "api-gateway,frontend"         # Deploy specific services to prod
    $0 -b -s "models-service"                    # Only build models-service image
    $0 -d -e prod                                # Only deploy to prod (no build)
    $0 -f -e dev                                 # Force rebuild and deploy all to dev

EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -s|--services)
            SELECTED_SERVICES="$2"
            shift 2
            ;;
        -b|--build-only)
            BUILD_IMAGES="true"
            DEPLOY_HELM="false"
            shift
            ;;
        -d|--deploy-only)
            BUILD_IMAGES="false"
            DEPLOY_HELM="true"
            shift
            ;;
        -f|--force-rebuild)
            FORCE_REBUILD="true"
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

# Validate environment
if [[ "$ENVIRONMENT" != "dev" && "$ENVIRONMENT" != "prod" ]]; then
    print_error "Environment must be 'dev' or 'prod'"
    exit 1
fi

# Set namespace based on environment
if [[ "$ENVIRONMENT" == "prod" ]]; then
    NAMESPACE="$NAMESPACE_PROD"
    VALUES_FILE="values-complete.yaml"
else
    NAMESPACE="$NAMESPACE_DEV"
    VALUES_FILE="values-dev.yaml"
fi

print_status "Starting MantraPath deployment..."
print_status "Environment: $ENVIRONMENT"
print_status "Namespace: $NAMESPACE"
print_status "Registry: $REGISTRY"

# Change to project root
cd "$PROJECT_ROOT"
PROJECT_ROOT_ABS=$(pwd)
print_status "Project root: $PROJECT_ROOT_ABS"

# Verify we're in the right directory
if [[ ! -d "backend/services" ]]; then
    print_error "Not in correct project root. Expected to find backend/services directory."
    exit 1
fi

# Function to check if Docker is running
check_docker() {
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker is not running or not accessible"
        exit 1
    fi
}

# Function to login to Vultr registry
login_registry() {
    print_status "Logging in to Vultr Container Registry..."
    if [[ -z "${VULTR_REGISTRY_PASSWORD:-}" ]]; then
        print_warning "VULTR_REGISTRY_PASSWORD not set. Please enter password:"
        read -s VULTR_REGISTRY_PASSWORD
    fi
    
    echo "$VULTR_REGISTRY_PASSWORD" | docker login https://blr.vultrcr.com/mantrapath -u "$REGISTRY_USERNAME" --password-stdin
    print_success "Successfully logged in to registry"
}

# Function to build a service image
build_service() {
    local service_name="$1"
    local dockerfile="$2"
    local context="$3"
    local image_name="$4"
    
    print_status "Building $service_name..."
    
    # Check if Dockerfile exists
    if [[ ! -f "$dockerfile" ]]; then
        print_warning "Dockerfile not found: $dockerfile"
        print_status "Creating basic Dockerfile for $service_name..."
        
        mkdir -p "$(dirname "$dockerfile")"
        cat > "$dockerfile" << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["python", "main.py"]
EOF
        print_success "Created basic Dockerfile for $service_name"
    fi
    
    # Build image
    local temp_tag="temp-$image_name:latest"
    local final_tags=(
        "$REGISTRY/$image_name:latest"
        "$REGISTRY/$image_name:$(git rev-parse --short HEAD 2>/dev/null || echo 'manual')"
    )
    
    if [[ "$ENVIRONMENT" == "prod" ]]; then
        final_tags+=("$REGISTRY/$image_name:prod")
    else
        final_tags+=("$REGISTRY/$image_name:dev")
    fi
    
    cd "$context"
    docker build -f "../$dockerfile" -t "$temp_tag" .
    
    # Tag and push all variants
    for tag in "${final_tags[@]}"; do
        print_status "Tagging: $temp_tag -> $tag"
        docker tag "$temp_tag" "$tag"
        print_status "Pushing: $tag"
        docker push "$tag"
    done
    
    # Cleanup
    docker rmi "$temp_tag" || true
    cd "$PROJECT_ROOT_ABS"
    
    print_success "Successfully built and pushed $service_name"
}

# Function to determine services to process
get_services_to_process() {
    local services_to_process=()
    
    if [[ -n "$SELECTED_SERVICES" ]]; then
        IFS=',' read -ra SELECTED_ARRAY <<< "$SELECTED_SERVICES"
        for selected in "${SELECTED_ARRAY[@]}"; do
            selected=$(echo "$selected" | xargs) # trim whitespace
            for service in "${ALL_SERVICES[@]}"; do
                if [[ "$service" == "$selected:"* ]]; then
                    services_to_process+=("$service")
                    break
                fi
            done
        done
    else
        services_to_process=("${ALL_SERVICES[@]}")
    fi
    
    printf '%s\n' "${services_to_process[@]}"
}

# Function to build all images
build_images() {
    print_status "Building Docker images..."
    
    check_docker
    login_registry
    
    local services_to_build
    readarray -t services_to_build < <(get_services_to_process)
    
    if [[ ${#services_to_build[@]} -eq 0 ]]; then
        print_warning "No services to build"
        return
    fi
    
    print_status "Building ${#services_to_build[@]} services..."
    
    for service in "${services_to_build[@]}"; do
        IFS=':' read -ra SERVICE_PARTS <<< "$service"
        local service_name="${SERVICE_PARTS[0]}"
        local dockerfile="${SERVICE_PARTS[1]}"
        local context="${SERVICE_PARTS[2]}"
        local image_name="${SERVICE_PARTS[3]}"
        
        build_service "$service_name" "$dockerfile" "$context" "$image_name"
    done
    
    print_success "All images built and pushed successfully!"
}

# Function to setup Kubernetes context
setup_k8s_context() {
    print_status "Setting up Kubernetes context for $ENVIRONMENT..."
    
    if [[ "$ENVIRONMENT" == "dev" ]]; then
        # Setup Kind cluster for development
        if ! command -v kind &> /dev/null; then
            print_status "Installing Kind..."
            curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.20.0/kind-linux-amd64
            chmod +x ./kind
            sudo mv ./kind /usr/local/bin/
        fi
        
        # Create Kind cluster if it doesn't exist
        if ! kind get clusters | grep -q "mantrapath-dev"; then
            print_status "Creating Kind cluster for development..."
            kind create cluster --name mantrapath-dev --config deployment/environments/kind-dev.yaml
        fi
        
        # Set kubectl context
        kubectl cluster-info --context kind-mantrapath-dev
    else
        # Production cluster setup would go here
        print_status "Using production Kubernetes context..."
        # Assume production cluster is already configured
    fi
}

# Function to create registry secret
create_registry_secret() {
    print_status "Creating Docker registry secret..."
    
    kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -
    
    if [[ -z "${VULTR_REGISTRY_PASSWORD:-}" ]]; then
        print_warning "VULTR_REGISTRY_PASSWORD not set. Please enter password:"
        read -s VULTR_REGISTRY_PASSWORD
    fi
    
    kubectl create secret docker-registry mantrapath-registry \
        --namespace="$NAMESPACE" \
        --docker-server=blr.vultrcr.com \
        --docker-username="$REGISTRY_USERNAME" \
        --docker-password="$VULTR_REGISTRY_PASSWORD" \
        --dry-run=client -o yaml | kubectl apply -f -
    
    print_success "Registry secret created"
}

# Function to deploy with Helm
deploy_helm() {
    print_status "Deploying with Helm..."
    
    cd deployment/helm/mantrapath
    
    # Check if values file exists
    if [[ ! -f "$VALUES_FILE" ]]; then
        print_warning "Values file not found: $VALUES_FILE"
        if [[ "$ENVIRONMENT" == "dev" ]]; then
            print_status "Using values-dev.yaml (unified) instead"
            VALUES_FILE="values-dev.yaml"
        else
            print_error "Production values file not found"
            exit 1
        fi
    fi
    
    # Update Helm dependencies
    print_status "Updating Helm dependencies..."
    helm dependency update
    
    # Validate Helm chart
    print_status "Validating Helm chart..."
    helm lint . --values "$VALUES_FILE" --strict
    
    # Deploy
    print_status "Deploying MantraPath to $ENVIRONMENT..."
    helm upgrade --install "mantrapath-$ENVIRONMENT" . \
        --namespace "$NAMESPACE" \
        --values "$VALUES_FILE" \
        --set global.registry="$REGISTRY" \
        --set global.env="$ENVIRONMENT" \
        --set global.namespace="$NAMESPACE" \
        --set-string global.labels.deployment-id="$(date -u +%Y%m%d-%H%M%S)" \
        --set-string global.labels.git-sha="$(git rev-parse --short HEAD 2>/dev/null || echo 'manual')" \
        --timeout 15m \
        --wait \
        --atomic
    
    cd "$PROJECT_ROOT_ABS"
    print_success "Helm deployment completed!"
}

# Function to verify deployment
verify_deployment() {
    print_status "Verifying deployment..."
    
    print_status "Pods in namespace $NAMESPACE:"
    kubectl get pods -n "$NAMESPACE" -l app.kubernetes.io/instance="mantrapath-$ENVIRONMENT"
    
    print_status "Services in namespace $NAMESPACE:"
    kubectl get services -n "$NAMESPACE" -l app.kubernetes.io/instance="mantrapath-$ENVIRONMENT"
    
    # Wait for pods to be ready
    print_status "Waiting for pods to be ready..."
    kubectl wait --for=condition=ready pod \
        -l app.kubernetes.io/instance="mantrapath-$ENVIRONMENT" \
        -n "$NAMESPACE" \
        --timeout=300s || print_warning "Some pods may still be starting"
    
    # Check critical services
    local critical_services=("api-gateway" "frontend")
    for service in "${critical_services[@]}"; do
        print_status "Checking $service..."
        local pod_name
        pod_name=$(kubectl get pods -n "$NAMESPACE" -l component="$service" -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")
        
        if [[ -n "$pod_name" ]]; then
            kubectl get pod "$pod_name" -n "$NAMESPACE"
            print_success "$service is running"
        else
            print_warning "$service pod not found"
        fi
    done
    
    print_success "Deployment verification completed"
}

# Function to show deployment summary
show_summary() {
    print_success "=== MantraPath Deployment Summary ==="
    echo "Environment: $ENVIRONMENT"
    echo "Namespace: $NAMESPACE"
    echo "Registry: $REGISTRY"
    echo "Timestamp: $(date)"
    echo ""
    
    if [[ "$BUILD_IMAGES" == "true" ]]; then
        echo "✅ Images built and pushed to registry"
    fi
    
    if [[ "$DEPLOY_HELM" == "true" ]]; then
        echo "✅ Services deployed to Kubernetes"
        
        if [[ "$ENVIRONMENT" == "dev" ]]; then
            echo "🌐 Access URL: http://localhost:30880"
        else
            echo "🌐 Access URL: https://mantrapath.com"
        fi
    fi
    
    echo ""
    echo "Quick commands:"
    echo "  View pods:     kubectl get pods -n $NAMESPACE"
    echo "  View services: kubectl get services -n $NAMESPACE"
    echo "  View logs:     kubectl logs -f deployment/mantrapath-$ENVIRONMENT-api-gateway -n $NAMESPACE"
    echo ""
}

# Main execution
main() {
    # Build images if requested
    if [[ "$BUILD_IMAGES" == "true" ]]; then
        build_images
    fi
    
    # Deploy with Helm if requested
    if [[ "$DEPLOY_HELM" == "true" ]]; then
        setup_k8s_context
        create_registry_secret
        deploy_helm
        verify_deployment
    fi
    
    show_summary
}

# Run main function
main "$@"
