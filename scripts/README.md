# MantraPath Scripts Directory

This directory contains all development and deployment scripts for the MantraPath project.

## 🚀 Quick Start

```bash
# Run the interactive script manager
./manage.sh

# Or run specific scripts directly:
./start-dev.sh      # Full development environment
./start-backend.sh  # Backend services only  
./start-demo.sh     # Quick demo setup
```

## 📁 Script Organization

### 🆕 New Enhanced Scripts
- **`manage.sh`** - Interactive script manager with menu
- **`start-dev.sh`** - Complete development environment (Backend + Frontend)
- **`start-backend.sh`** - Backend services only with health checks
- **`start-demo.sh`** - Quick demo with simplified setup

### 🔄 Legacy Scripts  
- **`start-backend-services.sh`** - Original backend services script
- **`start-backend.sh`** - Existing backend start script
- **`stop-backend.sh`** - Stop backend services
- **`dev-setup.sh`** - Development environment setup
- **`run-backend.py`** - Python backend runner
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
