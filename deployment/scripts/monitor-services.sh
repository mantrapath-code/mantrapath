#!/bin/bash

# MantraPath Service Monitoring Script
# This script monitors all deployed services and provides health status

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE_DEV="mantrapath-dev"
NAMESPACE_PROD="mantrapath-prod"
WATCH_INTERVAL=30
MAX_RETRIES=3

# Default values
ENVIRONMENT="dev"
WATCH_MODE="false"
DETAILED="false"
ONLY_UNHEALTHY="false"

# Service port mappings for local testing
declare -A SERVICE_PORTS=(
    ["api-gateway"]="8000"
    ["translation-service"]="8010"
    ["models-service"]="8080"
    ["auth-service"]="8001"
    ["chatbot-service"]="8003"
    ["voice-service"]="8007"
    ["ml-service"]="8004"
    ["mood-service"]="8015"
    ["profile-service"]="8002"
    ["content-service"]="8009"
    ["community-service"]="8011"
    ["notification-service"]="8013"
    ["memory-service"]="8014"
    ["media-service"]="8012"
    ["ai-context-store"]="8005"
    ["ai-event-processor"]="8006"
    ["action-orchestrator"]="8016"
    ["voice-event-processor"]="8008"
    ["proactive-assistance"]="8017"
    ["deployment-api"]="8086"
    ["phi3-agent"]="8018"
    ["frontend"]="3000"
)

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${PURPLE}=== $1 ===${NC}"
}

# Function to show usage
usage() {
    cat << EOF
MantraPath Service Monitoring Script

Usage: $0 [OPTIONS]

Options:
    -e, --environment ENV       Target environment (dev|prod) [default: dev]
    -w, --watch                Enable watch mode (continuous monitoring)
    -d, --detailed             Show detailed service information
    -u, --unhealthy-only       Show only unhealthy services
    -i, --interval SECONDS     Watch mode interval in seconds [default: 30]
    -h, --help                 Show this help message

Examples:
    $0 -e dev                           # Check dev environment once
    $0 -e prod -w -i 60                # Watch prod environment every 60 seconds
    $0 -d -u                           # Show detailed info for unhealthy services only
    $0 -e dev --watch --detailed       # Continuous detailed monitoring of dev

EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -w|--watch)
            WATCH_MODE="true"
            shift
            ;;
        -d|--detailed)
            DETAILED="true"
            shift
            ;;
        -u|--unhealthy-only)
            ONLY_UNHEALTHY="true"
            shift
            ;;
        -i|--interval)
            WATCH_INTERVAL="$2"
            shift 2
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

# Validate environment
if [[ "$ENVIRONMENT" != "dev" && "$ENVIRONMENT" != "prod" ]]; then
    print_error "Environment must be 'dev' or 'prod'"
    exit 1
fi

# Set namespace based on environment
if [[ "$ENVIRONMENT" == "prod" ]]; then
    NAMESPACE="$NAMESPACE_PROD"
else
    NAMESPACE="$NAMESPACE_DEV"
fi

# Function to check if kubectl is available and configured
check_kubectl() {
    if ! command -v kubectl &> /dev/null; then
        print_error "kubectl is not installed or not in PATH"
        exit 1
    fi
    
    if ! kubectl cluster-info &> /dev/null; then
        print_error "kubectl is not configured or cluster is not accessible"
        exit 1
    fi
}

# Function to check if namespace exists
check_namespace() {
    if ! kubectl get namespace "$NAMESPACE" &> /dev/null; then
        print_error "Namespace '$NAMESPACE' does not exist"
        exit 1
    fi
}

# Function to get pod status
get_pod_status() {
    local service_name="$1"
    local pod_info
    
    pod_info=$(kubectl get pods -n "$NAMESPACE" -l component="$service_name" -o json 2>/dev/null || echo '{"items":[]}')
    
    local pod_count
    pod_count=$(echo "$pod_info" | jq -r '.items | length')
    
    if [[ "$pod_count" -eq 0 ]]; then
        echo "NO_PODS"
        return
    fi
    
    local ready_count=0
    local running_count=0
    local total_count=0
    
    while IFS= read -r pod; do
        if [[ -n "$pod" ]]; then
            local phase
            phase=$(echo "$pod" | jq -r '.status.phase // "Unknown"')
            
            local ready_conditions
            ready_conditions=$(echo "$pod" | jq -r '.status.conditions[]? | select(.type=="Ready") | .status // "False"')
            
            ((total_count++))
            
            if [[ "$phase" == "Running" ]]; then
                ((running_count++))
            fi
            
            if [[ "$ready_conditions" == "True" ]]; then
                ((ready_count++))
            fi
        fi
    done < <(echo "$pod_info" | jq -c '.items[]')
    
    echo "${ready_count}/${total_count}"
}

# Function to check service health endpoint
check_service_health() {
    local service_name="$1"
    local port="${SERVICE_PORTS[$service_name]:-8000}"
    
    # Try to port-forward and check health endpoint
    local health_status="UNKNOWN"
    local response_time="N/A"
    
    # Start port-forward in background
    kubectl port-forward "svc/mantrapath-$ENVIRONMENT-$service_name" "$port:$port" -n "$NAMESPACE" &>/dev/null &
    local pf_pid=$!
    
    # Wait a moment for port-forward to establish
    sleep 2
    
    # Check health endpoint
    local start_time
    start_time=$(date +%s.%N)
    
    if curl -s --max-time 5 "http://localhost:$port/health" &>/dev/null; then
        local end_time
        end_time=$(date +%s.%N)
        response_time=$(echo "$end_time - $start_time" | bc | xargs printf "%.3f")
        health_status="HEALTHY"
    else
        health_status="UNHEALTHY"
    fi
    
    # Clean up port-forward
    kill $pf_pid 2>/dev/null || true
    
    echo "$health_status:$response_time"
}

# Function to get service details
get_service_details() {
    local service_name="$1"
    
    local pod_status
    pod_status=$(get_pod_status "$service_name")
    
    local health_info
    health_info=$(check_service_health "$service_name")
    local health_status
    health_status=$(echo "$health_info" | cut -d: -f1)
    local response_time
    response_time=$(echo "$health_info" | cut -d: -f2)
    
    # Get resource usage
    local cpu_usage="N/A"
    local memory_usage="N/A"
    
    if kubectl top pods -n "$NAMESPACE" -l component="$service_name" &>/dev/null; then
        local resource_info
        resource_info=$(kubectl top pods -n "$NAMESPACE" -l component="$service_name" --no-headers 2>/dev/null | head -1)
        if [[ -n "$resource_info" ]]; then
            cpu_usage=$(echo "$resource_info" | awk '{print $2}')
            memory_usage=$(echo "$resource_info" | awk '{print $3}')
        fi
    fi
    
    echo "$pod_status:$health_status:$response_time:$cpu_usage:$memory_usage"
}

# Function to display service status
display_service_status() {
    local service_name="$1"
    local details="$2"
    
    IFS=':' read -ra DETAILS <<< "$details"
    local pod_status="${DETAILS[0]}"
    local health_status="${DETAILS[1]}"
    local response_time="${DETAILS[2]}"
    local cpu_usage="${DETAILS[3]}"
    local memory_usage="${DETAILS[4]}"
    
    # Determine overall status color
    local status_color="$RED"
    local overall_status="UNHEALTHY"
    
    if [[ "$pod_status" != "NO_PODS" && "$health_status" == "HEALTHY" ]]; then
        status_color="$GREEN"
        overall_status="HEALTHY"
    elif [[ "$pod_status" != "NO_PODS" && "$health_status" == "UNKNOWN" ]]; then
        status_color="$YELLOW"
        overall_status="DEGRADED"
    fi
    
    # Skip if only showing unhealthy and this service is healthy
    if [[ "$ONLY_UNHEALTHY" == "true" && "$overall_status" == "HEALTHY" ]]; then
        return
    fi
    
    printf "%-25s ${status_color}%-10s${NC} %-12s %-12s" "$service_name" "$overall_status" "$pod_status" "$health_status"
    
    if [[ "$DETAILED" == "true" ]]; then
        printf " %-10s %-10s %-10s" "$response_time" "$cpu_usage" "$memory_usage"
    fi
    
    echo ""
}

# Function to monitor all services
monitor_services() {
    print_header "MantraPath Service Status - $ENVIRONMENT Environment"
    echo "Namespace: $NAMESPACE"
    echo "Timestamp: $(date)"
    echo ""
    
    # Header
    printf "%-25s %-10s %-12s %-12s" "SERVICE" "STATUS" "PODS" "HEALTH"
    if [[ "$DETAILED" == "true" ]]; then
        printf " %-10s %-10s %-10s" "RESP_TIME" "CPU" "MEMORY"
    fi
    echo ""
    printf "%-25s %-10s %-12s %-12s" "-------" "------" "----" "------"
    if [[ "$DETAILED" == "true" ]]; then
        printf " %-10s %-10s %-10s" "---------" "---" "------"
    fi
    echo ""
    
    # Check each service
    local total_services=0
    local healthy_services=0
    local unhealthy_services=0
    
    for service in "${!SERVICE_PORTS[@]}"; do
        ((total_services++))
        
        local details
        details=$(get_service_details "$service")
        
        display_service_status "$service" "$details"
        
        # Count healthy/unhealthy
        local health_status
        health_status=$(echo "$details" | cut -d: -f2)
        if [[ "$health_status" == "HEALTHY" ]]; then
            ((healthy_services++))
        else
            ((unhealthy_services++))
        fi
    done
    
    echo ""
    print_header "Summary"
    echo "Total Services: $total_services"
    echo -e "Healthy: ${GREEN}$healthy_services${NC}"
    echo -e "Unhealthy: ${RED}$unhealthy_services${NC}"
    
    # Overall system status
    if [[ $unhealthy_services -eq 0 ]]; then
        echo -e "Overall Status: ${GREEN}ALL SYSTEMS OPERATIONAL${NC}"
    elif [[ $healthy_services -gt $unhealthy_services ]]; then
        echo -e "Overall Status: ${YELLOW}DEGRADED PERFORMANCE${NC}"
    else
        echo -e "Overall Status: ${RED}SYSTEM ISSUES DETECTED${NC}"
    fi
    
    echo ""
}

# Function to show cluster information
show_cluster_info() {
    print_header "Cluster Information"
    
    echo "Kubernetes Context: $(kubectl config current-context)"
    echo "Cluster Info:"
    kubectl cluster-info | head -3
    
    echo ""
    echo "Node Status:"
    kubectl get nodes --no-headers | awk '{printf "  %-20s %s\n", $1, $2}'
    
    echo ""
    echo "Namespace Resources:"
    kubectl get all -n "$NAMESPACE" --no-headers | wc -l | xargs echo "  Total Resources:"
    
    echo ""
}

# Function to show troubleshooting information
show_troubleshooting_info() {
    print_header "Troubleshooting Information"
    
    echo "Quick Commands:"
    echo "  View all pods:           kubectl get pods -n $NAMESPACE"
    echo "  View services:           kubectl get services -n $NAMESPACE"
    echo "  View events:             kubectl get events -n $NAMESPACE --sort-by=.metadata.creationTimestamp"
    echo "  Describe failing pod:    kubectl describe pod <pod-name> -n $NAMESPACE"
    echo "  View pod logs:           kubectl logs <pod-name> -n $NAMESPACE"
    echo "  Port forward service:    kubectl port-forward svc/<service-name> <local-port>:<service-port> -n $NAMESPACE"
    echo ""
    
    echo "Common Issues:"
    echo "  • Image pull errors: Check registry credentials and image tags"
    echo "  • CrashLoopBackOff: Check application logs and configuration"
    echo "  • Pending pods: Check resource requests and node capacity"
    echo "  • Service unreachable: Check service discovery and networking"
    echo ""
}

# Function to run continuous monitoring
run_watch_mode() {
    print_status "Starting continuous monitoring (Ctrl+C to stop)"
    print_status "Update interval: ${WATCH_INTERVAL} seconds"
    echo ""
    
    while true; do
        clear
        monitor_services
        
        if [[ "$DETAILED" == "true" ]]; then
            show_cluster_info
        fi
        
        echo ""
        print_status "Next update in $WATCH_INTERVAL seconds... (Ctrl+C to stop)"
        
        sleep "$WATCH_INTERVAL"
    done
}

# Main execution
main() {
    check_kubectl
    check_namespace
    
    if [[ "$WATCH_MODE" == "true" ]]; then
        run_watch_mode
    else
        monitor_services
        
        if [[ "$DETAILED" == "true" ]]; then
            show_cluster_info
            show_troubleshooting_info
        fi
    fi
}

# Handle Ctrl+C gracefully
trap 'echo -e "\n${YELLOW}Monitoring stopped by user${NC}"; exit 0' INT

# Run main function
main "$@"
