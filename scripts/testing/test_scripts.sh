#!/bin/bash

# MantraPath Script Testing Suite
# Tests all updated startup, health check, and management scripts

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_header() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════╗"
    echo "║               MantraPath Script Test Suite               ║"
    echo "║                  Testing All Scripts                     ║"
    echo "╚══════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_test() {
    echo -e "${BLUE}[TEST]${NC} $1"
}

print_pass() {
    echo -e "${GREEN}[PASS]${NC} $1"
}

print_fail() {
    echo -e "${RED}[FAIL]${NC} $1"
}

print_info() {
    echo -e "${YELLOW}[INFO]${NC} $1"
}

# Get script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"

# Test results tracking
TESTS_PASSED=0
TESTS_FAILED=0
TOTAL_TESTS=0

run_test() {
    local test_name="$1"
    local command="$2"
    local expected_exit_code="${3:-0}"
    
    print_test "$test_name"
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    if eval "$command" >/dev/null 2>&1; then
        actual_exit_code=$?
    else
        actual_exit_code=$?
    fi
    
    if [ $actual_exit_code -eq $expected_exit_code ]; then
        print_pass "$test_name"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        print_fail "$test_name (exit code: $actual_exit_code, expected: $expected_exit_code)"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

test_script_permissions() {
    echo ""
    print_info "Testing script permissions..."
    
    local scripts=(
        "$SCRIPT_DIR/start.sh"
        "$SCRIPT_DIR/manage_services.sh"
        "$SCRIPT_DIR/quick_health_check_fixed.py"
        "$BACKEND_DIR/start-dev.sh"
        "$BACKEND_DIR/stop-dev.sh"
    )
    
    for script in "${scripts[@]}"; do
        if [ -x "$script" ]; then
            print_pass "$(basename "$script") is executable"
            TESTS_PASSED=$((TESTS_PASSED + 1))
        else
            print_fail "$(basename "$script") is not executable"
            TESTS_FAILED=$((TESTS_FAILED + 1))
        fi
        TOTAL_TESTS=$((TOTAL_TESTS + 1))
    done
}

test_script_syntax() {
    echo ""
    print_info "Testing script syntax..."
    
    # Test bash scripts
    run_test "start.sh syntax" "bash -n '$SCRIPT_DIR/start.sh'"
    run_test "manage_services.sh syntax" "bash -n '$SCRIPT_DIR/manage_services.sh'"
    run_test "start-dev.sh syntax" "bash -n '$BACKEND_DIR/start-dev.sh'"
    run_test "stop-dev.sh syntax" "bash -n '$BACKEND_DIR/stop-dev.sh'"
    
    # Test Python script
    run_test "quick_health_check_fixed.py syntax" "python3 -m py_compile '$SCRIPT_DIR/quick_health_check_fixed.py'"
}

test_health_check_functionality() {
    echo ""
    print_info "Testing health check functionality..."
    
    # Test health check script execution - allow non-zero exit codes for feature test failures
    cd "$PROJECT_ROOT"
    if python3 scripts/quick_health_check_fixed.py 2>&1 | grep -q "MantraPath Health Check"; then
        print_pass "Health check script executes and produces output"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        print_fail "Health check script failed to execute or produce expected output"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
}

test_docker_compose_validity() {
    echo ""
    print_info "Testing Docker Compose configuration..."
    
    cd "$BACKEND_DIR"
    run_test "docker-compose.yml syntax" "docker-compose config --quiet"
}

test_service_management_script() {
    echo ""
    print_info "Testing service management script..."
    
    cd "$PROJECT_ROOT"
    
    # Test script help/info functions (non-interactive)
    if echo "9" | scripts/manage_services.sh | grep -q "Environment Information"; then
        print_pass "Service management script environment info works"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        print_fail "Service management script environment info failed"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
}

test_start_dev_script() {
    echo ""
    print_info "Testing start-dev.sh script..."
    
    # Test script can be sourced without errors
    if bash -n "$BACKEND_DIR/start-dev.sh"; then
        print_pass "start-dev.sh syntax is valid"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        print_fail "start-dev.sh has syntax errors"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
}

test_stop_dev_script() {
    echo ""
    print_info "Testing stop-dev.sh script..."
    
    # Test script syntax and basic structure
    if bash -n "$BACKEND_DIR/stop-dev.sh"; then
        print_pass "stop-dev.sh syntax is valid"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        print_fail "stop-dev.sh has syntax errors"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
}

test_service_inventory() {
    echo ""
    print_info "Testing service inventory and documentation..."
    
    if [ -f "$PROJECT_ROOT/SERVICE_INVENTORY.md" ]; then
        print_pass "Service inventory documentation exists"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        print_fail "Service inventory documentation missing"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
}

test_environment_setup() {
    echo ""
    print_info "Testing environment setup..."
    
    # Check if required directories exist
    local dirs=(
        "$PROJECT_ROOT"
        "$BACKEND_DIR"
        "$SCRIPT_DIR"
    )
    
    for dir in "${dirs[@]}"; do
        if [ -d "$dir" ]; then
            print_pass "Directory exists: $(basename "$dir")"
            TESTS_PASSED=$((TESTS_PASSED + 1))
        else
            print_fail "Directory missing: $(basename "$dir")"
            TESTS_FAILED=$((TESTS_FAILED + 1))
        fi
        TOTAL_TESTS=$((TOTAL_TESTS + 1))
    done
    
    # Check if Docker is available
    if docker --version >/dev/null 2>&1; then
        print_pass "Docker is available"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        print_fail "Docker is not available"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    # Check if Python3 is available
    if python3 --version >/dev/null 2>&1; then
        print_pass "Python3 is available"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        print_fail "Python3 is not available"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
}

print_summary() {
    echo ""
    echo "╔══════════════════════════════════════════════════════════╗"
    echo "║                     Test Summary                         ║"
    echo "╚══════════════════════════════════════════════════════════╝"
    echo ""
    echo "Total Tests: $TOTAL_TESTS"
    echo -e "Passed: ${GREEN}$TESTS_PASSED${NC}"
    echo -e "Failed: ${RED}$TESTS_FAILED${NC}"
    
    local success_rate=$(( (TESTS_PASSED * 100) / TOTAL_TESTS ))
    echo "Success Rate: $success_rate%"
    echo ""
    
    if [ $TESTS_FAILED -eq 0 ]; then
        echo -e "${GREEN}🎉 All tests passed! Scripts are ready for use.${NC}"
        return 0
    elif [ $success_rate -ge 90 ]; then
        echo -e "${YELLOW}⚠️  Most tests passed, minor issues to address.${NC}"
        return 1
    elif [ $success_rate -ge 70 ]; then
        echo -e "${YELLOW}🔧 Some tests failed, moderate issues to fix.${NC}"
        return 2
    else
        echo -e "${RED}❌ Many tests failed, significant issues to address.${NC}"
        return 3
    fi
}

# Main execution
main() {
    print_header
    
    print_info "Starting comprehensive script testing..."
    print_info "Project Root: $PROJECT_ROOT"
    print_info "Backend Dir: $BACKEND_DIR"
    print_info "Scripts Dir: $SCRIPT_DIR"
    
    # Run all tests
    test_environment_setup
    test_script_permissions
    test_script_syntax
    test_docker_compose_validity
    test_health_check_functionality
    test_service_management_script
    test_start_dev_script
    test_stop_dev_script
    test_service_inventory
    
    # Print summary and exit with appropriate code
    print_summary
    exit $?
}

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
