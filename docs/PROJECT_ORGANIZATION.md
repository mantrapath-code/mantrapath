# 📁 Project Structure

This document describes the organized project structure after cleanup.

## Root Directory Structure

```
mantrapath/
├── 📄 README.md                 # Main project documentation
├── 📄 LICENSE                   # Project license
├── 📄 package.json             # Root package configuration
├── 🚀 start.sh                 # Main startup script
├── 🖥️  backend/                # Backend services and infrastructure
├── 🌐 frontend/               # React/TypeScript frontend application
├── ⚙️  config/                # Global configuration files
├── 🚀 deployment/             # Deployment configurations
├── 📚 docs/                   # Organized documentation
├── 🧪 tests/                  # Test files and utilities
├── 🔧 scripts/                # Development and utility scripts
├── 🗂️  tools/                 # Development tools
├── 📋 planning/               # Project planning documents
└── 🔄 documentation/          # Legacy documentation (to be reorganized)
```

## Organized Directories

### 📚 `/docs/` - Documentation Hub
```
docs/
├── reports/                   # Project reports and analyses
│   ├── BACKEND_ANALYSIS_COMPREHENSIVE.md
│   ├── SPRINT_2_COMPLETION_REPORT.md
│   ├── SPRINT_3_COMPLETION_ANALYSIS.md
│   └── SPRINT_3_FINAL_VALIDATION.md
└── setup/                     # Setup and configuration guides
    ├── SETUP_COMPLETE.md
    ├── TEAM_ACCESS.md
    ├── TEAM_ACCESS_COMPLETE.md
    ├── TEAM_ACCESS_GUIDE.md
    └── PYTHON_INTERN_ASSESSMENT_TEST.md
```

### 🧪 `/tests/` - Testing Organization
```
tests/
├── integration/               # Integration tests
│   ├── test_mood_api_integration.py
│   └── test_mood_memory_integration.py
└── [other test files]
```

### 🔧 `/scripts/` - Development Scripts
```
scripts/
├── start-ngrok.sh            # ngrok tunnel setup
├── quick-start.sh            # Quick start with ngrok option
├── setup/                    # Setup scripts
│   └── setup-team-access.sh
└── testing/                  # Testing utilities
    ├── test-ngrok-setup.sh
    └── test-api-gateway-flow.sh
```

## Quick Start Options

### 1. 🖥️ Local Development
```bash
./start.sh
```

### 2. 🌐 Public Access (with ngrok)
```bash
./scripts/quick-start.sh
# Then select option 2
```

### 3. 🔧 Manual ngrok Setup
```bash
# Start services first
./start.sh

# In another terminal, start ngrok
./scripts/start-ngrok.sh
```

## ngrok Configuration

The project now includes proper ngrok support:

- **Configuration**: Automatic ngrok.yml generation
- **Tunnels**: Both API (port 8000) and Frontend (port 5173)
- **Dashboard**: Available at http://localhost:4040
- **Health Checks**: Automatic service detection

### Prerequisites for ngrok
1. Install ngrok: https://ngrok.com/download
2. Sign up for free account: https://dashboard.ngrok.com/signup
3. Get auth token: https://dashboard.ngrok.com/get-started/your-authtoken
4. Configure: `ngrok config add-authtoken <your-token>`

## Development Workflow

### Starting Development
```bash
# Option 1: Interactive start
./start.sh

# Option 2: Quick start with ngrok
./scripts/quick-start.sh

# Option 3: Manual component start
./start.sh backend    # Backend only
./start.sh frontend   # Frontend only
```

### Frontend Development
- **Port**: 5173 (configurable via VITE_FRONTEND_PORT)
- **Host**: 0.0.0.0 (allows external access)
- **HMR**: Hot module replacement enabled
- **Proxy**: API requests to /api/* are proxied to backend
- **ngrok**: Full support for external access

### Environment Configuration
- **Frontend**: `.env.development` for local settings
- **Backend**: `backend/.env` for backend configuration
- **ngrok**: Dynamic configuration based on running services

## File Movement Summary

The following files were moved to improve organization:

**Moved to `/docs/reports/`:**
- `BACKEND_ANALYSIS_COMPREHENSIVE.md`
- `SPRINT_*.md` files

**Moved to `/docs/setup/`:**
- `SETUP_COMPLETE.md`
- `TEAM_ACCESS*.md` files
- `PYTHON_INTERN_ASSESSMENT_TEST.md`

**Moved to `/tests/integration/`:**
- `test_mood_*.py` files

**Moved to `/scripts/testing/`:**
- `test-*-setup.sh` files
- `test-api-gateway-flow.sh`

**Moved to `/scripts/setup/`:**
- `setup-team-access.sh`

## Benefits of New Structure

1. **🧹 Clean Root**: Root directory only contains essential files
2. **📁 Logical Organization**: Related files are grouped together
3. **🔍 Easy Navigation**: Clear directory purposes
4. **🌐 ngrok Ready**: Proper external access support
5. **🚀 Quick Start**: Multiple startup options for different needs

## Next Steps

1. **Update Documentation**: Review and update remaining docs
2. **Test ngrok Setup**: Verify external access works correctly
3. **Team Onboarding**: Share new structure with team members
4. **CI/CD Updates**: Update any deployment scripts if needed
