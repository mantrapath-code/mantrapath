#!/bin/bash

# MantraPath Environment Synchronization Script
# This script ensures frontend and backend environment files are synchronized

set -e

BACKEND_ENV="./backend/.env"
FRONTEND_ENV="./frontend/.env"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔄 MantraPath Environment Synchronization${NC}"
echo "=================================================="

# Check if backend .env exists
if [ ! -f "$BACKEND_ENV" ]; then
    echo -e "${RED}❌ Backend .env file not found at $BACKEND_ENV${NC}"
    exit 1
fi

# Read values from backend .env
echo -e "${YELLOW}📖 Reading backend environment configuration...${NC}"

# Extract key variables from backend .env
DOMAIN=$(grep "^DOMAIN=" "$BACKEND_ENV" | cut -d'=' -f2)
PROTOCOL=$(grep "^PROTOCOL=" "$BACKEND_ENV" | cut -d'=' -f2)
FRONTEND_PORT=$(grep "^FRONTEND_PORT=" "$BACKEND_ENV" | cut -d'=' -f2)
API_GATEWAY_PORT=$(grep "^API_GATEWAY_PORT=" "$BACKEND_ENV" | cut -d'=' -f2)
DEBUG=$(grep "^DEBUG=" "$BACKEND_ENV" | cut -d'=' -f2)
ENVIRONMENT=$(grep "^ENVIRONMENT=" "$BACKEND_ENV" | cut -d'=' -f2)

echo "  Domain: $DOMAIN"
echo "  Protocol: $PROTOCOL"
echo "  Frontend Port: $FRONTEND_PORT"
echo "  API Gateway Port: $API_GATEWAY_PORT"
echo "  Environment: $ENVIRONMENT"

# Generate frontend .env
echo -e "${YELLOW}📝 Generating synchronized frontend .env...${NC}"

cat > "$FRONTEND_ENV" << EOF
# MantraPath Frontend Environment Configuration
# Single Source of Truth - Synchronized with backend/.env
# Auto-generated on $(date)

# =============================================================================
# DOMAIN & HOST CONFIGURATION  
# =============================================================================
VITE_DOMAIN=$DOMAIN
VITE_PROTOCOL=$PROTOCOL

# =============================================================================
# PORT CONFIGURATION
# =============================================================================
VITE_FRONTEND_PORT=$FRONTEND_PORT
VITE_API_GATEWAY_PORT=$API_GATEWAY_PORT

# =============================================================================
# APPLICATION URLS (Computed from above variables)
# =============================================================================
VITE_FRONTEND_URL=\${VITE_PROTOCOL}://\${VITE_DOMAIN}:\${VITE_FRONTEND_PORT}
VITE_API_GATEWAY_URL=\${VITE_PROTOCOL}://\${VITE_DOMAIN}:\${VITE_API_GATEWAY_PORT}
VITE_API_URL=\${VITE_API_GATEWAY_URL}
VITE_WS_URL=ws://\${VITE_DOMAIN}:\${VITE_API_GATEWAY_PORT}

# =============================================================================
# APPLICATION CONFIGURATION
# =============================================================================
VITE_APP_NAME=MantraPath
VITE_APP_VERSION=1.0.0
VITE_ENVIRONMENT=$ENVIRONMENT

# =============================================================================
# FEATURE FLAGS
# =============================================================================
VITE_ENABLE_ANALYTICS=false
VITE_ENABLE_WEBSOCKETS=true
VITE_ENABLE_PWA=false
EOF

echo -e "${GREEN}✅ Frontend .env synchronized successfully!${NC}"

# Validate generated URLs
echo -e "${YELLOW}🔍 Validating generated URLs...${NC}"

FRONTEND_URL="${PROTOCOL}://${DOMAIN}:${FRONTEND_PORT}"
API_URL="${PROTOCOL}://${DOMAIN}:${API_GATEWAY_PORT}"

echo "  Frontend URL: $FRONTEND_URL"
echo "  API Gateway URL: $API_URL"

echo -e "${GREEN}✅ Environment synchronization complete!${NC}"
echo ""
echo -e "${BLUE}📋 Next Steps:${NC}"
echo "  1. Restart frontend: cd frontend && npm run dev"
echo "  2. Restart backend: cd backend && docker-compose restart"
echo "  3. Update production deployment with new environment variables"
echo ""
echo -e "${YELLOW}💡 To change domain/ports for production:${NC}"
echo "  Edit backend/.env then run this script again"
echo "  Example: DOMAIN=mantrapath.com PROTOCOL=https"
