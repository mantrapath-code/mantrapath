#!/bin/bash

# Local Deployment Script for MantraPath
# This script handles deployment to your local development cluster

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
REGISTRY="blr.vultrcr.com/mantrapath"
USERNAME="e9b950f6-81b8-4433-bb62-844d3f44b6bb"
PASSWORD="D5w5WAevjZQhcUrEQPcuuA6qgCTXzTfLHtYJ"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
ENVIRONMENT="dev"
BUILD_IMAGES=false
DEPLOY_ONLY=false
SERVICES=""
WATCH=false

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

show_help() {
    cat << EOF
🚀 MantraPath Local Deployment Script

USAGE:
    $0 [OPTIONS]

OPTIONS:
    -e, --environment ENV    Target environment (dev|prod) [default: dev]
    -b, --build             Build and push images before deployment
    -d, --deploy-only       Skip image builds, deploy only
    -s, --services LIST     Deploy specific services (comma-separated)
    -w, --watch             Watch for changes and auto-redeploy
    -h, --help              Show this help message

EXAMPLES:
    # Deploy dev environment
    $0 --environment dev

    # Build images and deploy
    $0 --build --environment dev

    # Deploy only specific services
    $0 --services api-gateway,frontend --deploy-only

    # Watch mode for development
    $0 --watch --environment dev

PREREQUISITES:
    - Docker logged in to Vultr registry
    - kubectl configured for your cluster
    - Helm 3.x installed
    - Kind cluster running (for dev)

EOF
}

parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -e|--environment)
                ENVIRONMENT="$2"
                shift 2
                ;;
            -b|--build)
                BUILD_IMAGES=true
                shift
                ;;
            -d|--deploy-only)
                DEPLOY_ONLY=true
                shift
                ;;
            -s|--services)
                SERVICES="$2"
                shift 2
                ;;
            -w|--watch)
                WATCH=true
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
}

check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi
    
    # Check kubectl
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl is not installed"
        exit 1
    fi
    
    # Check Helm
    if ! command -v helm &> /dev/null; then
        log_error "Helm is not installed"
        exit 1
    fi
    
    # Check cluster connectivity
    if ! kubectl cluster-info &> /dev/null; then
        log_error "Cannot connect to Kubernetes cluster"
        exit 1
    fi
    
    log_success "All prerequisites met"
}

login_to_registry() {
    log_info "Logging in to Vultr Container Registry..."
    echo "$PASSWORD" | docker login https://blr.vultrcr.com/mantrapath -u "$USERNAME" --password-stdin
    log_success "Successfully logged in to registry"
}

build_and_push_images() {
    if [[ "$BUILD_IMAGES" != "true" ]]; then
        return 0
    fi
    
    log_info "Building and pushing images..."
    
    # Use the build script
    "$PROJECT_ROOT/scripts/build-and-push-images.sh"
    
    log_success "Images built and pushed successfully"
}

deploy_with_helm() {
    log_info "Deploying with Helm to $ENVIRONMENT environment..."
    
    cd "$PROJECT_ROOT"
    
    # Determine values file
    local values_file="values-$ENVIRONMENT.yaml"
    if [[ "$ENVIRONMENT" == "dev" ]] && [[ -n "$SERVICES" ]]; then
        values_file="values-dev-minimal.yaml"
    fi
    
    # Deploy using the Helm deploy script
    ./deployment/helm-deploy.sh \
        --environment "$ENVIRONMENT" \
        --values-file "$values_file" \
        --timeout 15m
    
    log_success "Deployment completed successfully"
}

get_deployment_status() {
    local namespace="mantrapath-$ENVIRONMENT"
    local release="mantrapath-$ENVIRONMENT"
    
    echo "=== Deployment Status ==="
    helm status "$release" -n "$namespace" || echo "No deployment found"
    
    echo "=== Pods ==="
    kubectl get pods -n "$namespace" -l app.kubernetes.io/instance="$release"
    
    echo "=== Services ==="
    kubectl get services -n "$namespace" -l app.kubernetes.io/instance="$release"
    
    echo "=== Ingress ==="
    kubectl get ingress -n "$namespace" -l app.kubernetes.io/instance="$release" 2>/dev/null || echo "No ingress found"
}

watch_and_redeploy() {
    if [[ "$WATCH" != "true" ]]; then
        return 0
    fi
    
    log_info "Starting watch mode..."
    log_info "Monitoring changes in backend/, frontend/, and deployment/ directories"
    log_info "Press Ctrl+C to stop watching"
    
    # Use inotifywait if available, otherwise fall back to polling
    if command -v inotifywait &> /dev/null; then
        while true; do
            inotifywait -r -e modify,create,delete \
                "$PROJECT_ROOT/backend/" \
                "$PROJECT_ROOT/frontend/" \
                "$PROJECT_ROOT/deployment/" \
                2>/dev/null || true
            
            log_info "Changes detected, redeploying..."
            build_and_push_images
            deploy_with_helm
            log_success "Redeployment completed"
        done
    else
        log_warning "inotifywait not available, using polling mode"
        local last_change=$(find "$PROJECT_ROOT/backend" "$PROJECT_ROOT/frontend" "$PROJECT_ROOT/deployment" -type f -name "*.py" -o -name "*.js" -o -name "*.ts" -o -name "*.yaml" -o -name "*.yml" | xargs stat -c %Y | sort -n | tail -1)
        
        while true; do
            sleep 10
            local current_change=$(find "$PROJECT_ROOT/backend" "$PROJECT_ROOT/frontend" "$PROJECT_ROOT/deployment" -type f -name "*.py" -o -name "*.js" -o -name "*.ts" -o -name "*.yaml" -o -name "*.yml" | xargs stat -c %Y | sort -n | tail -1)
            
            if [[ "$current_change" != "$last_change" ]]; then
                log_info "Changes detected, redeploying..."
                build_and_push_images
                deploy_with_helm
                log_success "Redeployment completed"
                last_change="$current_change"
            fi
        done
    fi
}

main() {
    cd "$PROJECT_ROOT"
    
    parse_args "$@"
    
    log_info "Starting MantraPath local deployment..."
    log_info "Environment: $ENVIRONMENT"
    log_info "Build images: $BUILD_IMAGES"
    log_info "Deploy only: $DEPLOY_ONLY"
    log_info "Services: ${SERVICES:-all}"
    log_info "Watch mode: $WATCH"
    
    check_prerequisites
    
    if [[ "$DEPLOY_ONLY" != "true" ]]; then
        login_to_registry
        build_and_push_images
    fi
    
    deploy_with_helm
    get_deployment_status
    
    log_success "Local deployment completed!"
    
    if [[ "$ENVIRONMENT" == "dev" ]]; then
        log_info "Access your application at: http://localhost:30880"
        log_info "API Gateway: http://localhost:30880/api"
        log_info "Frontend: http://localhost:30880/frontend"
    fi
    
    watch_and_redeploy
}

# Handle Ctrl+C gracefully
trap 'log_info "Stopping..."; exit 0' INT

main "$@"
