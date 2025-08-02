# 🐍 MantraPath Unified Environment Setup

## Overview

We've successfully unified the MantraPath project to use a single, well-managed environment setup that prioritizes Docker Compose while providing Python fallback options.

## What Was Fixed

### ❌ Previous Issues
- **Multiple Virtual Environments**: 
  - Root `.venv` directory
  - Backend-specific `venv311` directory
  - Confusion about which Python interpreter to use
  - Inconsistent dependency management

### ✅ New Unified Solution
- **Single Virtual Environment**: All Python dependencies in `/venv`
- **Docker-First Approach**: Production-like Docker containers by default
- **Smart Fallback**: Automatic detection and Python mode fallback
- **Integrated Scripts**: All startup logic unified in organized scripts

## Project Structure

```
mantrapath/
├── start.sh                          # 🌟 Main project startup (Docker-first)
├── venv/                             # 🐍 Unified virtual environment
├── scripts/
│   ├── setup-venv.sh                # 🔧 Virtual environment setup
│   └── start-backend-integrated.sh  # 🔄 Backend startup (Python mode)
├── backend/
│   ├── docker-compose.yml           # 🐳 Docker services definition
│   └── start-dev.sh                 # 🐳 Docker startup script
└── frontend/
    └── package.json                 # 📦 Frontend dependencies
```

## Usage

### 🚀 Quick Start (Recommended)
```bash
# Start everything with auto-detection
./start.sh

# Docker will be used if available, Python fallback otherwise
```

### 🎯 Specific Modes
```bash
# Force Docker mode
./start.sh --docker

# Force Python development mode  
./start.sh --python

# Backend only
./start.sh --backend-only

# Frontend only
./start.sh --frontend-only
```

### 🔧 Setup Commands
```bash
# Set up unified virtual environment (run once)
./scripts/setup-venv.sh

# Check what's running
curl http://localhost:8000/health
```

## Environment Detection Logic

### Docker Mode (Preferred)
1. ✅ Docker is installed and running
2. ✅ Uses `docker-compose.yml` in backend/
3. ✅ Full microservices architecture
4. ✅ Production-like environment
5. ✅ PostgreSQL and Redis included

### Python Mode (Fallback)
1. ⚠️ Docker not available or forced with `--python`
2. ✅ Uses unified virtual environment in `/venv`
3. ✅ SQLite database for development
4. ✅ Direct uvicorn processes
5. ✅ Good for debugging and development

## Key Benefits

### 🎯 **Simplified Management**
- One command to start everything: `./start.sh`
- No confusion about which environment to use
- Clear documentation and help messages

### 🐳 **Production Parity**
- Docker Compose provides production-like services
- Consistent environment across different machines
- Easy scaling and service isolation

### 🔄 **Developer Flexibility**
- Python fallback for debugging and development
- Force specific modes when needed
- Works with or without Docker

### 🧹 **Clean Architecture**
- Removed duplicate virtual environments
- Organized scripts in `/scripts` directory
- Clear separation of concerns

## Service Endpoints

When running, services are available at:

- **🌐 API Gateway**: http://localhost:8000
- **🔐 Auth Service**: http://localhost:8001 (Docker mode)
- **👤 Profile Service**: http://localhost:8002 (Docker mode)
- **😊 Mood Service**: http://localhost:8003 (Docker mode)
- **🤖 Chatbot Service**: http://localhost:8004 (Docker mode)
- **🎨 Frontend**: http://localhost:5173

## Authentication Fix

The original 401/403 authentication errors were caused by:
1. Backend services not running
2. No unified startup process
3. Inconsistent environment setup

**✅ Now Fixed With:**
- Proper Docker Compose orchestration
- All microservices running correctly
- Unified authentication flow through API Gateway
- Consistent token handling across services

## Quick Commands

```bash
# 🚀 Start everything
./start.sh

# 🛑 Stop everything  
Ctrl+C (in the startup terminal)

# 🔍 Check status
curl http://localhost:8000/health

# 📊 View Docker containers (if using Docker mode)
cd backend && docker-compose ps

# 📋 View logs (if using Docker mode)
cd backend && docker-compose logs -f

# 🧹 Clean environment
./scripts/setup-venv.sh --clean
```

## Next Steps

1. **✅ Environment Setup**: Complete
2. **✅ Backend Services**: Running via Docker/Python
3. **✅ Frontend Integration**: Ready
4. **🎯 Authentication**: Should now work properly
5. **📱 Full Application**: Ready for development

The authentication errors you were experiencing should now be resolved since all backend services are properly running and orchestrated.
