# 🚀 MantraPath GitOps - Quick Start Guide

Get your MantraPath application deployed with automated GitOps in just a few steps!

## ⚡ Quick Setup (5 minutes)

### Step 1: Run the Setup Script
```bash
# Run as root to install system dependencies
sudo ./scripts/setup-gitops.sh
```

This will:
- Install Docker, Docker Compose, Nginx, Node.js
- Set up GitHub Actions runner
- Create environment files
- Configure monitoring and health checks

### Step 2: Configure GitHub Secrets

Go to your GitHub repository → Settings → Secrets and variables → Actions

Add these secrets:

| Secret Name | Value | Description |
|-------------|--------|-------------|
| `POSTGRES_PASSWORD` | `your_secure_password` | Database password |
| `JWT_SECRET_KEY` | `your_super_secret_jwt_key` | JWT signing key |
| `DOMAIN` | `139.84.213.185` | Your server IP/domain |
| `PROTOCOL` | `http` | Protocol (http/https) |

Optional secrets:
- `OPENAI_API_KEY` - For enhanced AI features
- `SMTP_*` - For email notifications

### Step 3: Complete GitHub Runner Setup

```bash
# Switch to runner user and configure
sudo -u runner /home/runner/actions-runner/config.sh \
  --url https://github.com/YOUR_USERNAME/mantrapath \
  --token YOUR_GITHUB_TOKEN

# Install as service
cd /home/runner/actions-runner
sudo ./svc.sh install runner
sudo ./svc.sh start
```

### Step 4: Deploy!

Push any change to trigger deployment:
```bash
git add .
git commit -m "🚀 Initial GitOps deployment"
git push origin main
```

## 🎯 What Happens Next?

1. **GitHub Actions triggers** on push to main
2. **Smart detection** determines what changed
3. **Infrastructure starts** (PostgreSQL, Redis, NATS)
4. **Core services deploy** (Models, AI services)
5. **Application services** start (API Gateway, Auth, etc.)
6. **Frontend builds** and deploys
7. **Nginx configures** reverse proxy
8. **Health checks** verify everything works

## 🌐 Access Your Application

After deployment completes:

- **Frontend**: http://YOUR_SERVER_IP
- **API Gateway**: http://YOUR_SERVER_IP:8000
- **API Docs**: http://YOUR_SERVER_IP:8000/docs
- **Health Check**: http://YOUR_SERVER_IP:8000/health

## 🔍 Monitoring & Management

### Check Status
```bash
# Quick health check
./scripts/health-monitor.sh status

# Full system validation
./scripts/validate-deployment.sh

# View service status
cd backend && docker-compose -f docker-compose.prod.yml ps
```

### View Logs
```bash
# All services
cd backend && docker-compose -f docker-compose.prod.yml logs -f

# Specific service
docker-compose -f backend/docker-compose.prod.yml logs -f api-gateway

# Deployment logs
tail -f ~/mantrapath-deploy.log

# Health monitoring logs
tail -f /var/log/mantrapath/health-monitor.log
```

### Manual Operations
```bash
# Manual deployment
sudo ./scripts/production-deploy.sh

# Restart services
sudo ./scripts/production-deploy.sh restart

# Health check with auto-restart
./scripts/health-monitor.sh restart

# Force restart all services
./scripts/health-monitor.sh force-restart
```

## 🛠️ Customization

### Environment Configuration

Edit these files for your setup:
- `backend/.env` - Backend configuration
- `frontend/.env` - Frontend configuration
- `nginx/mantrapath.conf` - Nginx reverse proxy

### Service Scaling

Modify `backend/docker-compose.prod.yml`:
```yaml
services:
  api-gateway:
    deploy:
      replicas: 3  # Scale to 3 instances
      resources:
        limits:
          memory: 1G
        reservations:
          memory: 512M
```

### SSL/HTTPS Setup

1. Get SSL certificates (Let's Encrypt recommended)
2. Update `nginx/mantrapath.conf` with SSL configuration
3. Set `PROTOCOL=https` in GitHub secrets
4. Redeploy

## 🚨 Troubleshooting

### Common Issues

**Services won't start:**
```bash
# Check system resources
df -h && free -h

# Check Docker
docker system df
docker system prune -f

# Restart everything
sudo ./scripts/production-deploy.sh restart
```

**Database connection errors:**
```bash
# Check PostgreSQL
docker-compose -f backend/docker-compose.prod.yml logs postgres
docker-compose -f backend/docker-compose.prod.yml exec postgres pg_isready -U mantrapath
```

**Frontend not loading:**
```bash
# Check Nginx
sudo nginx -t
sudo systemctl status nginx

# Check frontend build
docker-compose -f backend/docker-compose.prod.yml logs frontend
```

**GitHub Actions failing:**
```bash
# Check runner status
sudo systemctl status actions.runner.*

# Check runner logs
sudo journalctl -u actions.runner.* -f
```

### Get Help

1. **Validate setup**: `./scripts/validate-deployment.sh`
2. **Check logs**: See logging commands above
3. **Health report**: `./scripts/health-monitor.sh report`
4. **System status**: `./scripts/production-deploy.sh status`

## 📈 Advanced Features

### Auto-scaling
- Configure Docker Swarm mode
- Use Kubernetes for production scaling
- Set up load balancers

### Monitoring
- Prometheus metrics at `:9090`
- Grafana dashboards at `:3001`
- Custom alerts and notifications

### Backup & Recovery
- Automated database backups
- Configuration backups
- Disaster recovery procedures

### Security
- SSL/TLS termination
- Rate limiting and DDoS protection
- Security headers and CSP
- Regular security updates

## 🎉 Success!

Your MantraPath application is now running with:

✅ **Automated deployment** on every push  
✅ **Health monitoring** with auto-restart  
✅ **Production-ready** configuration  
✅ **Scalable architecture** with microservices  
✅ **Comprehensive logging** and monitoring  
✅ **Zero-downtime updates** with rolling deployment  

## 📚 Documentation

- **Full Setup Guide**: [GITOPS_SETUP.md](GITOPS_SETUP.md)
- **Architecture**: [project-doc/architecture/](project-doc/architecture/)
- **API Documentation**: http://YOUR_SERVER_IP:8000/docs
- **Service Documentation**: [backend/services/README.md](backend/services/README.md)

---

**Need help?** Check the troubleshooting section above or review the full documentation in `GITOPS_SETUP.md`.

**Ready to scale?** Consider Kubernetes deployment for production environments with high traffic.
