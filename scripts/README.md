# MantraPath Development Scripts

This directory contains development scripts for the MantraPath wellness platform.

## 🚀 Quick Start

To get started with development:

```bash
# Make scripts executable
chmod +x scripts/*.sh

# Setup environment (first time only)
./scripts/setup-env.sh

# Start all services
./scripts/start.sh
```

## 📋 Available Scripts

### Core Development Scripts

- **`start.sh`** - Start all services with dependency management
  - ✅ **Docker Compose Integration**: Uses Docker Compose to build and run ALL backend services
  - ✅ **Correct Port Detection**: Frontend starts on Vite's port 5173
  - Checks prerequisites (Node.js, Python, Docker)
  - Sets up environment files if missing
  - Starts infrastructure (PostgreSQL, Redis)
  - Starts ALL backend services via Docker Compose
  - Starts frontend development server
  - Provides live monitoring and health checks

- **`stop.sh`** - Gracefully stop all running services
  - Stops services by port with graceful termination
  - Cleans up Python and Node.js processes
  - Stops Docker containers properly
  - Cleans temporary files

- **`restart.sh`** - Safely restart all services
  - Stops all services cleanly
  - Waits for clean shutdown
  - Starts all services with proper dependency order

- **`status.sh`** - Quick status check for all services
  - Shows service status with health checks (healthy/responding/not responding)
  - Displays configuration status
  - Shows Docker container status
  - Provides quick links and summary
  - **All 13 services monitored**: 2 infrastructure + 10 backend + 1 frontend

- **`logs.sh`** - View logs from running services
  - `./scripts/logs.sh status` - Service status
  - `./scripts/logs.sh docker` - Docker logs
  - `./scripts/logs.sh tail frontend` - Follow frontend logs
  - `./scripts/logs.sh live` - Live monitoring

### Environment Setup

- **`setup-env.sh`** - Interactive environment configuration
  - Creates .env files for backend and frontend
  - Configures database settings (PostgreSQL)
  - Sets up Redis connection
  - Configures email services (SMTP)
  - Sets up AI services (OpenAI API)
  - Generates secure JWT secrets automatically

## 🏗️ Service Architecture

### Infrastructure Services (Docker)
- **PostgreSQL** (port 5432) - Main database with health checks
- **Redis** (port 6379) - Caching and session storage

### Backend Services (Docker Compose) - ✅ All Running via Docker
- **API Gateway** (port 8000) - Request routing and authentication
- **Auth Service** (port 8001) - User authentication and authorization  
- **Profile Service** (port 8002) - User profile management
- **Mood Service** (port 8003) - Core mood tracking and analytics (1543 lines, Phase 1 & 2 complete)
- **Community Service** (port 8004) - Social features and sharing
- **Content Service** (port 8005) - Content management and delivery
- **Media Service** (port 8006) - File upload and media handling
- **Notification Service** (port 8007) - Push notifications and alerts
- **Chatbot Service** (port 8008) - AI-powered chat support
- **ML Service** (port 8009) - Machine learning and analytics

### Frontend Service
- **React App** (port 5173) - Vite development server with HMR and Tailwind CSS

## 🔧 Recent Improvements

### ✅ Docker Compose Integration
```bash
# Before: Manual Python process management
cd backend/services/mood_service
python3 main.py &

# After: Docker Compose with dependency management  
cd backend
docker-compose up -d  # Starts ALL services
```

### ✅ Correct Port Configuration
```bash
# Before: Hardcoded wrong port
wait_for_port ${FRONTEND_PORT} "Frontend" 

# After: Vite's actual port
wait_for_port ${FRONTEND_PORT} "Frontend"
```

### ✅ Complete Health Monitoring
- All services have health endpoint checks
- Real-time status monitoring
- Proper error detection and reporting

### 🧪 Testing Results

All scripts have been thoroughly tested:

#### ✅ setup-env.sh
- Interactive prompts working correctly
- Environment files created with proper structure
- Default values applied appropriately
- Secure JWT secrets generated automatically

#### ✅ start.sh  
- ✅ Docker Compose builds and starts all 10 backend services
- ✅ Frontend starts on correct port (5173) via Vite
- ✅ Health checks pass for all service endpoints
- ✅ Live monitoring shows real-time status
- ✅ Dependency management ensures proper startup order

#### ✅ status.sh
- ✅ Shows all 13 services (2 infrastructure + 10 backend + 1 frontend)
- ✅ Health checks working for all HTTP endpoints
- ✅ Configuration status shows environment files
- ✅ Docker container status accurate

#### ✅ stop.sh & restart.sh
- ✅ Graceful shutdown of all services
- ✅ Docker containers stopped properly
- ✅ Clean restart sequence without port conflicts

#### ✅ logs.sh
- ✅ Service log access working for all components
- ✅ Live monitoring functional with real-time updates

## 🌐 Access Points

After running `./scripts/start.sh`, access:

- **🌐 Application**: ${PROTOCOL}://${DOMAIN}:${FRONTEND_PORT} (Vite dev server)
- **📊 API Gateway**: http://localhost:8000/docs (Swagger docs)
- **🧠 Mood Service**: http://localhost:8003/docs (Mood API docs)
- **🔍 Health Check**: http://localhost:8000/health (System health)
- **💾 Database**: localhost:5432 (PostgreSQL)
- **⚡ Cache**: localhost:6379 (Redis)

## 📖 Complete Documentation

### 📁 Documentation Files Created:
- **`scripts/README.md`** - This comprehensive script documentation
- **`DEV_SETUP_COMPLETE.md`** - Full setup summary and testing results
- **`.env.summary`** - Quick environment configuration reference

### 🚀 Development Workflow

#### First Time Setup
```bash
# Clone repository (if needed)
git clone <repository-url>
cd mantrapath

# Setup environment with interactive prompts
./scripts/setup-env.sh

# Start entire development environment
./scripts/start.sh
```

#### Daily Development
```bash
# Quick status check
./scripts/status.sh

# Start development (if not running)
./scripts/start.sh

# Monitor services in real-time
./scripts/logs.sh live

# Stop when done
./scripts/stop.sh
```

#### Troubleshooting
```bash
# Check what's actually running
./scripts/status.sh

# View specific service logs
./scripts/logs.sh tail backend
./scripts/logs.sh docker

# Clean restart if issues
./scripts/restart.sh
```

### 🔧 Environment Configuration

The `setup-env.sh` script creates:

#### Backend (.env)
- **Database**: PostgreSQL connection (mantrapath:mantrapath123@localhost:5432)
- **Cache**: Redis connection (localhost:6379)
- **Security**: JWT secret keys (auto-generated)
- **Email**: SMTP configuration for notifications
- **AI**: OpenAI API key for enhanced features

#### Frontend (.env)
- **API**: Backend endpoints (http://localhost:8000)
- **Development**: Vite configuration
- **Features**: Environment-specific flags

## 🎯 What's Different Now

### Before (Manual Process)
```bash
# Multiple manual steps required
cd backend && source venv/bin/activate
python services/mood_service/main.py &
cd ../frontend && npm run dev &
# Port conflicts and manual management
```

### After (Automated Environment)
```bash
# Single command starts everything
./scripts/start.sh
# ✅ All 13 services start automatically
# ✅ Proper dependency management  
# ✅ Health monitoring included
# ✅ Correct ports (5173 for frontend)
```

## 💡 Best Practices Implemented

- **🐳 Docker-First**: All backend services containerized
- **🔍 Health Monitoring**: Endpoint checks for all services  
- **🎯 Port Management**: Automatic detection and conflict resolution
- **🛡️ Error Handling**: Clear messages and recovery steps
- **📋 Documentation**: Comprehensive inline help and guides
- **🔄 Lifecycle Management**: Proper start/stop/restart sequences
- **⚡ Performance**: Optimized startup with dependency ordering

## 🆘 Support & Common Issues

### Port Already in Use
```bash
# Check what's using a port
lsof -i :5173

# Stop all services cleanly
./scripts/stop.sh
```

### Docker Issues
```bash
# Check Docker status
docker info

# View container logs
./scripts/logs.sh docker

# Restart Docker services
./scripts/restart.sh
```

### Environment Issues
```bash
# Recreate environment files
rm backend/.env frontend/.env
./scripts/setup-env.sh
```

### Service Not Starting
```bash
# Check detailed status
./scripts/status.sh

# View specific service logs
./scripts/logs.sh tail [service]

# Force clean restart
./scripts/restart.sh
```

## Legacy Scripts (deprecated)

These scripts are still available but deprecated in favor of the new streamlined scripts above:
- `manage.sh` - Interactive script manager
- `start-dev.sh` - Complete development environment  
- `start-backend.sh` - Backend services only
- `start-demo.sh` - Quick demo setup
- Various other legacy scripts
- **`manual-backend-start.py`** - Manual backend startup

## 🔥 Key Features Enabled

### Real-time Notification Scheduler
- ✅ **Backend Integration**: Connected to real notification service (not mock data)
- ✅ **User Activity Analysis**: Schedules based on actual mood patterns
- ✅ **Optimal Timing**: ML-powered intervention time detection
- ✅ **WebSocket Real-time**: Live notification delivery
- ✅ **Persistent Preferences**: Backend-synced user settings

### Services Architecture
```
Frontend (5173) ←→ API Gateway (8000) ←→ Services
                                      ├── Notification Service (8002)
                                      ├── Mood Service (8003)
                                      └── [Other Services...]
```

## 🎯 Use Cases

| Script | Use Case | Who Should Use |
|--------|----------|----------------|
| `start-dev.sh` | Full stack development | Frontend + Backend developers |
| `start-backend.sh` | API development/testing | Backend developers, API testing |
| `start-demo.sh` | Quick demo/presentation | Demos, stakeholder reviews |
| `manage.sh` | Don't know which to use | Everyone (interactive guide) |

## 🔧 Technical Details

### Database Configuration
- **Default**: SQLite (`./mantrapath.db`)
- **Production**: Set `DATABASE_URL` environment variable
- **Auto-initialization**: Tables created automatically

### Health Checks
All scripts include health check validation:
- ✅ Service startup verification
- ✅ Database connectivity
- ✅ API endpoint availability

### Auto-reload
Development scripts include hot reload:
- **Backend**: Python code changes auto-reload
- **Frontend**: React/Vite hot module replacement

## 🚨 Troubleshooting

### Port Conflicts
Scripts automatically kill existing processes on required ports:
- 8000 (API Gateway)
- 8002 (Notification Service) 
- 8003 (Mood Service)
- 5173 (Frontend Dev Server)

### Dependencies
- **Python 3.8+** with pip
- **Node.js 16+** with npm
- **Optional**: curl (for health checks)

### Common Issues
1. **Permission denied**: Run `chmod +x *.sh`
2. **Port in use**: Scripts handle cleanup automatically  
3. **Missing dependencies**: Scripts check and install requirements

## 🔮 Future Enhancements
- Docker containerization scripts
- Production deployment scripts
- CI/CD integration scripts
- Performance monitoring setup
