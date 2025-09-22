#!/bin/bash

# MantraPath Chart Testing Script
# Comprehensive Helm chart testing and validation
# Author: MantraPath Team

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
HELM_CHART_DIR="$SCRIPT_DIR/../helm/mantrapath"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

# Test configuration
TEST_NAMESPACE="mantrapath-test-$(date +%s)"
TEST_RELEASE="mantrapath-test"
CLEANUP_ON_EXIT=true
VERBOSE=false

show_usage() {
    cat << EOF
${BOLD}MantraPath Chart Testing${NC}

Usage: $0 [OPTIONS]

${BOLD}Options:${NC}
  -v, --verbose             Verbose output
  -k, --keep-resources      Don't cleanup test resources on exit
  -n, --namespace NAME      Use specific test namespace
  -r, --release NAME        Use specific test release name
  -h, --help                Show this help message

${BOLD}Test Categories:${NC}
  - Helm chart linting
  - Template validation
  - Security policy validation
  - Resource requirement validation
  - Service connectivity tests
  - Database initialization tests
  - Health check validation

${BOLD}Examples:${NC}
  $0                        # Run all tests with cleanup
  $0 --keep-resources       # Run tests and keep resources for debugging
  $0 --verbose              # Run with detailed output

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

log_test() {
    echo -e "${CYAN}[TEST]${NC} $1"
}

check_prerequisites() {
    log_info "Checking prerequisites..."
    
    local required_commands=("kubectl" "helm" "jq")
    for cmd in "${required_commands[@]}"; do
        if ! command -v "$cmd" &> /dev/null; then
            log_error "Required command '$cmd' not found"
            exit 1
        fi
    done
    
    if ! kubectl cluster-info &> /dev/null; then
        log_error "Cannot connect to Kubernetes cluster"
        exit 1
    fi
    
    if [[ ! -f "$HELM_CHART_DIR/Chart.yaml" ]]; then
        log_error "Helm chart not found at: $HELM_CHART_DIR"
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

setup_test_environment() {
    log_info "Setting up test environment..."
    
    # Create test namespace
    if kubectl get namespace "$TEST_NAMESPACE" &>/dev/null; then
        log_warning "Test namespace already exists, cleaning up..."
        kubectl delete namespace "$TEST_NAMESPACE" --wait=true
    fi
    
    kubectl create namespace "$TEST_NAMESPACE"
    kubectl label namespace "$TEST_NAMESPACE" test="true" managed-by="mantrapath-test"
    
    log_success "Test environment created: $TEST_NAMESPACE"
}

cleanup_test_environment() {
    if [[ "$CLEANUP_ON_EXIT" == "true" ]]; then
        log_info "Cleaning up test environment..."
        
        # Uninstall helm release if exists
        if helm list -n "$TEST_NAMESPACE" | grep -q "$TEST_RELEASE"; then
            helm uninstall "$TEST_RELEASE" -n "$TEST_NAMESPACE" --wait || true
        fi
        
        # Delete namespace
        kubectl delete namespace "$TEST_NAMESPACE" --wait=true || true
        
        log_success "Test environment cleaned up"
    else
        log_info "Keeping test resources in namespace: $TEST_NAMESPACE"
    fi
}

test_helm_lint() {
    log_test "Running Helm lint tests..."
    
    local lint_output
    lint_output=$(mktemp)
    
    if helm lint "$HELM_CHART_DIR" > "$lint_output" 2>&1; then
        log_success "✓ Helm lint passed"
        [[ "$VERBOSE" == "true" ]] && cat "$lint_output"
    else
        log_error "✗ Helm lint failed"
        cat "$lint_output"
        rm -f "$lint_output"
        return 1
    fi
    
    rm -f "$lint_output"
    return 0
}

test_template_validation() {
    log_test "Running template validation tests..."
    
    local environments=("dev" "prod")
    local validation_errors=0
    
    for env in "${environments[@]}"; do
        log_info "Validating templates for environment: $env"
        
        local values_file="$HELM_CHART_DIR/values-$env.yaml"
        if [[ ! -f "$values_file" ]]; then
            log_warning "Values file not found: $values_file"
            continue
        fi
        
        local template_output
        template_output=$(mktemp)
        
        # Generate templates
        if helm template "$TEST_RELEASE" "$HELM_CHART_DIR" \
            --namespace "$TEST_NAMESPACE" \
            --values "$values_file" > "$template_output" 2>&1; then
            
            # Validate with kubectl dry-run
            if kubectl apply --dry-run=client -f "$template_output" &>/dev/null; then
                log_success "✓ Template validation passed for $env"
            else
                log_error "✗ Template validation failed for $env with kubectl"
                ((validation_errors++))
            fi
        else
            log_error "✗ Template generation failed for $env"
            [[ "$VERBOSE" == "true" ]] && cat "$template_output"
            ((validation_errors++))
        fi
        
        rm -f "$template_output"
    done
    
    return $validation_errors
}

test_security_policies() {
    log_test "Running security policy validation..."
    
    local template_output
    template_output=$(mktemp)
    
    # Generate templates with security enabled
    helm template "$TEST_RELEASE" "$HELM_CHART_DIR" \
        --namespace "$TEST_NAMESPACE" \
        --values "$HELM_CHART_DIR/values-dev.yaml" \
        --set global.security.enabled=true > "$template_output"
    
    local security_checks=0
    local security_passed=0
    
    # Check for NetworkPolicies
    if grep -q "kind: NetworkPolicy" "$template_output"; then
        log_success "✓ NetworkPolicy resources found"
        ((security_passed++))
    else
        log_warning "✗ No NetworkPolicy resources found"
    fi
    ((security_checks++))
    
    # Check for SecurityContext
    if grep -q "securityContext:" "$template_output"; then
        log_success "✓ SecurityContext configurations found"
        ((security_passed++))
    else
        log_warning "✗ No SecurityContext configurations found"
    fi
    ((security_checks++))
    
    # Check for resource limits
    if grep -q "limits:" "$template_output"; then
        log_success "✓ Resource limits found"
        ((security_passed++))
    else
        log_warning "✗ No resource limits found"
    fi
    ((security_checks++))
    
    # Check for readiness/liveness probes
    if grep -q "readinessProbe:" "$template_output"; then
        log_success "✓ Readiness probes found"
        ((security_passed++))
    else
        log_warning "✗ No readiness probes found"
    fi
    ((security_checks++))
    
    rm -f "$template_output"
    
    log_info "Security validation: $security_passed/$security_checks checks passed"
    
    if [[ $security_passed -ge $((security_checks * 3 / 4)) ]]; then
        return 0
    else
        return 1
    fi
}

test_deployment() {
    log_test "Running deployment test..."
    
    local values_file="$HELM_CHART_DIR/values-dev.yaml"
    
    # Install chart with minimal configuration
    log_info "Installing test deployment..."
    
    if helm upgrade --install "$TEST_RELEASE" "$HELM_CHART_DIR" \
        --namespace "$TEST_NAMESPACE" \
        --values "$values_file" \
        --set frontend.enabled=true \
        --set apiGateway.enabled=true \
        --set postgres.enabled=true \
        --set redis.enabled=true \
        --set translationService.enabled=false \
        --set modelsService.enabled=false \
        --timeout 5m \
        --wait; then
        
        log_success "✓ Test deployment completed"
    else
        log_error "✗ Test deployment failed"
        return 1
    fi
    
    return 0
}

test_service_connectivity() {
    log_test "Running service connectivity tests..."
    
    # Wait a bit for pods to be fully ready
    sleep 10
    
    local connectivity_tests=0
    local connectivity_passed=0
    
    # Test database connectivity
    local postgres_pod
    postgres_pod=$(kubectl get pods -n "$TEST_NAMESPACE" -l app.kubernetes.io/name=postgres -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")
    
    if [[ -n "$postgres_pod" ]]; then
        log_info "Testing PostgreSQL connectivity..."
        if kubectl exec -n "$TEST_NAMESPACE" "$postgres_pod" -- pg_isready -h localhost; then
            log_success "✓ PostgreSQL connectivity test passed"
            ((connectivity_passed++))
        else
            log_error "✗ PostgreSQL connectivity test failed"
        fi
        ((connectivity_tests++))
    fi
    
    # Test Redis connectivity
    local redis_pod
    redis_pod=$(kubectl get pods -n "$TEST_NAMESPACE" -l app.kubernetes.io/name=redis -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")
    
    if [[ -n "$redis_pod" ]]; then
        log_info "Testing Redis connectivity..."
        if kubectl exec -n "$TEST_NAMESPACE" "$redis_pod" -- redis-cli ping | grep -q "PONG"; then
            log_success "✓ Redis connectivity test passed"
            ((connectivity_passed++))
        else
            log_error "✗ Redis connectivity test failed"
        fi
        ((connectivity_tests++))
    fi
    
    # Test API Gateway health endpoint
    local api_gateway_pod
    api_gateway_pod=$(kubectl get pods -n "$TEST_NAMESPACE" -l app.kubernetes.io/name=api-gateway -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")
    
    if [[ -n "$api_gateway_pod" ]]; then
        log_info "Testing API Gateway health endpoint..."
        if kubectl exec -n "$TEST_NAMESPACE" "$api_gateway_pod" -- wget -q -O- http://localhost:8000/health 2>/dev/null | grep -q "healthy\|ok"; then
            log_success "✓ API Gateway health test passed"
            ((connectivity_passed++))
        else
            log_warning "API Gateway health test failed (service may still be starting)"
        fi
        ((connectivity_tests++))
    fi
    
    log_info "Connectivity tests: $connectivity_passed/$connectivity_tests passed"
    
    if [[ $connectivity_passed -ge $((connectivity_tests / 2)) ]]; then
        return 0
    else
        return 1
    fi
}

test_helm_tests() {
    log_test "Running Helm tests..."
    
    # Run built-in Helm tests
    if helm test "$TEST_RELEASE" --namespace "$TEST_NAMESPACE" --timeout 5m; then
        log_success "✓ Helm tests passed"
        return 0
    else
        log_error "✗ Helm tests failed"
        return 1
    fi
}

test_resource_validation() {
    log_test "Running resource validation tests..."
    
    local validation_errors=0
    
    # Check if all expected resources are created
    local expected_resources=("deployment" "service" "configmap")
    
    for resource_type in "${expected_resources[@]}"; do
        local resource_count
        resource_count=$(kubectl get "$resource_type" -n "$TEST_NAMESPACE" --no-headers 2>/dev/null | wc -l)
        
        if [[ $resource_count -gt 0 ]]; then
            log_success "✓ Found $resource_count $resource_type resources"
        else
            log_warning "No $resource_type resources found"
            ((validation_errors++))
        fi
    done
    
    # Check pod resource limits
    log_info "Checking pod resource configurations..."
    local pods_without_limits=0
    
    local pods
    pods=$(kubectl get pods -n "$TEST_NAMESPACE" -o jsonpath='{.items[*].metadata.name}')
    
    for pod in $pods; do
        local has_limits
        has_limits=$(kubectl get pod "$pod" -n "$TEST_NAMESPACE" -o jsonpath='{.spec.containers[0].resources.limits}')
        
        if [[ "$has_limits" == "null" || -z "$has_limits" ]]; then
            ((pods_without_limits++))
        fi
    done
    
    if [[ $pods_without_limits -gt 0 ]]; then
        log_warning "$pods_without_limits pods found without resource limits"
    else
        log_success "✓ All pods have resource limits configured"
    fi
    
    return $validation_errors
}

run_all_tests() {
    local total_tests=0
    local passed_tests=0
    
    echo -e "${BOLD}${CYAN}Starting MantraPath Chart Tests${NC}"
    echo "Test Namespace: $TEST_NAMESPACE"
    echo "Test Release: $TEST_RELEASE"
    echo
    
    # Lint tests
    ((total_tests++))
    if test_helm_lint; then
        ((passed_tests++))
    fi
    
    # Template validation
    ((total_tests++))
    if test_template_validation; then
        ((passed_tests++))
    fi
    
    # Security policy validation
    ((total_tests++))
    if test_security_policies; then
        ((passed_tests++))
    fi
    
    # Deployment test
    ((total_tests++))
    if test_deployment; then
        ((passed_tests++))
        
        # Only run these tests if deployment succeeded
        
        # Resource validation
        ((total_tests++))
        if test_resource_validation; then
            ((passed_tests++))
        fi
        
        # Service connectivity
        ((total_tests++))
        if test_service_connectivity; then
            ((passed_tests++))
        fi
        
        # Helm tests
        ((total_tests++))
        if test_helm_tests; then
            ((passed_tests++))
        fi
    else
        # Skip dependent tests if deployment failed
        total_tests=$((total_tests + 3))
        log_warning "Skipping connectivity and Helm tests due to deployment failure"
    fi
    
    # Test summary
    echo
    echo -e "${BOLD}Test Summary${NC}"
    echo "============"
    echo "Total tests: $total_tests"
    echo "Passed: $passed_tests"
    echo "Failed: $((total_tests - passed_tests))"
    
    local pass_percentage
    pass_percentage=$((passed_tests * 100 / total_tests))
    echo "Success rate: $pass_percentage%"
    
    if [[ $pass_percentage -ge 80 ]]; then
        log_success "🎉 Chart testing completed successfully!"
        return 0
    else
        log_error "❌ Chart testing failed - too many test failures"
        return 1
    fi
}

trap cleanup_test_environment EXIT

main() {
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -v|--verbose)
                VERBOSE=true
                shift
                ;;
            -k|--keep-resources)
                CLEANUP_ON_EXIT=false
                shift
                ;;
            -n|--namespace)
                TEST_NAMESPACE="$2"
                shift 2
                ;;
            -r|--release)
                TEST_RELEASE="$2"
                shift 2
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
    
    check_prerequisites
    setup_test_environment
    run_all_tests
}

main "$@"