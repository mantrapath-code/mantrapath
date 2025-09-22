#!/bin/bash

# MantraPath Health Monitoring Script
# Comprehensive health monitoring for all services
# Author: MantraPath Team

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

# Default configuration
ENVIRONMENT="dev"
NAMESPACE=""
WATCH_MODE=false
WATCH_INTERVAL=30
DETAILED=false
OUTPUT_FORMAT="table"
ALERT_THRESHOLD=80  # CPU/Memory percentage

show_usage() {
    cat << EOF
${BOLD}MantraPath Health Monitor${NC}

Usage: $0 [OPTIONS]

${BOLD}Options:${NC}
  -e, --env ENVIRONMENT      Target environment [default: dev]
  -n, --namespace NAMESPACE  Kubernetes namespace [default: mantrapath-{env}]
  -w, --watch               Watch mode (refresh automatically)
  -i, --interval SECONDS    Watch interval [default: 30]
  -d, --detailed            Show detailed information
  -f, --format FORMAT       Output format (table|json|yaml) [default: table]
  -t, --threshold PERCENT   Alert threshold for resources [default: 80]
  -h, --help                Show this help message

${BOLD}Examples:${NC}
  $0 --env prod                    # Check production health
  $0 --watch --interval 10         # Watch with 10s interval
  $0 --detailed --format json      # Detailed output in JSON format

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

check_prerequisites() {
    for cmd in kubectl helm jq; do
        if ! command -v "$cmd" &> /dev/null; then
            log_error "Required command '$cmd' not found"
            exit 1
        fi
    done
    
    if ! kubectl cluster-info &> /dev/null; then
        log_error "Cannot connect to Kubernetes cluster"
        exit 1
    fi
}

setup_environment() {
    if [[ -z "$NAMESPACE" ]]; then
        NAMESPACE="mantrapath-$ENVIRONMENT"
    fi
    
    if ! kubectl get namespace "$NAMESPACE" &> /dev/null; then
        log_error "Namespace '$NAMESPACE' not found"
        exit 1
    fi
}

get_service_health() {
    local service_name=$1
    local pod_name=$2
    
    # Check if service has health endpoint
    local health_check=""
    case $service_name in
        *api-gateway*|*translation*|*models*|*auth*|*profile*|*chatbot*|*content*|*community*|*notification*|*ml*|*voice*|*mood*|*memory*|*action-orchestrator*|*ai-context*|*ai-event*|*proactive*)
            health_check="/health"
            ;;
        *frontend*)
            health_check="/"
            ;;
        *postgres*|*redis*|*nats*)
            health_check=""  # No HTTP health check
            ;;
    esac
    
    if [[ -n "$health_check" ]]; then
        # Try to get health status
        local health_status
        health_status=$(kubectl exec -n "$NAMESPACE" "$pod_name" -- wget -q -O- "http://localhost:8000$health_check" 2>/dev/null || echo "UNKNOWN")
        
        if [[ "$health_status" == *"healthy"* || "$health_status" == *"ok"* || "$health_status" == *"200"* ]]; then
            echo "HEALTHY"
        else
            echo "UNHEALTHY"
        fi
    else
        # For services without HTTP health checks, check if container is ready
        local ready_status
        ready_status=$(kubectl get pod "$pod_name" -n "$NAMESPACE" -o jsonpath='{.status.conditions[?(@.type=="Ready")].status}' 2>/dev/null || echo "Unknown")
        
        if [[ "$ready_status" == "True" ]]; then
            echo "READY"
        else
            echo "NOT_READY"
        fi
    fi
}

get_resource_usage() {
    local pod_name=$1
    
    # Get CPU and memory usage
    local usage_data
    usage_data=$(kubectl top pod "$pod_name" -n "$NAMESPACE" --no-headers 2>/dev/null || echo "$pod_name 0m 0Mi")
    
    local cpu_usage
    local memory_usage
    cpu_usage=$(echo "$usage_data" | awk '{print $2}' | sed 's/m$//')
    memory_usage=$(echo "$usage_data" | awk '{print $3}' | sed 's/Mi$//')
    
    # Convert to percentages (this is simplified - in reality you'd need the limits)
    local cpu_percent=0
    local memory_percent=0
    
    if [[ "$cpu_usage" != "0" ]]; then
        cpu_percent=$((cpu_usage / 10))  # Simplified calculation
    fi
    
    if [[ "$memory_usage" != "0" ]]; then
        memory_percent=$((memory_usage / 10))  # Simplified calculation
    fi
    
    echo "${cpu_percent},${memory_percent}"
}

check_pod_health() {
    echo -e "\n${BOLD}Pod Health Status${NC}"
    echo "=================================================================="
    
    if [[ "$OUTPUT_FORMAT" == "json" ]]; then
        echo "{"
        echo "  \"pods\": ["
    elif [[ "$OUTPUT_FORMAT" == "table" ]]; then
        printf "%-30s %-15s %-10s %-15s %-10s %-10s\n" "POD NAME" "SERVICE" "STATUS" "HEALTH" "CPU%" "MEMORY%"
        echo "------------------------------------------------------------------"
    fi
    
    local pods
    pods=$(kubectl get pods -n "$NAMESPACE" -o jsonpath='{.items[*].metadata.name}')
    
    local pod_count=0
    local healthy_count=0
    
    for pod in $pods; do
        local service_label
        service_label=$(kubectl get pod "$pod" -n "$NAMESPACE" -o jsonpath='{.metadata.labels.app\.kubernetes\.io/name}' 2>/dev/null || echo "unknown")
        
        local pod_status
        pod_status=$(kubectl get pod "$pod" -n "$NAMESPACE" -o jsonpath='{.status.phase}')
        
        local health_status
        health_status=$(get_service_health "$service_label" "$pod")
        
        local resource_usage
        resource_usage=$(get_resource_usage "$pod")
        local cpu_percent
        local memory_percent
        cpu_percent=$(echo "$resource_usage" | cut -d',' -f1)
        memory_percent=$(echo "$resource_usage" | cut -d',' -f2)
        
        ((pod_count++))
        
        if [[ "$pod_status" == "Running" && ("$health_status" == "HEALTHY" || "$health_status" == "READY") ]]; then
            ((healthy_count++))
        fi
        
        # Color coding based on status
        local status_color=$RED
        if [[ "$pod_status" == "Running" ]]; then
            status_color=$GREEN
        fi
        
        local health_color=$RED
        if [[ "$health_status" == "HEALTHY" || "$health_status" == "READY" ]]; then
            health_color=$GREEN
        fi
        
        # Alert on high resource usage
        local cpu_alert=""
        local memory_alert=""
        if [[ "$cpu_percent" -gt "$ALERT_THRESHOLD" ]]; then
            cpu_alert="⚠️"
        fi
        if [[ "$memory_percent" -gt "$ALERT_THRESHOLD" ]]; then
            memory_alert="⚠️"
        fi
        
        if [[ "$OUTPUT_FORMAT" == "json" ]]; then
            [[ $pod_count -gt 1 ]] && echo ","
            cat << EOF
    {
      "name": "$pod",
      "service": "$service_label",
      "status": "$pod_status",
      "health": "$health_status",
      "cpu_percent": $cpu_percent,
      "memory_percent": $memory_percent
    }
EOF
        elif [[ "$OUTPUT_FORMAT" == "table" ]]; then
            printf "%-30s %-15s ${status_color}%-10s${NC} ${health_color}%-15s${NC} %-8s%-2s %-8s%-2s\n" \
                "$pod" "$service_label" "$pod_status" "$health_status" "$cpu_percent" "$cpu_alert" "$memory_percent" "$memory_alert"
        fi
    done
    
    if [[ "$OUTPUT_FORMAT" == "json" ]]; then
        echo
        echo "  ],"
        echo "  \"summary\": {"
        echo "    \"total_pods\": $pod_count,"
        echo "    \"healthy_pods\": $healthy_count,"
        echo "    \"health_percentage\": $((healthy_count * 100 / pod_count))"
        echo "  }"
        echo "}"
    else
        echo
        echo -e "${BOLD}Summary:${NC} $healthy_count/$pod_count pods healthy ($((healthy_count * 100 / pod_count))%)"
    fi
}

check_service_endpoints() {
    echo -e "\n${BOLD}Service Endpoints${NC}"
    echo "=================================================================="
    
    local services
    services=$(kubectl get services -n "$NAMESPACE" -o jsonpath='{.items[*].metadata.name}')
    
    for service in $services; do
        local endpoints
        endpoints=$(kubectl get endpoints "$service" -n "$NAMESPACE" -o jsonpath='{.subsets[*].addresses[*].ip}' 2>/dev/null || echo "")
        
        local endpoint_count
        endpoint_count=$(echo "$endpoints" | wc -w)
        
        local port
        port=$(kubectl get service "$service" -n "$NAMESPACE" -o jsonpath='{.spec.ports[0].port}')
        
        if [[ "$endpoint_count" -gt 0 ]]; then
            echo -e "${GREEN}✓${NC} $service:$port ($endpoint_count endpoints)"
        else
            echo -e "${RED}✗${NC} $service:$port (no endpoints)"
        fi
    done
}

check_ingress_status() {
    echo -e "\n${BOLD}Ingress Status${NC}"
    echo "=================================================================="
    
    local ingresses
    ingresses=$(kubectl get ingress -n "$NAMESPACE" -o jsonpath='{.items[*].metadata.name}' 2>/dev/null || echo "")
    
    if [[ -z "$ingresses" ]]; then
        echo "No ingresses found"
        return
    fi
    
    for ingress in $ingresses; do
        local hosts
        hosts=$(kubectl get ingress "$ingress" -n "$NAMESPACE" -o jsonpath='{.spec.rules[*].host}')
        
        local load_balancer
        load_balancer=$(kubectl get ingress "$ingress" -n "$NAMESPACE" -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "")
        
        echo -e "${CYAN}Ingress:${NC} $ingress"
        echo -e "  Hosts: $hosts"
        
        if [[ -n "$load_balancer" ]]; then
            echo -e "  ${GREEN}Load Balancer:${NC} $load_balancer"
        else
            echo -e "  ${YELLOW}Load Balancer:${NC} Pending"
        fi
    done
}

check_persistent_volumes() {
    echo -e "\n${BOLD}Persistent Volume Status${NC}"
    echo "=================================================================="
    
    local pvcs
    pvcs=$(kubectl get pvc -n "$NAMESPACE" -o jsonpath='{.items[*].metadata.name}' 2>/dev/null || echo "")
    
    if [[ -z "$pvcs" ]]; then
        echo "No persistent volume claims found"
        return
    fi
    
    for pvc in $pvcs; do
        local status
        status=$(kubectl get pvc "$pvc" -n "$NAMESPACE" -o jsonpath='{.status.phase}')
        
        local capacity
        capacity=$(kubectl get pvc "$pvc" -n "$NAMESPACE" -o jsonpath='{.status.capacity.storage}')
        
        local storage_class
        storage_class=$(kubectl get pvc "$pvc" -n "$NAMESPACE" -o jsonpath='{.spec.storageClassName}')
        
        if [[ "$status" == "Bound" ]]; then
            echo -e "${GREEN}✓${NC} $pvc ($capacity, $storage_class)"
        else
            echo -e "${RED}✗${NC} $pvc ($status)"
        fi
    done
}

check_recent_events() {
    echo -e "\n${BOLD}Recent Events${NC}"
    echo "=================================================================="
    
    kubectl get events -n "$NAMESPACE" --sort-by='.lastTimestamp' | tail -10
}

show_detailed_info() {
    if [[ "$DETAILED" != "true" ]]; then
        return
    fi
    
    echo -e "\n${BOLD}Detailed Information${NC}"
    echo "=================================================================="
    
    # Helm release info
    echo -e "\n${CYAN}Helm Releases:${NC}"
    helm list -n "$NAMESPACE"
    
    # Resource quotas
    echo -e "\n${CYAN}Resource Quotas:${NC}"
    kubectl get resourcequota -n "$NAMESPACE" 2>/dev/null || echo "No resource quotas found"
    
    # Network policies
    echo -e "\n${CYAN}Network Policies:${NC}"
    kubectl get networkpolicy -n "$NAMESPACE" 2>/dev/null || echo "No network policies found"
}

run_health_check() {
    clear
    echo -e "${BOLD}${CYAN}MantraPath Health Monitor${NC}"
    echo -e "${BOLD}Environment:${NC} $ENVIRONMENT"
    echo -e "${BOLD}Namespace:${NC} $NAMESPACE"
    echo -e "${BOLD}Timestamp:${NC} $(date)"
    
    check_pod_health
    check_service_endpoints
    check_ingress_status
    check_persistent_volumes
    check_recent_events
    show_detailed_info
    
    echo
    echo -e "${BOLD}Health check completed at $(date)${NC}"
    
    if [[ "$WATCH_MODE" == "true" ]]; then
        echo -e "Refreshing in ${WATCH_INTERVAL} seconds... (Press Ctrl+C to exit)"
        sleep "$WATCH_INTERVAL"
    fi
}

main() {
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -e|--env)
                ENVIRONMENT="$2"
                shift 2
                ;;
            -n|--namespace)
                NAMESPACE="$2"
                shift 2
                ;;
            -w|--watch)
                WATCH_MODE=true
                shift
                ;;
            -i|--interval)
                WATCH_INTERVAL="$2"
                shift 2
                ;;
            -d|--detailed)
                DETAILED=true
                shift
                ;;
            -f|--format)
                OUTPUT_FORMAT="$2"
                shift 2
                ;;
            -t|--threshold)
                ALERT_THRESHOLD="$2"
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
    setup_environment
    
    if [[ "$WATCH_MODE" == "true" ]]; then
        while true; do
            run_health_check
        done
    else
        run_health_check
    fi
}

main "$@"