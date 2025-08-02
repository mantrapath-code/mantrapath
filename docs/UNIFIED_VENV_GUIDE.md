# 🐍 MantraPath Unified Virtual Environment Management

## Overview

MantraPath now uses a **single unified virtual environment** instead of multiple scattered environments. This solution provides:

✅ **Single source of truth** for Python dependencies  
✅ **Simplified development setup**  
✅ **Consistent environment across all services**  
✅ **Easy startup and management scripts**  
✅ **Both Docker and Python execution modes**  

## Quick Start

### 1. Setup Environment (First Time)
```bash
./scripts/setup-venv.sh
```

### 2. Start the Project
```bash
# Start everything
./start.sh

# Backend only
./start.sh --backend-only

# Frontend only  
./start.sh --frontend-only

# Force Python mode (no Docker)
./start.sh --python

# Force Docker mode
./start.sh --docker
```

## Directory Structure

```
mantrapath/
├── venv/                          # ✅ Single unified virtual environment
├── scripts/
│   ├── setup-venv.sh             # Setup/recreate virtual environment
│   └── start-backend-integrated.sh # Integrated backend startup
├── start.sh                      # Main project startup script
├── activate-venv.sh              # Quick environment activation
├── run-backend.sh                # Backend services runner
├── requirements.txt              # Unified Python dependencies
└── backend/
    ├── requirements.txt          # Backend-specific requirements
    └── services/                 # Microservices
```

## Scripts Reference

### Environment Management

| Script | Purpose |
|--------|---------|
| `./scripts/setup-venv.sh` | Create/setup unified virtual environment |
| `./activate-venv.sh` | Activate virtual environment manually |
| `./scripts/setup-venv.sh --clean` | Clean old environments and recreate |

### Project Startup

| Script | Purpose |
|--------|---------|
| `./start.sh` | Start both backend and frontend |
| `./start.sh --backend-only` | Start only backend services |
| `./start.sh --frontend-only` | Start only frontend |
| `./start.sh --python` | Force Python mode (no Docker) |
| `./start.sh --docker` | Force Docker mode |

### Backend Services

| Script | Purpose |
|--------|---------|
| `./run-backend.sh` | Start all backend services |
| `./run-backend.sh auth` | Start only auth service |
| `./run-backend.sh gateway` | Start only API gateway |
| `./scripts/start-backend-integrated.sh` | Integrated backend startup with env setup |

## Environment Variables

The unified environment automatically sets:

```bash
PYTHONPATH="${PROJECT_ROOT}/backend/shared:${PYTHONPATH}"
DATABASE_URL="sqlite:///${PROJECT_ROOT}/backend/mantrapath.db"
JWT_SECRET_KEY="dev-secret-key-change-in-production"
MANTRAPATH_ROOT="${PROJECT_ROOT}"
```

## Migration from Old Setup

### What Changed

**Before:**
- Multiple virtual environments: `.venv`, `backend/venv311`
- Scattered Python setups
- Confusing startup process
- Inconsistent dependencies

**After:**
- Single `venv/` directory
- Unified dependencies management
- Integrated startup scripts
- Consistent environment

### Migration Steps

1. **Automatic cleanup** - Run `./scripts/setup-venv.sh --clean`
2. **Dependencies consolidation** - All requirements in `requirements.txt`
3. **Update scripts** - Use new startup commands

## Development Workflow

### Daily Development
```bash
# Start everything
./start.sh

# Or start components separately
./start.sh --backend-only &
cd frontend && npm run dev
```

### Adding Dependencies
```bash
# Activate environment
source ./activate-venv.sh

# Add package
pip install new-package

# Update requirements
pip freeze > requirements.txt
```

### Troubleshooting
```bash
# Recreate environment
./scripts/setup-venv.sh --clean

# Check environment
source ./activate-venv.sh
python --version
pip list

# Check backend health
curl http://localhost:8000/health
```

## Benefits

### For Developers
- **Simplified setup**: One command to get started
- **Consistent environment**: Same Python/packages everywhere
- **Easy troubleshooting**: Single environment to debug
- **Flexible startup**: Choose Docker or Python mode

### For Deployment
- **Reproducible builds**: Single requirements.txt
- **Container-ready**: Works with Docker
- **Production consistency**: Same env setup everywhere

### For CI/CD
- **Faster builds**: Single dependency installation
- **Reliable tests**: Consistent environment
- **Easy caching**: Single venv to cache

## Advanced Usage

### Environment Activation
```bash
# Quick activation
source ./activate-venv.sh

# Manual activation
source venv/bin/activate
export PYTHONPATH="backend/shared:$PYTHONPATH"
```

### Service Management
```bash
# Start specific services
./run-backend.sh auth     # Auth service only
./run-backend.sh gateway  # API Gateway only

# Background mode
./start.sh --backend-only &
BACKEND_PID=$!

# Stop background services
kill $BACKEND_PID
```

### Docker Integration
```bash
# Docker mode (if Docker available)
./start.sh --docker

# Python mode (bypass Docker)
./start.sh --python
```

## File Locations

### Virtual Environment
- **Location**: `${PROJECT_ROOT}/venv/`
- **Python**: `venv/bin/python`
- **Pip**: `venv/bin/pip`

### Dependencies
- **Unified**: `requirements.txt` (all dependencies)
- **Backend**: `backend/requirements.txt` (backend-specific)
- **Frontend**: `frontend/package.json` (Node.js dependencies)

### Scripts
- **Setup**: `scripts/setup-venv.sh`
- **Startup**: `start.sh`, `run-backend.sh`
- **Backend**: `scripts/start-backend-integrated.sh`

### Database
- **Development**: `backend/mantrapath.db` (SQLite)
- **Production**: Configured via `DATABASE_URL`

## Best Practices

1. **Always use the unified environment**
   ```bash
   source ./activate-venv.sh
   ```

2. **Use startup scripts instead of manual commands**
   ```bash
   ./start.sh  # ✅ Good
   # python backend/services/... # ❌ Avoid
   ```

3. **Keep requirements.txt updated**
   ```bash
   pip freeze > requirements.txt
   ```

4. **Test both Docker and Python modes**
   ```bash
   ./start.sh --docker  # Test Docker
   ./start.sh --python  # Test Python
   ```

5. **Use environment variables**
   ```python
   import os
   db_url = os.getenv('DATABASE_URL')
   ```

## Troubleshooting

### Common Issues

**Environment not found**
```bash
./scripts/setup-venv.sh
```

**Import errors**
```bash
source ./activate-venv.sh
echo $PYTHONPATH  # Should include backend/shared
```

**Port conflicts**
```bash
lsof -ti:8000 | xargs kill -9  # Kill port 8000
./start.sh --python
```

**Missing dependencies**
```bash
source ./activate-venv.sh
pip install -r backend/requirements.txt
```

### Reset Everything
```bash
./scripts/setup-venv.sh --clean
./start.sh
```

This unified approach eliminates the confusion of multiple virtual environments and provides a single, consistent way to develop, test, and deploy MantraPath.
