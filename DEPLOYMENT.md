# 🚀 MantraPath Deployment Guide

This guide covers deploying MantraPath on a self-hosted GitHub Actions runner using Docker Compose.

## 📋 Prerequisites

### System Requirements
- **OS**: Ubuntu 20.04+ or similar Linux distribution
- **RAM**: Minimum 8GB (16GB recommended for production)
- **Storage**: Minimum 50GB free space
- **CPU**: 4+ cores recommended

### Software Requirements
- **Docker**: 20.10+ with Docker Compose 2.0+
- **Node.js**: 18+ (for frontend building)
- **Nginx**: 1.18+ (for reverse proxy)
- **Git**: Latest version

### GitHub Setup
- Self-hosted runner with label `ubuntu-latest-m`
- Required secrets configured in GitHub repository

## 🔧 GitHub Secrets Configuration

Configure the following secrets in your GitHub repository settings:

### Required Secrets
```bash
# Database
POSTGRES_PASSWORD=your-secure-database-password

# JWT Authentication
JWT_SECRET_KEY=your-256-bit-jwt-secret-key

# External APIs (only if using OpenAI)
OPENAI_API_KEY=your-openai-api-key

# SMTP Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=your-email@gmail.com
APP_URL=https://your-domain.com

# Domain Configuration
DOMAIN=your-domain.com
PROTOCOL=https
```

### Optional Secrets
```bash
# Additional API Keys (only if needed)
# BHASHINI_API_KEY=your-bhashini-api-key
# BHASHINI_USER_ID=your-bhashini-user-id
# BHASHINI_BASE_URL=https://meity-auth.ulcacontrib.org
# BHASHINI_COMPUTE_URL=https://dhruva-api.bhashini.gov.in/services/inference
# BHASHINI_API_VERSION=v1
```

## 🏗️ Deployment Architecture

### Self-Hosted Runner Setup
1. **Runner Registration**: Register runner with label `ubuntu-latest-m`
2. **Docker Installation**: Ensure Docker and Docker Compose are installed
3. **Permissions**: Runner needs sudo access for system operations

### Service Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     Nginx       │    │   API Gateway   │    │   PostgreSQL    │
│   (Port 80)     │────│   (Port 8000)   │────│   (Port 5432)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌────────┴────────┐              │
         │              │                 │              │
         │         ┌────▼────┐      ┌────▼────┐         │
         │         │  Redis  │      │  NATS   │         │
         │         │(Port6379)│      │(Port4222)│         │
         │         └─────────┘      └─────────┘         │
         │                                               │
         │              ┌───────────────────────────────┘
         │              │
    ┌────▼────┐    ┌────▼──────────────────────────────┐
    │Frontend │    │        Microservices              │
    │(Port5173)│    │  • Auth Service (8001)           │
    └─────────┘    │  • Profile Service (8002)        │
                   │  • Mood Service (8003)            │
                   │  • Chatbot Service (8004)         │
                   │  • Community Service (8006)       │
                   │  • Notification Service (8007)    │
                   │  • ML Service (8008)              │
                   │  • Translation Service (8010)     │
                   │  • Voice Service (8011)           │
                   │  • Action Orchestrator (8012)     │
                   │  • AI Context Store (8013)        │
                   │  • Memory Service (8017)          │
                   └───────────────────────────────────┘
```

## 🚀 Deployment Process

### 1. Automatic Deployment (GitHub Actions)

The deployment is triggered automatically when code is pushed to the `main` branch:

```yaml
# .github/workflows/deploy.yml
name: Deploy MantraPath to Self-Hosted Runner
on:
  push:
    branches: [ main ]
```

**Deployment Steps:**
1. Code checkout and environment setup
2. Docker image building and pushing to GitHub Container Registry
3. Service deployment using `docker-compose.prod.yml`
4. Frontend building and deployment
5. Nginx configuration and setup
6. Health checks and monitoring setup

### 2. Manual Deployment

If you need to deploy manually on the runner:

```bash
# Clone the repository
git clone https://github.com/your-username/mantrapath.git
cd mantrapath

# Run deployment script
sudo ./scripts/deploy.sh

# Check deployment status
./scripts/health-check.sh
```

## 📁 File Structure

```
mantrapath/
├── .github/
│   └── workflows/
│       └── deploy.yml                 # GitHub Actions workflow
├── backend/
│   ├── docker-compose.yml            # Development compose
│   ├── docker-compose.prod.yml       # Production compose
│   └── .env                          # Environment variables (auto-generated)
├── frontend/
│   ├── .env                          # Frontend environment (auto-generated)
│   └── dist/                         # Built frontend files
├── nginx/
│   └── mantrapath.conf               # Nginx configuration
├── scripts/
│   ├── deploy.sh                     # Deployment script
│   └── health-check.sh               # Health monitoring script
└── DEPLOYMENT.md                     # This file
```

## 🔍 Health Monitoring

### Health Check Script

The deployment includes a comprehensive health monitoring system:

```bash
# Quick health check
./scripts/health-check.sh quick

# Full health check
./scripts/health-check.sh

# Check specific components
./scripts/health-check.sh docker    # Docker services
./scripts/health-check.sh api       # API endpoints
./scripts/health-check.sh system    # System resources
./scripts/health-check.sh nginx     # Nginx status
```

### Monitoring Features
- **Service Health**: All microservices health endpoints
- **Database Connectivity**: PostgreSQL and Redis checks
- **System Resources**: CPU, memory, and disk usage
- **Docker Status**: Container health and resource usage
- **Nginx Status**: Reverse proxy configuration and connectivity

### Health Report Generation
```bash
# Generate detailed health report
./scripts/health-check.sh report
```

Reports are saved to `${HOME}/mantrapath-health-report-YYYYMMDD-HHMMSS.txt`

## 🛠️ Management Commands

### Deployment Script Commands
```bash
# Full deployment
sudo ./scripts/deploy.sh

# Check status
./scripts/deploy.sh status

# Restart services
./scripts/deploy.sh restart

# Stop services
./scripts/deploy.sh stop

# View logs
./scripts/deploy.sh logs
```

### Docker Compose Commands
```bash
# Start services
cd backend
docker-compose -f docker-compose.prod.yml up -d

# Stop services
docker-compose -f docker-compose.prod.yml down

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Check status
docker-compose -f docker-compose.prod.yml ps
```

## 🌐 Access URLs

After successful deployment, access the application at:

- **Frontend**: `http://your-domain.com` or `http://runner-ip`
- **API Gateway**: `http://your-domain.com:8000` or `http://runner-ip:8000`
- **Health Check**: `http://your-domain.com/health` or `http://runner-ip/health`
- **API Documentation**: `http://your-domain.com/docs` or `http://runner-ip/docs`

## 🔧 Configuration

### Environment Variables

The deployment automatically generates environment files based on GitHub secrets:

**Backend (.env)**:
```bash
# Database
POSTGRES_DB=mantrapath
POSTGRES_USER=mantrapath
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}

# JWT
JWT_SECRET_KEY=${JWT_SECRET_KEY}

# Service Ports
API_GATEWAY_PORT=8000
AUTH_SERVICE_PORT=8001
# ... (all service ports)

# External APIs (only if needed)
OPENAI_API_KEY=${OPENAI_API_KEY}
# ... (other external API keys if needed)
```

**Frontend (.env)**:
```bash
VITE_API_BASE_URL=https://your-domain.com:8000
VITE_WS_URL=ws://your-domain.com:8080
VITE_ENVIRONMENT=production
```

### Nginx Configuration

The Nginx configuration includes:
- **Reverse Proxy**: Routes API calls to backend services
- **WebSocket Support**: Handles real-time connections
- **Static File Serving**: Serves frontend assets
- **Security Headers**: CORS, CSP, and other security measures
- **Rate Limiting**: API and general request limiting
- **Gzip Compression**: Optimized content delivery

## 🚨 Troubleshooting

### Common Issues

**1. Services Not Starting**
```bash
# Check Docker logs
docker-compose -f backend/docker-compose.prod.yml logs

# Check system resources
./scripts/health-check.sh system
```

**2. Database Connection Issues**
```bash
# Check PostgreSQL
docker-compose -f backend/docker-compose.prod.yml exec postgres pg_isready -U mantrapath

# Check Redis
docker-compose -f backend/docker-compose.prod.yml exec redis redis-cli ping
```

**3. Frontend Not Loading**
```bash
# Check Nginx status
systemctl status nginx

# Check Nginx configuration
nginx -t

# Check frontend build
ls -la /var/www/mantrapath/
```

**4. API Endpoints Not Responding**
```bash
# Check API Gateway
curl http://localhost:8000/health

# Check individual services
./scripts/health-check.sh api
```

### Log Files

- **Deployment Logs**: `${HOME}/mantrapath-deploy.log`
- **Health Check Logs**: `${HOME}/mantrapath-health.log`
- **Docker Logs**: `docker-compose -f backend/docker-compose.prod.yml logs`
- **Nginx Logs**: `/var/log/nginx/access.log` and `/var/log/nginx/error.log`

### Recovery Procedures

**1. Restart All Services**
```bash
sudo ./scripts/deploy.sh restart
```

**2. Complete Redeployment**
```bash
sudo ./scripts/deploy.sh stop
sudo ./scripts/deploy.sh
```

**3. Database Recovery**
```bash
# Backup database
docker-compose -f backend/docker-compose.prod.yml exec postgres pg_dump -U mantrapath mantrapath > backup.sql

# Restore database
docker-compose -f backend/docker-compose.prod.yml exec -T postgres psql -U mantrapath mantrapath < backup.sql
```

## 📊 Monitoring and Maintenance

### System Monitoring
- **Health Checks**: Automated every 5 minutes via cron
- **Resource Monitoring**: CPU, memory, and disk usage tracking
- **Service Monitoring**: All microservices health endpoint monitoring
- **Log Rotation**: Automatic log file rotation and cleanup

### Maintenance Tasks
- **Regular Updates**: Pull latest images and restart services
- **Database Maintenance**: Regular backups and cleanup
- **Log Cleanup**: Remove old log files to free space
- **Security Updates**: Keep system and Docker images updated

### Performance Optimization
- **Resource Limits**: Configured memory and CPU limits for containers
- **Caching**: Redis caching for improved performance
- **Nginx Optimization**: Gzip compression and connection pooling
- **Database Optimization**: Proper indexing and query optimization

## 🔒 Security Considerations

### Network Security
- **Firewall**: Configure appropriate firewall rules
- **SSL/TLS**: Enable HTTPS for production deployments
- **Access Control**: Restrict access to management ports

### Application Security
- **JWT Tokens**: Secure token generation and validation
- **API Keys**: Secure storage of external API keys
- **Database Security**: Strong passwords and access controls
- **CORS**: Properly configured cross-origin resource sharing

### System Security
- **User Permissions**: Run services with appropriate user permissions
- **File Permissions**: Secure file and directory permissions
- **Regular Updates**: Keep all components updated
- **Monitoring**: Monitor for security issues and anomalies

## 📞 Support

For deployment issues or questions:

1. **Check Logs**: Review deployment and health check logs
2. **Health Check**: Run comprehensive health checks
3. **Documentation**: Refer to service-specific documentation
4. **GitHub Issues**: Create an issue in the repository
5. **Community**: Join discussions in GitHub Discussions

---

**MantraPath Deployment** - Deploying mental health support with modern technology and reliable infrastructure. 💜
