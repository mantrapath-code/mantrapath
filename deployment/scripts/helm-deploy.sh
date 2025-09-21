#!/bin/bash

# MantraPath Helm Deployment Script
# Comprehensive deployment script for all environments with health checks

set -euo pipefail

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
HELM_CHART_DIR="$SCRIPT_DIR/helm/mantrapath"
LOG_FILE="/tmp/mantrapath-helm-deploy-$(date +%Y%m%d_%H%M%S).log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Default values
ENVIRONMENT="dev"
NAMESPACE=""
RELEASE_NAME=""
VALUES_FILE=""
DRY_RUN=false
FORCE=false
WAIT_TIMEOUT="10m"
SKIP_HEALTH_CHECK=false
VERBOSE=false

# Logging functions
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

# Help function
show_help() {
    cat << EOF
🚀 MantraPath Helm Deployment Script

USAGE:
    $0 [OPTIONS]

OPTIONS:
    -e, --environment ENV    Target environment (dev|prod) [default: dev]
    -n, --namespace NS       Kubernetes namespace [default: mantrapath-ENV]
    -r, --release NAME       Helm release name [default: mantrapath-ENV]
    -f, --values-file FILE   Custom values file [default: values-ENV.yaml]
    -d, --dry-run           Perform dry run without actual deployment
    -F, --force             Force deployment even if validation fails
    -t, --timeout DURATION  Wait timeout for deployment [default: 10m]
    -s, --skip-health       Skip health checks after deployment
    -v, --verbose           Enable verbose output
    -h, --help              Show this help message

EXAMPLES:
    # Deploy to development
    $0 --environment dev

    # Deploy to production with custom timeout
    $0 --environment prod --timeout 15m

    # Dry run for production
    $0 --environment prod --dry-run

    # Deploy with custom values file
    $0 --environment dev --values-file custom-values.yaml

ENVIRONMENT SETUP:
    Before running, ensure:
    1. kubectl is configured for target cluster
    2. Helm 3.x is installed
    3. Required secrets are available
    4. Ingress controller is running (nginx recommended)
    5. cert-manager is installed (for production TLS)

EOF
}

# Parse command line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -e|--environment)
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
            -s|--skip-health)
                SKIP_HEALTH_CHECK=true
                shift
                ;;
            -v|--verbose)
                VERBOSE=true
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

    # Set defaults based on environment
    if [[ -z "$NAMESPACE" ]]; then
        NAMESPACE="mantrapath-$ENVIRONMENT"
    fi

    if [[ -z "$RELEASE_NAME" ]]; then
        RELEASE_NAME="mantrapath-$ENVIRONMENT"
    fi

    if [[ -z "$VALUES_FILE" ]]; then
        VALUES_FILE="values-$ENVIRONMENT.yaml"
    fi
}

# Validate environment and prerequisites
validate_environment() {
    log_info "🔍 Validating environment and prerequisites..."

    # Check if environment is valid
    if [[ ! "$ENVIRONMENT" =~ ^(dev|prod)$ ]]; then
        log_error "Invalid environment: $ENVIRONMENT. Must be 'dev' or 'prod'"
        exit 1
    fi

    # Check if kubectl is available and configured
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl is not installed or not in PATH"
        exit 1
    fi

    # Check kubectl connectivity
    if ! kubectl cluster-info &> /dev/null; then
        log_error "kubectl cannot connect to cluster. Check your kubeconfig"
        exit 1
    fi

    # Check if Helm is available
    if ! command -v helm &> /dev/null; then
        log_error "Helm is not installed or not in PATH"
        exit 1
    fi

    # Check Helm version
    HELM_VERSION=$(helm version --short --client | grep -o 'v[0-9]\+\.[0-9]\+\.[0-9]\+')
    log_info "Using Helm version: $HELM_VERSION"

    # Check if chart directory exists
    if [[ ! -d "$HELM_CHART_DIR" ]]; then
        log_error "Helm chart directory not found: $HELM_CHART_DIR"
        exit 1
    fi

    # Check if values file exists
    VALUES_PATH="$HELM_CHART_DIR/$VALUES_FILE"
    if [[ ! -f "$VALUES_PATH" ]]; then
        log_error "Values file not found: $VALUES_PATH"
        exit 1
    fi

    log_success "Environment validation completed"
}

# Lint Helm chart
lint_chart() {
    log_info "🔍 Linting Helm chart..."

    cd "$HELM_CHART_DIR"

    if helm lint . --values "$VALUES_FILE" --strict; then
        log_success "Helm chart lint passed"
    else
        log_error "Helm chart lint failed"
        if [[ "$FORCE" != "true" ]]; then
            exit 1
        else
            log_warning "Continuing despite lint failures (--force enabled)"
        fi
    fi
}

# Create or update namespace
setup_namespace() {
    log_info "📁 Setting up namespace: $NAMESPACE"

    # Create namespace if it doesn't exist
    kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -

    # Label namespace
    kubectl label namespace "$NAMESPACE" environment="$ENVIRONMENT" --overwrite
    kubectl label namespace "$NAMESPACE" managed-by=helm --overwrite

    log_success "Namespace $NAMESPACE is ready"
}

# Deploy secrets
deploy_secrets() {
    log_info "🔐 Deploying secrets..."

    # For production, secrets should be managed externally (e.g., external-secrets, sealed-secrets)
    # This is a basic implementation for development

    if [[ "$ENVIRONMENT" == "dev" ]]; then
        # Development secrets
        kubectl create secret generic mantrapath-secrets \
            --from-literal=postgres-password="dev-postgres-password" \
            --from-literal=jwt-secret-key="dev-jwt-secret-key" \
            --from-literal=service-auth-token="dev-service-auth-token" \
            --namespace="$NAMESPACE" \
            --dry-run=client -o yaml | kubectl apply -f -
        
        log_success "Development secrets deployed"
    else
        log_warning "Production secrets should be managed externally"
        log_info "Checking for existing secrets..."
        
        if kubectl get secret mantrapath-secrets -n "$NAMESPACE" &> /dev/null; then
            log_success "Production secrets found"
        else
            log_error "Production secrets not found. Please deploy them manually or use external secret management"
            if [[ "$FORCE" != "true" ]]; then
                exit 1
            fi
        fi
    fi
}

# Deploy with Helm
deploy_helm() {
    log_info "🚀 Deploying MantraPath with Helm..."

    cd "$HELM_CHART_DIR"

    # Prepare Helm command
    HELM_CMD="helm upgrade --install $RELEASE_NAME . \
        --namespace $NAMESPACE \
        --values $VALUES_FILE \
        --set global.env=$ENVIRONMENT \
        --set global.namespace=$NAMESPACE \
        --set-string global.labels.deployment-id=$(date -u +%Y%m%d-%H%M%S) \
        --timeout $WAIT_TIMEOUT"

    if [[ "$DRY_RUN" == "true" ]]; then
        HELM_CMD="$HELM_CMD --dry-run"
        log_info "Performing dry run..."
    else
        HELM_CMD="$HELM_CMD --wait --atomic"
    fi

    if [[ "$VERBOSE" == "true" ]]; then
        HELM_CMD="$HELM_CMD --debug"
    fi

    log_info "Executing: $HELM_CMD"

    if eval "$HELM_CMD"; then
        if [[ "$DRY_RUN" == "true" ]]; then
            log_success "Dry run completed successfully"
        else
            log_success "Helm deployment completed successfully"
        fi
    else
        log_error "Helm deployment failed"
        exit 1
    fi
}

# Verify deployment
verify_deployment() {
    if [[ "$DRY_RUN" == "true" ]] || [[ "$SKIP_HEALTH_CHECK" == "true" ]]; then
        return 0
    fi

    log_info "✅ Verifying deployment..."

    # Check pods
    log_info "Checking pod status..."
    kubectl get pods -n "$NAMESPACE" -l app.kubernetes.io/instance="$RELEASE_NAME"

    # Wait for pods to be ready
    log_info "Waiting for pods to be ready..."
    if kubectl wait --for=condition=ready pod -l app.kubernetes.io/instance="$RELEASE_NAME" -n "$NAMESPACE" --timeout=300s; then
        log_success "All pods are ready"
    else
        log_error "Some pods are not ready"
        kubectl get pods -n "$NAMESPACE" -l app.kubernetes.io/instance="$RELEASE_NAME"
        exit 1
    fi

    # Check services
    log_info "Checking services..."
    kubectl get services -n "$NAMESPACE" -l app.kubernetes.io/instance="$RELEASE_NAME"

    # Check ingress
    log_info "Checking ingress..."
    kubectl get ingress -n "$NAMESPACE" -l app.kubernetes.io/instance="$RELEASE_NAME"
}

# Run health checks
run_health_checks() {
    if [[ "$DRY_RUN" == "true" ]] || [[ "$SKIP_HEALTH_CHECK" == "true" ]]; then
        return 0
    fi

    log_info "🏥 Running health checks..."

    # Wait a bit for services to stabilize
    sleep 30

    # Get API gateway service
    API_SERVICE="$RELEASE_NAME-api-gateway"
    
    # Try to get the ingress endpoint
    INGRESS_HOST=""
    if kubectl get ingress "$RELEASE_NAME-ingress" -n "$NAMESPACE" &> /dev/null; then
        INGRESS_HOST=$(kubectl get ingress "$RELEASE_NAME-ingress" -n "$NAMESPACE" -o jsonpath='{.spec.rules[0].host}' 2>/dev/null || true)
    fi

    if [[ -n "$INGRESS_HOST" ]] && [[ "$INGRESS_HOST" != "null" ]]; then
        # Test via ingress
        log_info "Testing health endpoint via ingress: http://$INGRESS_HOST/health"
        if curl -f -s -m 10 "http://$INGRESS_HOST/health" &> /dev/null; then
            log_success "Health check via ingress passed"
        else
            log_warning "Health check via ingress failed (this might be expected in some environments)"
        fi
    else
        # Test via port-forward
        log_info "Testing health endpoint via port-forward..."
        kubectl port-forward "svc/$API_SERVICE" 8080:8000 -n "$NAMESPACE" &
        PF_PID=$!
        sleep 5
        
        if curl -f -s -m 10 "http://localhost:8080/health" &> /dev/null; then
            log_success "Health check via port-forward passed"
        else
            log_warning "Health check via port-forward failed"
        fi
        
        kill $PF_PID 2>/dev/null || true
    fi
}

# Generate deployment summary
generate_summary() {
    log_info "📊 Generating deployment summary..."

    cat << EOF

🎉 MantraPath Deployment Summary
================================

Environment: $ENVIRONMENT
Namespace: $NAMESPACE
Release: $RELEASE_NAME
Values File: $VALUES_FILE
Dry Run: $DRY_RUN

Deployment Status: $(if [[ "$DRY_RUN" == "true" ]]; then echo "DRY RUN COMPLETED"; else echo "DEPLOYED"; fi)
Timestamp: $(date -u +%Y-%m-%dT%H:%M:%SZ)

Kubernetes Resources:
EOF

    if [[ "$DRY_RUN" != "true" ]]; then
        echo "Pods:"
        kubectl get pods -n "$NAMESPACE" -l app.kubernetes.io/instance="$RELEASE_NAME" || true
        echo ""
        echo "Services:"
        kubectl get services -n "$NAMESPACE" -l app.kubernetes.io/instance="$RELEASE_NAME" || true
        echo ""
        echo "Ingress:"
        kubectl get ingress -n "$NAMESPACE" -l app.kubernetes.io/instance="$RELEASE_NAME" || true
    fi

    echo ""
    echo "Log file: $LOG_FILE"
    echo ""
}

# Cleanup function
cleanup() {
    local exit_code=$?
    if [[ $exit_code -ne 0 ]]; then
        log_error "Deployment failed with exit code $exit_code"
        echo "Check the log file for details: $LOG_FILE"
    fi
    exit $exit_code
}

# Main function
main() {
    # Set up trap for cleanup
    trap cleanup EXIT

    # Parse arguments
    parse_args "$@"

    # Start deployment
    log "🚀 Starting MantraPath Helm deployment..."
    log "Environment: $ENVIRONMENT"
    log "Namespace: $NAMESPACE"
    log "Release: $RELEASE_NAME"
    log "Values: $VALUES_FILE"
    log "Log file: $LOG_FILE"

    # Execute deployment steps
    validate_environment
    lint_chart
    setup_namespace
    deploy_secrets
    deploy_helm
    verify_deployment
    run_health_checks
    generate_summary

    log_success "🎉 MantraPath deployment completed successfully!"
}

# Run main function with all arguments
main "$@"
