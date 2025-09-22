# MantraPath Scripts Directory

This directory contains essential development and utility scripts for the MantraPath project. With the migration to Kubernetes deployment, most production deployment scripts have been moved to `/deployment/scripts/`.

## 📁 Directory Structure

```
scripts/
├── README.md                         # This file
├── build-and-push-services.sh        # Build and push Docker images
├── build-single-service.sh           # Build individual service images
├── health-check.sh                   # Basic health check utilities
├── quick-start.sh                    # Quick development setup
├── start.sh                          # Basic startup script
├── dev/                              # Development utilities
├── management/                       # Service management scripts
├── setup/                            # Environment setup scripts
└── _cleanup/                         # Archived/obsolete scripts

```

## 🚀 Essential Scripts

### Build Scripts

#### `build-and-push-services.sh`
**Purpose**: Build and push Docker images for all services to container registry

**Usage**:
```bash
# Build and push all services
./build-and-push-services.sh

# With custom registry
VULTR_REGISTRY=your-registry.com ./build-and-push-services.sh
```

**Environment Variables**:
- `VULTR_REGISTRY`: Container registry URL
- `VULTR_REGISTRY_USERNAME`: Registry username  
- `VULTR_REGISTRY_PASSWORD`: Registry password

#### `build-single-service.sh`
**Purpose**: Build and push a single service image

**Usage**:
```bash
# Build specific service
./build-single-service.sh api-gateway
./build-single-service.sh translation-service
```

### Development Scripts

#### `quick-start.sh`
**Purpose**: Quick development environment setup

**Usage**:
```bash
./quick-start.sh
```

**Features**:
- Sets up development dependencies
- Configures local environment
- Starts essential services for development

#### `start.sh`
**Purpose**: Basic service startup script

**Usage**:
```bash
./start.sh
```

### Utility Scripts

#### `health-check.sh`
**Purpose**: Basic health check utilities for development

**Usage**:
```bash
./health-check.sh
```

**Note**: For production health monitoring, use `/deployment/scripts/health-monitor.sh`

## 📂 Subdirectories

### `dev/`
Development-specific utilities and helper scripts.

### `management/`
Service management scripts for local development:
- `manage.sh` - Interactive service management
- `manage_services.sh` - Comprehensive service manager
- `activate_event_bus.sh` - Event bus activation

### `setup/`
Environment setup and configuration scripts:
- `dev-setup.sh` - Development environment setup
- `docker-dev.sh` - Docker development configuration
- `setup-env.sh` - Environment variable setup
- `setup-team-access.sh` - Team access configuration
- `setup-venv.sh` - Python virtual environment setup
- `sync-env.sh` - Environment synchronization

## 🔄 Migration Notes

### Moved to Kubernetes Deployment
The following scripts have been replaced by the comprehensive Kubernetes deployment system in `/deployment/scripts/`:

**Old Scripts** → **New Kubernetes Equivalent**:
- `deploy.sh` → `/deployment/scripts/deploy-k8s.sh`
- `production-deploy.sh` → `/deployment/scripts/deploy-k8s.sh --env prod`
- `health-monitor.sh` → `/deployment/scripts/health-monitor.sh`
- `validate-deployment.sh` → `/deployment/scripts/test-charts.sh`

### Archived Scripts
Obsolete and legacy scripts have been moved to `_cleanup/` directory:
- **obsolete/**: Replaced deployment scripts
- **archived/**: Test scripts, analysis tools, and monitoring utilities

## 🛠️ Development Workflow

### 1. Initial Setup
```bash
# Set up development environment
./setup/dev-setup.sh

# Set up Python virtual environment
./setup/setup-venv.sh
```

### 2. Daily Development
```bash
# Quick start for development
./quick-start.sh

# Or start specific services
./start.sh
```

### 3. Building Images
```bash
# Build all services for testing
./build-and-push-services.sh

# Build specific service
./build-single-service.sh api-gateway
```

### 4. Health Checks
```bash
# Basic health check
./health-check.sh

# For comprehensive monitoring, use Kubernetes scripts
../deployment/scripts/health-monitor.sh --env dev
```

## 🎯 When to Use These Scripts

### Use Local Scripts For:
- ✅ Initial development setup
- ✅ Local development workflow
- ✅ Building images for testing
- ✅ Service management in development
- ✅ Environment setup and configuration

### Use Kubernetes Scripts For:
- ✅ Production deployments
- ✅ Multi-environment management
- ✅ Comprehensive health monitoring
- ✅ Chart testing and validation
- ✅ Production-grade operations

## 🔧 Integration with Kubernetes Deployment

These scripts complement the Kubernetes deployment system:

1. **Development Phase**: Use local scripts for setup and development
2. **Build Phase**: Use build scripts to create images
3. **Deployment Phase**: Use `/deployment/scripts/deploy-k8s.sh`
4. **Operations Phase**: Use `/deployment/scripts/health-monitor.sh`

## 📋 Prerequisites

### Required Tools
- Docker >= 20.10
- Node.js >= 16.0
- Python >= 3.9
- Git

### Optional Tools (for Kubernetes integration)
- kubectl >= 1.20
- helm >= 3.8

## 🚨 Important Notes

1. **No Production Use**: These scripts are for development only
2. **Kubernetes First**: For production, always use Kubernetes deployment scripts
3. **Environment Variables**: Set up proper environment variables for registry access
4. **Security**: Never commit registry credentials to version control

## 📞 Support

For issues with:
- **Local development**: Check these scripts and their documentation
- **Kubernetes deployment**: See `/deployment/scripts/README.md`
- **Build issues**: Check Docker setup and registry credentials
- **Environment setup**: Review setup scripts and prerequisites

---

**Version**: 2.0  
**Last Updated**: September 2025  
**Maintained by**: MantraPath Team