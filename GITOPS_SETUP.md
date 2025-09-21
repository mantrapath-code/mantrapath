# MantraPath GitOps Deployment Guide

This guide explains the complete GitOps setup for MantraPath, enabling automatic deployment to your server whenever code is pushed to the main branch.

## 🎯 Overview

The GitOps setup includes:
- **Automated Deployment**: Triggers on every push to `main` branch
- **Smart Change Detection**: Only rebuilds changed components
- **Health Monitoring**: Comprehensive service health checks
- **Zero-Downtime Deployment**: Rolling updates with health verification
- **Production-Ready Configuration**: Optimized for production environments

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   GitHub Push   │───▶│  GitHub Actions  │───▶│  Self-Hosted    │
│   to main       │    │  Workflow        │    │  Runner         │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                         │
                                                         ▼
                              ┌─────────────────────────────────────┐
                              │         Production Server           │
                              │  ┌─────────┐ ┌─────────┐ ┌────────┐│
                              │  │ Backend │ │Frontend │ │ Nginx  ││
                              │  │Services │ │  React  │ │Reverse ││
                              │  │(Docker) │ │ (Docker)│ │ Proxy  ││
                              │  └─────────┘ └─────────┘ └────────┘│
                              └─────────────────────────────────────┘
```

## 🚀 Quick Start

### 1. Configure GitHub Secrets

Add these secrets to your GitHub repository (Settings → Secrets and variables → Actions):

```bash
# Required secrets
POSTGRES_PASSWORD=your_secure_password
JWT_SECRET_KEY=your_super_secret_jwt_key_change_in_production

# Optional secrets (use defaults if not set)
DOMAIN=139.84.213.185  # Your server IP or domain
PROTOCOL=http          # or https if you have SSL
OPENAI_API_KEY=your_openai_key  # Optional

# Email configuration (optional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
FROM_EMAIL=noreply@mantrapath.com
APP_URL=http://139.84.213.185
```

### 2. Set up Self-Hosted Runner

On your server, set up a GitHub Actions self-hosted runner:

```bash
# Download and configure runner
mkdir actions-runner && cd actions-runner
curl -o actions-runner-linux-x64-2.311.0.tar.gz -L https://github.com/actions/runner/releases/download/v2.311.0/actions-runner-linux-x64-2.311.0.tar.gz
tar xzf ./actions-runner-linux-x64-2.311.0.tar.gz

# Configure (follow GitHub instructions for your repo)
./config.sh --url https://github.com/YOUR_USERNAME/mantrapath --token YOUR_TOKEN

# Install as service
sudo ./svc.sh install
sudo ./svc.sh start
```

### 3. Initial Deployment

Push any change to the main branch to trigger the first deployment:

```bash
git add .
git commit -m "Initial GitOps deployment"
git push origin main
```

## 📋 Workflow Features

### Change Detection
The workflow automatically detects what has changed:
- **Backend changes**: Triggers backend service rebuild
- **Frontend changes**: Triggers frontend rebuild  
- **Configuration changes**: Updates Nginx and system config
- **Force rebuild**: Manual option to rebuild everything

### Deployment Strategy
1. **Validation Phase**: System checks and change detection
2. **Infrastructure**: Start databases and core services
3. **Core Services**: Deploy AI models and processing services
4. **Application Services**: Deploy business logic services
5. **API Gateway**: Start the main API gateway
6. **Frontend**: Build and deploy React application
7. **Configuration**: Update Nginx reverse proxy
8. **Health Checks**: Comprehensive service verification

### Health Monitoring
The deployment includes comprehensive health checks:
- Service endpoint health checks
- Database connectivity tests
- Redis connectivity tests
- System resource monitoring
- Automatic service restart on failures

## 🔧 Manual Operations

### Deploy Manually
```bash
# Run the production deployment script
sudo ./scripts/production-deploy.sh

# Check deployment status
./scripts/production-deploy.sh status

# Restart services
./scripts/production-deploy.sh restart
```

### Monitor Health
```bash
# Check all services
./scripts/health-monitor.sh check

# Check and auto-restart failed services
./scripts/health-monitor.sh restart

# Generate health report
./scripts/health-monitor.sh report

# View monitoring status
./scripts/health-monitor.sh status
```

### View Logs
```bash
# View all service logs
cd backend
docker-compose -f docker-compose.prod.yml logs -f

# View specific service logs
docker-compose -f docker-compose.prod.yml logs -f api-gateway

# View deployment logs
tail -f ~/mantrapath-deploy.log

# View health monitoring logs
tail -f /var/log/mantrapath/health-monitor.log
```

## 🌐 Access URLs

After successful deployment, access your application at:

- **Frontend**: http://YOUR_SERVER_IP
- **API Gateway**: http://YOUR_SERVER_IP:8000
- **API Documentation**: http://YOUR_SERVER_IP:8000/docs
- **Health Check**: http://YOUR_SERVER_IP:8000/health

## 🐳 Service Architecture

### Backend Services
- **API Gateway** (8000): Main entry point, routing, WebSocket
- **Auth Service** (8001): Authentication and authorization
- **Profile Service** (8002): User profile management
- **Mood Service** (8003): Mood tracking and analysis
- **Chatbot Service** (8004): AI-powered chatbot
- **Content Service** (8005): Content management
- **Community Service** (8006): Social features
- **Notification Service** (8007): Push notifications
- **ML Service** (8008): Machine learning insights
- **Media Service** (8009): File and media handling
- **Translation Service** (8010): Multi-language support
- **Voice Service** (8011): Speech processing
- **Action Orchestrator** (8012): Workflow coordination
- **AI Context Store** (8013): Context management
- **AI Event Processor** (8014): Event processing
- **Memory Service** (8017): Pattern analysis
- **Models Service** (8081): Centralized AI models

### Infrastructure Services
- **PostgreSQL** (5432): Primary database
- **Redis** (6379): Caching and sessions
- **NATS** (4222): Message streaming
- **Nginx** (80): Reverse proxy and load balancer

## 🔧 Configuration

### Environment Variables
The deployment uses environment variables for configuration. Key variables:

```bash
# Database
POSTGRES_PASSWORD=secure_password
DATABASE_URL=postgresql://mantrapath:password@postgres:5432/mantrapath

# Security
JWT_SECRET_KEY=your_jwt_secret
CORS_ORIGINS=["http://your-domain.com"]

# Services
DOMAIN=your-domain.com
PROTOCOL=https
ENVIRONMENT=production
```

### Nginx Configuration
The Nginx configuration (`nginx/mantrapath.conf`) handles:
- Reverse proxy to backend services
- Static file serving for frontend
- WebSocket proxy for real-time features
- Security headers and rate limiting
- GZIP compression

### Docker Compose
Production deployment uses `backend/docker-compose.prod.yml` with:
- Production-optimized images
- Health checks for all services
- Resource limits and reservations
- Persistent volumes for data
- Restart policies

## 🔍 Monitoring and Troubleshooting

### Health Monitoring
Automated health monitoring runs every 5 minutes:
- Checks all service endpoints
- Monitors system resources
- Automatically restarts failed services
- Sends alerts for critical issues

### Log Management
- Application logs: `/var/log/mantrapath/`
- Docker logs: `docker-compose logs`
- System logs: `journalctl -u mantrapath`
- Nginx logs: `/var/log/nginx/`

### Common Issues

1. **Service startup failures**
   ```bash
   # Check service logs
   docker-compose -f backend/docker-compose.prod.yml logs service-name
   
   # Restart specific service
   docker-compose -f backend/docker-compose.prod.yml restart service-name
   ```

2. **Database connection issues**
   ```bash
   # Check database health
   docker-compose -f backend/docker-compose.prod.yml exec postgres pg_isready
   
   # View database logs
   docker-compose -f backend/docker-compose.prod.yml logs postgres
   ```

3. **Memory or disk issues**
   ```bash
   # Check system resources
   df -h
   free -h
   
   # Clean up Docker resources
   docker system prune -f
   ```

## 🔄 Updates and Maintenance

### Automatic Updates
- Push to main branch triggers automatic deployment
- Only changed components are rebuilt and deployed
- Health checks ensure successful deployment
- Automatic rollback on critical failures

### Manual Updates
```bash
# Update specific service
docker-compose -f backend/docker-compose.prod.yml pull service-name
docker-compose -f backend/docker-compose.prod.yml up -d service-name

# Update all services
docker-compose -f backend/docker-compose.prod.yml pull
docker-compose -f backend/docker-compose.prod.yml up -d
```

### Backup and Recovery
```bash
# Backup database
docker-compose -f backend/docker-compose.prod.yml exec postgres pg_dump -U mantrapath mantrapath > backup.sql

# Restore database
docker-compose -f backend/docker-compose.prod.yml exec -T postgres psql -U mantrapath mantrapath < backup.sql
```

## 🛡️ Security Considerations

1. **Secrets Management**: Use GitHub Secrets for sensitive data
2. **Network Security**: Configure firewall rules appropriately
3. **SSL/TLS**: Configure HTTPS in production
4. **Database Security**: Use strong passwords and connection encryption
5. **Container Security**: Regular image updates and vulnerability scanning

## 📈 Performance Optimization

1. **Resource Allocation**: Configure Docker resource limits
2. **Caching**: Redis caching for frequently accessed data
3. **Database Optimization**: Connection pooling and query optimization
4. **CDN**: Use CDN for static assets in production
5. **Monitoring**: Set up performance monitoring and alerting

## 🆘 Support and Troubleshooting

For issues with the GitOps setup:

1. Check GitHub Actions workflow logs
2. Review deployment logs on the server
3. Run health checks manually
4. Check service-specific logs
5. Verify environment configuration

## 📚 Additional Resources

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Nginx Configuration Guide](https://nginx.org/en/docs/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

---

This GitOps setup provides a robust, automated deployment pipeline for MantraPath, ensuring reliable and efficient deployments with comprehensive monitoring and health checks.
