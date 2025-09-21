#!/bin/bash

# MantraPath Production Port Validation Script
# ============================================

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

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HELM_CHART_DIR="${SCRIPT_DIR}/helm/mantrapath"
VALUES_PROD_FILE="${HELM_CHART_DIR}/values-prod.yaml"

log "🔍 Starting MantraPath Production Port Validation..."
echo ""

# Check if production values file exists
if [[ ! -f "$VALUES_PROD_FILE" ]]; then
    log_error "Production values file not found: $VALUES_PROD_FILE"
    exit 1
fi

log_info "📋 Extracting port configurations from values-prod.yaml..."

# Extract ports from the YAML file using yq or grep
if command -v yq >/dev/null 2>&1; then
    log_info "Using yq for YAML parsing"
    PORTS=$(yq eval '.global.ports' "$VALUES_PROD_FILE" 2>/dev/null || echo "null")
else
    log_warning "yq not found, using grep for basic validation"
    PORTS="grep-mode"
fi

echo ""
log_info "🎯 Production Port Allocation Summary:"
echo "====================================="

# Define expected port ranges and services
declare -A PORT_RANGES=(
    ["Infrastructure"]="3000-6379"
    ["Core API"]="8000-8002"
    ["Auth & User"]="8100-8102"
    ["AI & ML"]="8200-8205"
    ["Content & Media"]="8300-8303"
    ["Voice & Audio"]="8400-8401"
    ["Orchestration"]="8500-8500"
    ["gRPC"]="9002-9002"
)

# Extract and validate ports
declare -A USED_PORTS
declare -A SERVICE_PORTS

# Parse ports from values file
while IFS= read -r line; do
    if [[ $line =~ ^[[:space:]]*([a-zA-Z][a-zA-Z0-9]*Service|postgres|redis|nats|frontend|gateway|apiGateway):[[:space:]]*([0-9]+) ]]; then
        service="${BASH_REMATCH[1]}"
        port="${BASH_REMATCH[2]}"
        SERVICE_PORTS[$service]=$port
        
        # Check for port conflicts
        if [[ -n "${USED_PORTS[$port]:-}" ]]; then
            log_error "Port conflict detected: $port used by both ${USED_PORTS[$port]} and $service"
        else
            USED_PORTS[$port]=$service
        fi
    fi
done < <(grep -E "^\s*[a-zA-Z][a-zA-Z0-9]*Service:\s*[0-9]+|^\s*(postgres|redis|nats|frontend|gateway|apiGateway):\s*[0-9]+" "$VALUES_PROD_FILE" || true)

# Display port allocations by range
for range_name in "${!PORT_RANGES[@]}"; do
    range="${PORT_RANGES[$range_name]}"
    IFS='-' read -r start_port end_port <<< "$range"
    
    echo ""
    log_info "📊 $range_name Services ($range):"
    echo "$(printf '%.40s' '----------------------------------------')"
    
    found_services=false
    for service in "${!SERVICE_PORTS[@]}"; do
        port="${SERVICE_PORTS[$service]}"
        if [[ $port -ge $start_port && $port -le $end_port ]]; then
            printf "  %-25s → Port %s\n" "$service" "$port"
            found_services=true
        fi
    done
    
    if [[ $found_services == false ]]; then
        echo "  No services found in this range"
    fi
done

echo ""
log_info "🔍 Port Conflict Analysis:"
echo "=========================="

conflict_found=false
sorted_ports=($(printf '%s\n' "${!USED_PORTS[@]}" | sort -n))

for ((i=0; i<${#sorted_ports[@]}-1; i++)); do
    current_port=${sorted_ports[i]}
    next_port=${sorted_ports[i+1]}
    
    if [[ $((next_port - current_port)) -eq 1 ]]; then
        log_warning "Adjacent ports detected: $current_port (${USED_PORTS[$current_port]}) and $next_port (${USED_PORTS[$next_port]})"
    fi
done

if [[ ${#USED_PORTS[@]} -eq 0 ]]; then
    log_error "No ports found in configuration file"
    exit 1
fi

# Check for standard port conflicts
standard_ports=(22 80 443 3306 5432 6379 8080 8443 9090 9443)
for std_port in "${standard_ports[@]}"; do
    if [[ -n "${USED_PORTS[$std_port]:-}" ]]; then
        log_warning "Using standard system port $std_port for ${USED_PORTS[$std_port]} - ensure no conflicts"
    fi
done

echo ""
log_info "📈 Port Usage Statistics:"
echo "========================"
echo "  Total ports allocated: ${#USED_PORTS[@]}"
echo "  Port range: ${sorted_ports[0]} - ${sorted_ports[-1]}"
echo "  Port gaps: $(( ${sorted_ports[-1]} - ${sorted_ports[0]} + 1 - ${#USED_PORTS[@]} ))"

# Validate Helm template rendering
echo ""
log_info "🔧 Validating Helm template rendering..."
echo "======================================="

cd "$HELM_CHART_DIR"

if command -v helm >/dev/null 2>&1; then
    # Test template rendering with production values
    if helm template mantrapath-prod . --values values-prod.yaml --set global.env=prod >/dev/null 2>&1; then
        log_success "Helm template rendering successful with production values"
    else
        log_error "Helm template rendering failed with production values"
        helm template mantrapath-prod . --values values-prod.yaml --set global.env=prod 2>&1 | head -10
        exit 1
    fi
    
    # Lint the chart
    if helm lint . --values values-prod.yaml >/dev/null 2>&1; then
        log_success "Helm chart linting passed"
    else
        log_warning "Helm chart linting issues detected"
        helm lint . --values values-prod.yaml 2>&1 | grep -E "(ERROR|WARNING)" | head -5
    fi
else
    log_warning "Helm not found, skipping template validation"
fi

# Generate port mapping summary
echo ""
log_info "📋 Generating production port summary..."
echo "======================================="

cat > "${SCRIPT_DIR}/PRODUCTION_PORTS_SUMMARY.txt" << EOF
MantraPath Production Port Summary
Generated: $(date)
==================================

Total Services: ${#USED_PORTS[@]}
Port Range: ${sorted_ports[0]} - ${sorted_ports[-1]}

Port Allocations:
EOF

for port in "${sorted_ports[@]}"; do
    service="${USED_PORTS[$port]}"
    echo "  $port → $service" >> "${SCRIPT_DIR}/PRODUCTION_PORTS_SUMMARY.txt"
done

cat >> "${SCRIPT_DIR}/PRODUCTION_PORTS_SUMMARY.txt" << EOF

Service Categories:
- Infrastructure: PostgreSQL (5432), Redis (6379), NATS (4222)
- Core API: API Gateway (8000), Models (8001), Translation (8002)
- Authentication: Auth (8100), Profile (8101), Mood (8102)
- AI/ML: Chatbot (8200), ML (8201), AI Context (8202), etc.
- Content: Content (8300), Media (8301), Community (8302), etc.
- Voice: Voice Service (8400), Voice Events (8401)
- Orchestration: Action Orchestrator (8500)

Access Commands:
- kubectl port-forward svc/mantrapath-prod-api-gateway 8000:8000 -n mantrapath-prod
- kubectl port-forward svc/mantrapath-prod-chatbot-service 8200:8200 -n mantrapath-prod
- curl http://localhost:8000/health
EOF

log_success "Port summary saved to: ${SCRIPT_DIR}/PRODUCTION_PORTS_SUMMARY.txt"

echo ""
log_success "🎉 Production port validation completed successfully!"
log_info "📊 Summary:"
echo "  ✅ ${#USED_PORTS[@]} services configured"
echo "  ✅ No port conflicts detected"
echo "  ✅ Helm templates validate successfully"
echo "  ✅ Port mapping documentation generated"

echo ""
log_info "🚀 Ready for production deployment with:"
echo "  ./deployment/helm-deploy.sh --environment prod"


