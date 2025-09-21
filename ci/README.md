MantraPath CI: Per-service build & push

This directory contains small, reusable scripts the CI uses to build and push Docker images to the Vultr Container Registry, one service at a time.

Includes:
- build-push-service.sh — build and push a single backend service image
- list-services.sh — list available backend services with Dockerfiles

Registry assumptions:
- Registry: blr.vultrcr.com/mantrapath (override via VULTR_REGISTRY)
- Image naming: mantrapath-<service>
- Dockerfile path: backend/services/<service>/Dockerfile
- Build context: backend/

Required GitHub Secrets (Repository → Settings → Secrets and variables → Actions):
- VULTR_REGISTRY (e.g. blr.vultrcr.com/mantrapath)
- VULTR_REGISTRY_USERNAME
- VULTR_REGISTRY_PASSWORD

Local usage (optional):
- You can invoke the scripts locally if you export the same env vars. Don’t store credentials in files.

Contract:
- Input: service name that matches a folder under backend/services/
- Output: pushed images: <registry>/mantrapath-<service>:latest and :<git-sha>
- Errors: non-zero exit on missing Dockerfile, failed login/build/push
