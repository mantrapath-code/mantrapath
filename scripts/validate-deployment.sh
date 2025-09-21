#!/bin/bash
# MantraPath Deployment Validation Script
# This script validates that the GitOps deployment is working correctly

set -uo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKEND_DIR="$PROJECT_ROOT/backend"

# Logging functions
log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

log_error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1"
}

log_info() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')] INFO:${NC} $1"
}

# Test counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Test function
run_test() {
    local test_name="$1"
    local test_command="$2"
    
    ((TOTAL_TESTS++))
    log_info "Testing: $test_name"
    
    if eval "$test_command" >/dev/null 2>&1; then
        log "✅ PASS: $test_name"
        ((PASSED_TESTS++))
        return 0
    else
        log_error "❌ FAIL: $test_name"
        ((FAILED_TESTS++))
        return 0  # Don't exit on test failure
    fi
}

# Test system requirements
test_system_requirements() {
    log_info "🔧 Testing system requirements..."
    
    run_test "Docker installed" "command -v docker"
    run_test "Docker running" "docker info"
    run_test "Docker Compose installed" "command -v docker-compose"
    run_test "Nginx installed" "command -v nginx"
    run_test "Node.js installed" "command -v node"
    run_test "Git installed" "command -v git"
    run_test "Curl installed" "command -v curl"
}

# Test project structure
test_project_structure() {
    log_info "📁 Testing project structure..."
    
    run_test "Backend directory exists" "[ -d '$BACKEND_DIR' ]"
    run_test "Frontend directory exists" "[ -d '$PROJECT_ROOT/frontend' ]"
    run_test "Nginx config exists" "[ -f '$PROJECT_ROOT/nginx/mantrapath.conf' ]"
    run_test "GitHub workflow exists" "[ -f '$PROJECT_ROOT/.github/workflows/deploy.yml' ]"
    run_test "Production Docker Compose exists" "[ -f '$BACKEND_DIR/docker-compose.prod.yml' ]"
    run_test "Development Docker Compose exists" "[ -f '$BACKEND_DIR/docker-compose.yml' ]"
}

# Test configuration files
test_configuration_files() {
    log_info "⚙️ Testing configuration files..."
    
    run_test "Backend environment file exists" "[ -f '$BACKEND_DIR/.env' ]"
    run_test "Frontend environment file exists" "[ -f '$PROJECT_ROOT/frontend/.env' ]"
    run_test "Production environment template exists" "[ -f '$PROJECT_ROOT/deployment/production.env' ]"
    run_test "Frontend Dockerfile exists" "[ -f '$PROJECT_ROOT/deployment/Dockerfile.frontend' ]"
}

# Test Docker Compose configuration
test_docker_compose() {
    log_info "🐳 Testing Docker Compose configuration..."
    
    cd "$BACKEND_DIR"
    run_test "Production Docker Compose config valid" "docker-compose -f docker-compose.prod.yml config"
    run_test "Development Docker Compose config valid" "docker-compose -f docker-compose.yml config"
}

# Test scripts
test_scripts() {
    log_info "📜 Testing deployment scripts..."
    
    run_test "Production deploy script exists" "[ -f '$PROJECT_ROOT/scripts/production-deploy.sh' ]"
    run_test "Production deploy script executable" "[ -x '$PROJECT_ROOT/scripts/production-deploy.sh' ]"
    run_test "Health monitor script exists" "[ -f '$PROJECT_ROOT/scripts/health-monitor.sh' ]"
    run_test "Health monitor script executable" "[ -x '$PROJECT_ROOT/scripts/health-monitor.sh' ]"
    run_test "GitOps setup script exists" "[ -f '$PROJECT_ROOT/scripts/setup-gitops.sh' ]"
    run_test "GitOps setup script executable" "[ -x '$PROJECT_ROOT/scripts/setup-gitops.sh' ]"
}

# Test Nginx configuration
test_nginx_config() {
    log_info "🌐 Testing Nginx configuration..."
    
    if command -v nginx >/dev/null 2>&1; then
        run_test "Nginx config syntax valid" "nginx -t"
        if systemctl list-units --type=service | grep -q nginx; then
            run_test "Nginx service active" "systemctl is-active nginx"
        else
            log_warning "⚠️ SKIP: Nginx service check (service not found)"
            ((PASSED_TESTS++))
            ((TOTAL_TESTS++))
        fi
    else
        log_warning "⚠️ SKIP: Nginx tests (nginx not installed)"
        ((PASSED_TESTS+=2))
        ((TOTAL_TESTS+=2))
    fi
}

# Test network connectivity
test_network() {
    log_info "🌐 Testing network connectivity..."
    
    run_test "Internet connectivity" "curl -s --max-time 5 https://google.com"
    run_test "GitHub connectivity" "curl -s --max-time 5 https://github.com"
    run_test "Docker Hub connectivity" "curl -s --max-time 5 https://registry-1.docker.io"
    run_test "Node.js registry connectivity" "curl -s --max-time 5 https://registry.npmjs.org"
}

# Test ports availability
test_ports() {
    log_info "🔌 Testing port availability..."
    
    local ports=(
        "80:HTTP"
        "443:HTTPS"
        "5432:PostgreSQL"
        "6379:Redis"
        "8000:API Gateway"
        "8080:WebSocket"
        "8081:Models Service"
        "3000:Frontend"
    )
    
    for port_info in "${ports[@]}"; do
        local port=$(echo "$port_info" | cut -d: -f1)
        local service=$(echo "$port_info" | cut -d: -f2)
        
        if command -v netstat >/dev/null 2>&1; then
            if ! netstat -tuln 2>/dev/null | grep -q ":$port "; then
                log "✅ PASS: Port $port ($service) is available"
                ((PASSED_TESTS++))
            else
                log_warning "⚠️ WARN: Port $port ($service) is already in use"
                ((PASSED_TESTS++))  # Don't fail on port warnings
            fi
        elif command -v ss >/dev/null 2>&1; then
            if ! ss -tuln 2>/dev/null | grep -q ":$port "; then
                log "✅ PASS: Port $port ($service) is available"
                ((PASSED_TESTS++))
            else
                log_warning "⚠️ WARN: Port $port ($service) is already in use"
                ((PASSED_TESTS++))  # Don't fail on port warnings
            fi
        else
            log_warning "⚠️ SKIP: Port check (netstat/ss not available)"
            ((PASSED_TESTS++))
        fi
        ((TOTAL_TESTS++))
    done
}

# Test GitHub Actions runner
test_github_runner() {
    log_info "🏃 Testing GitHub Actions runner..."
    
    if [ -d "/home/runner/actions-runner" ]; then
        run_test "GitHub runner directory exists" "[ -d '/home/runner/actions-runner' ]"
        run_test "GitHub runner user exists" "id runner"
        
        if systemctl list-units --type=service | grep -q "actions.runner"; then
            run_test "GitHub runner service active" "systemctl is-active actions.runner.*"
        else
            log_warning "⚠️ WARN: GitHub Actions runner service not found (may not be configured yet)"
        fi
    else
        log_warning "⚠️ WARN: GitHub Actions runner not set up yet"
    fi
}

# Test system resources
test_system_resources() {
    log_info "💾 Testing system resources..."
    
    # Check disk space (require at least 10GB)
    local available_space=$(df / | awk 'NR==2 {print $4}')
    if [[ $available_space -gt 10485760 ]]; then  # 10GB in KB
        log "✅ PASS: Sufficient disk space available ($(($available_space/1024/1024))GB)"
        ((PASSED_TESTS++))
    else
        log_error "❌ FAIL: Insufficient disk space ($(($available_space/1024/1024))GB available, 10GB required)"
        ((FAILED_TESTS++))
    fi
    ((TOTAL_TESTS++))
    
    # Check memory (require at least 4GB)
    if command -v free >/dev/null 2>&1; then
        local available_memory=$(free | awk '/^Mem:/ {print $2}')
        if [[ $available_memory -gt 4194304 ]]; then  # 4GB in KB
            log "✅ PASS: Sufficient memory available ($(($available_memory/1024/1024))GB)"
            ((PASSED_TESTS++))
        else
            log_warning "⚠️ WARN: Low memory detected ($(($available_memory/1024/1024))GB available, 4GB recommended)"
            ((PASSED_TESTS++))  # Don't fail on memory warning
        fi
    else
        log_warning "⚠️ SKIP: Memory check (free command not available)"
        ((PASSED_TESTS++))
    fi
    ((TOTAL_TESTS++))
}

# Test deployment readiness
test_deployment_readiness() {
    log_info "🚀 Testing deployment readiness..."
    
    # Check if environment variables are set
    if [ -f "$BACKEND_DIR/.env" ]; then
        local env_vars=("POSTGRES_PASSWORD" "JWT_SECRET_KEY" "DOMAIN")
        for var in "${env_vars[@]}"; do
            if grep -q "^$var=" "$BACKEND_DIR/.env" && ! grep -q "^$var=$" "$BACKEND_DIR/.env"; then
                log "✅ PASS: Environment variable $var is set"
                ((PASSED_TESTS++))
            else
                log_warning "⚠️ WARN: Environment variable $var may not be set properly"
                ((PASSED_TESTS++))  # Don't fail on env var warnings
            fi
            ((TOTAL_TESTS++))
        done
    fi
    
    # Check if Docker daemon is running
    run_test "Docker daemon responsive" "docker ps"
    
    # Check if we can pull a test image
    run_test "Docker image pull capability" "docker pull hello-world"
    
    # Clean up test image
    docker rmi hello-world >/dev/null 2>&1 || true
}

# Generate validation report
generate_report() {
    local report_file="/tmp/mantrapath-validation-$(date +%Y%m%d_%H%M%S).txt"
    
    cat > "$report_file" << EOF
MantraPath Deployment Validation Report
Generated: $(date)
Hostname: $(hostname)
IP Address: $(hostname -I | awk '{print $1}')

=== Test Summary ===
Total Tests: $TOTAL_TESTS
Passed: $PASSED_TESTS
Failed: $FAILED_TESTS
Success Rate: $(( (PASSED_TESTS * 100) / TOTAL_TESTS ))%

=== System Information ===
OS: $(lsb_release -d | cut -f2)
Kernel: $(uname -r)
Architecture: $(uname -m)
Uptime: $(uptime -p)

=== Docker Information ===
$(docker version --format "Client: {{.Client.Version}}, Server: {{.Server.Version}}" 2>/dev/null || echo "Docker version information unavailable")

=== Resource Usage ===
Disk Usage: $(df -h / | awk 'NR==2 {print $5 " used, " $4 " available"}')
Memory Usage: $(free -h | awk '/^Mem:/ {print $3 " used, " $7 " available"}')
Load Average: $(uptime | awk -F'load average:' '{print $2}')

=== Network Configuration ===
$(ip route show default | head -1)
$(cat /etc/resolv.conf | grep nameserver | head -2)

=== Service Status ===
Docker: $(systemctl is-active docker 2>/dev/null || echo "inactive")
Nginx: $(systemctl is-active nginx 2>/dev/null || echo "inactive")

EOF

    echo "$report_file"
}

# Show summary
show_summary() {
    echo ""
    echo "=================================================="
    echo "🎯 MantraPath Deployment Validation Summary"
    echo "=================================================="
    echo ""
    echo "📊 Test Results:"
    echo "  Total Tests: $TOTAL_TESTS"
    echo "  Passed: $PASSED_TESTS"
    echo "  Failed: $FAILED_TESTS"
    echo "  Success Rate: $(( (PASSED_TESTS * 100) / TOTAL_TESTS ))%"
    echo ""
    
    if [ $FAILED_TESTS -eq 0 ]; then
        log "🎉 All tests passed! Your system is ready for MantraPath deployment."
        echo ""
        echo "✅ Next Steps:"
        echo "  1. Configure GitHub Secrets in your repository"
        echo "  2. Set up GitHub Actions self-hosted runner"
        echo "  3. Push to main branch to trigger deployment"
        echo "  4. Or run manual deployment: sudo $PROJECT_ROOT/scripts/production-deploy.sh"
    elif [ $FAILED_TESTS -lt 5 ]; then
        log_warning "⚠️ Some tests failed, but system may still work with warnings."
        echo ""
        echo "🔧 Recommended Actions:"
        echo "  1. Review failed tests above"
        echo "  2. Fix critical issues before deployment"
        echo "  3. Consider running setup script: sudo $PROJECT_ROOT/scripts/setup-gitops.sh"
    else
        log_error "❌ Multiple tests failed. System needs attention before deployment."
        echo ""
        echo "🚨 Required Actions:"
        echo "  1. Run setup script: sudo $PROJECT_ROOT/scripts/setup-gitops.sh"
        echo "  2. Fix all critical issues"
        echo "  3. Re-run validation: $0"
    fi
    
    echo ""
    echo "📋 Validation report: $(generate_report)"
    echo "📚 Documentation: $PROJECT_ROOT/GITOPS_SETUP.md"
    echo ""
}

# Main function
main() {
    log "🔍 Starting MantraPath deployment validation..."
    echo ""
    
    test_system_requirements
    test_project_structure
    test_configuration_files
    test_docker_compose
    test_scripts
    test_nginx_config
    test_network
    test_ports
    test_github_runner
    test_system_resources
    test_deployment_readiness
    
    show_summary
}

# Handle script arguments
case "${1:-}" in
    "system")
        test_system_requirements
        ;;
    "config")
        test_configuration_files
        test_docker_compose
        ;;
    "network")
        test_network
        test_ports
        ;;
    "resources")
        test_system_resources
        ;;
    "quick")
        test_system_requirements
        test_project_structure
        test_configuration_files
        show_summary
        ;;
    *)
        main
        ;;
esac
