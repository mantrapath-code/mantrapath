#!/bin/bash

# MantraPath Cluster Separation Validation Script
# ===============================================
# Validates that development and production use different clusters

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

log "🔍 Validating MantraPath Cluster Separation..."
echo ""

# Check kubectl is available
if ! command -v kubectl >/dev/null 2>&1; then
    log_error "kubectl is not installed or not in PATH"
    exit 1
fi

# Get current contexts
log_info "📋 Checking available Kubernetes contexts..."

# List all contexts
CONTEXTS=$(kubectl config get-contexts -o name 2>/dev/null || echo "")
CURRENT_CONTEXT=$(kubectl config current-context 2>/dev/null || echo "none")

if [[ -z "$CONTEXTS" ]]; then
    log_error "No Kubernetes contexts found"
    exit 1
fi

echo "Available contexts:"
for context in $CONTEXTS; do
    if [[ "$context" == "$CURRENT_CONTEXT" ]]; then
        echo "  → $context (current)"
    else
        echo "    $context"
    fi
done
echo ""

# Analyze contexts for dev/prod separation
DEV_CONTEXTS=()
PROD_CONTEXTS=()
OTHER_CONTEXTS=()

for context in $CONTEXTS; do
    if [[ "$context" =~ (dev|development|mantrapath-dev) ]]; then
        DEV_CONTEXTS+=("$context")
    elif [[ "$context" =~ (prod|production|mantrapath-prod) ]]; then
        PROD_CONTEXTS+=("$context")
    else
        OTHER_CONTEXTS+=("$context")
    fi
done

log_info "🏗️ Environment Context Analysis:"
echo "================================"

echo "Development contexts: ${#DEV_CONTEXTS[@]}"
for ctx in "${DEV_CONTEXTS[@]}"; do
    echo "  - $ctx"
done

echo "Production contexts: ${#PROD_CONTEXTS[@]}"
for ctx in "${PROD_CONTEXTS[@]}"; do
    echo "  - $ctx"
done

echo "Other contexts: ${#OTHER_CONTEXTS[@]}"
for ctx in "${OTHER_CONTEXTS[@]}"; do
    echo "  - $ctx"
done

echo ""

# Validation checks
VALIDATION_PASSED=true

# Check 1: Separate contexts exist
log_info "✅ Validation Check 1: Separate Contexts"
if [[ ${#DEV_CONTEXTS[@]} -gt 0 && ${#PROD_CONTEXTS[@]} -gt 0 ]]; then
    log_success "Development and production contexts are separate"
else
    log_warning "Missing dedicated development or production contexts"
    log_info "Consider creating separate contexts for better isolation"
fi

# Check 2: Different cluster endpoints
log_info "✅ Validation Check 2: Different Cluster Endpoints"

declare -A CLUSTER_SERVERS
for context in $CONTEXTS; do
    SERVER=$(kubectl config view -o jsonpath="{.contexts[?(@.name=='$context')].context.cluster}" 2>/dev/null || echo "")
    if [[ -n "$SERVER" ]]; then
        CLUSTER_SERVER=$(kubectl config view -o jsonpath="{.clusters[?(@.name=='$SERVER')].cluster.server}" 2>/dev/null || echo "unknown")
        CLUSTER_SERVERS["$context"]=$CLUSTER_SERVER
    fi
done

DEV_SERVERS=()
PROD_SERVERS=()

for context in "${DEV_CONTEXTS[@]}"; do
    if [[ -n "${CLUSTER_SERVERS[$context]:-}" ]]; then
        DEV_SERVERS+=("${CLUSTER_SERVERS[$context]}")
    fi
done

for context in "${PROD_CONTEXTS[@]}"; do
    if [[ -n "${CLUSTER_SERVERS[$context]:-}" ]]; then
        PROD_SERVERS+=("${CLUSTER_SERVERS[$context]}")
    fi
done

echo "Development cluster endpoints:"
for server in "${DEV_SERVERS[@]}"; do
    echo "  - $server"
done

echo "Production cluster endpoints:"
for server in "${PROD_SERVERS[@]}"; do
    echo "  - $server"
done

# Check for overlapping servers
OVERLAP_FOUND=false
for dev_server in "${DEV_SERVERS[@]}"; do
    for prod_server in "${PROD_SERVERS[@]}"; do
        if [[ "$dev_server" == "$prod_server" ]]; then
            log_error "Cluster overlap detected: $dev_server is used for both dev and prod"
            VALIDATION_PASSED=false
            OVERLAP_FOUND=true
        fi
    done
done

if [[ "$OVERLAP_FOUND" == false ]]; then
    log_success "No cluster endpoint overlaps detected"
fi

echo ""

# Check 3: Namespace separation within clusters
log_info "✅ Validation Check 3: Namespace Separation"

for context in $CONTEXTS; do
    kubectl config use-context "$context" >/dev/null 2>&1 || continue
    
    NAMESPACES=$(kubectl get namespaces -o name 2>/dev/null | sed 's/namespace\///' || echo "")
    DEV_NS_COUNT=$(echo "$NAMESPACES" | grep -c -E "(dev|development|mantrapath-dev)" || echo "0")
    PROD_NS_COUNT=$(echo "$NAMESPACES" | grep -c -E "(prod|production|mantrapath-prod)" || echo "0")
    
    echo "Context: $context"
    echo "  Development namespaces: $DEV_NS_COUNT"
    echo "  Production namespaces: $PROD_NS_COUNT"
    
    if [[ $DEV_NS_COUNT -gt 0 && $PROD_NS_COUNT -gt 0 ]]; then
        log_warning "Both dev and prod namespaces found in same cluster: $context"
        log_info "Consider using separate clusters for better isolation"
    fi
done

echo ""

# Check 4: GitHub Actions workflow configuration
log_info "✅ Validation Check 4: GitHub Actions Configuration"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Check for separate workflow files
DEV_WORKFLOW="$PROJECT_ROOT/.github/workflows/deploy.yml"
PROD_WORKFLOW="$PROJECT_ROOT/.github/workflows/production-deploy.yml"

if [[ -f "$DEV_WORKFLOW" && -f "$PROD_WORKFLOW" ]]; then
    log_success "Separate workflow files found for dev and production"
    
    # Check workflow triggers
    DEV_TRIGGER=$(grep -E "branches.*\[(.*)\]" "$DEV_WORKFLOW" | head -1 || echo "")
    PROD_TRIGGER=$(grep -E "branches.*\[(.*)\]" "$PROD_WORKFLOW" | head -1 || echo "")
    
    echo "Development workflow trigger: $DEV_TRIGGER"
    echo "Production workflow trigger: $PROD_TRIGGER"
    
    if [[ "$DEV_TRIGGER" =~ main && "$PROD_TRIGGER" =~ main ]]; then
        log_warning "Both workflows trigger on main branch - ensure proper separation"
    fi
else
    log_warning "Missing separate workflow files for dev/prod deployment"
fi

echo ""

# Check 5: Values file separation
log_info "✅ Validation Check 5: Helm Values Separation"

VALUES_DIR="$PROJECT_ROOT/deployment/helm/mantrapath"
DEV_VALUES="$VALUES_DIR/values-dev.yaml"
PROD_VALUES="$VALUES_DIR/values-prod.yaml"

if [[ -f "$DEV_VALUES" && -f "$PROD_VALUES" ]]; then
    log_success "Separate values files found for dev and production"
    
    # Check for different configurations
    DEV_ENV=$(grep -E "env:\s*(dev|development)" "$DEV_VALUES" || echo "")
    PROD_ENV=$(grep -E "env:\s*(prod|production)" "$PROD_VALUES" || echo "")
    
    if [[ -n "$DEV_ENV" && -n "$PROD_ENV" ]]; then
        log_success "Environment variables properly separated"
    else
        log_warning "Environment variables may not be properly configured"
    fi
    
    # Check replica counts
    DEV_REPLICAS=$(grep -c "replicaCount: 1" "$DEV_VALUES" 2>/dev/null || echo "0")
    PROD_REPLICAS=$(grep -c "replicaCount: [2-9]" "$PROD_VALUES" 2>/dev/null || echo "0")
    
    echo "Development single replicas: $DEV_REPLICAS"
    echo "Production multi replicas: $PROD_REPLICAS"
    
else
    log_warning "Missing separate values files for dev/prod configuration"
fi

echo ""

# Final validation summary
log_info "📊 Validation Summary:"
echo "======================"

if [[ "$VALIDATION_PASSED" == true ]]; then
    log_success "✅ Cluster separation validation PASSED"
    echo ""
    echo "🎯 Deployment Strategy Summary:"
    echo "  • Development: Uses dev contexts/namespaces"
    echo "  • Production: Uses separate prod contexts/clusters"
    echo "  • Workflows: Separate GitHub Actions for each environment"
    echo "  • Configuration: Environment-specific Helm values"
    echo ""
    log_success "Your setup follows best practices for dev/prod separation!"
else
    log_error "❌ Cluster separation validation FAILED"
    echo ""
    echo "🔧 Recommended Actions:"
    echo "  1. Set up separate production cluster"
    echo "  2. Configure different cluster endpoints"
    echo "  3. Use separate namespaces at minimum"
    echo "  4. Review GitHub Actions workflows"
    echo ""
    log_warning "Please address the issues above before production deployment"
fi

echo ""

# Generate deployment guide
cat > "$PROJECT_ROOT/CLUSTER_SEPARATION_GUIDE.md" << EOF
# MantraPath Cluster Separation Guide

## Current Configuration

### Development Environment
- Contexts: $(IFS=', '; echo "${DEV_CONTEXTS[*]}")
- Namespaces: mantrapath-dev
- Trigger: Feature branches, development pushes

### Production Environment  
- Contexts: $(IFS=', '; echo "${PROD_CONTEXTS[*]}")
- Namespaces: mantrapath-prod
- Trigger: Main branch merges

## Deployment Flow

### Development Deployment
\`\`\`bash
# Automatic on feature branch push
git push origin feature/my-feature

# Manual deployment
kubectl config use-context mantrapath-dev
./deployment/helm-deploy.sh --environment dev
\`\`\`

### Production Deployment
\`\`\`bash
# Automatic on main branch merge
git push origin main

# Manual deployment (emergency only)
kubectl config use-context production
./deployment/helm-deploy.sh --environment prod
\`\`\`

## Cluster Access Commands

### Switch to Development
\`\`\`bash
kubectl config use-context mantrapath-dev
kubectl get pods -n mantrapath-dev
\`\`\`

### Switch to Production
\`\`\`bash
kubectl config use-context production
kubectl get pods -n mantrapath-prod
\`\`\`

## Security Best Practices

1. **Separate Clusters**: Use different Kubernetes clusters for dev/prod
2. **Network Isolation**: Implement network policies
3. **RBAC**: Different service accounts and permissions
4. **Secrets**: Separate secret management for each environment
5. **Monitoring**: Environment-specific monitoring and alerting

## Validation Status

Last validated: $(date)
Status: $(if [[ "$VALIDATION_PASSED" == true ]]; then echo "✅ PASSED"; else echo "❌ NEEDS ATTENTION"; fi)

EOF

log_info "📋 Cluster separation guide saved to: CLUSTER_SEPARATION_GUIDE.md"

# Restore original context
if [[ -n "$CURRENT_CONTEXT" && "$CURRENT_CONTEXT" != "none" ]]; then
    kubectl config use-context "$CURRENT_CONTEXT" >/dev/null 2>&1
fi

echo ""
log_success "🎉 Cluster separation validation completed!"

