#!/bin/bash

# MantraPath Helm Health Check Script
# Comprehensive health monitoring for Helm-deployed MantraPath services

set -euo pipefail

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="/tmp/mantrapath-health-check-$(date +%Y%m%d_%H%M%S).log"

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
CONTINUOUS=false
CHECK_INTERVAL=60
MAX_RETRIES=3
TIMEOUT=10
VERBOSE=false

# Health check results
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0

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
🏥 MantraPath Helm Health Check Script

USAGE:
    $0 [OPTIONS]

OPTIONS:
    -e, --environment ENV    Target environment (dev|prod) [default: dev]
    -n, --namespace NS       Kubernetes namespace [default: mantrapath-ENV]
    -r, --release NAME       Helm release name [default: mantrapath-ENV]
    -c, --continuous        Run continuous health checks
    -i, --interval SECONDS  Check interval for continuous mode [default: 60]
    -t, --timeout SECONDS   Request timeout [default: 10]
    -R, --retries COUNT     Max retries per check [default: 3]
    -v, --verbose           Enable verbose output
    -h, --help              Show this help message

EXAMPLES:
    # Single health check for dev
    $0 --environment dev

    # Continuous monitoring for production
    $0 --environment prod --continuous --interval 30

    # Quick health check with custom timeout
    $0 --environment dev --timeout 5

HEALTH CHECKS:
    1. Kubernetes pod status
    2. Service endpoints
    3. HTTP health endpoints
    4. Database connectivity
    5. Redis connectivity
    6. NATS connectivity
    7. Inter-service communication

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
            -c|--continuous)
                CONTINUOUS=true
                shift
                ;;
            -i|--interval)
                CHECK_INTERVAL="$2"
                shift 2
                ;;
            -t|--timeout)
                TIMEOUT="$2"
                shift 2
                ;;
            -R|--retries)
                MAX_RETRIES="$2"
                shift 2
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
}

# Initialize health check
init_health_check() {
    log "🏥 Initializing MantraPath health check..."
    log "Environment: $ENVIRONMENT"
    log "Namespace: $NAMESPACE"
    log "Release: $RELEASE_NAME"
    log "Continuous: $CONTINUOUS"
    log "Log file: $LOG_FILE"

    # Reset counters
    TOTAL_CHECKS=0
    PASSED_CHECKS=0
    FAILED_CHECKS=0
}

# Run a health check with retries
run_check() {
    local check_name="$1"
    local check_command="$2"
    local retry_count=0

    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))

    while [[ $retry_count -lt $MAX_RETRIES ]]; do
        if [[ $retry_count -gt 0 ]]; then
            log_info "Retrying $check_name (attempt $((retry_count + 1))/$MAX_RETRIES)..."
            sleep 2
        fi

        if eval "$check_command"; then
            log_success "$check_name: PASSED"
            PASSED_CHECKS=$((PASSED_CHECKS + 1))
            return 0
        fi

        retry_count=$((retry_count + 1))
    done

    log_error "$check_name: FAILED (after $MAX_RETRIES attempts)"
    FAILED_CHECKS=$((FAILED_CHECKS + 1))
    return 1
}

# Check Kubernetes pod status
check_pod_status() {
    log_info "🔍 Checking pod status..."

    # Check if pods are running
    local pod_check="kubectl get pods -n $NAMESPACE -l app.kubernetes.io/instance=$RELEASE_NAME --no-headers | grep -v 'Running\|Completed' | wc -l | grep -q '^0$'"
    run_check "Pod Status" "$pod_check"

    # List all pods for visibility
    if [[ "$VERBOSE" == "true" ]]; then
        log_info "Pod details:"
        kubectl get pods -n "$NAMESPACE" -l app.kubernetes.io/instance="$RELEASE_NAME" || true
    fi
}

# Check service endpoints
check_service_endpoints() {
    log_info "🔍 Checking service endpoints..."

    # Get all services
    local services
    services=$(kubectl get services -n "$NAMESPACE" -l app.kubernetes.io/instance="$RELEASE_NAME" -o name 2>/dev/null || echo "")

    if [[ -z "$services" ]]; then
        run_check "Service Endpoints" "false"
        return 1
    fi

    # Check each service has endpoints
    for service in $services; do
        local service_name
        service_name=$(echo "$service" | cut -d'/' -f2)
        local endpoint_check="kubectl get endpoints $service_name -n $NAMESPACE -o jsonpath='{.subsets[*].addresses[*].ip}' | grep -q '.'"
        run_check "Service Endpoint: $service_name" "$endpoint_check"
    done
}

# Check HTTP health endpoints
check_http_endpoints() {
    log_info "🔍 Checking HTTP health endpoints..."

    # API Gateway health check
    local api_service="$RELEASE_NAME-api-gateway"
    
    # Try ingress first
    local ingress_host=""
    if kubectl get ingress "$RELEASE_NAME-ingress" -n "$NAMESPACE" &> /dev/null; then
        ingress_host=$(kubectl get ingress "$RELEASE_NAME-ingress" -n "$NAMESPACE" -o jsonpath='{.spec.rules[0].host}' 2>/dev/null || echo "")
    fi

    if [[ -n "$ingress_host" ]] && [[ "$ingress_host" != "null" ]]; then
        # Test via ingress
        local ingress_check="curl -f -s -m $TIMEOUT http://$ingress_host/health > /dev/null 2>&1"
        run_check "HTTP Health (Ingress)" "$ingress_check"

        local api_check="curl -f -s -m $TIMEOUT http://$ingress_host/api/health > /dev/null 2>&1"
        run_check "API Health (Ingress)" "$api_check"
    else
        # Test via port-forward
        log_info "Testing via port-forward (ingress not available)..."
        
        # Start port-forward in background
        kubectl port-forward "svc/$api_service" 8080:8000 -n "$NAMESPACE" > /dev/null 2>&1 &
        local pf_pid=$!
        sleep 3

        local pf_check="curl -f -s -m $TIMEOUT http://localhost:8080/health > /dev/null 2>&1"
        run_check "HTTP Health (Port-forward)" "$pf_check"

        # Clean up port-forward
        kill $pf_pid 2>/dev/null || true
        sleep 1
    fi
}

# Check database connectivity
check_database_connectivity() {
    log_info "🔍 Checking database connectivity..."

    # Check if PostgreSQL pod is running
    local postgres_pod
    postgres_pod=$(kubectl get pods -n "$NAMESPACE" -l app.kubernetes.io/name=postgres -o name 2>/dev/null | head -1 || echo "")

    if [[ -z "$postgres_pod" ]]; then
        run_check "Database Connectivity" "false"
        return 1
    fi

    # Test database connection
    local db_check="kubectl exec $postgres_pod -n $NAMESPACE -- pg_isready -U postgres > /dev/null 2>&1"
    run_check "Database Connectivity" "$db_check"
}

# Check Redis connectivity
check_redis_connectivity() {
    log_info "🔍 Checking Redis connectivity..."

    # Check if Redis pod is running
    local redis_pod
    redis_pod=$(kubectl get pods -n "$NAMESPACE" -l app.kubernetes.io/name=redis -o name 2>/dev/null | head -1 || echo "")

    if [[ -z "$redis_pod" ]]; then
        run_check "Redis Connectivity" "false"
        return 1
    fi

    # Test Redis connection
    local redis_check="kubectl exec $redis_pod -n $NAMESPACE -- redis-cli ping | grep -q PONG"
    run_check "Redis Connectivity" "$redis_check"
}

# Check NATS connectivity
check_nats_connectivity() {
    log_info "🔍 Checking NATS connectivity..."

    # Check if NATS pod is running
    local nats_pod
    nats_pod=$(kubectl get pods -n "$NAMESPACE" -l app.kubernetes.io/name=nats -o name 2>/dev/null | head -1 || echo "")

    if [[ -z "$nats_pod" ]]; then
        run_check "NATS Connectivity" "false"
        return 1
    fi

    # Test NATS connection (basic port check)
    local nats_check="kubectl exec $nats_pod -n $NAMESPACE -- nc -z localhost 4222"
    run_check "NATS Connectivity" "$nats_check"
}

# Check inter-service communication
check_inter_service_communication() {
    log_info "🔍 Checking inter-service communication..."

    # Get API gateway pod for testing
    local api_pod
    api_pod=$(kubectl get pods -n "$NAMESPACE" -l app.kubernetes.io/name=api-gateway -o name 2>/dev/null | head -1 || echo "")

    if [[ -z "$api_pod" ]]; then
        run_check "Inter-service Communication" "false"
        return 1
    fi

    # Test service discovery (check if services are resolvable)
    local service_discovery_check="kubectl exec $api_pod -n $NAMESPACE -- nslookup $RELEASE_NAME-auth-service > /dev/null 2>&1"
    run_check "Service Discovery" "$service_discovery_check"
}

# Generate health check summary
generate_health_summary() {
    local success_rate=0
    if [[ $TOTAL_CHECKS -gt 0 ]]; then
        success_rate=$((PASSED_CHECKS * 100 / TOTAL_CHECKS))
    fi

    log "📊 Health Check Summary"
    log "======================="
    log "Total Checks: $TOTAL_CHECKS"
    log "Passed: $PASSED_CHECKS"
    log "Failed: $FAILED_CHECKS"
    log "Success Rate: $success_rate%"
    log "Timestamp: $(date -u +%Y-%m-%dT%H:%M:%SZ)"

    if [[ $success_rate -ge 90 ]]; then
        log_success "🎉 System health is EXCELLENT ($success_rate%)"
    elif [[ $success_rate -ge 75 ]]; then
        log_warning "⚠️ System health is GOOD ($success_rate%) - some issues detected"
    elif [[ $success_rate -ge 50 ]]; then
        log_warning "⚠️ System health is POOR ($success_rate%) - multiple issues detected"
    else
        log_error "❌ System health is CRITICAL ($success_rate%) - immediate attention required"
    fi

    echo ""
    echo "Log file: $LOG_FILE"
    echo ""
}

# Run all health checks
run_all_health_checks() {
    log "🏥 Running comprehensive health checks..."

    # Reset counters for this run
    TOTAL_CHECKS=0
    PASSED_CHECKS=0
    FAILED_CHECKS=0

    # Run all checks
    check_pod_status
    check_service_endpoints
    check_http_endpoints
    check_database_connectivity
    check_redis_connectivity
    check_nats_connectivity
    check_inter_service_communication

    # Generate summary
    generate_health_summary

    # Return appropriate exit code
    if [[ $FAILED_CHECKS -eq 0 ]]; then
        return 0
    else
        return 1
    fi
}

# Main continuous monitoring loop
run_continuous_monitoring() {
    log "🔄 Starting continuous health monitoring..."
    log "Check interval: ${CHECK_INTERVAL}s"
    log "Press Ctrl+C to stop"

    local check_count=0
    while true; do
        check_count=$((check_count + 1))
        log "📋 Health Check Run #$check_count"

        run_all_health_checks

        if [[ $CONTINUOUS == "true" ]]; then
            log "⏰ Next check in ${CHECK_INTERVAL}s..."
            sleep "$CHECK_INTERVAL"
        else
            break
        fi
    done
}

# Cleanup function
cleanup() {
    local exit_code=$?
    log "🧹 Cleaning up..."
    
    # Kill any background processes
    jobs -p | xargs -r kill 2>/dev/null || true
    
    if [[ $exit_code -ne 0 ]] && [[ $CONTINUOUS != "true" ]]; then
        log_error "Health check completed with issues (exit code: $exit_code)"
    fi
    
    exit $exit_code
}

# Main function
main() {
    # Set up trap for cleanup
    trap cleanup EXIT INT TERM

    # Parse arguments
    parse_args "$@"

    # Initialize
    init_health_check

    # Validate prerequisites
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl is not installed or not in PATH"
        exit 1
    fi

    if ! kubectl cluster-info &> /dev/null; then
        log_error "kubectl cannot connect to cluster. Check your kubeconfig"
        exit 1
    fi

    # Run health checks
    if [[ $CONTINUOUS == "true" ]]; then
        run_continuous_monitoring
    else
        run_all_health_checks
    fi

    log_success "🎉 Health check completed!"
}

# Run main function with all arguments
main "$@"

