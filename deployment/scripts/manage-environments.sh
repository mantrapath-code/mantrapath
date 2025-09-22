#!/bin/bash

# MantraPath Environment Management Script
# Manage multiple environments and promotions
# Author: MantraPath Team

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

# Configuration
ENVIRONMENTS=("dev" "staging" "prod")
DEPLOY_SCRIPT="$SCRIPT_DIR/deploy-k8s.sh"

show_usage() {
    cat << EOF
${BOLD}MantraPath Environment Management${NC}

Usage: $0 COMMAND [OPTIONS]

${BOLD}Commands:${NC}
  list                      List all environments and their status
  deploy ENV               Deploy to specific environment
  promote FROM TO          Promote deployment from one environment to another
  rollback ENV [REVISION]  Rollback environment to previous or specific revision
  status ENV               Show detailed status of environment
  logs ENV [SERVICE]       Show logs for environment or specific service
  cleanup ENV              Clean up environment resources

${BOLD}Options:${NC}
  --dry-run                Perform dry run
  --force                  Force operation
  --wait-timeout DURATION  Wait timeout [default: 10m]
  -v, --verbose            Verbose output

${BOLD}Examples:${NC}
  $0 deploy dev                    # Deploy to development
  $0 promote dev staging           # Promote from dev to staging
  $0 rollback prod                 # Rollback production to previous version
  $0 status prod                   # Show production status
  $0 logs dev api-gateway          # Show API gateway logs in dev
  $0 cleanup dev                   # Clean up development environment

EOF
}

log_info() {
    echo -e "${BLUE}[$(date '+%H:%M:%S')] INFO:${NC} $1"
}

log_success() {
    echo -e "${GREEN}[$(date '+%H:%M:%S')] SUCCESS:${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[$(date '+%H:%M:%S')] WARNING:${NC} $1"
}

log_error() {
    echo -e "${RED}[$(date '+%H:%M:%S')] ERROR:${NC} $1"
}

check_environment() {
    local env=$1
    for supported_env in "${ENVIRONMENTS[@]}"; do
        if [[ "$env" == "$supported_env" ]]; then
            return 0
        fi
    done
    log_error "Unsupported environment: $env"
    log_error "Supported environments: ${ENVIRONMENTS[*]}"
    exit 1
}

list_environments() {
    echo -e "${BOLD}Environment Status:${NC}"
    echo
    
    for env in "${ENVIRONMENTS[@]}"; do
        local namespace="mantrapath-$env"
        echo -e "${CYAN}Environment: $env${NC}"
        echo -e "  Namespace: $namespace"
        
        # Check if namespace exists
        if kubectl get namespace "$namespace" &>/dev/null; then
            echo -e "  Status: ${GREEN}Active${NC}"
            
            # Get Helm release info
            local release_info
            release_info=$(helm list -n "$namespace" -o json 2>/dev/null || echo "[]")
            local release_count
            release_count=$(echo "$release_info" | jq '. | length')
            
            if [[ "$release_count" -gt 0 ]]; then
                echo -e "  Releases: $release_count"
                echo "$release_info" | jq -r '.[] | "    - \(.name) (v\(.revision)) - \(.status)"'
            else
                echo -e "  Releases: ${YELLOW}None${NC}"
            fi
            
            # Get pod count
            local pod_count
            pod_count=$(kubectl get pods -n "$namespace" --no-headers 2>/dev/null | wc -l)
            echo -e "  Pods: $pod_count"
            
            # Get service count
            local service_count
            service_count=$(kubectl get services -n "$namespace" --no-headers 2>/dev/null | wc -l)
            echo -e "  Services: $service_count"
            
        else
            echo -e "  Status: ${RED}Not Deployed${NC}"
        fi
        echo
    done
}

deploy_environment() {
    local env=$1
    shift
    
    check_environment "$env"
    
    log_info "Deploying to environment: $env"
    
    # Pass through all additional arguments to the deploy script
    bash "$DEPLOY_SCRIPT" --env "$env" "$@"
}

promote_environment() {
    local from_env=$1
    local to_env=$2
    shift 2
    
    check_environment "$from_env"
    check_environment "$to_env"
    
    log_info "Promoting from $from_env to $to_env"
    
    # Get the current image tags from source environment
    local from_namespace="mantrapath-$from_env"
    local to_namespace="mantrapath-$to_env"
    
    # Check if source environment exists
    if ! kubectl get namespace "$from_namespace" &>/dev/null; then
        log_error "Source environment '$from_env' not found"
        exit 1
    fi
    
    # Get current Helm values from source
    local temp_values
    temp_values=$(mktemp)
    
    if helm get values mantrapath -n "$from_namespace" -o yaml > "$temp_values"; then
        log_info "Retrieved values from $from_env environment"
        
        # Deploy to target environment with source values
        log_info "Deploying to $to_env with $from_env configuration"
        bash "$DEPLOY_SCRIPT" --env "$to_env" --values-file "$temp_values" "$@"
        
        rm -f "$temp_values"
        
        log_success "Successfully promoted from $from_env to $to_env"
    else
        log_error "Failed to retrieve values from $from_env"
        rm -f "$temp_values"
        exit 1
    fi
}

rollback_environment() {
    local env=$1
    local revision=${2:-}
    
    check_environment "$env"
    
    local namespace="mantrapath-$env"
    
    log_info "Rolling back environment: $env"
    
    if [[ -n "$revision" ]]; then
        log_info "Rolling back to revision: $revision"
        helm rollback mantrapath "$revision" --namespace "$namespace" --wait
    else
        log_info "Rolling back to previous revision"
        helm rollback mantrapath --namespace "$namespace" --wait
    fi
    
    log_success "Rollback completed for $env"
}

show_environment_status() {
    local env=$1
    
    check_environment "$env"
    
    local namespace="mantrapath-$env"
    
    echo -e "${BOLD}Environment Status: $env${NC}"
    echo
    
    # Helm status
    echo -e "${CYAN}Helm Releases:${NC}"
    helm list -n "$namespace" || echo "No releases found"
    echo
    
    # Pod status
    echo -e "${CYAN}Pod Status:${NC}"
    kubectl get pods -n "$namespace" -o wide || echo "No pods found"
    echo
    
    # Service status
    echo -e "${CYAN}Services:${NC}"
    kubectl get services -n "$namespace" || echo "No services found"
    echo
    
    # Ingress status
    echo -e "${CYAN}Ingresses:${NC}"
    kubectl get ingress -n "$namespace" || echo "No ingresses found"
    echo
    
    # Recent events
    echo -e "${CYAN}Recent Events:${NC}"
    kubectl get events -n "$namespace" --sort-by='.lastTimestamp' | tail -10
}

show_environment_logs() {
    local env=$1
    local service=${2:-}
    
    check_environment "$env"
    
    local namespace="mantrapath-$env"
    
    if [[ -n "$service" ]]; then
        log_info "Showing logs for service: $service in environment: $env"
        kubectl logs -n "$namespace" -l "app.kubernetes.io/name=$service" --tail=100 -f
    else
        log_info "Showing recent logs for environment: $env"
        kubectl logs -n "$namespace" --all-containers=true --tail=20
    fi
}

cleanup_environment() {
    local env=$1
    
    check_environment "$env"
    
    local namespace="mantrapath-$env"
    
    log_warning "This will delete all resources in environment: $env"
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "Cleaning up environment: $env"
        
        # Uninstall Helm releases
        local releases
        releases=$(helm list -n "$namespace" -q 2>/dev/null || true)
        
        if [[ -n "$releases" ]]; then
            while IFS= read -r release; do
                if [[ -n "$release" ]]; then
                    log_info "Uninstalling release: $release"
                    helm uninstall "$release" -n "$namespace" --wait || true
                fi
            done <<< "$releases"
        fi
        
        # Delete namespace
        if kubectl get namespace "$namespace" &>/dev/null; then
            log_info "Deleting namespace: $namespace"
            kubectl delete namespace "$namespace" --wait=true || true
        fi
        
        log_success "Environment $env cleaned up successfully"
    else
        log_info "Cleanup cancelled"
    fi
}

main() {
    if [[ $# -lt 1 ]]; then
        show_usage
        exit 1
    fi
    
    local command=$1
    shift
    
    case $command in
        list)
            list_environments
            ;;
        deploy)
            if [[ $# -lt 1 ]]; then
                log_error "Environment required for deploy command"
                show_usage
                exit 1
            fi
            deploy_environment "$@"
            ;;
        promote)
            if [[ $# -lt 2 ]]; then
                log_error "Source and target environments required for promote command"
                show_usage
                exit 1
            fi
            promote_environment "$@"
            ;;
        rollback)
            if [[ $# -lt 1 ]]; then
                log_error "Environment required for rollback command"
                show_usage
                exit 1
            fi
            rollback_environment "$@"
            ;;
        status)
            if [[ $# -lt 1 ]]; then
                log_error "Environment required for status command"
                show_usage
                exit 1
            fi
            show_environment_status "$1"
            ;;
        logs)
            if [[ $# -lt 1 ]]; then
                log_error "Environment required for logs command"
                show_usage
                exit 1
            fi
            show_environment_logs "$@"
            ;;
        cleanup)
            if [[ $# -lt 1 ]]; then
                log_error "Environment required for cleanup command"
                show_usage
                exit 1
            fi
            cleanup_environment "$1"
            ;;
        *)
            log_error "Unknown command: $command"
            show_usage
            exit 1
            ;;
    esac
}

# Check if required tools are available
for tool in kubectl helm jq; do
    if ! command -v "$tool" &> /dev/null; then
        log_error "Required tool '$tool' not found"
        exit 1
    fi
done

main "$@"