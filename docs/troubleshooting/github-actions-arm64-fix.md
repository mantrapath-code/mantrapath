# GitHub Actions ARM64 Build Fix

## Problem
The GitHub Actions workflow was failing for the frontend service when building ARM64 images due to QEMU emulation issues during npm install. The error was:
```
qemu: uncaught target signal 4 (Illegal instruction) - core dumped
```

## Root Cause
The issue occurs because:
1. GitHub Actions runs on x86_64 runners
2. Building ARM64 images requires QEMU emulation
3. npm install with native dependencies can be unstable under QEMU emulation
4. The frontend has several packages that may have native components (three.js, d3, canvas-confetti, etc.)

## Solutions Implemented

### Solution 1: Platform-Specific Builds (Recommended)
Modified `.github/workflows/docker-build.yml` to:
- Build frontend images only for `linux/amd64` (most common deployment target)
- Continue building backend services for both `linux/amd64,linux/arm64`

This is the most practical solution since:
- Frontend containers are typically deployed to x86_64 infrastructure
- ARM64 is more important for backend services that might run on ARM-based servers
- Reduces build time and eliminates the problematic QEMU emulation for frontend

### Solution 2: Improved Dockerfile
Enhanced `frontend/Dockerfile` with:
- Build tools installation (`python3`, `make`, `g++`, `libc6-compat`)
- Timeout protection for npm install (30 minutes max)
- Memory optimization (`NODE_OPTIONS="--max-old-space-size=4096"`)
- Script skipping during install to avoid native compilation issues
- Better npm configuration for offline/cache support

### Solution 3: Alternative Workflow (Optional)
Created `docker-build-platform-optimized.yml` that provides:
- Manual control over ARM64 builds via workflow dispatch
- Conditional platform building based on service type
- Better error handling and retry logic

## Files Modified

1. **`.github/workflows/docker-build.yml`**
   - Split build steps for frontend (AMD64 only) vs backend (multi-platform)
   
2. **`frontend/Dockerfile`**
   - Added ARM64 compatibility improvements
   - Added build tools and timeout protection
   
3. **`frontend/Dockerfile.arm64-optimized`** (Alternative)
   - Specialized Dockerfile for ARM64 builds if needed
   
4. **`.github/workflows/docker-build-platform-optimized.yml`** (Alternative)
   - Enhanced workflow with manual ARM64 control

## Verification
To verify the fix works:
1. Push changes to trigger the workflow
2. Check that frontend builds complete successfully on AMD64
3. Check that backend services still build on both architectures
4. Monitor build times (should be faster without ARM64 frontend builds)

## Future Considerations
- If ARM64 frontend support is needed later, use the optimized Dockerfile
- Consider using GitHub's native ARM64 runners when they become available
- Monitor npm dependencies for ARM64 compatibility improvements
- Use the alternative workflow for testing ARM64 builds manually

## Rollback Plan
If issues occur, revert to AMD64-only builds for all services:
```yaml
platforms: linux/amd64
```