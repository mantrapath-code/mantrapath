#!/bin/bash
# MantraPath Health Monitoring and Alerting Script
# This script monitors the health of all MantraPath services and can automatically restart failed services

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKEND_DIR="$PROJECT_ROOT/backend"
LOG_FILE="/var/log/mantrapath/health-monitor.log"
ALERT_FILE="/var/log/mantrapath/alerts.log"
RESTART_THRESHOLD=3  # Number of consecutive failures before restart
NOTIFICATION_WEBHOOK="${NOTIFICATION_WEBHOOK:-}"  # Optional webhook for alerts

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Ensure log directory exists
sudo mkdir -p "$(dirname "$LOG_FILE")" 2>/dev/null || mkdir -p "$(dirname "$LOG_FILE")" 2>/dev/null || {
    # Fallback to /tmp if we can't create in /var/log
    LOG_FILE="/tmp/mantrapath-health-monitor.log"
    ALERT_FILE="/tmp/mantrapath-alerts.log"
    mkdir -p "$(dirname "$LOG_FILE")"
    mkdir -p "$(dirname "$ALERT_FILE")"
}

# Logging functions
log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE" 2>/dev/null || true
}

log_error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1" >> "$LOG_FILE" 2>/dev/null || true
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1" >> "$ALERT_FILE" 2>/dev/null || true
}

log_warning() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] WARNING: $1" >> "$LOG_FILE" 2>/dev/null || true
}

log_info() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')] INFO:${NC} $1"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] INFO: $1" >> "$LOG_FILE" 2>/dev/null || true
}

# Send notification function
send_notification() {
    local message="$1"
    local severity="${2:-info}"
    
    if [ -n "$NOTIFICATION_WEBHOOK" ]; then
        curl -X POST "$NOTIFICATION_WEBHOOK" \
            -H "Content-Type: application/json" \
            -d "{\"text\":\"[MantraPath $severity] $message\"}" \
            >/dev/null 2>&1 || true
    fi
    
    # Log to system journal
    logger -t mantrapath-monitor "[$severity] $message"
}

# Check service health
check_service_health() {
    local service_name="$1"
    local port="$2"
    local endpoint="${3:-/health}"
    local timeout="${4:-10}"
    
    if curl -f -s --max-time "$timeout" "http://localhost:$port$endpoint" >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Check Docker container status
check_container_status() {
    local container_name="$1"
    
    if docker ps --format "{{.Names}}" | grep -q "^${container_name}$"; then
        if [ "$(docker inspect --format='{{.State.Health.Status}}' "$container_name" 2>/dev/null)" = "healthy" ]; then
            return 0
        elif [ "$(docker inspect --format='{{.State.Status}}' "$container_name" 2>/dev/null)" = "running" ]; then
            return 0  # Running but no health check defined
        fi
    fi
    return 1
}

# Get service failure count
get_failure_count() {
    local service="$1"
    local count_file="/tmp/mantrapath_failures_${service}"
    
    if [ -f "$count_file" ]; then
        cat "$count_file"
    else
        echo "0"
    fi
}

# Increment failure count
increment_failure_count() {
    local service="$1"
    local count_file="/tmp/mantrapath_failures_${service}"
    local current_count=$(get_failure_count "$service")
    
    echo $((current_count + 1)) > "$count_file"
}

# Reset failure count
reset_failure_count() {
    local service="$1"
    local count_file="/tmp/mantrapath_failures_${service}"
    
    rm -f "$count_file"
}

# Restart service
restart_service() {
    local service="$1"
    
    log_warning "Attempting to restart $service..."
    
    cd "$BACKEND_DIR"
    
    if docker-compose -f docker-compose.prod.yml restart "$service"; then
        log "✅ Successfully restarted $service"
        reset_failure_count "$service"
        send_notification "Service $service has been restarted successfully" "warning"
        return 0
    else
        log_error "❌ Failed to restart $service"
        send_notification "Failed to restart service $service" "error"
        return 1
    fi
}

# Restart all services
restart_all_services() {
    log_warning "Restarting all MantraPath services..."
    
    cd "$BACKEND_DIR"
    
    if docker-compose -f docker-compose.prod.yml restart; then
        log "✅ Successfully restarted all services"
        # Reset all failure counts
        rm -f /tmp/mantrapath_failures_*
        send_notification "All MantraPath services have been restarted" "warning"
        return 0
    else
        log_error "❌ Failed to restart all services"
        send_notification "Failed to restart all MantraPath services" "error"
        return 1
    fi
}

# Check system resources
check_system_resources() {
    local disk_usage=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
    local memory_usage=$(free | awk '/^Mem:/ {printf "%.0f", $3/$2 * 100}')
    local load_average=$(uptime | awk -F'load average:' '{print $2}' | awk '{print $1}' | sed 's/,//')
    
    # Check disk usage (alert if > 90%)
    if [ "$disk_usage" -gt 90 ]; then
        log_warning "⚠️ High disk usage: ${disk_usage}%"
        send_notification "High disk usage: ${disk_usage}%" "warning"
    fi
    
    # Check memory usage (alert if > 90%)
    if [ "$memory_usage" -gt 90 ]; then
        log_warning "⚠️ High memory usage: ${memory_usage}%"
        send_notification "High memory usage: ${memory_usage}%" "warning"
    fi
    
    # Check load average (alert if > 4.0)
    if [ "$(echo "$load_average > 4.0" | bc -l 2>/dev/null || echo 0)" -eq 1 ]; then
        log_warning "⚠️ High system load: $load_average"
        send_notification "High system load: $load_average" "warning"
    fi
}

# Main monitoring function
monitor_services() {
    local mode="${1:-check}"  # check, restart, or force-restart
    
    log_info "Starting health monitoring (mode: $mode)..."
    
    # Define services to monitor
    local services=(
        "api-gateway:8000:/health/live"
        "auth-service:8001:/health"
        "profile-service:8002:/health"
        "mood-service:8003:/health"
        "chatbot-service:8004:/health"
        "content-service:8005:/health"
        "community-service:8006:/health"
        "notification-service:8007:/health"
        "ml-service:8008:/health"
        "models-service:8081:/health"
        "translation-service:8010:/health"
        "voice-service:8011:/health"
        "action-orchestrator:8012:/health"
        "ai-context-store:8013:/health"
        "ai-event-processor:8014:/health"
        "memory-service:8017:/health/live"
    )
    
    local failed_services=()
    local critical_failures=0
    
    # Check each service
    for service_config in "${services[@]}"; do
        IFS=':' read -r service_name port endpoint <<< "$service_config"
        
        if check_service_health "$service_name" "$port" "$endpoint"; then
            log "✅ $service_name - Healthy"
            reset_failure_count "$service_name"
        else
            log_error "❌ $service_name - Unhealthy"
            failed_services+=("$service_name")
            increment_failure_count "$service_name"
            
            local failure_count=$(get_failure_count "$service_name")
            
            # Check if this is a critical service
            case "$service_name" in
                "api-gateway"|"auth-service"|"models-service")
                    ((critical_failures++))
                    ;;
            esac
            
            # Restart service if it has failed multiple times and restart mode is enabled
            if [ "$mode" = "restart" ] && [ "$failure_count" -ge "$RESTART_THRESHOLD" ]; then
                restart_service "$service_name"
            fi
        fi
    done
    
    # Check infrastructure services
    log_info "Checking infrastructure services..."
    
    # Check PostgreSQL
    cd "$BACKEND_DIR"
    if docker-compose -f docker-compose.prod.yml exec -T postgres pg_isready -U mantrapath -d mantrapath >/dev/null 2>&1; then
        log "✅ PostgreSQL - Healthy"
        reset_failure_count "postgres"
    else
        log_error "❌ PostgreSQL - Unhealthy"
        failed_services+=("postgres")
        increment_failure_count "postgres"
        ((critical_failures++))
        
        if [ "$mode" = "restart" ] && [ "$(get_failure_count "postgres")" -ge "$RESTART_THRESHOLD" ]; then
            restart_service "postgres"
        fi
    fi
    
    # Check Redis
    if docker-compose -f docker-compose.prod.yml exec -T redis redis-cli ping 2>/dev/null | grep -q PONG; then
        log "✅ Redis - Healthy"
        reset_failure_count "redis"
    else
        log_error "❌ Redis - Unhealthy"
        failed_services+=("redis")
        increment_failure_count "redis"
        ((critical_failures++))
        
        if [ "$mode" = "restart" ] && [ "$(get_failure_count "redis")" -ge "$RESTART_THRESHOLD" ]; then
            restart_service "redis"
        fi
    fi
    
    # Check NATS
    if check_service_health "nats" "8222" "/healthz"; then
        log "✅ NATS - Healthy"
        reset_failure_count "nats"
    else
        log_error "❌ NATS - Unhealthy"
        failed_services+=("nats")
        increment_failure_count "nats"
        
        if [ "$mode" = "restart" ] && [ "$(get_failure_count "nats")" -ge "$RESTART_THRESHOLD" ]; then
            restart_service "nats"
        fi
    fi
    
    # Check Nginx
    if systemctl is-active --quiet nginx; then
        log "✅ Nginx - Running"
    else
        log_error "❌ Nginx - Not running"
        failed_services+=("nginx")
        
        if [ "$mode" = "restart" ]; then
            systemctl restart nginx && log "✅ Nginx restarted" || log_error "❌ Failed to restart Nginx"
        fi
    fi
    
    # Check system resources
    check_system_resources
    
    # Summary and actions
    if [ ${#failed_services[@]} -eq 0 ]; then
        log "🎉 All services are healthy!"
        return 0
    else
        log_warning "⚠️ Failed services (${#failed_services[@]}): ${failed_services[*]}"
        
        # If too many critical services are down, restart everything
        if [ "$critical_failures" -gt 2 ] && [ "$mode" = "restart" ]; then
            log_warning "Too many critical services down, restarting all services..."
            restart_all_services
        elif [ "$mode" = "force-restart" ]; then
            restart_all_services
        fi
        
        return 1
    fi
}

# Generate health report
generate_health_report() {
    local report_file="/var/log/mantrapath/health-report-$(date +%Y%m%d_%H%M%S).json"
    
    log_info "Generating health report..."
    
    cat > "$report_file" << EOF
{
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "hostname": "$(hostname)",
    "services": {
EOF

    # Check each service and add to JSON
    local first=true
    local services=(
        "api-gateway:8000"
        "auth-service:8001"
        "profile-service:8002"
        "mood-service:8003"
        "chatbot-service:8004"
        "ml-service:8008"
        "models-service:8081"
    )
    
    for service_config in "${services[@]}"; do
        IFS=':' read -r service_name port <<< "$service_config"
        
        if [ "$first" = false ]; then
            echo "," >> "$report_file"
        fi
        first=false
        
        local status="unhealthy"
        local response_time="null"
        
        if check_service_health "$service_name" "$port"; then
            status="healthy"
            response_time=$(curl -o /dev/null -s -w "%{time_total}" "http://localhost:$port/health" 2>/dev/null || echo "null")
        fi
        
        cat >> "$report_file" << EOF
        "$service_name": {
            "status": "$status",
            "port": $port,
            "response_time": $response_time,
            "failure_count": $(get_failure_count "$service_name")
        }
EOF
    done
    
    # Add system info
    cat >> "$report_file" << EOF
    },
    "system": {
        "disk_usage": "$(df / | awk 'NR==2 {print $5}')",
        "memory_usage": "$(free | awk '/^Mem:/ {printf "%.1f%%", $3/$2 * 100}')",
        "load_average": "$(uptime | awk -F'load average:' '{print $2}' | awk '{print $1}' | sed 's/,//')",
        "uptime": "$(uptime -p)"
    }
}
EOF

    log "✅ Health report generated: $report_file"
    echo "$report_file"
}

# Cleanup old logs
cleanup_logs() {
    log_info "Cleaning up old log files..."
    
    # Keep only last 30 days of logs
    find /var/log/mantrapath -name "*.log" -mtime +30 -delete || true
    find /var/log/mantrapath -name "health-report-*.json" -mtime +7 -delete || true
    
    # Keep only last 100 lines in main log files
    if [ -f "$LOG_FILE" ]; then
        tail -n 100 "$LOG_FILE" > "${LOG_FILE}.tmp" && mv "${LOG_FILE}.tmp" "$LOG_FILE"
    fi
    
    if [ -f "$ALERT_FILE" ]; then
        tail -n 100 "$ALERT_FILE" > "${ALERT_FILE}.tmp" && mv "${ALERT_FILE}.tmp" "$ALERT_FILE"
    fi
    
    log "✅ Log cleanup completed"
}

# Main function
main() {
    case "${1:-check}" in
        "check")
            monitor_services "check"
            ;;
        "restart")
            monitor_services "restart"
            ;;
        "force-restart")
            monitor_services "force-restart"
            ;;
        "report")
            generate_health_report
            ;;
        "cleanup")
            cleanup_logs
            ;;
        "status")
            log_info "MantraPath Health Monitor Status"
            echo "Log file: $LOG_FILE"
            echo "Alert file: $ALERT_FILE"
            echo "Recent alerts:"
            tail -n 10 "$ALERT_FILE" 2>/dev/null || echo "No recent alerts"
            ;;
        *)
            echo "Usage: $0 {check|restart|force-restart|report|cleanup|status}"
            echo ""
            echo "Commands:"
            echo "  check         - Check service health (no restart)"
            echo "  restart       - Check health and restart failed services"
            echo "  force-restart - Force restart all services"
            echo "  report        - Generate detailed health report"
            echo "  cleanup       - Clean up old log files"
            echo "  status        - Show monitor status"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
