#!/bin/bash
# Quick Self-Signed Certificate Generator for MantraPath

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

SSL_DIR="/home/sachin/mantrapath/config/ssl"
IP="139.84.213.185"

echo -e "${GREEN}=== Generating Self-Signed SSL Certificate ===${NC}"

# Create SSL directory
mkdir -p "$SSL_DIR"

# Generate configuration file for certificate
cat > "$SSL_DIR/openssl.cnf" << EOF
[req]
default_bits = 4096
prompt = no
default_md = sha256
distinguished_name = dn
req_extensions = v3_req

[dn]
C=US
ST=California
L=San Francisco
O=MantraPath
OU=Development
CN=$IP

[v3_req]
keyUsage = critical, digitalSignature, keyEncipherment
extendedKeyUsage = serverAuth
subjectAltName = @alt_names

[v3_ca]
keyUsage = critical, digitalSignature, keyEncipherment, keyAgreement
extendedKeyUsage = serverAuth
subjectAltName = @alt_names
basicConstraints = CA:FALSE

[alt_names]
DNS.1 = localhost
DNS.2 = mantrapath.local
DNS.3 = *.mantrapath.local
DNS.4 = mantrapath.com
DNS.5 = *.mantrapath.com
DNS.6 = app.mantrapath.com
IP.1 = 127.0.0.1
IP.2 = $IP
EOF

# Generate private key and certificate in one command
openssl req -x509 -nodes -days 365 -newkey rsa:4096 \
    -keyout "$SSL_DIR/mantrapath.key" \
    -out "$SSL_DIR/mantrapath.crt" \
    -config "$SSL_DIR/openssl.cnf" \
    -extensions v3_ca

# Set permissions
chmod 600 "$SSL_DIR/mantrapath.key"
chmod 644 "$SSL_DIR/mantrapath.crt"

echo -e "${GREEN}✓ Certificate generated successfully!${NC}"
echo ""
echo "Files created:"
echo "  - Certificate: $SSL_DIR/mantrapath.crt"
echo "  - Private Key: $SSL_DIR/mantrapath.key"
echo ""
echo -e "${YELLOW}Certificate Details:${NC}"
openssl x509 -in "$SSL_DIR/mantrapath.crt" -noout -subject -dates
echo ""
echo -e "${YELLOW}To trust this certificate in your browser:${NC}"
echo "1. Download the certificate: $SSL_DIR/mantrapath.crt"
echo "2. Chrome: Settings → Privacy and security → Security → Manage certificates → Authorities → Import"
echo "3. Firefox: Settings → Privacy & Security → Certificates → View Certificates → Import"
echo ""
