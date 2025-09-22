#!/bin/bash
# MantraPath Production Deployment Script
# Enhanced GitOps-ready deployment for production environment

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"
NGINX_DIR="$PROJECT_ROOT/nginx"
DEPLOYMENT_DIR="$PROJECT_ROOT/deployment"
LOG_FILE="${HOME}/mantrapath-production-deploy.log"
DEPLOYMENT_ENV="${DEPLOYMENT_ENV:-production}"
FORCE_REBUILD="${FORCE_REBUILD:-false}"

# Logging functions
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

log_step() {
    echo -e "${PURPLE}[$(date '+%Y-%m-%d %H:%M:%S')] STEP:${NC} $1" | tee -a "$LOG_FILE"
}

# Error handling
handle_error() {
    log_error "Deployment failed at line $1"
    log_error "Command: $BASH_COMMAND"
    cleanup_on_error
    exit 1
}

trap 'handle_error $LINENO' ERR

# Cleanup function
cleanup_on_error() {
    log_warning "Performing cleanup due to error..."
    
    # Stop any partially started services
    cd "$BACKEND_DIR" || return
    docker-compose -f docker-compose.prod.yml down --remove-orphans || true
    
    log_info "Cleanup completed"
}

# Check prerequisites
check_prerequisites() {
    log_step "Checking system prerequisites..."
    
    # Check if running as root for system operations
    if [[ $EUID -eq 0 ]]; then
        log_warning "Running as root. This is required for system-level operations."
    else
        log_error "This script must be run as root for system-level operations."
        exit 1
    fi
    
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
    
    # Check available space (require at least 10GB)
    available_space=$(df / | awk 'NR==2 {print $4}')
    if [[ $available_space -lt 10485760 ]]; then  # 10GB in KB
        log_warning "Low disk space detected. Available: $(($available_space/1024/1024))GB"
    fi
    
    # Check memory (require at least 4GB)
    available_memory=$(free | awk '/^Mem:/ {print $2}')
    if [[ $available_memory -lt 4194304 ]]; then  # 4GB in KB
        log_warning "Low memory detected. Available: $(($available_memory/1024/1024))GB"
    fi
    
    log "✅ Prerequisites check completed"
}

# Setup environment
setup_environment() {
    log_step "Setting up deployment environment..."
    
    # Create necessary directories
    mkdir -p /var/www/mantrapath
    mkdir -p /var/log/mantrapath
    mkdir -p /etc/nginx/sites-available
    mkdir -p /etc/nginx/sites-enabled
    
    # Set proper permissions
    chown -R www-data:www-data /var/www/mantrapath
    chmod -R 755 /var/www/mantrapath
    
    # Create log directory with proper permissions
    chown -R syslog:adm /var/log/mantrapath
    chmod -R 755 /var/log/mantrapath
    
    log "✅ Environment setup completed"
}

# Install system dependencies
install_dependencies() {
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
        htop \
        iotop \
        iftop \
        jq
    
    # Install Nginx if not present
    if ! command -v nginx &> /dev/null; then
        log_info "Installing Nginx..."
        apt-get install -y nginx
        systemctl enable nginx
        systemctl start nginx
    fi
    
    # Install Node.js if not present
    if ! command -v node &> /dev/null; then
        log_info "Installing Node.js..."
        curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
        apt-get install -y nodejs
    fi
    
    # Install Docker if not present
    if ! command -v docker &> /dev/null; then
        log_info "Installing Docker..."
        curl -fsSL https://get.docker.com -o get-docker.sh
        sh get-docker.sh
        systemctl enable docker
        systemctl start docker
        rm get-docker.sh
    fi
    
    # Install Docker Compose if not present
    if ! command -v docker-compose &> /dev/null; then
        log_info "Installing Docker Compose..."
        DOCKER_COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | jq -r .tag_name)
        curl -L "https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        chmod +x /usr/local/bin/docker-compose
    fi
    
    log "✅ Dependencies installation completed"
}

# Backup current deployment
backup_current_deployment() {
    log_step "Creating backup of current deployment..."
    
    BACKUP_DIR="/var/backups/mantrapath/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    
    # Backup database
    if docker-compose -f "$BACKEND_DIR/docker-compose.prod.yml" ps | grep -q postgres; then
        log_info "Backing up database..."
        docker-compose -f "$BACKEND_DIR/docker-compose.prod.yml" exec -T postgres pg_dump -U mantrapath mantrapath > "$BACKUP_DIR/database_backup.sql" || true
    fi
    
    # Backup configuration files
    if [ -f "$BACKEND_DIR/.env" ]; then
        cp "$BACKEND_DIR/.env" "$BACKUP_DIR/backend_env_backup" || true
    fi
    
    if [ -f "$FRONTEND_DIR/.env" ]; then
        cp "$FRONTEND_DIR/.env" "$BACKUP_DIR/frontend_env_backup" || true
    fi
    
    # Backup nginx configuration
    if [ -f "/etc/nginx/sites-available/mantrapath" ]; then
        cp "/etc/nginx/sites-available/mantrapath" "$BACKUP_DIR/nginx_backup.conf" || true
    fi
    
    log "✅ Backup created at $BACKUP_DIR"
}

# Deploy infrastructure services
deploy_infrastructure() {
    log_step "Deploying infrastructure services..."
    
    cd "$BACKEND_DIR"
    
    # Start infrastructure services
    log_info "Starting database and cache services..."
    docker-compose -f docker-compose.prod.yml up -d postgres redis nats
    
    # Wait for infrastructure to be ready
    log_info "Waiting for infrastructure services..."
    sleep 30
    
    # Check database health
    local max_attempts=20
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if docker-compose -f docker-compose.prod.yml exec -T postgres pg_isready -U mantrapath -d mantrapath; then
            log "✅ Database is ready"
            break
        fi
        log_info "Waiting for database... ($attempt/$max_attempts)"
        sleep 5
        ((attempt++))
    done
    
    if [ $attempt -gt $max_attempts ]; then
        log_error "Database failed to start within expected time"
        exit 1
    fi
    
    # Check Redis
    if docker-compose -f docker-compose.prod.yml exec -T redis redis-cli ping | grep -q PONG; then
        log "✅ Redis is ready"
    else
        log_error "Redis failed to start"
        exit 1
    fi
    
    log "✅ Infrastructure services deployed"
}

# Deploy core services
deploy_core_services() {
    log_step "Deploying core services..."
    
    cd "$BACKEND_DIR"
    
    # Start models service first (it takes longest to initialize)
    log_info "Starting models service..."
    docker-compose -f docker-compose.prod.yml up -d models-service
    
    # Wait for models service to be ready
    log_info "Waiting for models service to initialize (this may take a few minutes)..."
    sleep 90
    
    # Check models service health
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f -s http://localhost:8081/health >/dev/null 2>&1; then
            log "✅ Models service is ready"
            break
        fi
        log_info "Waiting for models service... ($attempt/$max_attempts)"
        sleep 10
        ((attempt++))
    done
    
    if [ $attempt -gt $max_attempts ]; then
        log_warning "Models service may not be fully ready, but continuing deployment"
    fi
    
    log "✅ Core services deployed"
}

# Deploy application services
deploy_application_services() {
    log_step "Deploying application services..."
    
    cd "$BACKEND_DIR"
    
    # Start all application services
    log_info "Starting application services..."
    docker-compose -f docker-compose.prod.yml up -d \
        auth-service \
        profile-service \
        mood-service \
        chatbot-service \
        content-service \
        community-service \
        notification-service \
        ml-service \
        translation-service \
        voice-service \
        ai-context-store \
        action-orchestrator \
        memory-service \
        ai-event-processor \
        media-service
    
    # Wait for services to stabilize
    log_info "Waiting for application services to stabilize..."
    sleep 45
    
    # Start API Gateway last
    log_info "Starting API Gateway..."
    docker-compose -f docker-compose.prod.yml up -d api-gateway
    
    # Wait for API Gateway
    sleep 30
    
    log "✅ Application services deployed"
}

# Deploy frontend
deploy_frontend() {
    log_step "Deploying frontend..."
    
    cd "$FRONTEND_DIR"
    
    # Install dependencies
    log_info "Installing frontend dependencies..."
    npm ci --production
    
    # Build frontend
    log_info "Building frontend..."
    npm run build
    
    # Deploy frontend container
    log_info "Starting frontend container..."
    cd "$PROJECT_ROOT"
    docker-compose -f backend/docker-compose.prod.yml up -d frontend
    
    log "✅ Frontend deployed"
}

# Configure Nginx
configure_nginx() {
    log_step "Configuring Nginx..."
    
    # Copy configuration
    cp "$NGINX_DIR/mantrapath.conf" /etc/nginx/sites-available/mantrapath
    
    # Update server name if DOMAIN is set
    if [ -n "${DOMAIN:-}" ]; then
        sed -i "s/server_name _;/server_name $DOMAIN;/" /etc/nginx/sites-available/mantrapath
    fi
    
    # Enable site
    ln -sf /etc/nginx/sites-available/mantrapath /etc/nginx/sites-enabled/
    rm -f /etc/nginx/sites-enabled/default
    
    # Test configuration
    if nginx -t; then
        log "✅ Nginx configuration is valid"
    else
        log_error "Nginx configuration is invalid"
        exit 1
    fi
    
    # Reload Nginx
    systemctl reload nginx
    systemctl enable nginx
    
    log "✅ Nginx configured"
}

# Run health checks
run_health_checks() {
    log_step "Running comprehensive health checks..."
    
    local failed_services=()
    
    # Define services to check
    local services=(
        "8000:API Gateway"
        "8001:Auth Service"
        "8002:Profile Service"
        "8003:Mood Service"
        "8004:Chatbot Service"
        "8006:Community Service"
        "8007:Notification Service"
        "8008:ML Service"
        "8081:Models Service"
    )
    
    # Check each service
    for service in "${services[@]}"; do
        local port=$(echo $service | cut -d: -f1)
        local name=$(echo $service | cut -d: -f2)
        
        if curl -f -s "http://localhost:$port/health" >/dev/null 2>&1; then
            log "✅ $name (port $port) - Healthy"
        else
            log_warning "❌ $name (port $port) - Unhealthy"
            failed_services+=("$name")
        fi
    done
    
    # Check database
    cd "$BACKEND_DIR"
    if docker-compose -f docker-compose.prod.yml exec -T postgres pg_isready -U mantrapath -d mantrapath; then
        log "✅ PostgreSQL - Healthy"
    else
        log_warning "❌ PostgreSQL - Unhealthy"
        failed_services+=("PostgreSQL")
    fi
    
    # Check Redis
    if docker-compose -f docker-compose.prod.yml exec -T redis redis-cli ping | grep -q PONG; then
        log "✅ Redis - Healthy"
    else
        log_warning "❌ Redis - Unhealthy"
        failed_services+=("Redis")
    fi
    
    # Check frontend
    if curl -f -s "http://localhost:3000/health" >/dev/null 2>&1; then
        log "✅ Frontend - Healthy"
    else
        log_warning "❌ Frontend - Unhealthy"
        failed_services+=("Frontend")
    fi
    
    # Check Nginx
    if systemctl is-active --quiet nginx; then
        log "✅ Nginx - Running"
    else
        log_warning "❌ Nginx - Not running"
        failed_services+=("Nginx")
    fi
    
    # Summary
    if [ ${#failed_services[@]} -eq 0 ]; then
        log "🎉 All health checks passed!"
        return 0
    else
        log_warning "⚠️ Some services failed health checks: ${failed_services[*]}"
        return 1
    fi
}

# Setup monitoring and logging
setup_monitoring() {
    log_step "Setting up monitoring and logging..."
    
    # Create monitoring script
    cat > /usr/local/bin/mantrapath-monitor.sh << 'EOF'
#!/bin/bash
# MantraPath Health Monitoring Script

LOG_FILE="/var/log/mantrapath/monitor.log"
BACKEND_DIR="/home/sachin/mantrapath/backend"

check_service() {
    local service_name=$1
    local port=$2
    
    if curl -f -s "http://localhost:$port/health" >/dev/null 2>&1; then
        echo "$(date): $service_name is healthy" >> "$LOG_FILE"
        return 0
    else
        echo "$(date): $service_name is unhealthy" >> "$LOG_FILE"
        return 1
    fi
}

# Check critical services
critical_services=(
    "API Gateway:8000"
    "Auth Service:8001"
    "Models Service:8081"
)

failed_count=0
for service in "${critical_services[@]}"; do
    name=$(echo $service | cut -d: -f1)
    port=$(echo $service | cut -d: -f2)
    
    if ! check_service "$name" "$port"; then
        ((failed_count++))
    fi
done

# If multiple critical services are down, restart everything
if [ $failed_count -gt 1 ]; then
    echo "$(date): Multiple critical services down, restarting..." >> "$LOG_FILE"
    cd "$BACKEND_DIR"
    docker-compose -f docker-compose.prod.yml restart
fi
EOF

    chmod +x /usr/local/bin/mantrapath-monitor.sh
    
    # Setup cron job for monitoring (every 5 minutes)
    echo "*/5 * * * * /usr/local/bin/mantrapath-monitor.sh" | crontab -
    
    # Setup log rotation
    cat > /etc/logrotate.d/mantrapath << EOF
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
    
    log "✅ Monitoring and logging configured"
}

# Create systemd service
create_systemd_service() {
    log_step "Creating systemd service..."
    
    cat > /etc/systemd/system/mantrapath.service << EOF
[Unit]
Description=MantraPath Mental Health Platform
After=docker.service network.target
Requires=docker.service
StartLimitIntervalSec=0

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=$BACKEND_DIR
ExecStart=/usr/bin/docker-compose -f docker-compose.prod.yml up -d
ExecStop=/usr/bin/docker-compose -f docker-compose.prod.yml down
ExecReload=/usr/bin/docker-compose -f docker-compose.prod.yml restart
TimeoutStartSec=600
TimeoutStopSec=120
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

    # Reload systemd and enable service
    systemctl daemon-reload
    systemctl enable mantrapath.service
    
    log "✅ Systemd service configured"
}

# Display deployment summary
show_deployment_summary() {
    log_step "Deployment Summary"
    
    echo ""
    echo "🎉 MantraPath Production Deployment Completed!"
    echo ""
    echo "📊 System Information:"
    echo "  - Server: $(hostname -I | awk '{print $1}')"
    echo "  - Environment: $DEPLOYMENT_ENV"
    echo "  - Deployment Time: $(date)"
    echo ""
    echo "🌐 Access URLs:"
    echo "  - Frontend: http://$(hostname -I | awk '{print $1}')"
    echo "  - API Gateway: http://$(hostname -I | awk '{print $1}'):8000"
    echo "  - API Documentation: http://$(hostname -I | awk '{print $1}'):8000/docs"
    echo "  - Health Check: http://$(hostname -I | awk '{print $1}'):8000/health"
    echo ""
    echo "🐳 Service Status:"
    cd "$BACKEND_DIR"
    docker-compose -f docker-compose.prod.yml ps
    echo ""
    echo "💾 System Resources:"
    echo "  Disk Usage:"
    df -h / | tail -1
    echo "  Memory Usage:"
    free -h | grep Mem
    echo ""
    echo "📝 Useful Commands:"
    echo "  - View logs: docker-compose -f $BACKEND_DIR/docker-compose.prod.yml logs -f [service]"
    echo "  - Restart services: systemctl restart mantrapath"
    echo "  - Monitor health: tail -f /var/log/mantrapath/monitor.log"
    echo "  - Update deployment: $0"
    echo ""
}

# Main deployment function
main() {
    log "🚀 Starting MantraPath Production Deployment..."
    log "Environment: $DEPLOYMENT_ENV"
    log "Force Rebuild: $FORCE_REBUILD"
    
    check_prerequisites
    setup_environment
    install_dependencies
    backup_current_deployment
    
    # Clean up if force rebuild
    if [ "$FORCE_REBUILD" = "true" ]; then
        log_info "Force rebuild requested, cleaning up existing deployment..."
        cd "$BACKEND_DIR"
        docker-compose -f docker-compose.prod.yml down --remove-orphans || true
        docker system prune -f --volumes || true
    fi
    
    deploy_infrastructure
    deploy_core_services
    deploy_application_services
    deploy_frontend
    configure_nginx
    setup_monitoring
    create_systemd_service
    
    # Final health check
    log_step "Final health verification..."
    sleep 30  # Give services time to fully stabilize
    
    if run_health_checks; then
        log "🎉 Deployment completed successfully!"
    else
        log_warning "⚠️ Deployment completed with some warnings"
    fi
    
    show_deployment_summary
}

# Handle script arguments
case "${1:-}" in
    "status")
        cd "$BACKEND_DIR"
        docker-compose -f docker-compose.prod.yml ps
        run_health_checks
        ;;
    "restart")
        log "🔄 Restarting MantraPath services..."
        systemctl restart mantrapath
        log "✅ Services restarted"
        ;;
    "stop")
        log "🛑 Stopping MantraPath services..."
        systemctl stop mantrapath
        log "✅ Services stopped"
        ;;
    "logs")
        cd "$BACKEND_DIR"
        docker-compose -f docker-compose.prod.yml logs -f "${2:-}"
        ;;
    "backup")
        backup_current_deployment
        ;;
    "health")
        run_health_checks
        ;;
    *)
        main
        ;;
esac
