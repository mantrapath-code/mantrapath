#!/bin/bash
# MantraPath Domain and DNS Setup Script
# This script helps configure domain name and SSL for production

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
NGINX_CONFIG="$PROJECT_ROOT/nginx/mantrapath.conf"
SERVER_IP="139.84.213.185"

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

log_step() {
    echo -e "${PURPLE}[$(date '+%Y-%m-%d %H:%M:%S')] STEP:${NC} $1"
}

# Get user input for domain
get_domain_info() {
    echo ""
    log_step "Domain Configuration Setup"
    echo ""
    
    # Get domain name
    read -p "Enter your domain name (e.g., mantrapath.com): " DOMAIN_NAME
    if [ -z "$DOMAIN_NAME" ]; then
        log_error "Domain name is required"
        exit 1
    fi
    
    # Get email for SSL
    read -p "Enter email for SSL certificate (for Let's Encrypt): " SSL_EMAIL
    if [ -z "$SSL_EMAIL" ]; then
        log_error "Email is required for SSL certificate"
        exit 1
    fi
    
    # Confirm setup
    echo ""
    log_info "Configuration Summary:"
    echo "  Domain: $DOMAIN_NAME"
    echo "  Server IP: $SERVER_IP"
    echo "  SSL Email: $SSL_EMAIL"
    echo ""
    
    read -p "Continue with this configuration? (y/N): " CONFIRM
    if [[ ! "$CONFIRM" =~ ^[Yy]$ ]]; then
        log_info "Setup cancelled"
        exit 0
    fi
}

# Check DNS resolution
check_dns() {
    log_step "Checking DNS resolution..."
    
    log_info "Checking if $DOMAIN_NAME points to $SERVER_IP..."
    
    # Check DNS resolution
    if command -v dig >/dev/null 2>&1; then
        local resolved_ip=$(dig +short "$DOMAIN_NAME" | tail -n1)
    elif command -v nslookup >/dev/null 2>&1; then
        local resolved_ip=$(nslookup "$DOMAIN_NAME" | grep -A1 "Name:" | tail -1 | awk '{print $2}')
    else
        log_warning "⚠️ Cannot check DNS (dig/nslookup not available)"
        return 0
    fi
    
    if [ "$resolved_ip" = "$SERVER_IP" ]; then
        log "✅ DNS correctly points to $SERVER_IP"
        return 0
    else
        log_warning "⚠️ DNS does not point to correct IP"
        log_warning "  Expected: $SERVER_IP"
        log_warning "  Got: $resolved_ip"
        echo ""
        log_info "Please configure these DNS records:"
        echo "  Type: A, Name: @, Value: $SERVER_IP"
        echo "  Type: A, Name: www, Value: $SERVER_IP"
        echo ""
        read -p "Continue anyway? (y/N): " CONTINUE
        if [[ ! "$CONTINUE" =~ ^[Yy]$ ]]; then
            log_info "Please configure DNS first, then run this script again"
            exit 1
        fi
    fi
}

# Update Nginx configuration
update_nginx_config() {
    log_step "Updating Nginx configuration..."
    
    # Backup current config
    cp "$NGINX_CONFIG" "$NGINX_CONFIG.backup.$(date +%Y%m%d_%H%M%S)"
    log_info "Backed up current Nginx config"
    
    # Update server_name
    sed -i "s/server_name .*/server_name $DOMAIN_NAME www.$DOMAIN_NAME $SERVER_IP;/" "$NGINX_CONFIG"
    
    log "✅ Updated Nginx configuration with domain: $DOMAIN_NAME"
}

# Install Certbot
install_certbot() {
    log_step "Installing Certbot for SSL certificates..."
    
    if command -v certbot >/dev/null 2>&1; then
        log_info "Certbot already installed"
        return 0
    fi
    
    # Update package list
    apt-get update -y
    
    # Install certbot
    apt-get install -y certbot python3-certbot-nginx
    
    log "✅ Certbot installed"
}

# Setup SSL certificate
setup_ssl() {
    log_step "Setting up SSL certificate..."
    
    # Test Nginx configuration first
    if ! nginx -t; then
        log_error "Nginx configuration test failed"
        exit 1
    fi
    
    # Reload Nginx
    systemctl reload nginx
    
    # Get SSL certificate
    log_info "Requesting SSL certificate from Let's Encrypt..."
    
    if certbot --nginx \
        --non-interactive \
        --agree-tos \
        --email "$SSL_EMAIL" \
        --domains "$DOMAIN_NAME,www.$DOMAIN_NAME" \
        --redirect; then
        
        log "✅ SSL certificate installed successfully"
        
        # Setup auto-renewal
        setup_ssl_renewal
    else
        log_error "Failed to get SSL certificate"
        log_info "You can try manually with: certbot --nginx -d $DOMAIN_NAME -d www.$DOMAIN_NAME"
        return 1
    fi
}

# Setup SSL auto-renewal
setup_ssl_renewal() {
    log_step "Setting up SSL certificate auto-renewal..."
    
    # Add cron job for renewal
    (crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet") | crontab -
    
    log "✅ SSL auto-renewal configured"
}

# Update environment files
update_environment() {
    log_step "Updating environment configuration..."
    
    local protocol="https"
    local domain_url="https://$DOMAIN_NAME"
    
    # Update backend environment
    if [ -f "$PROJECT_ROOT/backend/.env" ]; then
        sed -i "s/DOMAIN=.*/DOMAIN=$DOMAIN_NAME/" "$PROJECT_ROOT/backend/.env"
        sed -i "s/PROTOCOL=.*/PROTOCOL=$protocol/" "$PROJECT_ROOT/backend/.env"
        sed -i "s|APP_URL=.*|APP_URL=$domain_url|" "$PROJECT_ROOT/backend/.env"
        log_info "Updated backend environment"
    fi
    
    # Update frontend environment
    if [ -f "$PROJECT_ROOT/frontend/.env" ]; then
        sed -i "s|VITE_API_BASE_URL=.*|VITE_API_BASE_URL=$domain_url:8000|" "$PROJECT_ROOT/frontend/.env"
        sed -i "s|VITE_API_GATEWAY_URL=.*|VITE_API_GATEWAY_URL=$domain_url:8000|" "$PROJECT_ROOT/frontend/.env"
        sed -i "s|VITE_WS_URL=.*|VITE_WS_URL=wss://$DOMAIN_NAME/ws|" "$PROJECT_ROOT/frontend/.env"
        sed -i "s|VITE_API_URL=.*|VITE_API_URL=$domain_url/api|" "$PROJECT_ROOT/frontend/.env"
        log_info "Updated frontend environment"
    fi
    
    # Update deployment environment template
    if [ -f "$PROJECT_ROOT/deployment/production.env" ]; then
        sed -i "s/DOMAIN=.*/DOMAIN=$DOMAIN_NAME/" "$PROJECT_ROOT/deployment/production.env"
        sed -i "s/PROTOCOL=.*/PROTOCOL=$protocol/" "$PROJECT_ROOT/deployment/production.env"
        sed -i "s|APP_URL=.*|APP_URL=$domain_url|" "$PROJECT_ROOT/deployment/production.env"
        log_info "Updated production environment template"
    fi
    
    log "✅ Environment files updated"
}

# Test the setup
test_setup() {
    log_step "Testing domain and SSL setup..."
    
    # Test HTTP redirect
    log_info "Testing HTTP to HTTPS redirect..."
    if curl -I -s "http://$DOMAIN_NAME" | grep -q "301\|302"; then
        log "✅ HTTP redirect working"
    else
        log_warning "⚠️ HTTP redirect may not be working"
    fi
    
    # Test HTTPS
    log_info "Testing HTTPS access..."
    if curl -I -s "https://$DOMAIN_NAME" | grep -q "200"; then
        log "✅ HTTPS access working"
    else
        log_warning "⚠️ HTTPS access may not be working"
    fi
    
    # Test API endpoint
    log_info "Testing API endpoint..."
    if curl -I -s "https://$DOMAIN_NAME/api/health" | grep -q "200\|404"; then
        log "✅ API endpoint accessible"
    else
        log_warning "⚠️ API endpoint may not be accessible"
    fi
    
    # Test SSL certificate
    log_info "Testing SSL certificate..."
    if openssl s_client -connect "$DOMAIN_NAME:443" -servername "$DOMAIN_NAME" </dev/null 2>/dev/null | grep -q "Verify return code: 0"; then
        log "✅ SSL certificate valid"
    else
        log_warning "⚠️ SSL certificate may have issues"
    fi
}

# Show final information
show_summary() {
    log_step "Domain Setup Complete!"
    
    echo ""
    echo "🌐 Your MantraPath application is now accessible at:"
    echo "  Frontend: https://$DOMAIN_NAME"
    echo "  API Gateway: https://$DOMAIN_NAME/api"
    echo "  API Documentation: https://$DOMAIN_NAME/docs"
    echo "  Health Check: https://$DOMAIN_NAME/api/health"
    echo ""
    echo "🔒 SSL Certificate:"
    echo "  Status: Active"
    echo "  Auto-renewal: Enabled"
    echo "  Provider: Let's Encrypt"
    echo ""
    echo "🔧 Next Steps:"
    echo "  1. Update GitHub Secrets with new domain:"
    echo "     DOMAIN=$DOMAIN_NAME"
    echo "     PROTOCOL=https"
    echo "     APP_URL=https://$DOMAIN_NAME"
    echo ""
    echo "  2. Redeploy your application:"
    echo "     git push origin main"
    echo "     # OR"
    echo "     sudo $SCRIPT_DIR/production-deploy.sh"
    echo ""
    echo "  3. Test all functionality with the new domain"
    echo ""
    echo "📋 Configuration files updated:"
    echo "  - $NGINX_CONFIG"
    echo "  - $PROJECT_ROOT/backend/.env"
    echo "  - $PROJECT_ROOT/frontend/.env"
    echo ""
}

# Show DNS setup instructions
show_dns_instructions() {
    echo ""
    log_step "DNS Configuration Instructions"
    echo ""
    echo "To set up DNS for your domain, add these records to your DNS provider:"
    echo ""
    echo "┌─────────────────────────────────────────────────────┐"
    echo "│                 DNS Records                         │"
    echo "├─────────────────────────────────────────────────────┤"
    echo "│ Type: A                                             │"
    echo "│ Name: @                                             │"
    echo "│ Value: $SERVER_IP                            │"
    echo "│ TTL: 3600                                           │"
    echo "├─────────────────────────────────────────────────────┤"
    echo "│ Type: A                                             │"
    echo "│ Name: www                                           │"
    echo "│ Value: $SERVER_IP                            │"
    echo "│ TTL: 3600                                           │"
    echo "└─────────────────────────────────────────────────────┘"
    echo ""
    echo "Popular DNS providers:"
    echo "  • Cloudflare: https://dash.cloudflare.com"
    echo "  • Namecheap: https://www.namecheap.com"
    echo "  • GoDaddy: https://www.godaddy.com"
    echo "  • Google Domains: https://domains.google.com"
    echo ""
    echo "After configuring DNS, wait 5-60 minutes for propagation, then run:"
    echo "  sudo $0"
    echo ""
}

# Main function
main() {
    # Check if running as root
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root"
        log_info "Please run: sudo $0"
        exit 1
    fi
    
    log "🌐 MantraPath Domain and SSL Setup"
    
    get_domain_info
    check_dns
    update_nginx_config
    install_certbot
    setup_ssl
    update_environment
    test_setup
    show_summary
}

# Handle script arguments
case "${1:-}" in
    "dns-help")
        show_dns_instructions
        ;;
    "test")
        if [ -z "${2:-}" ]; then
            log_error "Please provide domain name: $0 test your-domain.com"
            exit 1
        fi
        DOMAIN_NAME="$2"
        check_dns
        test_setup
        ;;
    "ssl-only")
        if [ -z "${2:-}" ] || [ -z "${3:-}" ]; then
            log_error "Usage: $0 ssl-only domain.com email@example.com"
            exit 1
        fi
        DOMAIN_NAME="$2"
        SSL_EMAIL="$3"
        install_certbot
        setup_ssl
        ;;
    *)
        main
        ;;
esac
