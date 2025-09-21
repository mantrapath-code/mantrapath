# MantraPath Services - Automated Build & Push Scripts

This directory contains automated scripts to build and push Docker images for all MantraPath services to the Vultr Container Registry.

## 🚀 Quick Start

### Build All Services (Interactive)
```bash
./build-and-push-services.sh
```

### Build All Services (Non-Interactive)
```bash
./quick-build.sh
```

### Build Specific Services
```bash
./build-and-push-services.sh models_service api_gateway auth_service
```

### Build Single Service
```bash
./build-single-service.sh models_service
```

## 📋 Available Scripts

| Script | Purpose | Interactive |
|--------|---------|-------------|
| `build-and-push-services.sh` | Full-featured build script with options | Yes |
| `quick-build.sh` | Fast, non-interactive build all services | No |
| `build-single-service.sh` | Build and push a single service | No |

## 🔧 Script Features

### Main Script (`build-and-push-services.sh`)

**Features:**
- ✅ Prerequisites checking (Docker, directories)
- ✅ Registry authentication
- ✅ Smart service discovery
- ✅ Build progress tracking
- ✅ Comprehensive error handling
- ✅ Build summary and reporting
- ✅ Image tagging with commit SHA
- ✅ Cleanup of temporary images

**Options:**
```bash
./build-and-push-services.sh [OPTIONS] [SERVICE_NAMES...]

Options:
  -h, --help     Show help message
  -l, --list     List all available services
  -a, --all      Build all services (default)
  -c, --check    Check prerequisites only

Examples:
  ./build-and-push-services.sh                    # Build all services
  ./build-and-push-services.sh --list             # List services
  ./build-and-push-services.sh models_service     # Build specific service
  ./build-and-push-services.sh --check            # Check prerequisites
```

### Quick Build Script (`quick-build.sh`)

**Features:**
- ⚡ Fast, non-interactive execution
- 🔄 Builds all services automatically
- 📊 Simple progress reporting
- 🏷️ Automatic tagging with latest + commit SHA

**Usage:**
```bash
./quick-build.sh
```

### Single Service Script (`build-single-service.sh`)

**Features:**
- 🎯 Build individual services
- 🔍 Service validation
- 📝 Detailed logging

**Usage:**
```bash
./build-single-service.sh <service_name>
```

## 🏗️ Build Process

Each script follows this process:

1. **Prerequisites Check**
   - Verify Docker installation and daemon
   - Check services directory exists
   - Validate Dockerfile presence

2. **Registry Authentication**
   - Login to Vultr Container Registry
   - Use configured credentials

3. **Image Building**
   - Build Docker image from service Dockerfile
   - Tag with temporary name

4. **Image Tagging**
   - Tag with `latest`
   - Tag with commit SHA or timestamp

5. **Image Pushing**
   - Push both tags to registry
   - Verify successful upload

6. **Cleanup**
   - Remove temporary local images
   - Report build status

## 📦 Registry Configuration

**Registry URL:** `blr.vultrcr.com/mantrapath`
**Username:** `e9b950f6-81b8-4433-bb62-844d3f44b6bb`
**API Key:** `D5w5WAevjZQhcUrEQPcuuA6qgCTXzTfLHtYJ`

### Image Naming Convention

Images are tagged with the following pattern:
```
blr.vultrcr.com/mantrapath/mantrapath-<service_name>:latest
blr.vultrcr.com/mantrapath/mantrapath-<service_name>:<commit_sha>
```

**Examples:**
- `blr.vultrcr.com/mantrapath/mantrapath-models-service:latest`
- `blr.vultrcr.com/mantrapath/mantrapath-api-gateway:abc1234`

## 🎯 Discovered Services

The scripts automatically discover and build these 21 services:

1. **ai_context_store** - AI context storage service
2. **ai_event_processor** - AI event processing service
3. **action_orchestrator** - Action orchestration service
4. **api_gateway** - API gateway service
5. **auth_service** - Authentication service
6. **chatbot_service** - Chatbot service
7. **community_service** - Community management service
8. **content_service** - Content management service
9. **deployment_api** - Deployment API service
10. **media_service** - Media processing service
11. **memory_service** - Memory management service
12. **ml_service** - Machine learning service
13. **models_service** - AI models service
14. **mood_service** - Mood tracking service
15. **notification_service** - Notification service
16. **phi3_agent** - Phi-3 AI agent service
17. **profile_service** - User profile service
18. **proactive_assistance_engine** - Proactive assistance service
19. **translation_service** - Translation service
20. **voice_event_processor** - Voice event processing service
21. **voice_service** - Voice processing service

## 🔍 Troubleshooting

### Common Issues

**Docker not running:**
```bash
sudo systemctl start docker
```

**Permission denied:**
```bash
sudo usermod -aG docker $USER
# Then logout and login again
```

**Registry authentication failed:**
- Verify credentials in script
- Check network connectivity
- Ensure registry URL is correct

**Build failures:**
- Check Dockerfile syntax
- Verify all required files exist
- Check for missing dependencies

### Debug Mode

For detailed debugging, run with verbose output:
```bash
set -x  # Enable debug mode
./build-and-push-services.sh
```

## 📊 Build Output

### Successful Build
```
[INFO] Building service: models_service
[SUCCESS] Successfully built models_service
[INFO] Tagging image for models_service...
[INFO] Pushing images for models_service...
[SUCCESS] Successfully pushed blr.vultrcr.com/mantrapath/mantrapath-models-service:latest
[SUCCESS] Successfully pushed blr.vultrcr.com/mantrapath/mantrapath-models-service:abc1234
[SUCCESS] Completed processing models_service
```

### Build Summary
```
========================================
Build Summary:
[SUCCESS] Successful builds: 21
[SUCCESS] All services built and pushed successfully!
```

## 🔄 Integration with CI/CD

These scripts integrate with the existing CI/CD pipeline:

- **GitHub Actions** use similar logic for automated builds
- **Helm deployments** reference the pushed images
- **Monitoring** tracks build success/failure

## 🛡️ Security Notes

- Registry credentials are embedded in scripts (for local use)
- For production CI/CD, use environment variables or secrets
- Scripts include cleanup to remove temporary images
- All builds are logged for audit purposes

## 📞 Support

If you encounter issues:

1. **Check Prerequisites:** Run `./build-and-push-services.sh --check`
2. **List Services:** Run `./build-and-push-services.sh --list`
3. **Test Single Service:** Use `./build-single-service.sh <service_name>`
4. **Check Docker:** Ensure Docker daemon is running
5. **Verify Registry:** Test registry connectivity

---

**Status:** ✅ **READY** - All scripts tested and functional!

