#!/bin/bash
# MantraPath Production Deployment Script
# This script handles the complete deployment process on the self-hosted runner

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"
NGINX_DIR="$PROJECT_ROOT/nginx"
LOG_FILE="${HOME}/mantrapath-deploy.log"

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

# Check if running as root for system operations
check_permissions() {
    if [[ $EUID -eq 0 ]]; then
        log_warning "Running as root. This is required for system-level operations."
    else
        log_error "This script must be run as root for system-level operations."
        exit 1
    fi
}

# Check system requirements
check_requirements() {
    log "Checking system requirements..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! docker info >/dev/null 2>&1; then
        log_error "Docker is not running. Please start Docker service."
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check Node.js for frontend
    if ! command -v node &> /dev/null; then
        log_warning "Node.js is not installed. Frontend build will be skipped."
        SKIP_FRONTEND=true
    fi
    
    # Check Nginx
    if ! command -v nginx &> /dev/null; then
        log_warning "Nginx is not installed. Will install Nginx."
        install_nginx
    fi
    
    log "System requirements check completed."
}

# Install Nginx
install_nginx() {
    log "Installing Nginx..."
    
    # Update package list
    apt-get update -y
    
    # Install Nginx
    apt-get install -y nginx
    
    # Enable and start Nginx
    systemctl enable nginx
    systemctl start nginx
    
    log "Nginx installed and started."
}

# Setup environment
setup_environment() {
    log "Setting up environment..."
    
    # Create log directory
    mkdir -p "$(dirname "$LOG_FILE")"
    
    # Create necessary directories
    mkdir -p /var/www/mantrapath
    mkdir -p /etc/nginx/sites-available
    mkdir -p /etc/nginx/sites-enabled
    
    # Set proper permissions
    chown -R www-data:www-data /var/www/mantrapath
    chmod -R 755 /var/www/mantrapath
    
    log "Environment setup completed."
}

# Deploy backend services
deploy_backend() {
    log "Deploying backend services..."
    
    cd "$BACKEND_DIR"
    
    # Check if .env exists
    if [ ! -f ".env" ]; then
        log_error "Environment file (.env) not found in backend directory."
        log "Please ensure the GitHub Actions workflow has created the .env file."
        exit 1
    fi
    
    # Stop existing services
    log "Stopping existing services..."
    docker-compose -f docker-compose.prod.yml down --remove-orphans || true
    
    # Pull latest images
    log "Pulling latest images..."
    docker-compose -f docker-compose.prod.yml pull
    
    # Start services
    log "Starting services..."
    docker-compose -f docker-compose.prod.yml up -d --build
    
    # Wait for services to be ready
    log "Waiting for services to initialize..."
    sleep 30
    
    # Health check
    if ! check_backend_health; then
        log_error "Backend health check failed."
        exit 1
    fi
    
    log "Backend services deployed successfully."
}

# Check backend health
check_backend_health() {
    log "Checking backend health..."
    
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f http://localhost:8000/health >/dev/null 2>&1; then
            log "API Gateway is healthy."
            return 0
        fi
        
        log_info "Health check attempt $attempt/$max_attempts - waiting..."
        sleep 10
        ((attempt++))
    done
    
    log_error "Backend health check failed after $max_attempts attempts."
    return 1
}

# Deploy frontend
deploy_frontend() {
    if [ "$SKIP_FRONTEND" = true ]; then
        log_warning "Skipping frontend deployment (Node.js not available)."
        return 0
    fi
    
    log "Deploying frontend..."
    
    cd "$FRONTEND_DIR"
    
    # Check if .env exists
    if [ ! -f ".env" ]; then
        log_warning "Frontend environment file (.env) not found. Using defaults."
    fi
    
    # Install dependencies
    log "Installing frontend dependencies..."
    npm ci --production
    
    # Build frontend
    log "Building frontend..."
    npm run build
    
    # Copy to web directory
    log "Copying frontend files to web directory..."
    cp -r dist/* /var/www/mantrapath/
    chown -R www-data:www-data /var/www/mantrapath
    chmod -R 755 /var/www/mantrapath
    
    log "Frontend deployed successfully."
}

# Configure Nginx
configure_nginx() {
    log "Configuring Nginx..."
    
    # Copy Nginx configuration
    cp "$NGINX_DIR/mantrapath.conf" /etc/nginx/sites-available/mantrapath
    
    # Enable site
    ln -sf /etc/nginx/sites-available/mantrapath /etc/nginx/sites-enabled/
    
    # Remove default site
    rm -f /etc/nginx/sites-enabled/default
    
    # Test Nginx configuration
    if nginx -t; then
        log "Nginx configuration is valid."
    else
        log_error "Nginx configuration is invalid."
        exit 1
    fi
    
    # Reload Nginx
    systemctl reload nginx
    
    log "Nginx configured and reloaded."
}

# Setup systemd service for MantraPath
setup_systemd_service() {
    log "Setting up systemd service..."
    
    cat > /etc/systemd/system/mantrapath.service << EOF
[Unit]
Description=MantraPath Mental Health Platform
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=$BACKEND_DIR
ExecStart=/usr/bin/docker-compose -f docker-compose.prod.yml up -d
ExecStop=/usr/bin/docker-compose -f docker-compose.prod.yml down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF

    # Reload systemd and enable service
    systemctl daemon-reload
    systemctl enable mantrapath.service
    
    log "Systemd service configured."
}

# Create monitoring script
create_monitoring_script() {
    log "Creating monitoring script..."
    
    cat > /usr/local/bin/mantrapath-monitor.sh << 'EOF'
#!/bin/bash
# MantraPath Health Monitoring Script

LOG_FILE="/var/log/mantrapath-monitor.log"
BACKEND_DIR="/path/to/mantrapath/backend"  # Update this path

check_service() {
    local service_name=$1
    local port=$2
    
    if curl -f "http://localhost:$port/health" >/dev/null 2>&1; then
        echo "$(date): $service_name is healthy" >> "$LOG_FILE"
        return 0
    else
        echo "$(date): $service_name is unhealthy" >> "$LOG_FILE"
        return 1
    fi
}

# Check API Gateway
if ! check_service "API Gateway" 8000; then
    echo "$(date): Restarting MantraPath services..." >> "$LOG_FILE"
    cd "$BACKEND_DIR"
    docker-compose -f docker-compose.prod.yml restart
fi
EOF

    chmod +x /usr/local/bin/mantrapath-monitor.sh
    
    # Setup cron job for monitoring
    echo "*/5 * * * * /usr/local/bin/mantrapath-monitor.sh" | crontab -
    
    log "Monitoring script created and scheduled."
}

# Show deployment status
show_status() {
    log "Deployment Status:"
    echo ""
    
    # Docker services
    echo "🐳 Docker Services:"
    cd "$BACKEND_DIR"
    docker-compose -f docker-compose.prod.yml ps
    
    echo ""
    echo "🌐 Nginx Status:"
    systemctl status nginx --no-pager -l
    
    echo ""
    echo "📊 Service Health:"
    
    services=(
        "8000:API Gateway"
        "8001:Auth Service"
        "8002:Profile Service"
        "8003:Mood Service"
        "8004:Chatbot Service"
        "8006:Community Service"
        "8007:Notification Service"
        "8008:ML Service"
    )
    
    for service in "${services[@]}"; do
        port=$(echo $service | cut -d: -f1)
        name=$(echo $service | cut -d: -f2)
        
        if curl -s -f "http://localhost:$port/health" >/dev/null 2>&1; then
            echo -e "  ${GREEN}✅${NC} $name (port $port)"
        else
            echo -e "  ${RED}❌${NC} $name (port $port)"
        fi
    done
    
    echo ""
    echo "🌍 Access URLs:"
    echo "  Frontend: http://$(hostname -I | awk '{print $1}'):80"
    echo "  API Gateway: http://$(hostname -I | awk '{print $1}'):8000"
    echo "  API Docs: http://$(hostname -I | awk '{print $1}'):80/docs"
    echo "  Health Check: http://$(hostname -I | awk '{print $1}'):80/health"
}

# Main deployment function
main() {
    log "Starting MantraPath deployment..."
    
    check_permissions
    check_requirements
    setup_environment
    deploy_backend
    deploy_frontend
    configure_nginx
    setup_systemd_service
    create_monitoring_script
    
    log "Deployment completed successfully!"
    
    show_status
}

# Handle script arguments
case "${1:-}" in
    "status")
        show_status
        ;;
    "restart")
        log "Restarting MantraPath services..."
        cd "$BACKEND_DIR"
        docker-compose -f docker-compose.prod.yml restart
        systemctl reload nginx
        log "Services restarted."
        ;;
    "stop")
        log "Stopping MantraPath services..."
        cd "$BACKEND_DIR"
        docker-compose -f docker-compose.prod.yml down
        systemctl stop nginx
        log "Services stopped."
        ;;
    "logs")
        cd "$BACKEND_DIR"
        docker-compose -f docker-compose.prod.yml logs -f
        ;;
    *)
        main
        ;;
esac
