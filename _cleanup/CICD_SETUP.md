# MantraPath CI/CD Setup

This document describes the complete continuous integration and deployment setup for MantraPath using GitHub Actions, Docker, and Kubernetes with Helm.

## Overview

The CI/CD pipeline automatically:
- 🔍 Detects changes in backend, frontend, or deployment configurations
- 🏗️ Builds Docker images for changed services
- 📦 Pushes images to Vultr Container Registry
- 🚀 Deploys to Kubernetes using Helm
- 🏥 Monitors deployment health
- 🔄 Supports rollbacks and manual deployments

## Architecture

```
GitHub Repository
├── Push to main → Production Deployment
├── Push to develop → Development Deployment  
├── Pull Request → Build & Test Only
└── Manual Trigger → Custom Environment
```

## Workflows

### 1. Continuous Build and Deploy (`.github/workflows/build-deploy.yml`)

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main`
- Manual workflow dispatch

**Features:**
- 🎯 Smart change detection (only builds what changed)
- 🏗️ Parallel image building
- 🔄 Automatic deployment based on branch
- ✅ Health checks and verification
- 📊 Deployment status reporting

**Branch Mapping:**
- `main` → Production environment (`mantrapath-prod`)
- `develop` → Development environment (`mantrapath-dev`)

### 2. Rollback Workflow (`.github/workflows/rollback.yml`)

**Purpose:** Manual rollback to previous deployment versions

**Features:**
- 🔄 Rollback to specific revision or previous version
- ✅ Post-rollback verification
- 🏥 Health checks after rollback

### 3. Monitoring Workflow (`.github/workflows/monitoring.yml`)

**Purpose:** Continuous monitoring of deployments

**Features:**
- ⏰ Runs every 5 minutes
- 🏥 Health checks for all environments
- 📊 Resource usage monitoring
- 🚨 Automated alerting for issues
- 📋 Detailed monitoring reports

## Repository Secrets

Configure these secrets in your GitHub repository settings:

### Required Secrets

```bash
VULTR_REGISTRY_PASSWORD=D5w5WAevjZQhcUrEQPcuuA6qgCTXzTfLHtYJ
```

### Optional Secrets (for production)

```bash
KUBE_CONFIG_DATA=<base64-encoded-kubeconfig>
SLACK_WEBHOOK_URL=<your-slack-webhook>
NOTIFICATION_EMAIL=<alert-email>
```

## Local Development

### Quick Start

```bash
# Deploy to dev environment
./scripts/local-deploy.sh --environment dev

# Build images and deploy
./scripts/local-deploy.sh --build --environment dev

# Watch mode for development
./scripts/local-deploy.sh --watch --environment dev
```

### Prerequisites

1. **Docker** - Logged in to Vultr registry
2. **kubectl** - Configured for your cluster
3. **Helm 3.x** - Installed and working
4. **Kind cluster** - Running for dev environment

### Registry Setup

```bash
# Login to Vultr Container Registry
docker login https://blr.vultrcr.com/mantrapath -u e9b950f6-81b8-4433-bb62-844d3f44b6bb -p D5w5WAevjZQhcUrEQPcuuA6qgCTXzTfLHtYJ

# Test registry access
docker pull hello-world:latest
docker tag hello-world:latest blr.vultrcr.com/mantrapath/hello-world:latest
docker push blr.vultrcr.com/mantrapath/hello-world:latest
```

## Image Build Process

The pipeline follows this exact process for each service:

```bash
# 1. Build image
cd <service-context>
docker build -f <dockerfile> -t temp-<image-name>:latest .

# 2. Tag for registry
docker tag temp-<image-name>:latest blr.vultrcr.com/mantrapath/<image-name>:latest
docker tag temp-<image-name>:latest blr.vultrcr.com/mantrapath/<image-name>:<commit-sha>

# 3. Push to registry
docker push blr.vultrcr.com/mantrapath/<image-name>:latest
docker push blr.vultrcr.com/mantrapath/<image-name>:<commit-sha>

# 4. Clean up
docker rmi temp-<image-name>:latest
```

## Services and Images

| Service | Image Name | Dockerfile Path | Build Context |
|---------|------------|-----------------|---------------|
| API Gateway | `mantrapath-api-gateway` | `backend/services/api_gateway/Dockerfile` | `backend` |
| Frontend | `mantrapath-frontend` | `deployment/Dockerfile.frontend` | `frontend` |
| Translation Service | `mantrapath-translation-service` | `backend/services/translation_service/Dockerfile` | `backend` |
| Models Service | `mantrapath-models-service` | `backend/services/models_service/Dockerfile` | `backend` |
| Auth Service | `mantrapath-auth-service` | `backend/services/auth_service/Dockerfile` | `backend` |
| ... | ... | ... | ... |

## Deployment Environments

### Development (`dev`)

- **Namespace:** `mantrapath-dev`
- **Values File:** `values-dev.yaml`
- **Access:** `http://localhost:30880` (via NodePort)
- **Auto-deploy:** On push to `develop` branch

### Production (`prod`)

- **Namespace:** `mantrapath-prod`  
- **Values File:** `values-prod.yaml`
- **Access:** `https://mantrapath.com` (via Ingress)
- **Auto-deploy:** On push to `main` branch

## Manual Operations

### Deploy Specific Environment

```bash
# Via GitHub Actions
# Go to Actions → Continuous Build and Deploy → Run workflow
# Select environment and options

# Via local script
./scripts/local-deploy.sh --environment prod --build
```

### Rollback Deployment

```bash
# Via GitHub Actions
# Go to Actions → Rollback Deployment → Run workflow
# Select environment and revision

# Via kubectl/helm
helm rollback mantrapath-dev -n mantrapath-dev
```

### Monitor Deployment

```bash
# Check deployment status
kubectl get pods -n mantrapath-dev
helm status mantrapath-dev -n mantrapath-dev

# View logs
kubectl logs -f deployment/mantrapath-dev-api-gateway -n mantrapath-dev

# Port forward for testing
kubectl port-forward svc/mantrapath-dev-api-gateway 8080:8000 -n mantrapath-dev
```

## Troubleshooting

### Common Issues

1. **Registry Login Failed**
   ```bash
   # Re-login to registry
   docker login https://blr.vultrcr.com/mantrapath -u e9b950f6-81b8-4433-bb62-844d3f44b6bb -p D5w5WAevjZQhcUrEQPcuuA6qgCTXzTfLHtYJ
   ```

2. **Cluster Connection Issues**
   ```bash
   # Check cluster status
   kubectl cluster-info
   
   # Recreate Kind cluster
   kind delete cluster --name mantrapath-dev
   kind create cluster --name mantrapath-dev --config deployment/kind-dev.yaml
   ```

3. **Helm Deployment Failed**
   ```bash
   # Check Helm status
   helm status mantrapath-dev -n mantrapath-dev
   
   # View deployment logs
   helm history mantrapath-dev -n mantrapath-dev
   
   # Rollback if needed
   helm rollback mantrapath-dev -n mantrapath-dev
   ```

4. **Image Pull Errors**
   ```bash
   # Verify registry secret
   kubectl get secret mantrapath-dev-registry -n mantrapath-dev -o yaml
   
   # Recreate if needed
   kubectl delete secret mantrapath-dev-registry -n mantrapath-dev
   kubectl create secret docker-registry mantrapath-dev-registry \
     --docker-server=blr.vultrcr.com \
     --docker-username=e9b950f6-81b8-4433-bb62-844d3f44b6bb \
     --docker-password=D5w5WAevjZQhcUrEQPcuuA6qgCTXzTfLHtYJ \
     --namespace=mantrapath-dev
   ```

## Security Notes

- Registry credentials are stored as GitHub secrets
- Kubernetes secrets are managed by Helm
- Production deployments require manual approval
- All images are scanned for vulnerabilities
- RBAC is configured for service accounts

## Next Steps

1. **Set up GitHub repository secrets**
2. **Configure production Kubernetes cluster access**
3. **Set up monitoring and alerting**
4. **Configure backup and disaster recovery**
5. **Add integration tests to pipeline**

## Support

For issues with the CI/CD pipeline:
1. Check GitHub Actions logs
2. Review monitoring reports
3. Check Kubernetes cluster status
4. Verify registry access
