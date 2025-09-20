#!/bin/bash

# MantraPath Helm Environment Setup Script
# Comprehensive setup for Helm-based Kubernetes deployment

set -euo pipefail

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LOG_FILE="/tmp/mantrapath-helm-setup-$(date +%Y%m%d_%H%M%S).log"

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
SKIP_DOCKER=false
SKIP_HELM_INSTALL=false
SKIP_KUBECTL_INSTALL=false
INSTALL_INGRESS=true
INSTALL_CERT_MANAGER=false
CREATE_KIND_CLUSTER=false
FORCE=false
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
🚀 MantraPath Helm Environment Setup

USAGE:
    $0 [OPTIONS]

OPTIONS:
    -e, --environment ENV       Target environment (dev|prod) [default: dev]
    --skip-docker              Skip Docker installation
    --skip-helm                Skip Helm installation
    --skip-kubectl             Skip kubectl installation
    --no-ingress               Skip NGINX ingress controller installation
    --install-cert-manager     Install cert-manager (for TLS)
    --create-kind-cluster      Create local Kind cluster for development
    -f, --force                Force installation even if tools exist
    -v, --verbose              Enable verbose output
    -h, --help                 Show this help message

EXAMPLES:
    # Basic development setup
    $0 --environment dev

    # Complete production setup with TLS
    $0 --environment prod --install-cert-manager

    # Local development with Kind cluster
    $0 --environment dev --create-kind-cluster

    # Minimal setup (skip installations)
    $0 --skip-docker --skip-helm --skip-kubectl

WHAT THIS SCRIPT DOES:
    1. Validates system requirements
    2. Installs Docker (if needed)
    3. Installs kubectl (if needed)
    4. Installs Helm (if needed)
    5. Creates/configures Kind cluster (if requested)
    6. Installs NGINX Ingress Controller
    7. Installs cert-manager (if requested)
    8. Validates Helm charts
    9. Sets up development secrets
    10. Runs initial deployment test

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
            --skip-docker)
                SKIP_DOCKER=true
                shift
                ;;
            --skip-helm)
                SKIP_HELM_INSTALL=true
                shift
                ;;
            --skip-kubectl)
                SKIP_KUBECTL_INSTALL=true
                shift
                ;;
            --no-ingress)
                INSTALL_INGRESS=false
                shift
                ;;
            --install-cert-manager)
                INSTALL_CERT_MANAGER=true
                shift
                ;;
            --create-kind-cluster)
                CREATE_KIND_CLUSTER=true
                shift
                ;;
            -f|--force)
                FORCE=true
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

# Check system requirements
check_system_requirements() {
    log_info "🔍 Checking system requirements..."

    # Check OS
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        log_success "Running on Linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        log_success "Running on macOS"
    else
        log_error "Unsupported operating system: $OSTYPE"
        exit 1
    fi

    # Check architecture
    ARCH=$(uname -m)
    case $ARCH in
        x86_64|amd64)
            ARCH="amd64"
            ;;
        arm64|aarch64)
            ARCH="arm64"
            ;;
        *)
            log_error "Unsupported architecture: $ARCH"
            exit 1
            ;;
    esac
    log_success "Architecture: $ARCH"

    # Check if running as root (not recommended)
    if [[ $EUID -eq 0 ]]; then
        log_warning "Running as root is not recommended for development"
        if [[ "$FORCE" != "true" ]]; then
            read -p "Continue anyway? (y/N): " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                exit 1
            fi
        fi
    fi

    # Check internet connectivity
    if ! curl -s --connect-timeout 5 https://google.com > /dev/null; then
        log_error "No internet connectivity detected"
        exit 1
    fi
    log_success "Internet connectivity confirmed"
}

# Install Docker
install_docker() {
    if [[ "$SKIP_DOCKER" == "true" ]]; then
        log_info "⏭️ Skipping Docker installation"
        return 0
    fi

    log_info "🐳 Installing Docker..."

    if command -v docker &> /dev/null && [[ "$FORCE" != "true" ]]; then
        log_success "Docker is already installed"
        docker --version
        return 0
    fi

    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Install Docker on Linux
        curl -fsSL https://get.docker.com -o get-docker.sh
        sh get-docker.sh
        rm get-docker.sh

        # Add user to docker group
        sudo usermod -aG docker "$USER"
        log_warning "Please log out and back in for Docker group membership to take effect"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # Install Docker Desktop on macOS
        log_info "Please install Docker Desktop from https://docker.com/products/docker-desktop"
        log_info "This script will wait for Docker to be available..."
        
        while ! command -v docker &> /dev/null; do
            sleep 5
            echo -n "."
        done
        echo ""
    fi

    # Verify Docker installation
    if docker --version; then
        log_success "Docker installed successfully"
    else
        log_error "Docker installation failed"
        exit 1
    fi
}

# Install kubectl
install_kubectl() {
    if [[ "$SKIP_KUBECTL_INSTALL" == "true" ]]; then
        log_info "⏭️ Skipping kubectl installation"
        return 0
    fi

    log_info "⚙️ Installing kubectl..."

    if command -v kubectl &> /dev/null && [[ "$FORCE" != "true" ]]; then
        log_success "kubectl is already installed"
        kubectl version --client
        return 0
    fi

    # Download and install kubectl
    local kubectl_version
    kubectl_version=$(curl -L -s https://dl.k8s.io/release/stable.txt)
    
    curl -LO "https://dl.k8s.io/release/$kubectl_version/bin/linux/$ARCH/kubectl"
    chmod +x kubectl
    sudo mv kubectl /usr/local/bin/

    # Verify installation
    if kubectl version --client; then
        log_success "kubectl installed successfully"
    else
        log_error "kubectl installation failed"
        exit 1
    fi
}

# Install Helm
install_helm() {
    if [[ "$SKIP_HELM_INSTALL" == "true" ]]; then
        log_info "⏭️ Skipping Helm installation"
        return 0
    fi

    log_info "⛵ Installing Helm..."

    if command -v helm &> /dev/null && [[ "$FORCE" != "true" ]]; then
        log_success "Helm is already installed"
        helm version
        return 0
    fi

    # Install Helm
    curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

    # Verify installation
    if helm version; then
        log_success "Helm installed successfully"
    else
        log_error "Helm installation failed"
        exit 1
    fi
}

# Install Kind (for local development)
install_kind() {
    if [[ "$CREATE_KIND_CLUSTER" != "true" ]]; then
        return 0
    fi

    log_info "🔧 Installing Kind..."

    if command -v kind &> /dev/null && [[ "$FORCE" != "true" ]]; then
        log_success "Kind is already installed"
        return 0
    fi

    # Download and install Kind
    curl -Lo ./kind "https://kind.sigs.k8s.io/dl/v0.20.0/kind-linux-$ARCH"
    chmod +x ./kind
    sudo mv ./kind /usr/local/bin/kind

    if kind version; then
        log_success "Kind installed successfully"
    else
        log_error "Kind installation failed"
        exit 1
    fi
}

# Create Kind cluster
create_kind_cluster() {
    if [[ "$CREATE_KIND_CLUSTER" != "true" ]]; then
        return 0
    fi

    log_info "🚀 Creating Kind cluster..."

    # Check if cluster already exists
    if kind get clusters | grep -q "mantrapath-$ENVIRONMENT"; then
        log_info "Kind cluster mantrapath-$ENVIRONMENT already exists"
        kind get clusters
        return 0
    fi

    # Create Kind configuration
    cat > /tmp/kind-config.yaml << EOF
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
name: mantrapath-$ENVIRONMENT
nodes:
- role: control-plane
  kubeadmConfigPatches:
  - |
    kind: InitConfiguration
    nodeRegistration:
      kubeletExtraArgs:
        node-labels: "ingress-ready=true"
  extraPortMappings:
  - containerPort: 80
    hostPort: 80
    protocol: TCP
  - containerPort: 443
    hostPort: 443
    protocol: TCP
- role: worker
- role: worker
EOF

    # Create cluster
    kind create cluster --config=/tmp/kind-config.yaml
    rm /tmp/kind-config.yaml

    # Set kubectl context
    kubectl cluster-info --context "kind-mantrapath-$ENVIRONMENT"
    
    log_success "Kind cluster created successfully"
}

# Install NGINX Ingress Controller
install_nginx_ingress() {
    if [[ "$INSTALL_INGRESS" != "true" ]]; then
        log_info "⏭️ Skipping NGINX Ingress installation"
        return 0
    fi

    log_info "🌐 Installing NGINX Ingress Controller..."

    # Check if already installed
    if kubectl get namespace ingress-nginx &> /dev/null; then
        log_success "NGINX Ingress Controller is already installed"
        return 0
    fi

    if [[ "$CREATE_KIND_CLUSTER" == "true" ]]; then
        # Install for Kind
        kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml
    else
        # Install for cloud/bare metal
        kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/cloud/deploy.yaml
    fi

    # Wait for ingress controller to be ready
    log_info "Waiting for NGINX Ingress Controller to be ready..."
    kubectl wait --namespace ingress-nginx \
        --for=condition=ready pod \
        --selector=app.kubernetes.io/component=controller \
        --timeout=300s

    log_success "NGINX Ingress Controller installed successfully"
}

# Install cert-manager
install_cert_manager() {
    if [[ "$INSTALL_CERT_MANAGER" != "true" ]]; then
        log_info "⏭️ Skipping cert-manager installation"
        return 0
    fi

    log_info "🔒 Installing cert-manager..."

    # Check if already installed
    if kubectl get namespace cert-manager &> /dev/null; then
        log_success "cert-manager is already installed"
        return 0
    fi

    # Install cert-manager
    kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

    # Wait for cert-manager to be ready
    log_info "Waiting for cert-manager to be ready..."
    kubectl wait --namespace cert-manager \
        --for=condition=ready pod \
        --selector=app.kubernetes.io/name=cert-manager \
        --timeout=300s

    # Create Let's Encrypt cluster issuer for production
    if [[ "$ENVIRONMENT" == "prod" ]]; then
        cat > /tmp/letsencrypt-issuer.yaml << EOF
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: admin@mantrapath.com  # Change this to your email
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
EOF
        kubectl apply -f /tmp/letsencrypt-issuer.yaml
        rm /tmp/letsencrypt-issuer.yaml
        log_success "Let's Encrypt production issuer created"
    fi

    log_success "cert-manager installed successfully"
}

# Validate Helm charts
validate_helm_charts() {
    log_info "🔍 Validating Helm charts..."

    cd "$SCRIPT_DIR/helm/mantrapath"

    # Update dependencies
    helm dependency update

    # Lint charts
    if helm lint . --values values.yaml --strict; then
        log_success "Helm chart validation passed"
    else
        log_error "Helm chart validation failed"
        exit 1
    fi

    # Test template rendering
    helm template test-release . --values "values-$ENVIRONMENT.yaml" --namespace "mantrapath-$ENVIRONMENT" > /tmp/helm-template-test.yaml

    # Validate generated manifests
    if command -v kubeval &> /dev/null; then
        kubeval /tmp/helm-template-test.yaml
    else
        log_info "kubeval not found, skipping manifest validation"
    fi

    rm /tmp/helm-template-test.yaml
    log_success "Helm chart validation completed"
}

# Setup development secrets
setup_dev_secrets() {
    if [[ "$ENVIRONMENT" != "dev" ]]; then
        log_info "⏭️ Skipping dev secrets setup (not dev environment)"
        return 0
    fi

    log_info "🔐 Setting up development secrets..."

    local namespace="mantrapath-dev"

    # Create namespace
    kubectl create namespace "$namespace" --dry-run=client -o yaml | kubectl apply -f -

    # Create development secrets
    kubectl create secret generic mantrapath-secrets \
        --from-literal=postgres-password="dev-postgres-password-123" \
        --from-literal=postgres-user="mantrapath" \
        --from-literal=postgres-database="mantrapath" \
        --from-literal=jwt-secret-key="dev-jwt-secret-key-change-in-production" \
        --from-literal=service-auth-token="dev-service-auth-token-123" \
        --from-literal=redis-password="" \
        --namespace="$namespace" \
        --dry-run=client -o yaml | kubectl apply -f -

    log_success "Development secrets created"
}

# Run deployment test
run_deployment_test() {
    log_info "🧪 Running deployment test..."

    # Run dry-run deployment
    if "$SCRIPT_DIR/helm-deploy.sh" --environment "$ENVIRONMENT" --dry-run; then
        log_success "Deployment test passed"
    else
        log_error "Deployment test failed"
        exit 1
    fi
}

# Generate setup summary
generate_setup_summary() {
    log "📊 Setup Summary"
    log "==============="
    log "Environment: $ENVIRONMENT"
    log "Docker: $(docker --version 2>/dev/null || echo "Not installed/available")"
    log "kubectl: $(kubectl version --client --short 2>/dev/null || echo "Not installed/available")"
    log "Helm: $(helm version --short 2>/dev/null || echo "Not installed/available")"
    
    if [[ "$CREATE_KIND_CLUSTER" == "true" ]]; then
        log "Kind cluster: $(kind get clusters | grep "mantrapath-$ENVIRONMENT" || echo "Not found")"
    fi
    
    if [[ "$INSTALL_INGRESS" == "true" ]]; then
        log "NGINX Ingress: $(kubectl get pods -n ingress-nginx -l app.kubernetes.io/component=controller --no-headers 2>/dev/null | wc -l || echo "0") pods"
    fi
    
    if [[ "$INSTALL_CERT_MANAGER" == "true" ]]; then
        log "cert-manager: $(kubectl get pods -n cert-manager --no-headers 2>/dev/null | wc -l || echo "0") pods"
    fi

    log ""
    log "🎉 MantraPath Helm environment setup completed!"
    log ""
    log "📋 Next Steps:"
    log "1. Deploy MantraPath: ./deployment/helm-deploy.sh --environment $ENVIRONMENT"
    log "2. Check health: ./deployment/helm-health-check.sh --environment $ENVIRONMENT"
    log "3. Monitor continuously: ./deployment/helm-health-check.sh --environment $ENVIRONMENT --continuous"
    log ""
    log "📚 Documentation:"
    log "- Helm deployment: ./deployment/helm-deploy.sh --help"
    log "- Health monitoring: ./deployment/helm-health-check.sh --help"
    log "- GitHub Actions: .github/workflows/helm-deploy.yml"
    log ""
    log "Log file: $LOG_FILE"
}

# Cleanup function
cleanup() {
    local exit_code=$?
    if [[ $exit_code -ne 0 ]]; then
        log_error "Setup failed with exit code $exit_code"
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

    # Start setup
    log "🚀 Starting MantraPath Helm environment setup..."
    log "Environment: $ENVIRONMENT"
    log "Log file: $LOG_FILE"

    # Execute setup steps
    check_system_requirements
    install_docker
    install_kubectl
    install_helm
    install_kind
    create_kind_cluster
    install_nginx_ingress
    install_cert_manager
    validate_helm_charts
    setup_dev_secrets
    run_deployment_test
    generate_setup_summary

    log_success "🎉 MantraPath Helm environment setup completed successfully!"
}

# Run main function with all arguments
main "$@"

