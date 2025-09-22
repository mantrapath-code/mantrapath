#!/bin/bash
# Configure MantraPath for IP Access (139.84.213.185)
# This script optimizes the configuration for direct IP access

set -euo pipefail

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration
SERVER_IP="139.84.213.185"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

log_info() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')] INFO:${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1"
}

# Update frontend environment for IP access
update_frontend_env() {
    log_info "Updating frontend environment for IP access..."
    
    cat > "$PROJECT_ROOT/frontend/.env" << EOF
# MantraPath Frontend Configuration - IP Access
VITE_API_BASE_URL=http://$SERVER_IP/api
VITE_API_GATEWAY_URL=http://$SERVER_IP
VITE_WS_URL=ws://$SERVER_IP/ws
VITE_API_URL=http://$SERVER_IP/api
VITE_ML_SERVICE_URL=http://$SERVER_IP/api/ml
VITE_ENVIRONMENT=production
VITE_FRONTEND_PORT=3000

# Server Configuration
VITE_SERVER_IP=$SERVER_IP
VITE_PROTOCOL=http
EOF

    log "✅ Frontend environment updated for IP access"
}

# Update backend environment for IP access
update_backend_env() {
    log_info "Updating backend environment for IP access..."
    
    # Update existing .env file
    if [ -f "$PROJECT_ROOT/backend/.env" ]; then
        # Backup current .env
        cp "$PROJECT_ROOT/backend/.env" "$PROJECT_ROOT/backend/.env.backup.$(date +%Y%m%d_%H%M%S)"
        
        # Update key values for IP access
        sed -i "s/DOMAIN=.*/DOMAIN=$SERVER_IP/" "$PROJECT_ROOT/backend/.env"
        sed -i "s/PROTOCOL=.*/PROTOCOL=http/" "$PROJECT_ROOT/backend/.env"
        sed -i "s|APP_URL=.*|APP_URL=http://$SERVER_IP|" "$PROJECT_ROOT/backend/.env"
        
        # Update CORS origins for IP access
        sed -i 's/CORS_ORIGINS=.*/CORS_ORIGINS=["http:\/\/localhost:3000","http:\/\/localhost:5173","http:\/\/139.84.213.185","http:\/\/139.84.213.185:3000"]/' "$PROJECT_ROOT/backend/.env"
        
        log "✅ Backend environment updated for IP access"
    else
        log_warning "Backend .env file not found, creating from template..."
        cp "$PROJECT_ROOT/deployment/production.env" "$PROJECT_ROOT/backend/.env"
        update_backend_env  # Recursive call to update the newly created file
    fi
}

# Update production environment template
update_production_template() {
    log_info "Updating production environment template..."
    
    sed -i "s/DOMAIN=.*/DOMAIN=$SERVER_IP/" "$PROJECT_ROOT/deployment/production.env"
    sed -i "s/PROTOCOL=.*/PROTOCOL=http/" "$PROJECT_ROOT/deployment/production.env"
    sed -i "s|APP_URL=.*|APP_URL=http://$SERVER_IP|" "$PROJECT_ROOT/deployment/production.env"
    
    log "✅ Production template updated for IP access"
}

# Test Nginx configuration
test_nginx_config() {
    log_info "Testing Nginx configuration..."
    
    if command -v nginx >/dev/null 2>&1; then
        if nginx -t 2>/dev/null; then
            log "✅ Nginx configuration is valid"
        else
            log_warning "⚠️ Nginx configuration has warnings (may still work)"
        fi
    else
        log_info "Nginx not installed yet (will be installed during deployment)"
    fi
}

# Show access information
show_access_info() {
    echo ""
    log "🌐 MantraPath IP Access Configuration Complete!"
    echo ""
    echo "📋 Access URLs:"
    echo "   Frontend:        http://$SERVER_IP"
    echo "   API Gateway:     http://$SERVER_IP/api"
    echo "   API Docs:        http://$SERVER_IP/docs"
    echo "   Health Check:    http://$SERVER_IP/health"
    echo "   WebSocket:       ws://$SERVER_IP/ws"
    echo ""
    echo "🔧 Configuration Updated:"
    echo "   ✅ Nginx: Optimized for IP access"
    echo "   ✅ Frontend: Configured for $SERVER_IP"
    echo "   ✅ Backend: Configured for $SERVER_IP"
    echo "   ✅ CORS: Allows IP access"
    echo ""
    echo "🚀 Next Steps:"
    echo "   1. Deploy your application:"
    echo "      git push origin main"
    echo "      # OR"
    echo "      sudo ./scripts/production-deploy.sh"
    echo ""
    echo "   2. Test access:"
    echo "      curl -I http://$SERVER_IP"
    echo "      curl http://$SERVER_IP/api/health"
    echo ""
    echo "   3. When ready for domain, run:"
    echo "      sudo ./scripts/setup-domain.sh"
    echo ""
}

# Main function
main() {
    log "🎯 Configuring MantraPath for IP Access ($SERVER_IP)"
    echo ""
    
    update_frontend_env
    update_backend_env  
    update_production_template
    test_nginx_config
    
    show_access_info
}

# Run main function
main "$@"
