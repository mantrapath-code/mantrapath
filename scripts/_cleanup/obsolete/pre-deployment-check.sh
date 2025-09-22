#!/bin/bash

# Pre-Deployment Prerequisites Check Script
# Validates all requirements before deploying MantraPath services

set -euo pipefail

# Configuration
REGISTRY_URL="https://blr.vultrcr.com/mantrapath"
REGISTRY_HOST="blr.vultrcr.com/mantrapath"
USERNAME="e9b950f6-81b8-4433-bb62-844d3f44b6bb"
API_KEY="D5w5WAevjZQhcUrEQPcuuA6qgCTXzTfLHtYJ"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

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
CHECK_IMAGES=true
CHECK_CLUSTER=true
CHECK_REGISTRY=true
FIX_ISSUES=false
VERBOSE=false

# Service definitions
declare -A SERVICES=(
    ["api-gateway"]="mantrapath-api-gateway"
    ["frontend"]="mantrapath-frontend"
    ["translation-service"]="mantrapath-translation-service"
    ["models-service"]="mantrapath-models-service"
    ["auth-service"]="mantrapath-auth-service"
    ["chatbot-service"]="mantrapath-chatbot-service"
    ["voice-service"]="mantrapath-voice-service"
    ["ml-service"]="mantrapath-ml-service"
    ["mood-service"]="mantrapath-mood-service"
    ["profile-service"]="mantrapath-profile-service"
    ["content-service"]="mantrapath-content-service"
    ["community-service"]="mantrapath-community-service"
    ["notification-service"]="mantrapath-notification-service"
    ["memory-service"]="mantrapath-memory-service"
    ["media-service"]="mantrapath-media-service"
    ["ai-context-store"]="mantrapath-ai-context-store"
    ["ai-event-processor"]="mantrapath-ai-event-processor"
    ["action-orchestrator"]="mantrapath-action-orchestrator"
    ["voice-event-processor"]="mantrapath-voice-event-processor"
    ["proactive-assistance"]="mantrapath-proactive-assistance"
)

# Logging functions
log_header() {
    echo -e "${CYAN}╔══════════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║ $1${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════════════════════════════════╝${NC}"
}

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✅ SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[⚠️  WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[❌ ERROR]${NC} $1"
}

log_check() {
    echo -e "${PURPLE}[🔍 CHECK]${NC} $1"
}

show_help() {
    cat << EOF
🔍 MantraPath Pre-Deployment Prerequisites Check

USAGE:
    $0 [OPTIONS]

OPTIONS:
    -e, --environment ENV    Target environment (dev|prod) [default: dev]
    --skip-images           Skip image availability checks
    --skip-cluster          Skip cluster connectivity checks
    --skip-registry         Skip registry connectivity checks
    --fix                   Attempt to fix found issues automatically
    -v, --verbose           Enable verbose output
    -h, --help              Show this help message

EXAMPLES:
    # Check all prerequisites for dev
    $0 --environment dev

    # Check with auto-fix enabled
    $0 --environment dev --fix

    # Check only registry and images
    $0 --skip-cluster

REGISTRY CONFIGURATION:
    Registry URL: $REGISTRY_URL
    Username: $USERNAME
    All images: $REGISTRY_HOST/<service-name>:latest

EOF
}

parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -e|--environment)
                ENVIRONMENT="$2"
                shift 2
                ;;
            --skip-images)
                CHECK_IMAGES=false
                shift
                ;;
            --skip-cluster)
                CHECK_CLUSTER=false
                shift
                ;;
            --skip-registry)
                CHECK_REGISTRY=false
                shift
                ;;
            --fix)
                FIX_ISSUES=true
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
}

check_prerequisites() {
    log_header "🔧 CHECKING SYSTEM PREREQUISITES"
    
    local issues=0
    
    # Check Docker
    log_check "Docker installation and status"
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        ((issues++))
    elif ! docker info &> /dev/null; then
        log_error "Docker daemon is not running"
        ((issues++))
    else
        log_success "Docker is installed and running"
    fi
    
    # Check kubectl
    log_check "kubectl installation and configuration"
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl is not installed"
        ((issues++))
    else
        log_success "kubectl is installed"
    fi
    
    # Check Helm
    log_check "Helm installation"
    if ! command -v helm &> /dev/null; then
        log_error "Helm is not installed"
        ((issues++))
    else
        local helm_version=$(helm version --short --client 2>/dev/null | grep -o 'v[0-9]\+\.[0-9]\+\.[0-9]\+')
        log_success "Helm is installed ($helm_version)"
    fi
    
    # Check Kind (for dev environment)
    if [[ "$ENVIRONMENT" == "dev" ]]; then
        log_check "Kind installation (for dev environment)"
        if ! command -v kind &> /dev/null; then
            log_warning "Kind is not installed (needed for dev environment)"
            if [[ "$FIX_ISSUES" == "true" ]]; then
                log_info "Installing Kind..."
                install_kind
            else
                ((issues++))
            fi
        else
            log_success "Kind is installed"
        fi
    fi
    
    return $issues
}

check_registry_connectivity() {
    if [[ "$CHECK_REGISTRY" != "true" ]]; then
        return 0
    fi
    
    log_header "🌐 CHECKING REGISTRY CONNECTIVITY"
    
    local issues=0
    
    # Check registry URL accessibility
    log_check "Registry URL accessibility"
    if curl -s --connect-timeout 10 "$REGISTRY_URL" > /dev/null 2>&1; then
        log_success "Registry URL is accessible"
    else
        log_error "Cannot reach registry at $REGISTRY_URL"
        ((issues++))
    fi
    
    # Check Docker registry login
    log_check "Docker registry authentication"
    if echo "$API_KEY" | docker login "$REGISTRY_URL" -u "$USERNAME" --password-stdin &> /dev/null; then
        log_success "Successfully authenticated with registry"
    else
        log_error "Failed to authenticate with registry"
        if [[ "$FIX_ISSUES" == "true" ]]; then
            log_info "Attempting to fix registry authentication..."
            echo "$API_KEY" | docker login "$REGISTRY_URL" -u "$USERNAME" --password-stdin
        else
            ((issues++))
        fi
    fi
    
    return $issues
}

check_cluster_connectivity() {
    if [[ "$CHECK_CLUSTER" != "true" ]]; then
        return 0
    fi
    
    log_header "☸️  CHECKING KUBERNETES CLUSTER"
    
    local issues=0
    
    # Check cluster connectivity
    log_check "Cluster connectivity"
    if kubectl cluster-info &> /dev/null; then
        local cluster_info=$(kubectl cluster-info 2>/dev/null | head -1)
        log_success "Connected to cluster: $cluster_info"
    else
        log_error "Cannot connect to Kubernetes cluster"
        if [[ "$ENVIRONMENT" == "dev" ]] && [[ "$FIX_ISSUES" == "true" ]]; then
            log_info "Attempting to create dev cluster..."
            create_dev_cluster
        else
            ((issues++))
        fi
    fi
    
    # Check namespace
    local namespace="mantrapath-$ENVIRONMENT"
    log_check "Namespace: $namespace"
    if kubectl get namespace "$namespace" &> /dev/null; then
        log_success "Namespace $namespace exists"
    else
        log_warning "Namespace $namespace does not exist"
        if [[ "$FIX_ISSUES" == "true" ]]; then
            log_info "Creating namespace $namespace..."
            kubectl create namespace "$namespace"
            log_success "Created namespace $namespace"
        else
            ((issues++))
        fi
    fi
    
    # Check registry secret
    log_check "Registry secret in namespace"
    if kubectl get secret "mantrapath-$ENVIRONMENT-registry" -n "$namespace" &> /dev/null; then
        log_success "Registry secret exists"
    else
        log_warning "Registry secret does not exist"
        if [[ "$FIX_ISSUES" == "true" ]]; then
            log_info "Creating registry secret..."
            kubectl create secret docker-registry "mantrapath-$ENVIRONMENT-registry" \
                --docker-server="$REGISTRY_HOST" \
                --docker-username="$USERNAME" \
                --docker-password="$API_KEY" \
                --namespace="$namespace"
            log_success "Created registry secret"
        else
            ((issues++))
        fi
    fi
    
    return $issues
}

check_image_availability() {
    if [[ "$CHECK_IMAGES" != "true" ]]; then
        return 0
    fi
    
    log_header "📦 CHECKING IMAGE AVAILABILITY"
    
    local issues=0
    local available_images=0
    local total_images=${#SERVICES[@]}
    
    for service_name in "${!SERVICES[@]}"; do
        local image_name="${SERVICES[$service_name]}"
        local full_image="$REGISTRY_HOST/$image_name:latest"
        
        log_check "Image: $full_image"
        
        if docker pull "$full_image" &> /dev/null; then
            log_success "✅ $image_name:latest is available"
            ((available_images++))
        else
            log_error "❌ $image_name:latest is NOT available"
            ((issues++))
        fi
        
        # Clean up pulled image to save space
        docker rmi "$full_image" &> /dev/null || true
    done
    
    echo
    log_info "📊 Image Availability Summary:"
    log_info "   Available: $available_images/$total_images images"
    
    if [[ $available_images -eq $total_images ]]; then
        log_success "All required images are available in registry"
    else
        log_warning "Some images are missing from registry"
        log_info "💡 Run './scripts/build-and-push-images.sh' to build missing images"
    fi
    
    return $issues
}

check_helm_configuration() {
    log_header "⛵ CHECKING HELM CONFIGURATION"
    
    local issues=0
    
    # Check Helm chart directory
    log_check "Helm chart directory"
    if [[ -d "$PROJECT_ROOT/deployment/helm/mantrapath" ]]; then
        log_success "Helm chart directory exists"
    else
        log_error "Helm chart directory not found"
        ((issues++))
    fi
    
    # Check values file
    local values_file="values-$ENVIRONMENT.yaml"
    if [[ "$ENVIRONMENT" == "dev" ]]; then
    values_file="values-dev.yaml"  # Unified dev values
    fi
    
    log_check "Values file: $values_file"
    if [[ -f "$PROJECT_ROOT/deployment/helm/mantrapath/$values_file" ]]; then
        log_success "Values file exists: $values_file"
    else
        log_error "Values file not found: $values_file"
        ((issues++))
    fi
    
    # Check registry configuration in values
    log_check "Registry configuration in values"
    if grep -q "$REGISTRY_HOST" "$PROJECT_ROOT/deployment/helm/mantrapath/$values_file" 2>/dev/null; then
        log_success "Registry correctly configured in values file"
    else
        log_warning "Registry not configured in values file"
        if [[ "$FIX_ISSUES" == "true" ]]; then
            log_info "This should be fixed in the values file"
        fi
        ((issues++))
    fi
    
    # Lint Helm chart
    log_check "Helm chart validation"
    cd "$PROJECT_ROOT/deployment/helm/mantrapath"
    if helm dependency update &> /dev/null && helm lint . --values "$values_file" --strict &> /dev/null; then
        log_success "Helm chart validation passed"
    else
        log_error "Helm chart validation failed"
        if [[ "$VERBOSE" == "true" ]]; then
            helm lint . --values "$values_file" --strict
        fi
        ((issues++))
    fi
    
    cd "$PROJECT_ROOT"
    return $issues
}

create_dev_cluster() {
    log_info "Creating Kind development cluster..."
    
    if kind get clusters | grep -q "mantrapath-dev"; then
        log_info "Deleting existing cluster..."
        kind delete cluster --name mantrapath-dev
    fi
    
    kind create cluster --name mantrapath-dev --config "$PROJECT_ROOT/deployment/kind-dev.yaml"
    log_success "Dev cluster created successfully"
}

install_kind() {
    log_info "Installing Kind..."
    
    local arch=$(uname -m)
    case $arch in
        x86_64|amd64)
            arch="amd64"
            ;;
        arm64|aarch64)
            arch="arm64"
            ;;
        *)
            log_error "Unsupported architecture: $arch"
            return 1
            ;;
    esac
    
    curl -Lo ./kind "https://kind.sigs.k8s.io/dl/v0.20.0/kind-linux-$arch"
    chmod +x ./kind
    sudo mv ./kind /usr/local/bin/kind
    
    log_success "Kind installed successfully"
}

generate_deployment_plan() {
    log_header "📋 GENERATING DEPLOYMENT PLAN"
    
    local namespace="mantrapath-$ENVIRONMENT"
    
    cat << EOF

🚀 DEPLOYMENT PLAN FOR $ENVIRONMENT ENVIRONMENT
═══════════════════════════════════════════════

📍 Target Configuration:
   Environment: $ENVIRONMENT
   Namespace: $namespace
   Registry: $REGISTRY_HOST
   
📦 Images to Deploy:
EOF

    for service_name in "${!SERVICES[@]}"; do
        local image_name="${SERVICES[$service_name]}"
        echo "   • $image_name:latest"
    done
    
    cat << EOF

🔧 Deployment Command:
   ./deployment/helm-deploy.sh \\
     --environment $ENVIRONMENT \\
     --values-file values-$ENVIRONMENT.yaml \\
     --timeout 15m

📊 Post-Deployment Verification:
   kubectl get pods -n $namespace
   kubectl get services -n $namespace
   kubectl get ingress -n $namespace

🌐 Access URLs:
EOF

    if [[ "$ENVIRONMENT" == "dev" ]]; then
        echo "   • Application: http://localhost:30880"
        echo "   • API Gateway: http://localhost:30880/api"
    else
        echo "   • Application: https://mantrapath.com"
        echo "   • API Gateway: https://mantrapath.com/api"
    fi
    
    echo
}

main() {
    cd "$PROJECT_ROOT"
    
    parse_args "$@"
    
    echo -e "${CYAN}"
    cat << 'EOF'
╔══════════════════════════════════════════════════════════════════════════════╗
║                    MantraPath Pre-Deployment Check                          ║
║                                                                              ║
║  🔍 Validating all prerequisites before deployment                          ║
║  📦 Checking image availability in Vultr registry                          ║
║  ☸️  Verifying Kubernetes cluster connectivity                             ║
║  ⛵ Validating Helm configuration                                           ║
╚══════════════════════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
    
    log_info "🎯 Target Environment: $ENVIRONMENT"
    log_info "🌐 Registry: $REGISTRY_URL"
    log_info "🔧 Auto-fix issues: $FIX_ISSUES"
    echo
    
    local total_issues=0
    
    # Run all checks
    check_prerequisites
    total_issues=$((total_issues + $?))
    
    check_registry_connectivity
    total_issues=$((total_issues + $?))
    
    check_cluster_connectivity
    total_issues=$((total_issues + $?))
    
    check_image_availability
    total_issues=$((total_issues + $?))
    
    check_helm_configuration
    total_issues=$((total_issues + $?))
    
    # Generate deployment plan if no critical issues
    if [[ $total_issues -eq 0 ]]; then
        generate_deployment_plan
        
        log_header "✅ PRE-DEPLOYMENT CHECK COMPLETE"
        log_success "All prerequisites validated successfully!"
        log_success "Ready to deploy to $ENVIRONMENT environment"
        
        echo
        log_info "🚀 Next steps:"
        log_info "1. Run: ./deployment/helm-deploy.sh --environment $ENVIRONMENT"
        log_info "2. Monitor: kubectl get pods -n mantrapath-$ENVIRONMENT -w"
        log_info "3. Access: http://localhost:30880 (dev) or https://mantrapath.com (prod)"
        
        exit 0
    else
        log_header "❌ PRE-DEPLOYMENT CHECK FAILED"
        log_error "Found $total_issues issue(s) that need to be resolved"
        
        echo
        log_info "🔧 To auto-fix issues, run:"
        log_info "   $0 --environment $ENVIRONMENT --fix"
        
        echo
        log_info "📚 Manual fixes:"
        log_info "• Install missing tools: Docker, kubectl, Helm, Kind"
        log_info "• Build missing images: ./scripts/build-and-push-images.sh"
        log_info "• Create cluster: kind create cluster --name mantrapath-dev"
        log_info "• Fix Helm charts: Check deployment/helm/mantrapath/"
        
        exit 1
    fi
}

# Handle Ctrl+C gracefully
trap 'echo -e "\n${YELLOW}[INFO]${NC} Pre-deployment check interrupted"; exit 130' INT

main "$@"

