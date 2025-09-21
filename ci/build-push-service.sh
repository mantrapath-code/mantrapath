#!/usr/bin/env bash

# Build and push a single backend service image to Vultr Container Registry.
# Usage:
#   ci/build-push-service.sh <service-name>
#
# Required env vars (prefer setting via CI secrets):
#   VULTR_REGISTRY             Registry host/path, e.g. blr.vultrcr.com/mantrapath
#   VULTR_REGISTRY_USERNAME    Vultr CR username
#   VULTR_REGISTRY_PASSWORD    Vultr CR password/token
# Optional env vars:
#   IMAGE_PREFIX               default: mantrapath
#   BUILD_CONTEXT              default: backend
#   DOCKERFILE                 override full Dockerfile path (rare)
#   PUSH_LATEST                default: true (also pushes :latest)
#   EXTRA_TAGS                 comma-separated list of extra tags to push

set -euo pipefail

SERVICE_NAME=${1:-}

log()  { echo -e "[ci/build] $*"; }
fail() { echo -e "[ci/build][error] $*" >&2; exit 1; }

if [[ -z "$SERVICE_NAME" ]]; then
  fail "usage: $0 <service-name>"
fi

VULTR_REGISTRY=${VULTR_REGISTRY:-"blr.vultrcr.com/mantrapath"}
IMAGE_PREFIX=${IMAGE_PREFIX:-"mantrapath"}
BUILD_CONTEXT=${BUILD_CONTEXT:-"backend"}
PUSH_LATEST=${PUSH_LATEST:-"true"}
EXTRA_TAGS=${EXTRA_TAGS:-""}

if [[ -z "${VULTR_REGISTRY_USERNAME:-}" || -z "${VULTR_REGISTRY_PASSWORD:-}" ]]; then
  fail "VULTR_REGISTRY_USERNAME and VULTR_REGISTRY_PASSWORD must be set"
fi

SERVICE_DIR="backend/services/${SERVICE_NAME}"
DOCKERFILE=${DOCKERFILE:-"${SERVICE_DIR}/Dockerfile"}

[[ -d "$SERVICE_DIR" ]] || fail "Service directory not found: $SERVICE_DIR"
[[ -f "$DOCKERFILE"   ]] || fail "Dockerfile not found: $DOCKERFILE"

# Compute tags
IMAGE_NAME="${IMAGE_PREFIX}-${SERVICE_NAME}"
IMAGE_FULL_BASE="${VULTR_REGISTRY}/${IMAGE_NAME}"

# Commit SHA (fallback to timestamp)
if git rev-parse --git-dir >/dev/null 2>&1; then
  COMMIT_SHA=$(git rev-parse --short HEAD)
else
  COMMIT_SHA=$(date +%Y%m%d-%H%M%S)
fi

TEMP_TAG="temp-${IMAGE_NAME}:latest"
SHA_TAG="${IMAGE_FULL_BASE}:${COMMIT_SHA}"

log "Registry: ${VULTR_REGISTRY}"
log "Service:  ${SERVICE_NAME}"
log "Dockerfile: ${DOCKERFILE}"
log "Context:  ${BUILD_CONTEXT}"

log "Logging into Vultr registry..."
echo -n "$VULTR_REGISTRY_PASSWORD" | docker login "https://${VULTR_REGISTRY}" -u "$VULTR_REGISTRY_USERNAME" --password-stdin

log "Building image..."
docker build -f "$DOCKERFILE" -t "$TEMP_TAG" "$BUILD_CONTEXT"

log "Tagging image: $SHA_TAG"
docker tag "$TEMP_TAG" "$SHA_TAG"

if [[ "${PUSH_LATEST}" == "true" ]]; then
  LATEST_TAG="${IMAGE_FULL_BASE}:latest"
  log "Tagging image: $LATEST_TAG"
  docker tag "$TEMP_TAG" "$LATEST_TAG"
fi

# Handle extra tags
IFS=',' read -r -a EXTRA <<< "$EXTRA_TAGS"
for t in "${EXTRA[@]}"; do
  [[ -z "$t" ]] && continue
  TAGGED="${IMAGE_FULL_BASE}:${t}"
  log "Tagging image: $TAGGED"
  docker tag "$TEMP_TAG" "$TAGGED"
done

log "Pushing: $SHA_TAG"
docker push "$SHA_TAG"

if [[ "${PUSH_LATEST}" == "true" ]]; then
  log "Pushing: $LATEST_TAG"
  docker push "$LATEST_TAG"
fi

for t in "${EXTRA[@]}"; do
  [[ -z "$t" ]] && continue
  TAGGED="${IMAGE_FULL_BASE}:${t}"
  log "Pushing: $TAGGED"
  docker push "$TAGGED"
done

# Cleanup temp
docker rmi "$TEMP_TAG" >/dev/null 2>&1 || true

log "Done. Pushed ${IMAGE_NAME} -> ${VULTR_REGISTRY} (:${COMMIT_SHA}${PUSH_LATEST:+, :latest})"
