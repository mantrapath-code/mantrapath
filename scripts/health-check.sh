#!/bin/bash
# MantraPath Health Check Script
# This script performs comprehensive health checks on all services

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BACKEND_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../backend" && pwd)"
LOG_FILE="${HOME}/mantrapath-health.log"

# Logging function
log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1" | tee -a "$LOG_FILE"
}

log_info() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')] INFO:${NC} $1" | tee -a "$LOG_FILE"
}

# Check if a service is healthy
check_service_health() {
    local service_name=$1
    local port=$2
    local endpoint=${3:-"/health"}
    local timeout=${4:-10}
    
    log_info "Checking $service_name on port $port..."
    
    # Use HEALTH_CHECK_HOST env var or default to localhost (for host-based checking)
    local host="${HEALTH_CHECK_HOST:-localhost}"
    if curl -f -s --max-time $timeout "http://$host:$port$endpoint" >/dev/null 2>&1; then
        log "✅ $service_name is healthy"
        return 0
    else
        log_error "❌ $service_name is unhealthy"
        return 1
    fi
}

# Check Docker services
check_docker_services() {
    log "Checking Docker services..."
    
    cd "$BACKEND_DIR"
    
    # Get list of running services
    local services=$(docker-compose -f docker-compose.prod.yml ps --services --filter "status=running")
    
    if [ -z "$services" ]; then
        log_error "No Docker services are running"
        return 1
    fi
    
    log "Running services: $services"
    
    # Check each service
    local failed_services=()
    
    for service in $services; do
        case $service in
            "postgres")
                if ! docker-compose -f docker-compose.prod.yml exec -T postgres pg_isready -U mantrapath -d mantrapath >/dev/null 2>&1; then
                    failed_services+=("postgres")
                fi
                ;;
            "redis")
                if ! docker-compose -f docker-compose.prod.yml exec -T redis redis-cli ping >/dev/null 2>&1; then
                    failed_services+=("redis")
                fi
                ;;
            "nats")
                if ! curl -f -s http://localhost:8222/healthz >/dev/null 2>&1; then
                    failed_services+=("nats")
                fi
                ;;
            *)
                # For other services, try to check their health endpoint
                local port=$(docker-compose -f docker-compose.prod.yml port $service 2>/dev/null | cut -d: -f2)
                if [ -n "$port" ]; then
                    if ! check_service_health "$service" "$port" "/health" 5; then
                        failed_services+=("$service")
                    fi
                fi
                ;;
        esac
    done
    
    if [ ${#failed_services[@]} -eq 0 ]; then
        log "All Docker services are healthy"
        return 0
    else
        log_error "Failed services: ${failed_services[*]}"
        return 1
    fi
}

# Check API endpoints
check_api_endpoints() {
    log "Checking API endpoints..."
    
    local endpoints=(
        "8000:/health:API Gateway"
        "8001:/health:Auth Service"
        "8002:/health:Profile Service"
        "8003:/health:Mood Service"
        "8004:/health:Chatbot Service"
        "8006:/health:Community Service"
        "8007:/health:Notification Service"
        "8008:/health:ML Service"
        "8010:/health:Translation Service"
        "8011:/health:Voice Service"
        "8012:/health:Action Orchestrator"
        "8013:/health:AI Context Store"
        "8017:/health/live:Memory Service"
    )
    
    local failed_endpoints=()
    
    for endpoint in "${endpoints[@]}"; do
        IFS=':' read -r port path name <<< "$endpoint"
        
        if ! check_service_health "$name" "$port" "$path" 10; then
            failed_endpoints+=("$name")
        fi
    done
    
    if [ ${#failed_endpoints[@]} -eq 0 ]; then
        log "All API endpoints are healthy"
        return 0
    else
        log_error "Failed endpoints: ${failed_endpoints[*]}"
        return 1
    fi
}

# Check database connectivity
check_database() {
    log "Checking database connectivity..."
    
    cd "$BACKEND_DIR"
    
    # Check PostgreSQL
    if docker-compose -f docker-compose.prod.yml exec -T postgres pg_isready -U mantrapath -d mantrapath >/dev/null 2>&1; then
        log "✅ PostgreSQL is accessible"
    else
        log_error "❌ PostgreSQL is not accessible"
        return 1
    fi
    
    # Check Redis
    if docker-compose -f docker-compose.prod.yml exec -T redis redis-cli ping >/dev/null 2>&1; then
        log "✅ Redis is accessible"
    else
        log_error "❌ Redis is not accessible"
        return 1
    fi
    
    return 0
}

# Check system resources
check_system_resources() {
    log "Checking system resources..."
    
    # Check disk space
    local disk_usage=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
    if [ "$disk_usage" -gt 90 ]; then
        log_warning "Disk usage is high: ${disk_usage}%"
    else
        log "✅ Disk usage: ${disk_usage}%"
    fi
    
    # Check memory usage
    if command -v free &> /dev/null; then
        local memory_usage=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
        if [ "$memory_usage" -gt 90 ]; then
            log_warning "Memory usage is high: ${memory_usage}%"
        else
            log "✅ Memory usage: ${memory_usage}%"
        fi
    else
        # macOS alternative
        local memory_usage=$(vm_stat | awk '/Pages free/ {free=$3} /Pages active/ {active=$3} /Pages inactive/ {inactive=$3} /Pages speculative/ {speculative=$3} END {total=free+active+inactive+speculative; used=active+inactive+speculative; printf "%.0f", used*100/total}')
        if [ "$memory_usage" -gt 90 ]; then
            log_warning "Memory usage is high: ${memory_usage}%"
        else
            log "✅ Memory usage: ${memory_usage}%"
        fi
    fi
    
    # Check Docker containers
    local container_count=$(docker ps -q | wc -l)
    log "✅ Running containers: $container_count"
    
    return 0
}

# Check Nginx
check_nginx() {
    log "Checking Nginx..."
    
    if systemctl is-active --quiet nginx; then
        log "✅ Nginx is running"
    else
        log_error "❌ Nginx is not running"
        return 1
    fi
    
    if nginx -t >/dev/null 2>&1; then
        log "✅ Nginx configuration is valid"
    else
        log_error "❌ Nginx configuration is invalid"
        return 1
    fi
    
    # Check if Nginx can reach backend
    if curl -f -s http://localhost/health >/dev/null 2>&1; then
        log "✅ Nginx can reach backend services"
    else
        log_warning "⚠️ Nginx cannot reach backend services"
    fi
    
    return 0
}

# Generate health report
generate_report() {
    local report_file="${HOME}/mantrapath-health-report-$(date +%Y%m%d-%H%M%S).txt"
    
    log "Generating health report: $report_file"
    
    {
        echo "MantraPath Health Report - $(date)"
        echo "=================================="
        echo ""
        
        echo "System Information:"
        echo "------------------"
        echo "Hostname: $(hostname)"
        echo "Uptime: $(uptime)"
        echo "Load Average: $(cat /proc/loadavg)"
        echo ""
        
        echo "Docker Services:"
        echo "---------------"
        cd "$BACKEND_DIR"
        docker-compose -f docker-compose.prod.yml ps
        echo ""
        
        echo "System Resources:"
        echo "----------------"
        echo "Disk Usage:"
        df -h
        echo ""
        echo "Memory Usage:"
        free -h
        echo ""
        echo "Docker Stats:"
        docker stats --no-stream
        echo ""
        
        echo "Service Logs (last 50 lines):"
        echo "----------------------------"
        docker-compose -f docker-compose.prod.yml logs --tail=50
        echo ""
        
    } > "$report_file"
    
    log "Health report generated: $report_file"
}

# Main health check function
main() {
    log "Starting MantraPath health check..."
    
    local overall_status=0
    
    # Run all checks
    check_docker_services || overall_status=1
    check_database || overall_status=1
    check_api_endpoints || overall_status=1
    check_system_resources || overall_status=1
    check_nginx || overall_status=1
    
    # Generate report
    generate_report
    
    if [ $overall_status -eq 0 ]; then
        log "🎉 All health checks passed!"
        exit 0
    else
        log_error "💥 Some health checks failed!"
        exit 1
    fi
}

# Handle script arguments
case "${1:-}" in
    "quick")
        log "Running quick health check..."
        check_docker_services
        check_api_endpoints
        ;;
    "report")
        generate_report
        ;;
    "docker")
        check_docker_services
        ;;
    "api")
        check_api_endpoints
        ;;
    "system")
        check_system_resources
        ;;
    "nginx")
        check_nginx
        ;;
    *)
        main
        ;;
esac
