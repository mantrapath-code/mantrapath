# MantraPath Deployment System

Complete deployment and orchestration system for MantraPath microservices platform.

## 🏗️ Architecture Overview

MantraPath consists of 22+ microservices deployed on Kubernetes using Helm charts, with all images stored in Vultr Container Registry.

### Services

#### Core Services
- **API Gateway** (8000) - Main entry point and routing
- **Frontend** (3000) - React-based user interface
- **Models Service** (8080) - AI/ML model management
- **Translation Service** (8010) - Multi-language support

#### User & Authentication
- **Auth Service** (8001) - Authentication and authorization
- **Profile Service** (8002) - User profile management

#### AI & Intelligence
- **Chatbot Service** (8003) - Conversational AI
- **ML Service** (8004) - Machine learning workflows
- **AI Context Store** (8005) - Context management
- **AI Event Processor** (8006) - Event processing
- **PHI3 Agent** (8018) - Advanced AI agent

#### Communication & Media
- **Voice Service** (8007) - Voice processing
- **Voice Event Processor** (8008) - Voice event handling
- **Media Service** (8012) - Media file management
- **Notification Service** (8013) - Notifications

#### Content & Community
- **Content Service** (8009) - Content management
- **Community Service** (8011) - Community features

#### System & Orchestration
- **Memory Service** (8014) - Memory management
- **Mood Service** (8015) - Mood tracking
- **Action Orchestrator** (8016) - Action coordination
- **Proactive Assistance** (8017) - Proactive help
- **Deployment API** (8086) - Deployment management

#### Infrastructure
- **PostgreSQL** (5432) - Primary database
- **Redis** (6379) - Caching and sessions
- **NATS** (4222) - Message broker

## 📁 Directory Structure

```
deployment/
├── configs/                    # Configuration files
│   └── Dockerfile.frontend    # Frontend container config
├── docs/                      # Documentation
│   ├── HELM_DEPLOYMENT_GUIDE.md
│   ├── PRODUCTION_DEPLOYMENT_STEPS.md
│   ├── PRODUCTION_PORT_MAPPING.md
│   └── vultr-prod-setup.md
├── environments/              # Environment configurations
│   ├── kind-dev.yaml         # Development cluster config
│   ├── kind-prod.yaml        # Production cluster config
│   └── production.env        # Production environment variables
├── helm/                     # Helm charts
│   └── mantrapath/          # Main umbrella chart
│       ├── charts/          # Service-specific charts
│       ├── templates/       # Kubernetes templates
│       ├── values-complete.yaml      # Complete service configuration
│       ├── values-vultr-prod.yaml   # Vultr production config
│       └── values-dev.yaml          # Development config
└── scripts/                  # Deployment scripts
    ├── deploy-all-services.sh       # Complete deployment
    ├── monitor-services.sh          # Service monitoring
    └── test-deployment.sh           # Deployment testing
```

## 🚀 Quick Start

### Prerequisites

1. **Docker** - For building container images
2. **kubectl** - Kubernetes command-line tool
3. **Helm 3.x** - Kubernetes package manager
4. **Kind** - For local development (dev environment)
5. **Access to Vultr Container Registry**

### Environment Setup

```bash
# Set registry credentials
export VULTR_REGISTRY_PASSWORD="your-password-here"

# For development (creates Kind cluster)
./scripts/deploy-all-services.sh -e dev

# For production
./scripts/deploy-all-services.sh -e prod
```

## 📋 Deployment Scripts

### 1. Complete Deployment (`deploy-all-services.sh`)

Builds all images, pushes to registry, and deploys to Kubernetes.

```bash
# Deploy all services to development
./scripts/deploy-all-services.sh -e dev

# Deploy specific services to production
./scripts/deploy-all-services.sh -e prod -s "api-gateway,frontend,models-service"

# Only build images (no deployment)
./scripts/deploy-all-services.sh -b

# Only deploy (no image building)
./scripts/deploy-all-services.sh -d

# Force rebuild all images
./scripts/deploy-all-services.sh -f
```

**Options:**
- `-e, --environment ENV` - Target environment (dev|prod)
- `-s, --services SERVICES` - Comma-separated service list
- `-b, --build-only` - Only build images
- `-d, --deploy-only` - Only deploy
- `-f, --force-rebuild` - Force rebuild all images

### 2. Service Monitoring (`monitor-services.sh`)

Monitors deployed services and provides health status.

```bash
# Check all services once
./scripts/monitor-services.sh -e dev

# Continuous monitoring (watch mode)
./scripts/monitor-services.sh -e prod -w -i 60

# Show only unhealthy services with details
./scripts/monitor-services.sh -d -u
```

**Options:**
- `-e, --environment ENV` - Target environment
- `-w, --watch` - Continuous monitoring
- `-d, --detailed` - Show detailed information
- `-u, --unhealthy-only` - Show only unhealthy services
- `-i, --interval SECONDS` - Watch interval

### 3. Deployment Testing (`test-deployment.sh`)

Comprehensive testing of the deployment pipeline.

```bash
# Full deployment test
./scripts/test-deployment.sh

# Quick test (essential services only)
./scripts/test-deployment.sh -q

# Test existing deployment without rebuilding
./scripts/test-deployment.sh -s -d

# Test and cleanup afterward
./scripts/test-deployment.sh -c
```

**Options:**
- `-e, --environment ENV` - Target environment
- `-s, --skip-build` - Skip image building
- `-d, --skip-deploy` - Skip deployment
- `-q, --quick-test` - Run essential tests only
- `-c, --cleanup` - Cleanup after testing

## 🔧 Configuration

### Helm Values Files

- **`values-complete.yaml`** - Complete production configuration with all services
- **`values-vultr-prod.yaml`** - Vultr-specific production settings
- **`values-dev.yaml`** - Development environment settings

### Key Configuration Sections

```yaml
global:
  registry: "blr.vultrcr.com/mantrapath"
  env: prod
  namespace: mantrapath-prod
  imagePullPolicy: Always
  
  # Registry credentials
  imagePullSecrets:
    - name: "mantrapath-registry"

# Service configuration example
apiGateway:
  enabled: true
  replicaCount: 3
  image:
    repository: mantrapath-api-gateway
    tag: latest
  service:
    port: 8000
  resources:
    requests:
      cpu: "500m"
      memory: "1Gi"
    limits:
      cpu: "2000m"
      memory: "4Gi"
  autoscaling:
    enabled: true
    minReplicas: 3
    maxReplicas: 15
```

## 🌍 Environments

### Development Environment

- **Cluster**: Kind (local)
- **Namespace**: `mantrapath-dev`
- **Registry**: Vultr Container Registry
- **Access**: http://localhost:30880

```bash
# Setup development environment
kind create cluster --name mantrapath-dev
./scripts/deploy-all-services.sh -e dev
```

### Production Environment

- **Cluster**: Vultr Kubernetes Engine (VKE)
- **Namespace**: `mantrapath-prod`
- **Registry**: Vultr Container Registry
- **Access**: https://mantrapath.com

```bash
# Deploy to production
./scripts/deploy-all-services.sh -e prod
```

## 📊 Monitoring & Health Checks

### Health Check Endpoints

All services expose standardized health endpoints:

- `/health` - Comprehensive health check
- `/health/live` - Kubernetes liveness probe
- `/health/ready` - Kubernetes readiness probe
- `/health/metrics` - Performance metrics

### Service Monitoring

```bash
# Real-time monitoring dashboard
./scripts/monitor-services.sh -e prod -w -d

# Check specific service health
kubectl port-forward svc/mantrapath-prod-api-gateway 8000:8000 -n mantrapath-prod
curl http://localhost:8000/health
```

## 🔄 CI/CD Integration

### GitHub Actions Workflow

The deployment system integrates with GitHub Actions:

- **Workflow**: `.github/workflows/complete-deployment.yml`
- **Triggers**: Push to main/develop, manual dispatch
- **Registry**: Vultr Container Registry
- **Environments**: Automatic dev/prod deployment

### Manual Deployment

```bash
# Trigger deployment workflow
gh workflow run complete-deployment.yml \
  --field environment=prod \
  --field force_rebuild=true
```

## 🛠️ Troubleshooting

### Common Issues

1. **Image Pull Errors**
   ```bash
   # Check registry secret
   kubectl get secret mantrapath-registry -n mantrapath-prod -o yaml
   
   # Recreate secret
   kubectl create secret docker-registry mantrapath-registry \
     --docker-server=blr.vultrcr.com \
     --docker-username=e9b950f6-81b8-4433-bb62-844d3f44b6bb \
     --docker-password="$VULTR_REGISTRY_PASSWORD" \
     -n mantrapath-prod
   ```

2. **Pod CrashLoopBackOff**
   ```bash
   # Check pod logs
   kubectl logs -f deployment/mantrapath-prod-api-gateway -n mantrapath-prod
   
   # Describe pod for events
   kubectl describe pod <pod-name> -n mantrapath-prod
   ```

3. **Service Unreachable**
   ```bash
   # Check service endpoints
   kubectl get endpoints -n mantrapath-prod
   
   # Test service connectivity
   kubectl port-forward svc/mantrapath-prod-api-gateway 8000:8000 -n mantrapath-prod
   ```

### Useful Commands

```bash
# View all resources
kubectl get all -n mantrapath-prod

# Check resource usage
kubectl top pods -n mantrapath-prod

# View recent events
kubectl get events -n mantrapath-prod --sort-by=.metadata.creationTimestamp

# Scale service
kubectl scale deployment mantrapath-prod-api-gateway --replicas=5 -n mantrapath-prod

# Rolling update
helm upgrade mantrapath-prod ./helm/mantrapath \
  --namespace mantrapath-prod \
  --values helm/mantrapath/values-complete.yaml
```

## 🔐 Security

### Production Security Features

- **Non-root containers** - All services run as non-root users
- **Resource limits** - CPU and memory limits enforced
- **Network policies** - Service-to-service communication controls
- **Secret management** - Kubernetes secrets for sensitive data
- **Image scanning** - Container images scanned for vulnerabilities
- **TLS encryption** - HTTPS/TLS for external traffic

### Registry Security

- **Private registry** - Images stored in private Vultr registry
- **Access tokens** - Service account tokens for registry access
- **Image signing** - Container image integrity verification

## 📈 Scaling

### Horizontal Pod Autoscaling

Services automatically scale based on CPU/memory usage:

```yaml
autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70
  targetMemoryUtilizationPercentage: 80
```

### Manual Scaling

```bash
# Scale specific service
kubectl scale deployment mantrapath-prod-chatbot-service --replicas=5 -n mantrapath-prod

# Update via Helm
helm upgrade mantrapath-prod ./helm/mantrapath \
  --set chatbotService.replicaCount=5 \
  -n mantrapath-prod
```

## 🆘 Support

### Getting Help

1. **Check logs**: Use monitoring script or kubectl logs
2. **Review documentation**: See docs/ directory
3. **Test deployment**: Run test-deployment.sh
4. **Monitor services**: Use monitor-services.sh

### Emergency Procedures

```bash
# Emergency rollback
helm rollback mantrapath-prod -n mantrapath-prod

# Emergency scaling down
kubectl scale deployment --all --replicas=1 -n mantrapath-prod

# Emergency pod restart
kubectl rollout restart deployment/mantrapath-prod-api-gateway -n mantrapath-prod
```

---

## 📝 Quick Reference

| Task | Command |
|------|---------|
| Deploy all services | `./scripts/deploy-all-services.sh -e prod` |
| Monitor services | `./scripts/monitor-services.sh -e prod -w` |
| Test deployment | `./scripts/test-deployment.sh` |
| Check pod status | `kubectl get pods -n mantrapath-prod` |
| View service logs | `kubectl logs -f deployment/service-name -n mantrapath-prod` |
| Port forward service | `kubectl port-forward svc/service-name port:port -n mantrapath-prod` |
| Scale service | `kubectl scale deployment service-name --replicas=N -n mantrapath-prod` |

---

*For detailed production deployment instructions, see [docs/PRODUCTION_DEPLOYMENT_STEPS.md](docs/PRODUCTION_DEPLOYMENT_STEPS.md)*
