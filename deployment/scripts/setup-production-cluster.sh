#!/bin/bash

# MantraPath Production Cluster Setup Script
# ==========================================
# Sets up a separate production Kubernetes cluster configuration

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Logging functions
log() { echo -e "${CYAN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"; }
log_info() { echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO:${NC} $1"; }
log_success() { echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] SUCCESS:${NC} $1"; }
log_warning() { echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1"; }
log_error() { echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1"; }

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Default values
CLUSTER_TYPE="kind"  # kind, gke, eks, aks, custom
CLUSTER_NAME="mantrapath-prod"
NAMESPACE="mantrapath-prod"
DOMAIN="mantrapath.com"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --cluster-type)
            CLUSTER_TYPE="$2"
            shift 2
            ;;
        --cluster-name)
            CLUSTER_NAME="$2"
            shift 2
            ;;
        --namespace)
            NAMESPACE="$2"
            shift 2
            ;;
        --domain)
            DOMAIN="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --cluster-type TYPE    Cluster type: kind, gke, eks, aks, custom (default: kind)"
            echo "  --cluster-name NAME    Production cluster name (default: mantrapath-prod)"
            echo "  --namespace NAMESPACE  Production namespace (default: mantrapath-prod)"
            echo "  --domain DOMAIN        Production domain (default: mantrapath.com)"
            echo "  --help                 Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0 --cluster-type kind"
            echo "  $0 --cluster-type gke --cluster-name my-prod-cluster"
            echo "  $0 --cluster-type custom --domain myapp.com"
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

log "🚀 Setting up MantraPath Production Cluster..."
log "Cluster Type: $CLUSTER_TYPE"
log "Cluster Name: $CLUSTER_NAME"
log "Namespace: $NAMESPACE"
log "Domain: $DOMAIN"
echo ""

# Function to setup Kind cluster (for testing)
setup_kind_cluster() {
    log_info "🐳 Setting up Kind production cluster..."
    
    # Check if Kind is installed
    if ! command -v kind >/dev/null 2>&1; then
        log_error "Kind is not installed. Please install Kind first."
        exit 1
    fi
    
    # Create Kind cluster config
    cat > /tmp/kind-prod-config.yaml << EOF
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
name: $CLUSTER_NAME
nodes:
- role: control-plane
  kubeadmConfigPatches:
  - |
    kind: InitConfiguration
    nodeRegistration:
      kubeletExtraArgs:
        node-labels: "ingress-ready=true,environment=production"
  extraPortMappings:
  - containerPort: 80
    hostPort: 80
    protocol: TCP
  - containerPort: 443
    hostPort: 443
    protocol: TCP
  - containerPort: 30880
    hostPort: 30880
    protocol: TCP
- role: worker
  labels:
    environment: production
    tier: application
- role: worker
  labels:
    environment: production
    tier: database
EOF
    
    # Create the cluster
    if kind get clusters | grep -q "$CLUSTER_NAME"; then
        log_warning "Kind cluster '$CLUSTER_NAME' already exists"
        log_info "Switching to existing cluster..."
        kind export kubeconfig --name "$CLUSTER_NAME"
    else
        log_info "Creating new Kind cluster '$CLUSTER_NAME'..."
        kind create cluster --config /tmp/kind-prod-config.yaml --wait 300s
    fi
    
    # Install NGINX Ingress Controller
    log_info "Installing NGINX Ingress Controller..."
    kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml
    
    # Wait for ingress controller
    log_info "Waiting for NGINX Ingress Controller to be ready..."
    kubectl wait --namespace ingress-nginx \
        --for=condition=ready pod \
        --selector=app.kubernetes.io/component=controller \
        --timeout=300s
    
    log_success "Kind production cluster setup completed"
}

# Function to setup GKE cluster
setup_gke_cluster() {
    log_info "☁️ Setting up GKE production cluster..."
    
    if ! command -v gcloud >/dev/null 2>&1; then
        log_error "Google Cloud SDK is not installed. Please install gcloud first."
        exit 1
    fi
    
    # Set default project and region
    read -p "Enter your GCP project ID: " PROJECT_ID
    read -p "Enter your preferred region (e.g., us-central1): " REGION
    
    gcloud config set project "$PROJECT_ID"
    
    # Create GKE cluster
    log_info "Creating GKE cluster '$CLUSTER_NAME'..."
    gcloud container clusters create "$CLUSTER_NAME" \
        --region="$REGION" \
        --machine-type=e2-standard-4 \
        --num-nodes=3 \
        --enable-autoscaling \
        --min-nodes=2 \
        --max-nodes=10 \
        --enable-autorepair \
        --enable-autoupgrade \
        --labels=environment=production,app=mantrapath
    
    # Get credentials
    gcloud container clusters get-credentials "$CLUSTER_NAME" --region="$REGION"
    
    # Install NGINX Ingress Controller
    kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.2/deploy/static/provider/cloud/deploy.yaml
    
    log_success "GKE production cluster setup completed"
}

# Function to setup EKS cluster
setup_eks_cluster() {
    log_info "☁️ Setting up EKS production cluster..."
    
    if ! command -v eksctl >/dev/null 2>&1; then
        log_error "eksctl is not installed. Please install eksctl first."
        exit 1
    fi
    
    read -p "Enter your AWS region (e.g., us-west-2): " AWS_REGION
    
    # Create EKS cluster
    log_info "Creating EKS cluster '$CLUSTER_NAME'..."
    eksctl create cluster \
        --name="$CLUSTER_NAME" \
        --region="$AWS_REGION" \
        --nodegroup-name=production-nodes \
        --node-type=m5.large \
        --nodes=3 \
        --nodes-min=2 \
        --nodes-max=10 \
        --managed \
        --tags environment=production,app=mantrapath
    
    # Install NGINX Ingress Controller
    kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.2/deploy/static/provider/aws/deploy.yaml
    
    log_success "EKS production cluster setup completed"
}

# Function to setup custom cluster
setup_custom_cluster() {
    log_info "⚙️ Setting up custom production cluster configuration..."
    
    echo "For custom cluster setup, please provide the following information:"
    read -p "Kubernetes API Server URL: " K8S_SERVER
    read -p "Cluster CA Certificate (base64): " K8S_CA_CERT
    read -p "Service Account Token: " K8S_TOKEN
    
    # Create kubeconfig
    mkdir -p ~/.kube/backup
    if [[ -f ~/.kube/config ]]; then
        cp ~/.kube/config ~/.kube/backup/config-$(date +%Y%m%d-%H%M%S)
    fi
    
    # Setup production context
    kubectl config set-cluster "$CLUSTER_NAME" \
        --server="$K8S_SERVER" \
        --certificate-authority-data="$K8S_CA_CERT"
    
    kubectl config set-credentials production-user \
        --token="$K8S_TOKEN"
    
    kubectl config set-context production \
        --cluster="$CLUSTER_NAME" \
        --user=production-user \
        --namespace="$NAMESPACE"
    
    kubectl config use-context production
    
    # Test connection
    if kubectl cluster-info >/dev/null 2>&1; then
        log_success "Custom cluster connection established"
    else
        log_error "Failed to connect to custom cluster"
        exit 1
    fi
}

# Main setup based on cluster type
case $CLUSTER_TYPE in
    kind)
        setup_kind_cluster
        ;;
    gke)
        setup_gke_cluster
        ;;
    eks)
        setup_eks_cluster
        ;;
    aks)
        log_error "AKS setup not implemented yet"
        exit 1
        ;;
    custom)
        setup_custom_cluster
        ;;
    *)
        log_error "Unknown cluster type: $CLUSTER_TYPE"
        exit 1
        ;;
esac

# Common post-setup tasks
log_info "🔧 Performing common setup tasks..."

# Create production namespace
kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -
kubectl label namespace "$NAMESPACE" environment=production --overwrite
kubectl label namespace "$NAMESPACE" app.kubernetes.io/name=mantrapath --overwrite

# Create resource quotas for production
log_info "Setting up resource quotas..."
cat > /tmp/prod-resource-quota.yaml << EOF
apiVersion: v1
kind: ResourceQuota
metadata:
  name: production-quota
  namespace: $NAMESPACE
spec:
  hard:
    requests.cpu: "20"
    requests.memory: 40Gi
    limits.cpu: "50"
    limits.memory: 100Gi
    persistentvolumeclaims: "10"
    services: "50"
    secrets: "20"
    pods: "100"
EOF

kubectl apply -f /tmp/prod-resource-quota.yaml

# Setup network policies (if supported)
log_info "Setting up network policies..."
cat > /tmp/prod-network-policy.yaml << EOF
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: production-network-policy
  namespace: $NAMESPACE
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    - namespaceSelector:
        matchLabels:
          name: $NAMESPACE
  egress:
  - {}
EOF

kubectl apply -f /tmp/prod-network-policy.yaml 2>/dev/null || log_warning "Network policies not supported on this cluster"

# Generate GitHub Actions secrets template
log_info "📋 Generating GitHub Actions secrets template..."
cat > "$PROJECT_ROOT/PRODUCTION_SECRETS_TEMPLATE.md" << EOF
# Production Deployment Secrets

Add these secrets to your GitHub repository settings:

## Kubernetes Cluster Access
\`\`\`
PROD_K8S_SERVER=$(kubectl config view --minify -o jsonpath='{.clusters[0].cluster.server}')
PROD_K8S_CA_CERT=$(kubectl config view --minify --raw -o jsonpath='{.clusters[0].cluster.certificate-authority-data}')
PROD_K8S_TOKEN=<your-service-account-token>
\`\`\`

## Application Secrets
\`\`\`
PROD_POSTGRES_PASSWORD=<secure-postgres-password>
PROD_POSTGRES_USER=mantrapath_prod
PROD_POSTGRES_DATABASE=mantrapath_prod
PROD_JWT_SECRET_KEY=<256-bit-secure-jwt-key>
PROD_REDIS_PASSWORD=<secure-redis-password>
PROD_SERVICE_AUTH_TOKEN=<secure-service-auth-token>
\`\`\`

## External Services
\`\`\`
OPENAI_API_KEY=<your-openai-api-key>
SMTP_USERNAME=<smtp-username>
SMTP_PASSWORD=<smtp-password>
SMTP_SERVER=smtp.gmail.com
\`\`\`

## Optional Notifications
\`\`\`
SLACK_WEBHOOK_URL=<slack-webhook-for-notifications>
\`\`\`

## How to Add Secrets:
1. Go to your GitHub repository
2. Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Add each secret with the exact name and value
EOF

# Create production deployment test
log_info "🧪 Creating production deployment test..."
cat > "$PROJECT_ROOT/deployment/test-production-deployment.sh" << 'EOF'
#!/bin/bash
# Production Deployment Test Script

set -euo pipefail

echo "🧪 Testing production deployment configuration..."

# Test Helm template rendering
cd "$(dirname "$0")/helm/mantrapath"

echo "1. Testing Helm template rendering..."
helm template mantrapath-prod . \
    --values values-prod.yaml \
    --set global.env=prod \
    --set global.namespace=mantrapath-prod \
    --dry-run > /tmp/prod-test-manifest.yaml

echo "2. Validating generated manifests..."
kubectl apply --dry-run=client -f /tmp/prod-test-manifest.yaml

echo "3. Checking resource counts..."
echo "  Deployments: $(grep -c "kind: Deployment" /tmp/prod-test-manifest.yaml)"
echo "  Services: $(grep -c "kind: Service" /tmp/prod-test-manifest.yaml)"
echo "  Secrets: $(grep -c "kind: Secret" /tmp/prod-test-manifest.yaml)"
echo "  Ingress: $(grep -c "kind: Ingress" /tmp/prod-test-manifest.yaml)"

echo "✅ Production deployment test completed successfully!"
EOF

chmod +x "$PROJECT_ROOT/deployment/test-production-deployment.sh"

# Final summary
echo ""
log_success "🎉 Production cluster setup completed!"
echo ""
log_info "📋 Summary:"
echo "  Cluster: $CLUSTER_NAME"
echo "  Namespace: $NAMESPACE"
echo "  Domain: $DOMAIN"
echo "  Context: $(kubectl config current-context)"
echo ""
log_info "🔧 Next Steps:"
echo "1. Review and add GitHub Actions secrets from: PRODUCTION_SECRETS_TEMPLATE.md"
echo "2. Update DNS records to point $DOMAIN to your cluster's ingress IP"
echo "3. Test deployment: ./deployment/test-production-deployment.sh"
echo "4. Merge to main branch to trigger production deployment"
echo ""
log_info "📚 Useful Commands:"
echo "  kubectl get pods -n $NAMESPACE"
echo "  kubectl get services -n $NAMESPACE"
echo "  kubectl logs -f deployment/mantrapath-prod-api-gateway -n $NAMESPACE"
echo ""
log_success "Production cluster is ready for deployment! 🚀"


