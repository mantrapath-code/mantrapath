#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(cd "$(dirname "$0")/.." && pwd)
SERVICES_DIR="${ROOT_DIR}/backend/services"

if [[ ! -d "$SERVICES_DIR" ]]; then
  echo "backend/services not found" >&2
  exit 1
fi

# Print service names that contain a Dockerfile
find "$SERVICES_DIR" -mindepth 2 -maxdepth 2 -type f -name Dockerfile \
  | sed -E "s#^.*/backend/services/([^/]+)/Dockerfile$#\1#" \
  | sort -u
