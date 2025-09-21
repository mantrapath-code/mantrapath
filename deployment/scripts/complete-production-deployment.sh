#!/bin/bash

# MantraPath Complete Production Deployment Script
# This script handles the complete production deployment with persistent storage

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
REGISTRY="blr.vultrcr.com/mantrapath"
REGISTRY_USERNAME="e9b950f6-81b8-4433-bb62-844d3f44b6bb"
NAMESPACE_DEV="mantrapath-dev"
NAMESPACE_PROD="mantrapath-prod"
PROJECT_ROOT="../.."
HELM_CHART_PATH="../helm/mantrapath"

# Default values
ENVIRONMENT="dev"
BUILD_IMAGES="true"
DEPLOY_HELM="true"
SETUP_STORAGE="true"
FORCE_REBUILD="false"
SELECTED_SERVICES=""
DRY_RUN="false"

# All services with their configurations
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

print_header() {
    echo -e "${PURPLE}=== $1 ===${NC}"
}

print_step() {
    echo -e "${CYAN}[STEP]${NC} $1"
}

# Function to show usage
usage() {
    cat << EOF
MantraPath Complete Production Deployment Script

Usage: $0 [OPTIONS]

Options:
    -e, --environment ENV       Target environment (dev|prod) [default: dev]
    -s, --services SERVICES     Comma-separated list of services to deploy (empty for all)
    -b, --build-only           Only build images, don't deploy
    -d, --deploy-only          Only deploy, don't build images
    -n, --no-storage           Skip storage setup
    -f, --force-rebuild        Force rebuild all images
    --dry-run                  Show what would be done without executing
    -h, --help                 Show this help message

Deployment Phases:
    1. Pre-flight checks (Docker, kubectl, Helm, registry)
    2. Persistent storage setup
    3. Image building and registry push
    4. Helm deployment with persistence
    5. Service verification and health checks
    6. Post-deployment validation

Examples:
    $0 -e prod                              # Full production deployment
    $0 -e dev -s "api-gateway,models-service" # Deploy specific services to dev
    $0 -b -f                               # Force rebuild all images only
    $0 -d -e prod                          # Deploy to prod (no build)
    $0 --dry-run -e prod                   # Show what would be deployed

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
            SETUP_STORAGE="false"
            shift
            ;;
        -d|--deploy-only)
            BUILD_IMAGES="false"
            DEPLOY_HELM="true"
            shift
            ;;
        -n|--no-storage)
            SETUP_STORAGE="false"
            shift
            ;;
        -f|--force-rebuild)
            FORCE_REBUILD="true"
            shift
            ;;
        --dry-run)
            DRY_RUN="true"
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

# Set namespace and values file based on environment
if [[ "$ENVIRONMENT" == "prod" ]]; then
    NAMESPACE="$NAMESPACE_PROD"
    VALUES_FILE="values-complete.yaml"
else
    NAMESPACE="$NAMESPACE_DEV"
    VALUES_FILE="values-dev.yaml"
fi

# Display deployment configuration
print_header "MantraPath Production Deployment Configuration"
echo "Environment: $ENVIRONMENT"
echo "Namespace: $NAMESPACE"
echo "Registry: $REGISTRY"
echo "Values File: $VALUES_FILE"
echo "Build Images: $BUILD_IMAGES"
echo "Deploy Helm: $DEPLOY_HELM"
echo "Setup Storage: $SETUP_STORAGE"
echo "Force Rebuild: $FORCE_REBUILD"
echo "Dry Run: $DRY_RUN"
echo ""

if [[ "$DRY_RUN" == "true" ]]; then
    print_warning "DRY RUN MODE - No actual changes will be made"
    echo ""
fi

# Change to project root
cd "$PROJECT_ROOT"
PROJECT_ROOT_ABS=$(pwd)
print_status "Project root: $PROJECT_ROOT_ABS"

# Verify we're in the right directory
if [[ ! -d "backend/services" ]]; then
    print_error "Not in correct project root. Expected to find backend/services directory."
    exit 1
fi

# Function to check prerequisites
check_prerequisites() {
    print_step "Checking prerequisites..."
    
    local errors=0
    
    # Check Docker
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker is not running or not accessible"
        ((errors++))
    else
        print_success "Docker is running"
    fi
    
    # Check kubectl
    if ! kubectl cluster-info >/dev/null 2>&1; then
        print_error "kubectl is not configured or cluster is not accessible"
        ((errors++))
    else
        print_success "Kubernetes cluster is accessible"
    fi
    
    # Check Helm
    if ! command -v helm >/dev/null 2>&1; then
        print_error "Helm is not installed"
        ((errors++))
    else
        print_success "Helm is available"
    fi
    
    # Check registry credentials
    if [[ -z "${VULTR_REGISTRY_PASSWORD:-}" ]]; then
        print_error "VULTR_REGISTRY_PASSWORD environment variable is not set"
        ((errors++))
    else
        print_success "Registry credentials are available"
    fi
    
    if [[ $errors -gt 0 ]]; then
        print_error "Prerequisites check failed with $errors errors"
        return 1
    fi
    
    print_success "All prerequisites satisfied"
    return 0
}

# Function to setup persistent storage
setup_persistent_storage() {
    if [[ "$SETUP_STORAGE" != "true" ]]; then
        print_status "Skipping storage setup"
        return 0
    fi
    
    print_step "Setting up persistent storage infrastructure..."
    
    if [[ "$DRY_RUN" == "true" ]]; then
        print_status "[DRY RUN] Would create namespace: $NAMESPACE"
        print_status "[DRY RUN] Would apply persistent volume templates"
        print_status "[DRY RUN] Would run storage initialization job"
        return 0
    fi
    
    # Create namespace if it doesn't exist
    kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -
    print_success "Namespace $NAMESPACE ready"
    
    # Apply persistent volume configurations
    cd deployment/helm/mantrapath
    
    # Create storage class if needed (for Vultr)
    cat << EOF | kubectl apply -f -
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: vultr-block-storage-hdd
provisioner: block.csi.vultr.com
parameters:
  type: "hdd"
allowVolumeExpansion: true
volumeBindingMode: WaitForFirstConsumer
EOF
    
    print_success "Storage class configured"
    
    # Apply persistent volume templates
    helm template mantrapath-storage . \
        --values "$VALUES_FILE" \
        --set global.env="$ENVIRONMENT" \
        --set global.namespace="$NAMESPACE" \
        --show-only templates/persistent-volumes.yaml | \
        kubectl apply -f -
    
    print_success "Persistent volumes configured"
    
    # Wait for storage initialization job to complete
    print_status "Waiting for storage initialization..."
    kubectl wait --for=condition=complete job/mantrapath-$ENVIRONMENT-init-storage \
        -n "$NAMESPACE" --timeout=300s || print_warning "Storage init job may still be running"
    
    cd "$PROJECT_ROOT_ABS"
    print_success "Persistent storage setup completed"
}

# Function to build and push images
build_and_push_images() {
    if [[ "$BUILD_IMAGES" != "true" ]]; then
        print_status "Skipping image building"
        return 0
    fi
    
    print_step "Building and pushing Docker images..."
    
    # Login to registry
    if [[ "$DRY_RUN" != "true" ]]; then
        echo "$VULTR_REGISTRY_PASSWORD" | docker login https://blr.vultrcr.com/mantrapath -u "$REGISTRY_USERNAME" --password-stdin
        print_success "Logged in to Vultr Container Registry"
    fi
    
    # Determine services to build
    local services_to_build=()
    if [[ -n "$SELECTED_SERVICES" ]]; then
        IFS=',' read -ra SELECTED_ARRAY <<< "$SELECTED_SERVICES"
        for selected in "${SELECTED_ARRAY[@]}"; do
            selected=$(echo "$selected" | xargs) # trim whitespace
            for service in "${ALL_SERVICES[@]}"; do
                if [[ "$service" == "$selected:"* ]]; then
                    services_to_build+=("$service")
                    break
                fi
            done
        done
    else
        services_to_build=("${ALL_SERVICES[@]}")
    fi
    
    if [[ ${#services_to_build[@]} -eq 0 ]]; then
        print_warning "No services to build"
        return 0
    fi
    
    print_status "Building ${#services_to_build[@]} services..."
    
    # Build each service
    local built_count=0
    local failed_count=0
    
    for service in "${services_to_build[@]}"; do
        IFS=':' read -ra SERVICE_PARTS <<< "$service"
        local service_name="${SERVICE_PARTS[0]}"
        local dockerfile="${SERVICE_PARTS[1]}"
        local context="${SERVICE_PARTS[2]}"
        local image_name="${SERVICE_PARTS[3]}"
        
        print_status "Building $service_name..."
        
        if [[ "$DRY_RUN" == "true" ]]; then
            print_status "[DRY RUN] Would build: $REGISTRY/$image_name:latest"
            ((built_count++))
            continue
        fi
        
        # Check if Dockerfile exists
        if [[ ! -f "$dockerfile" ]]; then
            print_error "Dockerfile not found: $dockerfile"
            ((failed_count++))
            continue
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
        if docker build -f "../$dockerfile" -t "$temp_tag" . >/dev/null 2>&1; then
            # Tag and push all variants
            for tag in "${final_tags[@]}"; do
                docker tag "$temp_tag" "$tag"
                if docker push "$tag" >/dev/null 2>&1; then
                    print_success "Pushed: $tag"
                else
                    print_error "Failed to push: $tag"
                    ((failed_count++))
                fi
            done
            
            # Cleanup temp image
            docker rmi "$temp_tag" >/dev/null 2>&1 || true
            ((built_count++))
            
            print_success "✅ $service_name built and pushed"
        else
            print_error "❌ Failed to build $service_name"
            ((failed_count++))
        fi
        
        cd "$PROJECT_ROOT_ABS"
    done
    
    print_success "Image building completed: $built_count built, $failed_count failed"
    
    if [[ $failed_count -gt 0 ]]; then
        print_warning "Some images failed to build. Deployment may have issues."
    fi
}

# Function to deploy with Helm
deploy_with_helm() {
    if [[ "$DEPLOY_HELM" != "true" ]]; then
        print_status "Skipping Helm deployment"
        return 0
    fi
    
    print_step "Deploying with Helm..."
    
    cd deployment/helm/mantrapath
    
    # Create registry secret
    if [[ "$DRY_RUN" != "true" ]]; then
        kubectl create secret docker-registry mantrapath-registry \
            --namespace="$NAMESPACE" \
            --docker-server=blr.vultrcr.com \
            --docker-username="$REGISTRY_USERNAME" \
            --docker-password="$VULTR_REGISTRY_PASSWORD" \
            --dry-run=client -o yaml | kubectl apply -f -
        print_success "Registry secret created"
    fi
    
    # Update Helm dependencies
    print_status "Updating Helm dependencies..."
    if [[ "$DRY_RUN" != "true" ]]; then
        helm dependency update >/dev/null 2>&1
    fi
    
    # Validate Helm chart
    print_status "Validating Helm chart..."
    helm lint . --values "$VALUES_FILE" --strict
    
    if [[ "$DRY_RUN" == "true" ]]; then
        print_status "[DRY RUN] Would deploy with Helm:"
        print_status "  Release: mantrapath-$ENVIRONMENT"
        print_status "  Namespace: $NAMESPACE"
        print_status "  Values: $VALUES_FILE"
        cd "$PROJECT_ROOT_ABS"
        return 0
    fi
    
    # Deploy with Helm
    print_status "Deploying MantraPath to $ENVIRONMENT..."
    helm upgrade --install "mantrapath-$ENVIRONMENT" . \
        --namespace "$NAMESPACE" \
        --values "$VALUES_FILE" \
        --set global.registry="$REGISTRY" \
        --set global.env="$ENVIRONMENT" \
        --set global.namespace="$NAMESPACE" \
        --set persistence.enabled=true \
        --set-string global.labels.deployment-id="$(date -u +%Y%m%d-%H%M%S)" \
        --set-string global.labels.git-sha="$(git rev-parse --short HEAD 2>/dev/null || echo 'manual')" \
        --timeout 20m \
        --wait \
        --atomic
    
    cd "$PROJECT_ROOT_ABS"
    print_success "Helm deployment completed successfully!"
}

# Function to verify deployment
verify_deployment() {
    if [[ "$DEPLOY_HELM" != "true" || "$DRY_RUN" == "true" ]]; then
        return 0
    fi
    
    print_step "Verifying deployment..."
    
    # Check pod status
    print_status "Checking pod status..."
    kubectl get pods -n "$NAMESPACE" -l app.kubernetes.io/instance="mantrapath-$ENVIRONMENT"
    
    # Check persistent volumes
    print_status "Checking persistent volumes..."
    kubectl get pvc -n "$NAMESPACE"
    
    # Wait for pods to be ready
    print_status "Waiting for pods to be ready..."
    kubectl wait --for=condition=ready pod \
        -l app.kubernetes.io/instance="mantrapath-$ENVIRONMENT" \
        -n "$NAMESPACE" \
        --timeout=600s || print_warning "Some pods may still be starting"
    
    # Check services
    print_status "Checking services..."
    kubectl get services -n "$NAMESPACE" -l app.kubernetes.io/instance="mantrapath-$ENVIRONMENT"
    
    print_success "Deployment verification completed"
}

# Function to run post-deployment tests
run_post_deployment_tests() {
    if [[ "$DEPLOY_HELM" != "true" || "$DRY_RUN" == "true" ]]; then
        return 0
    fi
    
    print_step "Running post-deployment tests..."
    
    # Test critical services
    local critical_services=("api-gateway" "models-service" "frontend")
    
    for service in "${critical_services[@]}"; do
        print_status "Testing $service health endpoint..."
        
        # Port forward and test
        local port="${service_ports[$service]:-8000}"
        kubectl port-forward "svc/mantrapath-$ENVIRONMENT-$service" "$port:$port" -n "$NAMESPACE" >/dev/null 2>&1 &
        local pf_pid=$!
        
        sleep 3
        
        if curl -s --max-time 10 "http://localhost:$port/health" >/dev/null 2>&1; then
            print_success "✅ $service is healthy"
        else
            print_warning "⚠️ $service health check failed"
        fi
        
        kill $pf_pid 2>/dev/null || true
    done
    
    # Test persistent storage
    print_status "Testing persistent storage..."
    
    # Create a test pod to verify storage
    cat << EOF | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: storage-test
  namespace: $NAMESPACE
spec:
  containers:
  - name: test
    image: busybox:latest
    command: ["sleep", "300"]
    volumeMounts:
    - name: app-data
      mountPath: /test/app-data
    - name: models-data
      mountPath: /test/models
    - name: media-data
      mountPath: /test/media
    - name: logs-data
      mountPath: /test/logs
  volumes:
  - name: app-data
    persistentVolumeClaim:
      claimName: mantrapath-$ENVIRONMENT-app-data-pvc
  - name: models-data
    persistentVolumeClaim:
      claimName: mantrapath-$ENVIRONMENT-models-pvc
  - name: media-data
    persistentVolumeClaim:
      claimName: mantrapath-$ENVIRONMENT-media-pvc
  - name: logs-data
    persistentVolumeClaim:
      claimName: mantrapath-$ENVIRONMENT-logs-pvc
  restartPolicy: Never
EOF
    
    # Wait for test pod and run storage tests
    kubectl wait --for=condition=ready pod/storage-test -n "$NAMESPACE" --timeout=60s
    
    # Test write/read operations
    kubectl exec storage-test -n "$NAMESPACE" -- sh -c "echo 'test' > /test/app-data/test.txt && cat /test/app-data/test.txt" >/dev/null 2>&1
    if [[ $? -eq 0 ]]; then
        print_success "✅ Persistent storage is working"
    else
        print_warning "⚠️ Persistent storage test failed"
    fi
    
    # Cleanup test pod
    kubectl delete pod storage-test -n "$NAMESPACE" --ignore-not-found
    
    print_success "Post-deployment tests completed"
}

# Function to show deployment summary
show_deployment_summary() {
    print_header "Deployment Summary"
    
    echo "Environment: $ENVIRONMENT"
    echo "Namespace: $NAMESPACE"
    echo "Registry: $REGISTRY"
    echo "Timestamp: $(date)"
    echo ""
    
    if [[ "$DRY_RUN" == "true" ]]; then
        echo "🔍 DRY RUN COMPLETED - No actual changes were made"
        echo ""
        echo "What would have been done:"
        if [[ "$SETUP_STORAGE" == "true" ]]; then
            echo "  ✓ Persistent storage setup"
        fi
        if [[ "$BUILD_IMAGES" == "true" ]]; then
            echo "  ✓ Docker image building and push"
        fi
        if [[ "$DEPLOY_HELM" == "true" ]]; then
            echo "  ✓ Helm deployment with persistence"
        fi
        echo ""
        echo "To execute for real, run the same command without --dry-run"
    else
        echo "🎉 DEPLOYMENT COMPLETED SUCCESSFULLY!"
        echo ""
        
        if [[ "$SETUP_STORAGE" == "true" ]]; then
            echo "✅ Persistent storage configured"
        fi
        if [[ "$BUILD_IMAGES" == "true" ]]; then
            echo "✅ Images built and pushed to registry"
        fi
        if [[ "$DEPLOY_HELM" == "true" ]]; then
            echo "✅ Services deployed to Kubernetes"
        fi
        
        echo ""
        echo "🌐 Access Information:"
        if [[ "$ENVIRONMENT" == "dev" ]]; then
            echo "  Frontend: http://localhost:30880"
            echo "  API Gateway: http://localhost:30800"
        else
            echo "  Frontend: https://mantrapath.com"
            echo "  API Gateway: https://api.mantrapath.com"
        fi
        
        echo ""
        echo "📊 Persistent Storage:"
        echo "  App Data: /data/mantrapath"
        echo "  Models: /data/models"
        echo "  Media: /data/media"
        echo "  Logs: /data/logs"
        
        echo ""
        echo "🔧 Management Commands:"
        echo "  View pods:     kubectl get pods -n $NAMESPACE"
        echo "  View storage:  kubectl get pvc -n $NAMESPACE"
        echo "  View logs:     kubectl logs -f deployment/mantrapath-$ENVIRONMENT-api-gateway -n $NAMESPACE"
        echo "  Monitor:       ./monitor-services.sh -e $ENVIRONMENT -w"
    fi
    
    echo ""
}

# Main execution function
main() {
    print_header "MantraPath Complete Production Deployment"
    
    # Check prerequisites
    if ! check_prerequisites; then
        exit 1
    fi
    
    # Setup persistent storage
    setup_persistent_storage
    
    # Build and push images
    build_and_push_images
    
    # Deploy with Helm
    deploy_with_helm
    
    # Verify deployment
    verify_deployment
    
    # Run post-deployment tests
    run_post_deployment_tests
    
    # Show summary
    show_deployment_summary
    
    print_success "🚀 MantraPath deployment pipeline completed!"
}

# Handle Ctrl+C gracefully
trap 'echo -e "\n${YELLOW}Deployment interrupted by user${NC}"; exit 130' INT

# Run main function
main "$@"
