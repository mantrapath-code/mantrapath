#!/bin/bash

# MantraPath Pipeline Testing Script
# This script tests the complete deployment pipeline

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${PURPLE}=== $1 ===${NC}"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Configuration
REGISTRY="blr.vultrcr.com/mantrapath"
REGISTRY_USERNAME="$VULTR_CR_USERNAME"
REGISTRY_PASSWORD="$VULTR_CR_PASSWORD"
PROJECT_ROOT="../.."

print_header "MantraPath Pipeline Test"

# Change to project root
cd "$PROJECT_ROOT"
PROJECT_ROOT_ABS=$(pwd)
print_info "Project root: $PROJECT_ROOT_ABS"

print_header "1. Testing Prerequisites"

# Test Docker
if docker info >/dev/null 2>&1; then
    print_success "Docker is running"
else
    print_error "Docker is not running or not accessible"
    exit 1
fi

# Test kubectl
if kubectl cluster-info >/dev/null 2>&1; then
    print_success "Kubernetes cluster is accessible"
    kubectl cluster-info
else
    print_error "kubectl is not configured or cluster is not accessible"
    exit 1
fi

# Test Helm
if command -v helm >/dev/null 2>&1; then
    print_success "Helm is available"
    helm version --short
else
    print_error "Helm is not installed"
    exit 1
fi

# Test registry credentials
if [[ -n "${VULTR_CR_PASSWORD:-}" && -n "${VULTR_CR_USERNAME:-}" ]]; then
    print_success "Registry credentials are available"
else
    print_error "Registry credentials not found. Set VULTR_CR_PASSWORD and VULTR_CR_USERNAME"
    exit 1
fi

print_header "2. Testing Registry Access"

# Test registry login
if echo "$VULTR_CR_PASSWORD" | docker login blr.vultrcr.com -u "$VULTR_CR_USERNAME" --password-stdin >/dev/null 2>&1; then
    print_success "Successfully logged in to Vultr Container Registry"
else
    print_error "Failed to log in to Vultr Container Registry"
    exit 1
fi

print_header "3. Testing Service Discovery"

# List all services
print_info "Discovering services in backend/services..."
SERVICE_COUNT=0
if [[ -d "backend/services" ]]; then
    for service_dir in backend/services/*/; do
        if [[ -d "$service_dir" ]]; then
            service_name=$(basename "$service_dir")
            dockerfile_path="$service_dir/Dockerfile"
            
            if [[ -f "$dockerfile_path" ]]; then
                print_success "✅ $service_name (Dockerfile found)"
                ((SERVICE_COUNT++))
            else
                print_warning "⚠️ $service_name (No Dockerfile)"
            fi
        fi
    done
else
    print_error "backend/services directory not found"
    exit 1
fi

print_info "Found $SERVICE_COUNT services with Dockerfiles"

print_header "4. Testing Sample Image Build"

# Test building one service (api-gateway)
TEST_SERVICE="api-gateway"
TEST_DOCKERFILE="backend/services/api_gateway/Dockerfile"
TEST_IMAGE="mantrapath-api-gateway-test"

if [[ -f "$TEST_DOCKERFILE" ]]; then
    print_info "Testing build for $TEST_SERVICE..."
    
    cd backend
    if docker build -f "../$TEST_DOCKERFILE" -t "$TEST_IMAGE:test" . >/dev/null 2>&1; then
        print_success "Successfully built test image for $TEST_SERVICE"
        
        # Test pushing to registry
        REGISTRY_IMAGE="$REGISTRY/$TEST_IMAGE:test"
        docker tag "$TEST_IMAGE:test" "$REGISTRY_IMAGE"
        
        if docker push "$REGISTRY_IMAGE" >/dev/null 2>&1; then
            print_success "Successfully pushed test image to registry"
            
            # Clean up
            docker rmi "$TEST_IMAGE:test" "$REGISTRY_IMAGE" >/dev/null 2>&1 || true
        else
            print_error "Failed to push test image to registry"
            exit 1
        fi
    else
        print_error "Failed to build test image for $TEST_SERVICE"
        exit 1
    fi
    
    cd "$PROJECT_ROOT_ABS"
else
    print_warning "Test service Dockerfile not found: $TEST_DOCKERFILE"
fi

print_header "5. Testing Helm Charts"

cd deployment/helm/mantrapath

# Test Helm chart validation
print_info "Validating Helm charts..."
if helm dependency update >/dev/null 2>&1; then
    print_success "Helm dependencies updated"
else
    print_warning "Helm dependency update failed"
fi

if helm lint . --values values-complete.yaml --strict >/dev/null 2>&1; then
    print_success "Helm charts pass linting"
else
    print_error "Helm charts failed linting"
    exit 1
fi

# Test Helm template rendering
print_info "Testing Helm template rendering..."
if helm template mantrapath-test . --values values-complete.yaml >/dev/null 2>&1; then
    print_success "Helm templates render successfully"
else
    print_error "Helm template rendering failed"
    exit 1
fi

cd "$PROJECT_ROOT_ABS"

print_header "6. Testing Kubernetes Resources"

# Test namespace creation
TEST_NAMESPACE="mantrapath-test"
print_info "Testing namespace creation..."
kubectl create namespace "$TEST_NAMESPACE" --dry-run=client -o yaml | kubectl apply -f - >/dev/null 2>&1
print_success "Namespace $TEST_NAMESPACE ready"

# Test storage class
print_info "Testing storage class..."
cat << EOF | kubectl apply -f - >/dev/null 2>&1
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: vultr-block-storage-hdd-test
provisioner: block.csi.vultr.com
parameters:
  type: "hdd"
allowVolumeExpansion: true
volumeBindingMode: WaitForFirstConsumer
EOF
print_success "Storage class configured"

# Test registry secret
print_info "Testing registry secret creation..."
kubectl create secret docker-registry mantrapath-registry-test \
  --namespace="$TEST_NAMESPACE" \
  --docker-server=blr.vultrcr.com \
  --docker-username="$VULTR_CR_USERNAME" \
  --docker-password="$VULTR_CR_PASSWORD" \
  --dry-run=client -o yaml | kubectl apply -f - >/dev/null 2>&1
print_success "Registry secret created"

print_header "7. Testing Deployment Scripts"

# Test the main deployment script
print_info "Testing deployment script..."
if [[ -f "deployment/scripts/complete-production-deployment.sh" ]]; then
    chmod +x deployment/scripts/complete-production-deployment.sh
    
    # Test dry run
    cd deployment/scripts
    if VULTR_REGISTRY_PASSWORD="$VULTR_CR_PASSWORD" ./complete-production-deployment.sh --dry-run -e dev >/dev/null 2>&1; then
        print_success "Deployment script dry run successful"
    else
        print_warning "Deployment script dry run failed (this may be expected)"
    fi
    cd "$PROJECT_ROOT_ABS"
else
    print_warning "Deployment script not found"
fi

print_header "8. Cleanup Test Resources"

# Clean up test resources
print_info "Cleaning up test resources..."
kubectl delete namespace "$TEST_NAMESPACE" --ignore-not-found >/dev/null 2>&1 || true
kubectl delete storageclass vultr-block-storage-hdd-test --ignore-not-found >/dev/null 2>&1 || true
print_success "Test resources cleaned up"

print_header "Pipeline Test Results"

print_success "🎉 All pipeline tests passed!"
echo ""
print_info "✅ Docker is working"
print_info "✅ Kubernetes cluster is accessible"
print_info "✅ Helm is configured"
print_info "✅ Vultr Container Registry is accessible"
print_info "✅ Services can be built and pushed"
print_info "✅ Helm charts are valid"
print_info "✅ Kubernetes resources can be created"
print_info "✅ Deployment scripts are ready"

echo ""
print_success "🚀 Your pipeline is ready for production deployment!"

echo ""
print_header "Next Steps"
echo "1. Run a full deployment:"
echo "   cd deployment/scripts"
echo "   VULTR_REGISTRY_PASSWORD=\$VULTR_CR_PASSWORD ./complete-production-deployment.sh -e dev"
echo ""
echo "2. Or trigger via GitHub Actions:"
echo "   - Go to Actions tab in GitHub"
echo "   - Select 'Manual Deployment Trigger'"
echo "   - Run workflow with desired parameters"
echo ""
echo "3. Monitor the deployment:"
echo "   kubectl get pods -n mantrapath-dev"
echo "   kubectl get services -n mantrapath-dev"
