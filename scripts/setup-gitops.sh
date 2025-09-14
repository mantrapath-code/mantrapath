#!/bin/bash
# MantraPath GitOps Setup Script
# This script helps you set up the GitOps deployment pipeline

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

# Check if running as root
check_permissions() {
    if [[ $EUID -eq 0 ]]; then
        log_warning "Running as root. This is required for system-level operations."
    else
        log_error "This script must be run as root for system-level operations."
        log_info "Please run: sudo $0"
        exit 1
    fi
}

# Install GitHub Actions runner
setup_github_runner() {
    log_step "Setting up GitHub Actions self-hosted runner..."
    
    # Check if runner already exists
    if [ -d "/home/runner/actions-runner" ]; then
        log_info "GitHub Actions runner already exists"
        return 0
    fi
    
    # Create runner user if doesn't exist
    if ! id "runner" &>/dev/null; then
        log_info "Creating runner user..."
        useradd -m -s /bin/bash runner
        usermod -aG docker runner
    fi
    
    # Create runner directory
    sudo -u runner mkdir -p /home/runner/actions-runner
    cd /home/runner/actions-runner
    
    # Download runner
    log_info "Downloading GitHub Actions runner..."
    RUNNER_VERSION="2.311.0"
    sudo -u runner curl -o actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz -L \
        https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz
    
    # Extract runner
    sudo -u runner tar xzf ./actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz
    
    # Set permissions
    chown -R runner:runner /home/runner/actions-runner
    
    log "✅ GitHub Actions runner downloaded"
    log_info "Next steps:"
    log_info "1. Go to your GitHub repository"
    log_info "2. Navigate to Settings → Actions → Runners"
    log_info "3. Click 'New self-hosted runner'"
    log_info "4. Follow the configuration instructions"
    log_info "5. Run the configuration as user 'runner':"
    log_info "   sudo -u runner /home/runner/actions-runner/config.sh --url https://github.com/YOUR_USERNAME/mantrapath --token YOUR_TOKEN"
    log_info "6. Install as service:"
    log_info "   cd /home/runner/actions-runner && sudo ./svc.sh install runner && sudo ./svc.sh start"
}

# Setup environment files
setup_environment() {
    log_step "Setting up environment configuration..."
    
    # Copy production environment template
    if [ ! -f "$PROJECT_ROOT/backend/.env" ]; then
        log_info "Creating backend environment file..."
        cp "$PROJECT_ROOT/deployment/production.env" "$PROJECT_ROOT/backend/.env"
        log_warning "Please edit $PROJECT_ROOT/backend/.env with your actual configuration"
    else
        log_info "Backend environment file already exists"
    fi
    
    # Create frontend environment file
    if [ ! -f "$PROJECT_ROOT/frontend/.env" ]; then
        log_info "Creating frontend environment file..."
        cat > "$PROJECT_ROOT/frontend/.env" << EOF
VITE_API_BASE_URL=http://139.84.213.185:8000
VITE_API_GATEWAY_URL=http://139.84.213.185:8000
VITE_WS_URL=ws://139.84.213.185:8080
VITE_API_URL=http://139.84.213.185:8000/api
VITE_ML_SERVICE_URL=http://139.84.213.185:8008
VITE_ENVIRONMENT=production
VITE_FRONTEND_PORT=3000
EOF
        log_warning "Please edit $PROJECT_ROOT/frontend/.env with your actual domain/IP"
    else
        log_info "Frontend environment file already exists"
    fi
    
    log "✅ Environment files configured"
}

# Setup system dependencies
setup_dependencies() {
    log_step "Installing system dependencies..."
    
    # Update package list
    apt-get update -y
    
    # Install essential packages
    apt-get install -y \
        curl \
        wget \
        git \
        unzip \
        software-properties-common \
        apt-transport-https \
        ca-certificates \
        gnupg \
        lsb-release \
        jq \
        bc
    
    # Install Docker if not present
    if ! command -v docker &> /dev/null; then
        log_info "Installing Docker..."
        curl -fsSL https://get.docker.com -o get-docker.sh
        sh get-docker.sh
        systemctl enable docker
        systemctl start docker
        usermod -aG docker runner 2>/dev/null || true
        rm get-docker.sh
    else
        log_info "Docker already installed"
    fi
    
    # Install Docker Compose if not present
    if ! command -v docker-compose &> /dev/null; then
        log_info "Installing Docker Compose..."
        DOCKER_COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | jq -r .tag_name)
        curl -L "https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        chmod +x /usr/local/bin/docker-compose
    else
        log_info "Docker Compose already installed"
    fi
    
    # Install Nginx if not present
    if ! command -v nginx &> /dev/null; then
        log_info "Installing Nginx..."
        apt-get install -y nginx
        systemctl enable nginx
        systemctl start nginx
    else
        log_info "Nginx already installed"
    fi
    
    # Install Node.js if not present
    if ! command -v node &> /dev/null; then
        log_info "Installing Node.js..."
        curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
        apt-get install -y nodejs
    else
        log_info "Node.js already installed"
    fi
    
    log "✅ System dependencies installed"
}

# Setup directories and permissions
setup_directories() {
    log_step "Setting up directories and permissions..."
    
    # Create necessary directories
    mkdir -p /var/www/mantrapath
    mkdir -p /var/log/mantrapath
    mkdir -p /var/backups/mantrapath
    
    # Set proper permissions
    chown -R www-data:www-data /var/www/mantrapath
    chmod -R 755 /var/www/mantrapath
    
    chown -R syslog:adm /var/log/mantrapath
    chmod -R 755 /var/log/mantrapath
    
    # Make scripts executable
    chmod +x "$PROJECT_ROOT/scripts"/*.sh
    
    log "✅ Directories and permissions configured"
}

# Setup monitoring
setup_monitoring() {
    log_step "Setting up monitoring and health checks..."
    
    # Copy health monitoring script to system location
    cp "$PROJECT_ROOT/scripts/health-monitor.sh" /usr/local/bin/mantrapath-health-monitor
    chmod +x /usr/local/bin/mantrapath-health-monitor
    
    # Setup cron job for health monitoring (every 5 minutes)
    echo "*/5 * * * * /usr/local/bin/mantrapath-health-monitor restart >/dev/null 2>&1" | crontab -
    
    # Setup log rotation
    cat > /etc/logrotate.d/mantrapath << 'EOF'
/var/log/mantrapath/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 0644 syslog adm
    postrotate
        systemctl reload rsyslog > /dev/null 2>&1 || true
    endscript
}
EOF
    
    log "✅ Monitoring configured"
}

# Test deployment
test_deployment() {
    log_step "Testing deployment configuration..."
    
    cd "$PROJECT_ROOT"
    
    # Test Docker Compose configuration
    if docker-compose -f backend/docker-compose.prod.yml config >/dev/null 2>&1; then
        log "✅ Docker Compose configuration is valid"
    else
        log_error "❌ Docker Compose configuration has errors"
        return 1
    fi
    
    # Test Nginx configuration
    if nginx -t >/dev/null 2>&1; then
        log "✅ Nginx configuration is valid"
    else
        log_warning "⚠️ Nginx configuration may have issues"
    fi
    
    # Test scripts
    if [ -x "$PROJECT_ROOT/scripts/production-deploy.sh" ]; then
        log "✅ Production deployment script is executable"
    else
        log_error "❌ Production deployment script is not executable"
        return 1
    fi
    
    if [ -x "$PROJECT_ROOT/scripts/health-monitor.sh" ]; then
        log "✅ Health monitoring script is executable"
    else
        log_error "❌ Health monitoring script is not executable"
        return 1
    fi
    
    log "✅ Configuration tests passed"
}

# Show setup summary
show_summary() {
    log_step "Setup Summary"
    
    echo ""
    echo "🎉 MantraPath GitOps setup completed!"
    echo ""
    echo "📋 What was configured:"
    echo "  ✅ System dependencies (Docker, Docker Compose, Nginx, Node.js)"
    echo "  ✅ GitHub Actions runner (download and setup)"
    echo "  ✅ Environment configuration files"
    echo "  ✅ Directory structure and permissions"
    echo "  ✅ Health monitoring and log rotation"
    echo "  ✅ Deployment scripts"
    echo ""
    echo "🔧 Next Steps:"
    echo ""
    echo "1. Configure GitHub Secrets in your repository:"
    echo "   - POSTGRES_PASSWORD=your_secure_password"
    echo "   - JWT_SECRET_KEY=your_super_secret_jwt_key"
    echo "   - DOMAIN=139.84.213.185 (or your domain)"
    echo "   - PROTOCOL=http (or https)"
    echo ""
    echo "2. Complete GitHub Actions runner setup:"
    echo "   - Go to GitHub repo → Settings → Actions → Runners"
    echo "   - Click 'New self-hosted runner'"
    echo "   - Run as user 'runner':"
    echo "     sudo -u runner /home/runner/actions-runner/config.sh --url YOUR_REPO_URL --token YOUR_TOKEN"
    echo "   - Install as service:"
    echo "     cd /home/runner/actions-runner && sudo ./svc.sh install runner && sudo ./svc.sh start"
    echo ""
    echo "3. Edit environment files:"
    echo "   - Backend: $PROJECT_ROOT/backend/.env"
    echo "   - Frontend: $PROJECT_ROOT/frontend/.env"
    echo ""
    echo "4. Test the deployment:"
    echo "   - Push any change to main branch"
    echo "   - Or run manually: sudo $PROJECT_ROOT/scripts/production-deploy.sh"
    echo ""
    echo "5. Monitor the deployment:"
    echo "   - Health check: $PROJECT_ROOT/scripts/health-monitor.sh status"
    echo "   - View logs: tail -f /var/log/mantrapath/health-monitor.log"
    echo ""
    echo "🌐 Access URLs (after deployment):"
    echo "  - Frontend: http://$(hostname -I | awk '{print $1}')"
    echo "  - API Gateway: http://$(hostname -I | awk '{print $1}'):8000"
    echo "  - API Docs: http://$(hostname -I | awk '{print $1}'):8000/docs"
    echo "  - Health Check: http://$(hostname -I | awk '{print $1}'):8000/health"
    echo ""
    echo "📚 Documentation: $PROJECT_ROOT/GITOPS_SETUP.md"
    echo ""
}

# Main function
main() {
    log "🚀 Starting MantraPath GitOps setup..."
    
    check_permissions
    setup_dependencies
    setup_directories
    setup_github_runner
    setup_environment
    setup_monitoring
    test_deployment
    
    log "✅ GitOps setup completed successfully!"
    show_summary
}

# Handle script arguments
case "${1:-}" in
    "dependencies")
        check_permissions
        setup_dependencies
        ;;
    "runner")
        check_permissions
        setup_github_runner
        ;;
    "environment")
        setup_environment
        ;;
    "monitoring")
        check_permissions
        setup_monitoring
        ;;
    "test")
        test_deployment
        ;;
    *)
        main
        ;;
esac
