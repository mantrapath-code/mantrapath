# MantraPath Kubernetes Deployment Scripts

This directory contains comprehensive deployment scripts for MantraPath microservices platform using Kubernetes and Helm.

## 🚀 Quick Start

### Deploy to Development Environment
```bash
./deploy-k8s.sh --env dev
```

### Deploy to Production
```bash
./deploy-k8s.sh --env prod --build-images
```

### Monitor Health
```bash
./health-monitor.sh --env prod --watch
```

## 📁 Script Overview

### 1. `deploy-k8s.sh` - Main Deployment Script
**Purpose**: Comprehensive deployment script with full lifecycle management

**Features**:
- ✅ Multi-environment support (dev, staging, prod)
- ✅ Helm chart validation and linting
- ✅ Image building and pushing
- ✅ Health checks and rollout verification
- ✅ Built-in testing framework
- ✅ Proper error handling and cleanup

**Usage**:
```bash
# Basic deployment
./deploy-k8s.sh --env dev

# Production deployment with image build
./deploy-k8s.sh --env prod --build-images --timeout 15m

# Dry run
./deploy-k8s.sh --env dev --dry-run

# Force deployment (deletes existing release)
./deploy-k8s.sh --env prod --force

# Custom values file
./deploy-k8s.sh --env dev --values-file custom-values.yaml
```

### 2. `manage-environments.sh` - Environment Management
**Purpose**: Manage multiple environments and perform promotions

**Features**:
- ✅ Environment status overview
- ✅ Deployment promotion (dev → staging → prod)
- ✅ Rollback functionality
- ✅ Environment cleanup
- ✅ Log aggregation

**Usage**:
```bash
# List all environments
./manage-environments.sh list

# Deploy to specific environment
./manage-environments.sh deploy dev

# Promote from dev to staging
./manage-environments.sh promote dev staging

# Rollback production
./manage-environments.sh rollback prod

# Show environment status
./manage-environments.sh status prod

# View logs
./manage-environments.sh logs dev api-gateway

# Clean up environment
./manage-environments.sh cleanup dev
```

### 3. `health-monitor.sh` - Health Monitoring
**Purpose**: Comprehensive health monitoring for all services

**Features**:
- ✅ Real-time pod health monitoring
- ✅ Service endpoint validation
- ✅ Resource usage tracking
- ✅ Alert thresholds
- ✅ Multiple output formats (table, JSON, YAML)
- ✅ Watch mode for continuous monitoring

**Usage**:
```bash
# Basic health check
./health-monitor.sh --env prod

# Watch mode with alerts
./health-monitor.sh --env prod --watch --threshold 80

# Detailed output in JSON format
./health-monitor.sh --env dev --detailed --format json

# Monitor specific namespace
./health-monitor.sh --namespace mantrapath-prod
```

### 4. `test-charts.sh` - Chart Testing
**Purpose**: Comprehensive Helm chart testing and validation

**Features**:
- ✅ Helm lint validation
- ✅ Template generation testing
- ✅ Security policy validation
- ✅ Resource requirement testing
- ✅ Service connectivity testing
- ✅ Database initialization testing

**Usage**:
```bash
# Run all tests
./test-charts.sh

# Run tests with verbose output
./test-charts.sh --verbose

# Keep test resources for debugging
./test-charts.sh --keep-resources
```

## 🏗️ Architecture Overview

### Environment Structure
```
├── dev          # Development environment (minimal resources)
├── staging      # Staging environment (production-like)
└── prod         # Production environment (full resources)
```

### Service Categories
- **Frontend**: React SPA (port 3000)
- **API Gateway**: Main routing layer (port 8000)
- **Microservices**: 15+ backend services (ports 8001-8020)
- **Databases**: PostgreSQL (StatefulSet), Redis (StatefulSet)
- **Infrastructure**: NATS messaging, monitoring stack

### Deployment Flow
```
1. Prerequisites Check
2. Environment Setup
3. Image Building (optional)
4. Chart Validation
5. Helm Deployment
6. Health Verification
7. Service Testing
8. Status Reporting
```

## 📋 Prerequisites

### Required Tools
- `kubectl` >= 1.20
- `helm` >= 3.8
- `docker` >= 20.10
- `jq` >= 1.6

### Kubernetes Cluster Requirements
- Kubernetes >= 1.20
- StorageClass for persistent volumes
- Ingress controller (nginx recommended)
- Sufficient resources for target environment

### Environment Variables
```bash
# Container Registry (optional for image building)
export DOCKER_REGISTRY="your-registry.com/mantrapath"
export REGISTRY_USERNAME="your-username"
export REGISTRY_PASSWORD="your-password"

# Kubernetes Configuration
export KUBECONFIG="path/to/your/kubeconfig"

# Debugging
export HELM_DEBUG=1  # Enable Helm debug output
```

## 🔧 Configuration

### Values Files Structure
```
helm/mantrapath/
├── values.yaml              # Base values
├── values-dev.yaml          # Development overrides
├── values-staging.yaml      # Staging overrides  
└── values-prod.yaml         # Production overrides
```

### Environment-Specific Settings

#### Development (values-dev.yaml)
- Minimal resource allocation
- Single replica for most services
- Local storage class
- Debug logging enabled

#### Production (values-prod.yaml)
- High availability (2-3 replicas)
- Resource limits and requests
- Persistent storage
- Security policies enabled
- Monitoring and alerting

## 🚨 Best Practices

### 1. Environment Promotion
Always follow the promotion pipeline:
```
dev → staging → prod
```

### 2. Resource Management
- Set appropriate resource limits
- Use HPA for auto-scaling
- Monitor resource usage regularly

### 3. Security
- Enable Pod Security Standards
- Use NetworkPolicies
- Set proper SecurityContexts
- Regularly update container images

### 4. Monitoring
- Use health checks for all services
- Set up alerts for critical metrics
- Monitor resource usage trends

### 5. Backup Strategy
- Regular database backups
- Helm release history
- Configuration backup

## 🔍 Troubleshooting

### Common Issues

#### 1. Deployment Failures
```bash
# Check deployment status
kubectl get pods -n mantrapath-{env}
kubectl describe pod <pod-name> -n mantrapath-{env}

# Check Helm release
helm status mantrapath -n mantrapath-{env}
helm history mantrapath -n mantrapath-{env}
```

#### 2. Service Connectivity Issues
```bash
# Test service endpoints
./health-monitor.sh --env {env} --detailed

# Check service discovery
kubectl get endpoints -n mantrapath-{env}

# Test internal connectivity
kubectl exec -it <pod-name> -n mantrapath-{env} -- wget -qO- http://service-name:port/health
```

#### 3. Resource Issues
```bash
# Check resource usage
kubectl top pods -n mantrapath-{env}
kubectl top nodes

# Check resource quotas
kubectl describe resourcequota -n mantrapath-{env}
```

#### 4. Storage Issues
```bash
# Check PVC status
kubectl get pvc -n mantrapath-{env}
kubectl describe pvc <pvc-name> -n mantrapath-{env}

# Check storage class
kubectl get storageclass
```

### Recovery Procedures

#### 1. Rollback Deployment
```bash
# Automatic rollback to previous version
./manage-environments.sh rollback {env}

# Rollback to specific revision
./manage-environments.sh rollback {env} 3
```

#### 2. Emergency Scaling
```bash
# Scale down problematic service
kubectl scale deployment <service-name> --replicas=0 -n mantrapath-{env}

# Scale up when fixed
kubectl scale deployment <service-name> --replicas=2 -n mantrapath-{env}
```

#### 3. Database Recovery
```bash
# Check database connectivity
kubectl exec -it postgres-0 -n mantrapath-{env} -- pg_isready

# Access database directly
kubectl exec -it postgres-0 -n mantrapath-{env} -- psql -U mantrapath
```

## 📊 Monitoring and Alerting

### Health Check Endpoints
- **API Gateway**: `http://{host}/health`
- **Frontend**: `http://{host}/`
- **Microservices**: `http://{service}:8000/health`
- **Databases**: Connection-based health checks

### Key Metrics to Monitor
- Pod restart count
- Resource utilization (CPU/Memory)
- Response times and error rates
- Database connection pools
- Message queue depths

### Alert Conditions
- Pod crash loops (restarts > 5)
- Resource usage > 80%
- Service unavailable > 2 minutes
- Database connection failures

## 🔄 CI/CD Integration

### GitHub Actions Example
```yaml
name: Deploy to Kubernetes

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to Development
        run: |
          ./deployment/scripts/deploy-k8s.sh \
            --env dev \
            --build-images
      
      - name: Run Tests
        run: |
          ./deployment/scripts/test-charts.sh
```

### GitOps Integration
For production environments, consider using ArgoCD or Flux for GitOps-based deployments:

```yaml
# argocd-application.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: mantrapath-prod
spec:
  source:
    repoURL: https://github.com/mantrapath-code/mantrapath
    path: deployment/helm/mantrapath
    targetRevision: main
  destination:
    server: https://kubernetes.default.svc
    namespace: mantrapath-prod
```

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Run diagnostics: `./health-monitor.sh --env {env} --detailed`
3. Check logs: `./manage-environments.sh logs {env}`
4. Create an issue in the repository

---

**Version**: 2.0  
**Last Updated**: September 2025  
**Maintained by**: MantraPath Team