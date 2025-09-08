# Backend Directory Structure

## 📁 Organized Directory Layout

### Core Files
- `.env` - Development environment variables
- `README.md` - Backend documentation  
- `requirements.txt` - Python dependencies
- `Dockerfile` - Container configuration
- `docker-compose.yml` / `docker-compose-secure.yml` - Service orchestration
- `start-dev.sh` / `stop-dev.sh` - Development scripts
- `mantrapath.db` - SQLite database file

### Organized Directories

#### `/config/` - Configuration Files
- `.env.example` - Environment template
- `.env.production` - Production environment template

#### `/debug/` - Debug Utilities  
- `debug_jwt.py` - JWT token debugging utility

#### `/docs/` - Documentation
- `DOCKER_INTEGRATION_SUMMARY.md` - Docker setup guide
- `SETUP.md` - Installation and setup instructions

#### `/tests/` - Test Files
- `test_chatbot.py` - Comprehensive chatbot testing (251 lines)
- `test_lang_prefs.py` - Language preferences testing
- `test_language_preferences.py` - Language preference tests
- `test_phi4_integration.py` - Phi-4 model integration tests
- `test_smtp.py` - Email service testing

#### Core Directories (Pre-existing)
- `/database/` - Database schemas and migrations
- `/monitoring/` - Monitoring and observability
- `/nginx/` - Reverse proxy configuration
- `/scripts/` - Build and deployment scripts
- `/services/` - Microservices implementations
- `/shared/` - Shared utilities and models

## 🧹 Cleanup Actions Performed

### Files Moved
- All `test_*.py` files → `/tests/`
- `debug_jwt.py` → `/debug/`
- Documentation files → `/docs/`
- Environment templates → `/config/`

### Files Removed
- Duplicate `scripts/start-dev.sh` (kept root version)
- Duplicate `scripts/test-chatbot.py` (kept comprehensive version)
- All `__pycache__/` directories
- All `*.pyc` compiled Python files

### Result
- ✅ 20 files/directories in root (down from 23)
- ✅ Logical grouping by purpose
- ✅ No duplicate files
- ✅ Clean development environment
- ✅ Proper separation of concerns
