# 🚀 MantraPath Helm Deployment Guide

Complete guide for deploying MantraPath using Kubernetes and Helm with comprehensive DevOps practices.

## 📋 Table of Contents

- [Overview](#-overview)
- [Prerequisites](#-prerequisites)
- [Quick Start](#-quick-start)
- [Architecture](#-architecture)
- [Configuration](#-configuration)
- [Deployment](#-deployment)
- [Monitoring & Health Checks](#-monitoring--health-checks)
- [CI/CD Integration](#-cicd-integration)
- [Security](#-security)
- [Troubleshooting](#-troubleshooting)
- [Production Considerations](#-production-considerations)

## 🎯 Overview

This Helm deployment provides:

- **Complete microservices architecture** with 20+ services
- **Automatic scaling** with HPA and resource management
- **High availability** with Pod Disruption Budgets
- **Secure secrets management** with Kubernetes secrets
- **Ingress with TLS** support via cert-manager
- **Health monitoring** and automated checks
- **CI/CD integration** with GitHub Actions
- **Multi-environment** support (dev/prod)

### 🏗️ Services Included

| Service | Description | Port | Autoscaling |
|---------|-------------|------|-------------|
| **Frontend** | React/Vite web application | 3000 | Manual |
| **API Gateway** | Main API entry point | 8000 | ✅ 2-10 pods |
| **Models Service** | AI/ML model inference | 8080 | ✅ 1-5 pods |
| **Translation Service** | Language translation | 8010 | ✅ 1-5 pods |
| **Chatbot Service** | Conversational AI | 8004 | ✅ 2-8 pods |
| **Auth Service** | Authentication & authorization | 8001 | Manual |
| **Profile Service** | User profile management | 8002 | Manual |
| **Mood Service** | Mood tracking & analysis | 8003 | Manual |
| **Content Service** | Content management | 8005 | Manual |
| **Community Service** | Community features | 8006 | Manual |
| **Notification Service** | Push notifications | 8007 | Manual |
| **ML Service** | Machine learning pipeline | 8008 | Manual |
| **Voice Service** | Voice processing | 8011 | Manual |
| **Memory Service** | Context & memory store | 8017 | Manual |
| **Media Service** | Media file handling | 8021 | Manual |
| **PostgreSQL** | Primary database | 5432 | Stateful |
| **Redis** | Caching & sessions | 6379 | Stateful |
| **NATS** | Message broker | 4222 | Stateful |

## ✅ Prerequisites

### System Requirements

- **Kubernetes cluster** (1.24+)
- **Helm 3.8+**
- **kubectl** configured for your cluster
- **Docker** (for building images)
- **4+ CPU cores, 8+ GB RAM** (minimum for dev)
- **50+ GB storage** (for persistent volumes)

### Tools Installation

```bash
# Quick setup (installs everything)
./deployment/setup-helm-environment.sh --environment dev

# Or install manually:
# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"

# Install Helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Install Docker
curl -fsSL https://get.docker.com | sh
```

### Cluster Setup Options

#### Option 1: Local Development (Kind)
```bash
# Create local cluster with ingress
./deployment/setup-helm-environment.sh --environment dev --create-kind-cluster
```

#### Option 2: Cloud Provider
```bash
# Configure kubectl for your cloud provider
# AWS EKS
aws eks update-kubeconfig --region us-west-2 --name my-cluster

# Google GKE
gcloud container clusters get-credentials my-cluster --zone us-central1-a

# Azure AKS
az aks get-credentials --resource-group myResourceGroup --name myAKSCluster
```

## 🚀 Quick Start

### 1. Environment Setup

```bash
# Clone repository
git clone https://github.com/mantrapath-code/mantrapath.git
cd mantrapath

# Setup environment (installs tools, creates cluster if needed)
./deployment/setup-helm-environment.sh --environment dev --create-kind-cluster

# Verify setup
kubectl cluster-info
helm version
```

### 2. Deploy to Development

```bash
# Deploy all services
./deployment/helm-deploy.sh --environment dev

# Check deployment status
kubectl get pods -n mantrapath-dev

# Run health checks
./deployment/helm-health-check.sh --environment dev
```

### 3. Access Application

```bash
# Get ingress IP/hostname
kubectl get ingress -n mantrapath-dev

# For local Kind cluster, add to /etc/hosts:
echo "127.0.0.1 mantrapath-dev.local" | sudo tee -a /etc/hosts

# Access application
open http://mantrapath-dev.local
```

## 🏗️ Architecture

### High-Level Architecture

```
Internet → Ingress → API Gateway → Microservices
                                ↓
                        Database Layer (PostgreSQL, Redis, NATS)
```

### Kubernetes Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Ingress       │    │  Frontend       │    │  API Gateway    │
│  (nginx)        │────│  (React/Vite)   │    │  (FastAPI)      │
│  Port: 80/443   │    │  Port: 3000     │    │  Port: 8000     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
                       ┌────────────────────────────────┼────────────────────────────────┐
                       │                                │                                │
         ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
         │  Auth Service   │    │  Models Service │    │ Translation Svc │    │  Chatbot Svc    │
         │  Port: 8001     │    │  Port: 8080     │    │  Port: 8010     │    │  Port: 8004     │
         └─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
                                         │
                       ┌─────────────────┼─────────────────┐
                       │                 │                 │
         ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
         │   PostgreSQL    │    │     Redis       │    │      NATS       │
         │   Port: 5432    │    │   Port: 6379    │    │   Port: 4222    │
         └─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Scaling & High Availability

- **Horizontal Pod Autoscaler (HPA)**: Automatically scales critical services based on CPU/memory
- **Pod Disruption Budgets (PDB)**: Ensures minimum availability during updates
- **Resource Limits**: Prevents resource starvation
- **Health Checks**: Liveness and readiness probes for all services
- **Rolling Updates**: Zero-downtime deployments

## ⚙️ Configuration

### Environment-Specific Values

#### Development (`values-dev.yaml`)
- **Replicas**: 1 per service (cost-effective)
- **Resources**: Minimal (development workstation friendly)
- **Storage**: 10Gi for database
- **TLS**: Disabled (HTTP only)
- **Ingress**: `mantrapath-dev.local`

#### Production (`values-prod.yaml`)
- **Replicas**: 2-20 per service (high availability)
- **Resources**: Production-grade allocations
- **Storage**: 100Gi+ for database
- **TLS**: Enabled with Let's Encrypt
- **Ingress**: `mantrapath.com`

### Secret Management

Secrets are managed via Kubernetes secrets with the following structure:

```yaml
# Development secrets (auto-created)
postgres-password: "dev-postgres-password"
jwt-secret-key: "dev-jwt-secret-key"
service-auth-token: "dev-service-auth-token"

# Production secrets (must be provided)
postgres-password: "CHANGE_IN_PRODUCTION"
jwt-secret-key: "CHANGE_IN_PRODUCTION"
openai-api-key: "CHANGE_IN_PRODUCTION"
```

### Custom Configuration

```bash
# Use custom values file
./deployment/helm-deploy.sh --environment dev --values-file my-custom-values.yaml

# Override specific values
helm upgrade --install mantrapath-dev ./deployment/helm/mantrapath \
  --namespace mantrapath-dev \
  --set apiGateway.replicas=3 \
  --set global.registry=my-registry.com
```

## 🚀 Deployment

### Development Deployment

```bash
# Full deployment with health checks
./deployment/helm-deploy.sh --environment dev

# Dry run (validate without deploying)
./deployment/helm-deploy.sh --environment dev --dry-run

# Force deployment (ignore validation errors)
./deployment/helm-deploy.sh --environment dev --force

# Custom timeout for slow clusters
./deployment/helm-deploy.sh --environment dev --timeout 15m
```

### Production Deployment

```bash
# Production deployment (requires manual approval in CI/CD)
./deployment/helm-deploy.sh --environment prod

# Production with custom domain
helm upgrade --install mantrapath-prod ./deployment/helm/mantrapath \
  --namespace mantrapath-prod \
  --values values-prod.yaml \
  --set ingress.hosts[0].host=mycompany.com
```

### Deployment Verification

```bash
# Check all resources
kubectl get all -n mantrapath-dev

# Check pod logs
kubectl logs -f deployment/mantrapath-dev-api-gateway -n mantrapath-dev

# Check ingress
kubectl describe ingress mantrapath-dev-ingress -n mantrapath-dev

# Port forward for local testing
kubectl port-forward svc/mantrapath-dev-api-gateway 8080:8000 -n mantrapath-dev
```

## 🏥 Monitoring & Health Checks

### Automated Health Monitoring

```bash
# Single health check
./deployment/helm-health-check.sh --environment dev

# Continuous monitoring (every 60s)
./deployment/helm-health-check.sh --environment dev --continuous

# Quick health check (5s timeout)
./deployment/helm-health-check.sh --environment dev --timeout 5

# Verbose output with detailed logs
./deployment/helm-health-check.sh --environment dev --verbose
```

### Health Check Components

1. **Pod Status**: Ensures all pods are running
2. **Service Endpoints**: Verifies service discovery
3. **HTTP Health Endpoints**: Tests application health
4. **Database Connectivity**: PostgreSQL connection test
5. **Redis Connectivity**: Cache availability
6. **NATS Connectivity**: Message broker status
7. **Inter-service Communication**: Service mesh validation

### Monitoring Dashboard

```bash
# Access built-in metrics (if enabled)
kubectl port-forward svc/mantrapath-dev-api-gateway 9090:9090 -n mantrapath-dev
open http://localhost:9090/metrics

# Grafana dashboard (production)
kubectl port-forward svc/mantrapath-prod-grafana 3000:3000 -n mantrapath-prod
open http://localhost:3000
```

## 🔄 CI/CD Integration

### GitHub Actions Workflow

The deployment includes a comprehensive GitHub Actions workflow (`.github/workflows/helm-deploy.yml`) that:

1. **Validates** Helm charts on PR
2. **Builds** Docker images for all services
3. **Deploys** to development on main branch
4. **Deploys** to production on manual trigger
5. **Runs** health checks and verification

### Workflow Triggers

```yaml
# Automatic triggers
on:
  push:
    branches: [main]
    paths: ['backend/**', 'frontend/**', 'deployment/helm/**']
  pull_request:
    branches: [main]

# Manual trigger
  workflow_dispatch:
    inputs:
      environment:
        type: choice
        options: [dev, prod]
```

### Required GitHub Secrets

```bash
# Development secrets
DEV_POSTGRES_PASSWORD
DEV_JWT_SECRET
DEV_SERVICE_AUTH_TOKEN

# Production secrets
PROD_POSTGRES_PASSWORD
PROD_JWT_SECRET
PROD_SERVICE_AUTH_TOKEN
PROD_OPENAI_API_KEY

# Container registry
GITHUB_TOKEN  # Automatic for GHCR
```

### Manual CI/CD Setup

```bash
# Setup GitHub secrets
gh secret set DEV_POSTGRES_PASSWORD --body "your-dev-password"
gh secret set PROD_POSTGRES_PASSWORD --body "your-prod-password"

# Trigger deployment
gh workflow run helm-deploy.yml --field environment=dev
gh workflow run helm-deploy.yml --field environment=prod
```

## 🔒 Security

### Secrets Management

```bash
# Create production secrets manually
kubectl create secret generic mantrapath-secrets \
  --from-literal=postgres-password="$(openssl rand -base64 32)" \
  --from-literal=jwt-secret-key="$(openssl rand -base64 64)" \
  --from-literal=service-auth-token="$(openssl rand -base64 32)" \
  --namespace mantrapath-prod

# Use external secret management (recommended)
# - AWS Secrets Manager
# - Azure Key Vault  
# - HashiCorp Vault
# - Kubernetes External Secrets Operator
```

### Security Contexts

All containers run with:
- **Non-root user** (UID 1000)
- **Read-only root filesystem**
- **No privilege escalation**
- **Dropped capabilities**

### Network Policies

```yaml
# Example network policy (add to values.yaml)
networkPolicies:
  enabled: true
  ingress:
    - from:
      - namespaceSelector:
          matchLabels:
            name: ingress-nginx
  egress:
    - to: []  # Allow all egress (customize as needed)
```

### TLS Configuration

```bash
# Production TLS with Let's Encrypt
helm upgrade --install mantrapath-prod ./deployment/helm/mantrapath \
  --set ingress.tls[0].secretName=mantrapath-tls \
  --set ingress.tls[0].hosts[0]=mantrapath.com \
  --set ingress.annotations."cert-manager\.io/cluster-issuer"=letsencrypt-prod
```

## 🐛 Troubleshooting

### Common Issues

#### 1. Pods Stuck in Pending State

```bash
# Check node resources
kubectl describe nodes

# Check pod events
kubectl describe pod <pod-name> -n mantrapath-dev

# Check storage classes
kubectl get storageclass
```

**Solution**: Ensure sufficient cluster resources or adjust resource requests.

#### 2. Ingress Not Working

```bash
# Check ingress controller
kubectl get pods -n ingress-nginx

# Check ingress resource
kubectl describe ingress mantrapath-dev-ingress -n mantrapath-dev

# Check DNS resolution
nslookup mantrapath-dev.local
```

**Solution**: Verify ingress controller installation and DNS configuration.

#### 3. Database Connection Issues

```bash
# Check PostgreSQL pod
kubectl logs deployment/mantrapath-dev-postgres -n mantrapath-dev

# Test database connectivity
kubectl exec -it deployment/mantrapath-dev-postgres -n mantrapath-dev -- psql -U postgres

# Check secrets
kubectl get secret mantrapath-secrets -n mantrapath-dev -o yaml
```

**Solution**: Verify database credentials and network connectivity.

#### 4. Service Discovery Issues

```bash
# Test service resolution
kubectl exec -it deployment/mantrapath-dev-api-gateway -n mantrapath-dev -- nslookup mantrapath-dev-auth-service

# Check service endpoints
kubectl get endpoints -n mantrapath-dev

# Check service labels
kubectl get services -n mantrapath-dev --show-labels
```

### Debug Commands

```bash
# Get all resources with issues
kubectl get events --sort-by=.metadata.creationTimestamp -n mantrapath-dev

# Check resource usage
kubectl top pods -n mantrapath-dev
kubectl top nodes

# Debug specific pod
kubectl exec -it <pod-name> -n mantrapath-dev -- /bin/bash

# Check logs for all services
kubectl logs -f -l app.kubernetes.io/instance=mantrapath-dev -n mantrapath-dev
```

### Log Analysis

```bash
# Centralized logging (if available)
kubectl logs -f deployment/mantrapath-dev-api-gateway -n mantrapath-dev | jq .

# Export logs for analysis
kubectl logs deployment/mantrapath-dev-api-gateway -n mantrapath-dev --since=1h > api-gateway.log

# Monitor real-time logs
stern mantrapath-dev -n mantrapath-dev
```

## 🏢 Production Considerations

### Resource Planning

| Environment | CPU Cores | Memory | Storage | Nodes |
|-------------|-----------|--------|---------|-------|
| **Development** | 4+ cores | 8+ GB | 50+ GB | 1 node |
| **Staging** | 8+ cores | 16+ GB | 100+ GB | 2 nodes |
| **Production** | 16+ cores | 32+ GB | 500+ GB | 3+ nodes |

### High Availability Setup

```yaml
# Production values.yaml additions
global:
  affinity:
    podAntiAffinity:
      preferredDuringSchedulingIgnoredDuringExecution:
      - weight: 100
        podAffinityTerm:
          labelSelector:
            matchExpressions:
            - key: app.kubernetes.io/name
              operator: In
              values: ["mantrapath"]
          topologyKey: kubernetes.io/hostname

# Database with replicas
postgres:
  architecture: replication
  primary:
    persistence:
      size: 100Gi
  readReplicas:
    replicaCount: 2
```

### Backup Strategy

```bash
# Database backups
kubectl create cronjob postgres-backup \
  --image=postgres:15 \
  --schedule="0 2 * * *" \
  --restart=OnFailure \
  -- pg_dump -h mantrapath-prod-postgres -U postgres mantrapath > /backup/backup-$(date +%Y%m%d).sql

# Persistent volume snapshots
kubectl patch pvc postgres-data -p '{"metadata":{"annotations":{"volume.beta.kubernetes.io/storage-provisioner":"snapshot.storage.k8s.io"}}}'
```

### Monitoring & Alerting

```bash
# Install monitoring stack
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install monitoring prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace

# Configure alerts for MantraPath
kubectl apply -f - <<EOF
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: mantrapath-alerts
spec:
  groups:
  - name: mantrapath
    rules:
    - alert: MantraPathServiceDown
      expr: up{job="mantrapath-api-gateway"} == 0
      for: 5m
      labels:
        severity: critical
      annotations:
        summary: MantraPath API Gateway is down
EOF
```

### Performance Optimization

```yaml
# Optimized resource allocation
apiGateway:
  resources:
    requests:
      cpu: "500m"
      memory: "512Mi"
    limits:
      cpu: "2000m"
      memory: "2Gi"
  autoscaling:
    enabled: true
    minReplicas: 3
    maxReplicas: 20
    metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 60
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 70
```

### Security Hardening

```bash
# Pod Security Standards
kubectl label namespace mantrapath-prod pod-security.kubernetes.io/enforce=restricted

# Network segmentation
kubectl apply -f - <<EOF
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: mantrapath-network-policy
  namespace: mantrapath-prod
spec:
  podSelector:
    matchLabels:
      app.kubernetes.io/part-of: mantrapath
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
  egress:
  - to: []
    ports:
    - protocol: TCP
      port: 443
    - protocol: TCP
      port: 53
    - protocol: UDP
      port: 53
EOF
```

## 📚 Additional Resources

- **Helm Documentation**: https://helm.sh/docs/
- **Kubernetes Documentation**: https://kubernetes.io/docs/
- **MantraPath Architecture**: [ARCHITECTURE.md](../ARCHITECTURE.md)
- **API Documentation**: Available at `/docs` endpoint
- **Contributing Guide**: [CONTRIBUTING.md](../CONTRIBUTING.md)

## 🆘 Support

- **GitHub Issues**: https://github.com/mantrapath-code/mantrapath/issues
- **Documentation**: https://docs.mantrapath.com
- **Community**: https://discord.gg/mantrapath

---

**🎉 Congratulations!** You now have a complete, production-ready MantraPath deployment with Kubernetes and Helm. The setup includes automatic scaling, health monitoring, CI/CD integration, and enterprise-grade security features.


