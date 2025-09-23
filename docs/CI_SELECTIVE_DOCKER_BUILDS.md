# Selective Docker image builds in CI

This repository uses GitHub Actions workflows to build and push only the Docker images for services that changed in a commit or pull request, instead of rebuilding everything every time, and to preview which images would be built on PRs.

## Where

Workflows:
- Build & Push: `.github/workflows/docker-build.yml`
- PR preview (comment): `.github/workflows/pr-docker-preview.yml`

## What it does

- Detects changed files relative to the previous commit (or PR base) and maps them to services under `backend/services/<service>/Dockerfile` and optionally `frontend/Dockerfile`.
- If a shared backend area changes (e.g., `backend/shared/**`, `backend/requirements.txt`, `backend/config/**`, `backend/database/**`), it rebuilds all backend services because they may be affected.
- Builds multi-arch-ready images with Docker Buildx and pushes them to GitHub Container Registry (GHCR) under:
  - `ghcr.io/<org>/<repo>-<service>:<tags>`
- Tags include: `<full-sha>`, `<short-sha>`, `<branch>`, and `latest` on the default branch. Optionally, `latest-<branch>` for non-default branches (controlled by `BRANCH_LATEST` env in the workflow).
- Uses GitHub Actions cache for BuildKit to speed up subsequent builds.

## Triggers

- On push to any branch: builds and pushes changed images.
- On pull requests: builds but does not push (for validation). A separate PR workflow posts a comment listing the images and tags that would be built.
- Manual: you can force-build a specific service via workflow dispatch `force_service` input.

## Forcing a service build

Use the "Run workflow" button and provide the service directory name under `backend/services`, e.g.:

- `api_gateway`
- `auth_service`
- `profile_service`

This will build just that service even if there are no detected changes.

## Changing the registry

- Default registry is GHCR (`ghcr.io`). To push to Docker Hub instead, set:
  - `REGISTRY: docker.io`
  - Update the login step to use Docker Hub credentials (create `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN` repository secrets) and set `username`/`password` accordingly.
  - Image names are formed as `<registry>/<owner>/<repo>-<service>`; for Docker Hub, you may want `<username>/<repo>-<service>`.

## Required permissions and secrets

- The workflow uses the built-in `GITHUB_TOKEN` with `packages: write` permission for GHCR pushes.
- No additional secrets are required for GHCR. For other registries, add appropriate secrets and adjust the login step.

## Adding a new service

- Ensure there's a `Dockerfile` at `backend/services/<service>/Dockerfile`.
- The workflow will auto-discover it and include it in selective builds when changes are detected.

## Using docker-compose for production

An example compose file `docker-compose.prod.yml` is provided at the repo root. It references images published to GHCR using variables for flexibility:

- OWNER (default: `mantrapath-code`)
- REPO (default: `mantrapath`)
- TAG (default: `latest`)

Examples:

- Use branch tag:
  - `TAG=feature-x docker compose -f docker-compose.prod.yml up -d`
- Use short SHA:
  - `TAG=$(git rev-parse --short HEAD) docker compose -f docker-compose.prod.yml up -d`
- Use latest-branch tag (if enabled by CI):
  - `TAG=latest-feature-x docker compose -f docker-compose.prod.yml up -d`
