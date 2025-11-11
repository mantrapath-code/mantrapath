#!/bin/bash
# Start Nginx Reverse Proxy with SSL for MantraPath

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}=== Starting Nginx Reverse Proxy with SSL ===${NC}"

# Check if certificates exist
if [ ! -f "/home/sachin/mantrapath/config/ssl/mantrapath.crt" ]; then
    echo -e "${YELLOW}SSL certificates not found. Generating...${NC}"
    /home/sachin/mantrapath/scripts/setup/generate-self-signed-cert.sh
fi

# Run nginx in docker with proper configuration
docker run -d \
    --name mantrapath-nginx \
    --network mantrapath_mantrapath-network \
    -p 80:80 \
    -p 443:443 \
    -v /home/sachin/mantrapath/config/nginx.conf:/etc/nginx/nginx.conf:ro \
    -v /home/sachin/mantrapath/config/ssl:/etc/nginx/ssl:ro \
    -v /home/sachin/mantrapath/frontend/dist:/usr/share/nginx/html:ro \
    --restart unless-stopped \
    nginx:alpine

echo -e "${GREEN}✓ Nginx started successfully${NC}"
echo ""
echo "Access your application at:"
echo "  - HTTP:  http://139.84.213.185"
echo "  - HTTPS: https://139.84.213.185"
echo ""
echo -e "${YELLOW}Note: Browsers will show a security warning for self-signed certificates${NC}"
echo "You can accept the warning or import the certificate from:"
echo "  /home/sachin/mantrapath/config/ssl/mantrapath.crt"
echo ""
