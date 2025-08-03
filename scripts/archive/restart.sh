#!/bin/bash

# MantraPath Development Environment - Restart Script
# Safely restarts all services

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${BLUE}🔄 MantraPath Development Environment - Restart${NC}"
echo -e "${CYAN}Restarting all services safely...${NC}"
echo ""

# Step 1: Stop all services
echo -e "${YELLOW}Step 1: Stopping all services...${NC}"
chmod +x "$SCRIPT_DIR/stop.sh"
"$SCRIPT_DIR/stop.sh"

echo ""
echo -e "${YELLOW}⏳ Waiting 3 seconds for clean shutdown...${NC}"
sleep 3

# Step 2: Start all services
echo ""
echo -e "${YELLOW}Step 2: Starting all services...${NC}"
chmod +x "$SCRIPT_DIR/start.sh"
"$SCRIPT_DIR/start.sh"
