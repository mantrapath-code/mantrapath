#!/bin/bash

# MantraPath Kubernetes Deployment Script
# Comprehensive deployment script with environment support, health checks, and monitoring
# Author: MantraPath Team
# Version: 2.0

set -euo pipefail

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
HELM_CHART_DIR="$SCRIPT_DIR/../helm/mantrapath"
LOG_DIR="$PROJECT_ROOT/logs/deployment"
LOG_FILE="$LOG_DIR/mantrapath-k8s-deploy-$(date +%Y%m%d_%H%M%S).log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Default configuration
ENVIRONMENT="dev"
NAMESPACE=""
RELEASE_NAME="mantrapath"
VALUES_FILE=""
DRY_RUN=false
FORCE=false
WAIT_TIMEOUT="10m"
SKIP_HEALTH_CHECK=false
SKIP_TESTS=false
VERBOSE=false
ENABLE_MONITORING=true
ENABLE_SECURITY=true
BUILD_IMAGES=false

# Supported environments
SUPPORTED_ENVS=("dev" "staging" "prod")

# Create log directory
mkdir -p "$LOG_DIR"

#=============================================================================
# Logging Functions
#=============================================================================

log() {
    echo -e "${CYAN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

log_info() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')] INFO:${NC} $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] SUCCESS:${NC} $1" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1" | tee -a "$LOG_FILE"
}

log_header() {
    echo -e "\n${BOLD}${PURPLE}=== $1 ===${NC}" | tee -a "$LOG_FILE"
}

#=============================================================================
# Utility Functions
#=============================================================================

show_usage() {
    cat << EOF
${BOLD}MantraPath Kubernetes Deployment Script v2.0${NC}

Usage: $0 [OPTIONS]

${BOLD}Options:${NC}
  -e, --env ENVIRONMENT      Target environment (dev, staging, prod) [default: dev]
  -n, --namespace NAMESPACE  Kubernetes namespace [default: mantrapath-{env}]
  -r, --release RELEASE      Helm release name [default: mantrapath]
  -f, --values-file FILE     Custom values file path
  -d, --dry-run             Perform dry run without applying changes
  -F, --force               Force deployment (delete existing release first)
  -t, --timeout DURATION   Wait timeout for deployment [default: 10m]
  -s, --skip-health-check   Skip health checks after deployment
  -T, --skip-tests          Skip running Helm tests
  -v, --verbose             Enable verbose logging
  -b, --build-images        Build and push images before deployment
  --no-monitoring           Disable monitoring components
  --no-security             Disable security policies
  -h, --help                Show this help message

${BOLD}Environment Variables:${NC}
  KUBECONFIG               Path to kubeconfig file
  HELM_DEBUG               Enable Helm debug output
  DOCKER_REGISTRY          Docker registry URL
  REGISTRY_USERNAME        Registry username
  REGISTRY_PASSWORD        Registry password

${BOLD}Examples:${NC}
  # Deploy to development environment
  $0 --env dev

  # Deploy to production with custom values
  $0 --env prod --values-file values-custom.yaml

  # Dry run deployment
  $0 --env dev --dry-run

  # Force deployment with image build
  $0 --env prod --force --build-images

${BOLD}Supported Environments:${NC}
  dev      - Development environment (minimal resources)
  staging  - Staging environment (production-like)
  prod     - Production environment (full resources)

EOF
}

validate_environment() {
    local env=$1
    for supported_env in "${SUPPORTED_ENVS[@]}"; do
        if [[ "$env" == "$supported_env" ]]; then
            return 0
        fi
    done
    log_error "Unsupported environment: $env"
    log_error "Supported environments: ${SUPPORTED_ENVS[*]}"
    exit 1
}

check_prerequisites() {
    log_header "Checking Prerequisites"
    
    # Check required commands
    local required_commands=("kubectl" "helm" "docker")
    for cmd in "${required_commands[@]}"; do
        if ! command -v "$cmd" &> /dev/null; then
            log_error "Required command '$cmd' not found"
            exit 1
        fi
        log_info "✓ $cmd is available"
    done
    
    # Check Kubernetes connection
    if ! kubectl cluster-info &> /dev/null; then
        log_error "Cannot connect to Kubernetes cluster"
        log_error "Please check your kubeconfig and cluster access"
        exit 1
    fi
    log_info "✓ Kubernetes cluster connection verified"
    
    # Check Helm version
    local helm_version
    helm_version=$(helm version --short --client | cut -d'"' -f2)
    log_info "✓ Helm version: $helm_version"
    
    # Verify Helm chart exists
    if [[ ! -f "$HELM_CHART_DIR/Chart.yaml" ]]; then
        log_error "Helm chart not found at: $HELM_CHART_DIR"
        exit 1
    fi
    log_info "✓ Helm chart found: $HELM_CHART_DIR"
}

setup_environment() {
    log_header "Setting Up Environment: $ENVIRONMENT"
    
    # Set default namespace if not provided
    if [[ -z "$NAMESPACE" ]]; then
        NAMESPACE="mantrapath-$ENVIRONMENT"
    fi
    
    # Set default values file if not provided
    if [[ -z "$VALUES_FILE" ]]; then
        VALUES_FILE="$HELM_CHART_DIR/values-$ENVIRONMENT.yaml"
    fi
    
    # Verify values file exists
    if [[ ! -f "$VALUES_FILE" ]]; then
        log_error "Values file not found: $VALUES_FILE"
        exit 1
    fi
    
    log_info "Environment: $ENVIRONMENT"
    log_info "Namespace: $NAMESPACE"
    log_info "Release: $RELEASE_NAME"
    log_info "Values file: $VALUES_FILE"
    
    # Create namespace if it doesn't exist
    if ! kubectl get namespace "$NAMESPACE" &> /dev/null; then
        log_info "Creating namespace: $NAMESPACE"
        kubectl create namespace "$NAMESPACE"
        
        # Label namespace for monitoring and security
        kubectl label namespace "$NAMESPACE" name="$NAMESPACE" --overwrite
        kubectl label namespace "$NAMESPACE" environment="$ENVIRONMENT" --overwrite
        kubectl label namespace "$NAMESPACE" managed-by="helm" --overwrite
    else
        log_info "✓ Namespace '$NAMESPACE' already exists"
    fi
}

build_and_push_images() {
    if [[ "$BUILD_IMAGES" != "true" ]]; then
        return 0
    fi
    
    log_header "Building and Pushing Images"
    
    # Check if we have registry credentials
    if [[ -z "${DOCKER_REGISTRY:-}" ]]; then
        log_warning "DOCKER_REGISTRY not set, skipping image build"
        return 0
    fi
    
    # Login to registry if credentials provided
    if [[ -n "${REGISTRY_USERNAME:-}" && -n "${REGISTRY_PASSWORD:-}" ]]; then
        echo "$REGISTRY_PASSWORD" | docker login "$DOCKER_REGISTRY" -u "$REGISTRY_USERNAME" --password-stdin
        log_info "✓ Logged into registry: $DOCKER_REGISTRY"
    fi
    
    # Use the CI build script if available
    local build_script="$PROJECT_ROOT/ci/build-push-service.sh"
    if [[ -f "$build_script" ]]; then
        log_info "Using CI build script for image building"
        # Build all services (this would need to be customized based on your services)
        for service in api-gateway translation-service models-service; do
            log_info "Building service: $service"
            bash "$build_script" "$service" || log_warning "Failed to build $service"
        done
    else
        log_warning "CI build script not found, skipping image build"
    fi
}

lint_and_validate_chart() {
    log_header "Linting and Validating Helm Chart"
    
    # Helm lint
    log_info "Running Helm lint..."
    if helm lint "$HELM_CHART_DIR" --values "$VALUES_FILE"; then
        log_success "✓ Helm lint passed"
    else
        log_error "Helm lint failed"
        exit 1
    fi
    
    # Helm template validation
    log_info "Validating Helm templates..."
    local template_output
    template_output=$(mktemp)
    
    if helm template "$RELEASE_NAME" "$HELM_CHART_DIR" \
        --namespace "$NAMESPACE" \
        --values "$VALUES_FILE" > "$template_output"; then
        
        # Validate with kubectl dry-run
        if kubectl apply --dry-run=client -f "$template_output" &> /dev/null; then
            log_success "✓ Template validation passed"
        else
            log_error "Template validation failed with kubectl"
            exit 1
        fi
    else
        log_error "Helm template generation failed"
        exit 1
    fi
    
    rm -f "$template_output"
}

deploy_helm_chart() {
    log_header "Deploying Helm Chart"
    
    local helm_args=()
    helm_args+=("upgrade" "--install" "$RELEASE_NAME" "$HELM_CHART_DIR")
    helm_args+=("--namespace" "$NAMESPACE")
    helm_args+=("--values" "$VALUES_FILE")
    helm_args+=("--timeout" "$WAIT_TIMEOUT")
    helm_args+=("--wait")
    helm_args+=("--create-namespace")
    
    if [[ "$DRY_RUN" == "true" ]]; then
        helm_args+=("--dry-run")
        log_info "Performing dry run deployment..."
    fi
    
    if [[ "$VERBOSE" == "true" ]]; then
        helm_args+=("--debug")
    fi
    
    if [[ "$FORCE" == "true" ]]; then
        log_warning "Force flag enabled - checking if release exists..."
        if helm list -n "$NAMESPACE" | grep -q "$RELEASE_NAME"; then
            log_warning "Deleting existing release: $RELEASE_NAME"
            helm uninstall "$RELEASE_NAME" --namespace "$NAMESPACE" --wait
        fi
    fi
    
    # Add environment-specific configurations
    helm_args+=("--set" "global.env=$ENVIRONMENT")
    helm_args+=("--set" "global.namespace=$NAMESPACE")
    
    log_info "Executing Helm deployment..."
    log_info "Command: helm ${helm_args[*]}"
    
    if helm "${helm_args[@]}"; then
        if [[ "$DRY_RUN" != "true" ]]; then
            log_success "✓ Deployment completed successfully"
        else
            log_success "✓ Dry run completed successfully"
        fi
    else
        log_error "Helm deployment failed"
        exit 1
    fi
}

wait_for_rollout() {
    if [[ "$DRY_RUN" == "true" || "$SKIP_HEALTH_CHECK" == "true" ]]; then
        return 0
    fi
    
    log_header "Waiting for Rollout to Complete"
    
    # Get all deployments in the namespace
    local deployments
    deployments=$(kubectl get deployments -n "$NAMESPACE" -o name 2>/dev/null || true)
    
    if [[ -z "$deployments" ]]; then
        log_warning "No deployments found to wait for"
        return 0
    fi
    
    # Wait for each deployment
    while IFS= read -r deployment; do
        if [[ -n "$deployment" ]]; then
            log_info "Waiting for $deployment rollout..."
            if kubectl rollout status "$deployment" -n "$NAMESPACE" --timeout="$WAIT_TIMEOUT"; then
                log_success "✓ $deployment rollout completed"
            else
                log_error "$deployment rollout failed or timed out"
                exit 1
            fi
        fi
    done <<< "$deployments"
    
    # Wait for StatefulSets
    local statefulsets
    statefulsets=$(kubectl get statefulsets -n "$NAMESPACE" -o name 2>/dev/null || true)
    
    while IFS= read -r statefulset; do
        if [[ -n "$statefulset" ]]; then
            log_info "Waiting for $statefulset to be ready..."
            kubectl wait "$statefulset" -n "$NAMESPACE" --for=condition=Ready --timeout="$WAIT_TIMEOUT" || {
                log_error "$statefulset failed to become ready"
                exit 1
            }
            log_success "✓ $statefulset is ready"
        fi
    done <<< "$statefulsets"
}

run_health_checks() {
    if [[ "$DRY_RUN" == "true" || "$SKIP_HEALTH_CHECK" == "true" ]]; then
        return 0
    fi
    
    log_header "Running Health Checks"
    
    # Check pod status
    log_info "Checking pod status..."
    kubectl get pods -n "$NAMESPACE" -o wide
    
    # Check failed pods
    local failed_pods
    failed_pods=$(kubectl get pods -n "$NAMESPACE" --field-selector=status.phase!=Running,status.phase!=Succeeded -o name 2>/dev/null || true)
    
    if [[ -n "$failed_pods" ]]; then
        log_warning "Found failed/pending pods:"
        echo "$failed_pods"
        
        # Show logs for failed pods
        while IFS= read -r pod; do
            if [[ -n "$pod" ]]; then
                log_warning "Logs for $pod:"
                kubectl logs "$pod" -n "$NAMESPACE" --tail=20 || true
            fi
        done <<< "$failed_pods"
    fi
    
    # Check service endpoints
    log_info "Checking service endpoints..."
    kubectl get endpoints -n "$NAMESPACE"
    
    # Basic connectivity tests
    log_info "Running basic connectivity tests..."
    
    # Test internal service connectivity (if api-gateway is available)
    local api_gateway_pod
    api_gateway_pod=$(kubectl get pods -n "$NAMESPACE" -l app.kubernetes.io/name=api-gateway -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || true)
    
    if [[ -n "$api_gateway_pod" ]]; then
        log_info "Testing API Gateway health endpoint..."
        if kubectl exec -n "$NAMESPACE" "$api_gateway_pod" -- wget -q -O- http://localhost:8000/health 2>/dev/null; then
            log_success "✓ API Gateway health check passed"
        else
            log_warning "API Gateway health check failed"
        fi
    fi
}

run_helm_tests() {
    if [[ "$DRY_RUN" == "true" || "$SKIP_TESTS" == "true" ]]; then
        return 0
    fi
    
    log_header "Running Helm Tests"
    
    if helm test "$RELEASE_NAME" --namespace "$NAMESPACE" --timeout "$WAIT_TIMEOUT"; then
        log_success "✓ Helm tests passed"
    else
        log_error "Helm tests failed"
        # Don't exit on test failure in non-production environments
        if [[ "$ENVIRONMENT" == "prod" ]]; then
            exit 1
        else
            log_warning "Continuing despite test failures in $ENVIRONMENT environment"
        fi
    fi
}

show_deployment_status() {
    if [[ "$DRY_RUN" == "true" ]]; then
        return 0
    fi
    
    log_header "Deployment Status"
    
    # Helm release status
    log_info "Helm Release Status:"
    helm status "$RELEASE_NAME" --namespace "$NAMESPACE"
    
    # Resource summary
    log_info "Resource Summary:"
    echo "Pods:"
    kubectl get pods -n "$NAMESPACE"
    echo
    echo "Services:"
    kubectl get services -n "$NAMESPACE"
    echo
    echo "Ingresses:"
    kubectl get ingress -n "$NAMESPACE" 2>/dev/null || echo "No ingresses found"
    echo
    
    # Get external access information
    local ingress_info
    ingress_info=$(kubectl get ingress -n "$NAMESPACE" -o jsonpath='{.items[0].status.loadBalancer.ingress[0].ip}' 2>/dev/null || true)
    
    if [[ -n "$ingress_info" ]]; then
        log_success "✓ Application is accessible at: http://$ingress_info"
    else
        log_info "To access the application, run:"
        log_info "  kubectl port-forward -n $NAMESPACE svc/mantrapath-frontend 3000:3000"
        log_info "  kubectl port-forward -n $NAMESPACE svc/mantrapath-api-gateway 8000:8000"
    fi
}

cleanup_on_exit() {
    local exit_code=$?
    if [[ $exit_code -ne 0 ]]; then
        log_error "Deployment failed with exit code: $exit_code"
        log_info "Log file: $LOG_FILE"
        
        if [[ "$DRY_RUN" != "true" ]]; then
            log_info "To debug, run:"
            log_info "  kubectl get pods -n $NAMESPACE"
            log_info "  kubectl describe pods -n $NAMESPACE"
            log_info "  helm status $RELEASE_NAME -n $NAMESPACE"
        fi
    fi
}

#=============================================================================
# Main Function
#=============================================================================

main() {
    # Set up exit trap
    trap cleanup_on_exit EXIT
    
    log_header "MantraPath Kubernetes Deployment v2.0"
    log_info "Started at: $(date)"
    log_info "Log file: $LOG_FILE"
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -e|--env)
                ENVIRONMENT="$2"
                shift 2
                ;;
            -n|--namespace)
                NAMESPACE="$2"
                shift 2
                ;;
            -r|--release)
                RELEASE_NAME="$2"
                shift 2
                ;;
            -f|--values-file)
                VALUES_FILE="$2"
                shift 2
                ;;
            -d|--dry-run)
                DRY_RUN=true
                shift
                ;;
            -F|--force)
                FORCE=true
                shift
                ;;
            -t|--timeout)
                WAIT_TIMEOUT="$2"
                shift 2
                ;;
            -s|--skip-health-check)
                SKIP_HEALTH_CHECK=true
                shift
                ;;
            -T|--skip-tests)
                SKIP_TESTS=true
                shift
                ;;
            -v|--verbose)
                VERBOSE=true
                set -x
                shift
                ;;
            -b|--build-images)
                BUILD_IMAGES=true
                shift
                ;;
            --no-monitoring)
                ENABLE_MONITORING=false
                shift
                ;;
            --no-security)
                ENABLE_SECURITY=false
                shift
                ;;
            -h|--help)
                show_usage
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done
    
    # Validate environment
    validate_environment "$ENVIRONMENT"
    
    # Execute deployment steps
    check_prerequisites
    setup_environment
    build_and_push_images
    lint_and_validate_chart
    deploy_helm_chart
    wait_for_rollout
    run_health_checks
    run_helm_tests
    show_deployment_status
    
    log_success "🎉 Deployment completed successfully!"
    log_info "Environment: $ENVIRONMENT"
    log_info "Namespace: $NAMESPACE"
    log_info "Release: $RELEASE_NAME"
    log_info "Completed at: $(date)"
}

# Execute main function if script is run directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi