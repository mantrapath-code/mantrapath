# 🔧 Backend Tools

This directory contains utility tools and scripts specific to backend operations.

## 📁 Directory Structure

### 🚀 Startup Tools (`startup/`)
Scripts for starting and managing backend services:
- `start-dev.sh` - Development environment startup
- `start-sprint2.sh` - Sprint 2 specific startup
- `start_ai_context_store.sh` - AI context store initialization
- `stop-dev.sh` - Graceful service shutdown

### 🧪 Testing Tools (`testing/`)
Backend-specific testing utilities:
- `test-sprint2-parallel.sh` - Parallel testing for Sprint 2 features

## 🚀 Usage

### Start Development Environment
```bash
cd backend
./tools/startup/start-dev.sh
```

### Stop Services
```bash
cd backend
./tools/startup/stop-dev.sh
```

### Run Backend Tests
```bash
cd backend
./tools/testing/test-sprint2-parallel.sh
```

## 📝 Notes

- All scripts should be run from the backend directory
- Ensure Docker is running before executing startup scripts
- Check logs for any startup issues
