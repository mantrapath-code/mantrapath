#!/bin/bash
# SSL Certificate Setup Script for MantraPath
# Supports both self-signed certificates and Let's Encrypt

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default values
SSL_DIR="/home/sachin/mantrapath/config/ssl"
DOMAIN="mantrapath.com"
EMAIL="admin@mantrapath.com"
MODE="self-signed"  # Options: self-signed, letsencrypt

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --mode)
            MODE="$2"
            shift 2
            ;;
        --domain)
            DOMAIN="$2"
            shift 2
            ;;
        --email)
            EMAIL="$2"
            shift 2
            ;;
        --ssl-dir)
            SSL_DIR="$2"
            shift 2
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

echo -e "${GREEN}=== MantraPath SSL Certificate Setup ===${NC}"
echo "Mode: $MODE"
echo "Domain: $DOMAIN"
echo "SSL Directory: $SSL_DIR"
echo ""

# Create SSL directory if it doesn't exist
mkdir -p "$SSL_DIR"

# Function to generate self-signed certificate
generate_self_signed() {
    echo -e "${YELLOW}Generating self-signed SSL certificate...${NC}"
    
    # Generate private key
    openssl genrsa -out "$SSL_DIR/mantrapath.key" 4096
    
    # Generate certificate signing request
    openssl req -new -key "$SSL_DIR/mantrapath.key" \
        -out "$SSL_DIR/mantrapath.csr" \
        -subj "/C=US/ST=California/L=San Francisco/O=MantraPath/CN=$DOMAIN"
    
    # Generate self-signed certificate (valid for 365 days)
    openssl x509 -req -days 365 \
        -in "$SSL_DIR/mantrapath.csr" \
        -signkey "$SSL_DIR/mantrapath.key" \
        -out "$SSL_DIR/mantrapath.crt" \
        -extfile <(printf "subjectAltName=DNS:$DOMAIN,DNS:www.$DOMAIN,DNS:app.$DOMAIN,DNS:*.mantrapath.com,IP:139.84.213.185")
    
    # Set proper permissions
    chmod 600 "$SSL_DIR/mantrapath.key"
    chmod 644 "$SSL_DIR/mantrapath.crt"
    
    echo -e "${GREEN}✓ Self-signed certificate generated successfully${NC}"
    echo -e "${YELLOW}Note: Browsers will show security warnings for self-signed certificates${NC}"
    echo -e "${YELLOW}For production, use Let's Encrypt with: ./setup-ssl.sh --mode letsencrypt${NC}"
}

# Function to setup Let's Encrypt
setup_letsencrypt() {
    echo -e "${YELLOW}Setting up Let's Encrypt SSL certificate...${NC}"
    
    # Check if certbot is installed
    if ! command -v certbot &> /dev/null; then
        echo -e "${YELLOW}Installing Certbot...${NC}"
        sudo apt-get update
        sudo apt-get install -y certbot python3-certbot-nginx
    fi
    
    # Stop nginx if running
    echo -e "${YELLOW}Stopping nginx for certificate generation...${NC}"
    docker-compose -f /home/sachin/mantrapath/docker-compose.yml stop nginx || true
    
    # Generate certificate using standalone mode
    sudo certbot certonly --standalone \
        --preferred-challenges http \
        --email "$EMAIL" \
        --agree-tos \
        --no-eff-email \
        -d "$DOMAIN" \
        -d "www.$DOMAIN" \
        -d "app.$DOMAIN"
    
    # Copy certificates to our SSL directory
    sudo cp "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" "$SSL_DIR/mantrapath.crt"
    sudo cp "/etc/letsencrypt/live/$DOMAIN/privkey.pem" "$SSL_DIR/mantrapath.key"
    
    # Set proper permissions
    sudo chown $(whoami):$(whoami) "$SSL_DIR/mantrapath.key" "$SSL_DIR/mantrapath.crt"
    chmod 600 "$SSL_DIR/mantrapath.key"
    chmod 644 "$SSL_DIR/mantrapath.crt"
    
    # Setup auto-renewal
    setup_auto_renewal
    
    echo -e "${GREEN}✓ Let's Encrypt certificate generated successfully${NC}"
}

# Function to setup certificate auto-renewal
setup_auto_renewal() {
    echo -e "${YELLOW}Setting up automatic certificate renewal...${NC}"
    
    # Create renewal script
    cat > "$SSL_DIR/renew-certs.sh" << 'EOF'
#!/bin/bash
# Auto-renewal script for Let's Encrypt certificates

set -e

DOMAIN="mantrapath.com"
SSL_DIR="/home/sachin/mantrapath/config/ssl"

# Stop nginx
docker-compose -f /home/sachin/mantrapath/docker-compose.yml stop nginx

# Renew certificate
sudo certbot renew --standalone

# Copy renewed certificates
sudo cp "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" "$SSL_DIR/mantrapath.crt"
sudo cp "/etc/letsencrypt/live/$DOMAIN/privkey.pem" "$SSL_DIR/mantrapath.key"

# Set permissions
sudo chown $(whoami):$(whoami) "$SSL_DIR/mantrapath.key" "$SSL_DIR/mantrapath.crt"
chmod 600 "$SSL_DIR/mantrapath.key"
chmod 644 "$SSL_DIR/mantrapath.crt"

# Restart nginx
docker-compose -f /home/sachin/mantrapath/docker-compose.yml up -d nginx

echo "Certificate renewed successfully"
EOF
    
    chmod +x "$SSL_DIR/renew-certs.sh"
    
    # Add cron job for monthly renewal
    (crontab -l 2>/dev/null; echo "0 0 1 * * $SSL_DIR/renew-certs.sh >> $SSL_DIR/renewal.log 2>&1") | crontab -
    
    echo -e "${GREEN}✓ Auto-renewal configured (monthly)${NC}"
}

# Function to create DH parameters for better security
generate_dhparam() {
    if [ ! -f "$SSL_DIR/dhparam.pem" ]; then
        echo -e "${YELLOW}Generating DH parameters (this may take a while)...${NC}"
        openssl dhparam -out "$SSL_DIR/dhparam.pem" 2048
        echo -e "${GREEN}✓ DH parameters generated${NC}"
    else
        echo -e "${GREEN}✓ DH parameters already exist${NC}"
    fi
}

# Main execution
case $MODE in
    self-signed)
        generate_self_signed
        generate_dhparam
        ;;
    letsencrypt)
        setup_letsencrypt
        generate_dhparam
        ;;
    *)
        echo -e "${RED}Invalid mode: $MODE${NC}"
        echo "Valid modes: self-signed, letsencrypt"
        exit 1
        ;;
esac

# Display certificate information
echo -e "\n${GREEN}=== Certificate Information ===${NC}"
openssl x509 -in "$SSL_DIR/mantrapath.crt" -noout -subject -dates -issuer

echo -e "\n${GREEN}=== SSL Setup Complete ===${NC}"
echo "Certificate files:"
echo "  - Certificate: $SSL_DIR/mantrapath.crt"
echo "  - Private Key: $SSL_DIR/mantrapath.key"
echo "  - DH Params: $SSL_DIR/dhparam.pem"
echo ""
echo "Next steps:"
echo "1. Update nginx configuration to use these certificates"
echo "2. Restart nginx: docker-compose restart nginx"
if [ "$MODE" = "self-signed" ]; then
    echo "3. For browsers, you'll need to accept the security warning"
    echo "   or add the certificate to your trusted certificates"
fi
echo ""
