# SSL Certificate Setup and Troubleshooting Guide

## Current Status
✅ Self-signed SSL certificate generated
✅ Certificate location: `/home/sachin/mantrapath/config/ssl/`
⚠️  Browser shows security warning (expected for self-signed certificates)

## Quick Fix: Access via HTTP
**Recommended for development:**
```
http://139.84.213.185:3000
```

## Option 1: Accept Self-Signed Certificate (Easiest)

### Chrome/Edge
1. When you see the security warning, click "Advanced"
2. Click "Proceed to 139.84.213.185 (unsafe)"
3. The certificate will be temporarily trusted

### Firefox
1. Click "Advanced"
2. Click "Accept the Risk and Continue"

## Option 2: Trust the Certificate Permanently

### Windows
1. Download the certificate:
   ```bash
   scp sachin@139.84.213.185:/home/sachin/mantrapath/config/ssl/mantrapath.crt ~/Downloads/
   ```
2. Double-click the `.crt` file
3. Click "Install Certificate"
4. Choose "Local Machine" → Next
5. Select "Place all certificates in the following store"
6. Browse → "Trusted Root Certification Authorities"
7. Click OK → Next → Finish

### Mac/Linux
1. Download the certificate
2. **Chrome**: Settings → Privacy and security → Security → Manage certificates → Authorities → Import
3. **Firefox**: Settings → Privacy & Security → Certificates → View Certificates → Authorities → Import
4. Check "Trust this certificate for identifying websites"

### Linux System-Wide
```bash
# Copy certificate to system trust store
sudo cp /home/sachin/mantrapath/config/ssl/mantrapath.crt /usr/local/share/ca-certificates/mantrapath.crt
sudo update-ca-certificates

# Restart browser
```

## Option 3: Use Let's Encrypt (Production)

### Prerequisites
- Domain name pointing to your server (e.g., app.mantrapath.com)
- Ports 80 and 443 open in firewall

### Setup
```bash
cd /home/sachin/mantrapath
./scripts/setup/setup-ssl.sh \
    --mode letsencrypt \
    --domain mantrapath.com \
    --email admin@mantrapath.com
```

### Auto-Renewal
Let's Encrypt certificates expire every 90 days. The setup script automatically configures monthly renewal via cron.

## Current Certificate Details

```bash
# View certificate information
openssl x509 -in /home/sachin/mantrapath/config/ssl/mantrapath.crt -text -noout

# Check certificate validity
openssl x509 -in /home/sachin/mantrapath/config/ssl/mantrapath.crt -noout -dates
```

**Valid From:** Nov 11, 2025
**Valid To:** Nov 11, 2026

**Domains Covered:**
- localhost
- mantrapath.local
- *.mantrapath.local
- mantrapath.com
- *.mantrapath.com
- app.mantrapath.com
- 127.0.0.1
- 139.84.213.185

## Troubleshooting

### Error: ERR_CERT_AUTHORITY_INVALID
**Cause:** Browser doesn't trust the self-signed certificate
**Solution:** Accept the certificate (Option 1) or trust it permanently (Option 2)

### Error: NET::ERR_CERT_COMMON_NAME_INVALID
**Cause:** Accessing via IP/domain not in certificate
**Solution:** Regenerate certificate with correct domain:
```bash
cd /home/sachin/mantrapath
./scripts/setup/generate-self-signed-cert.sh
```

### Certificate Not Found
```bash
# Regenerate certificates
cd /home/sachin/mantrapath
./scripts/setup/generate-self-signed-cert.sh
```

### nginx Not Serving HTTPS
```bash
# Check nginx is running
docker ps | grep nginx

# Start nginx with SSL
chmod +x scripts/start-nginx.sh
./scripts/start-nginx.sh

# Check nginx logs
docker logs mantrapath-nginx
```

## Testing

### Test HTTP (No SSL)
```bash
curl http://139.84.213.185:3000
```

### Test HTTPS (Accept Self-Signed)
```bash
curl -k https://139.84.213.185
```

### Test Certificate
```bash
openssl s_client -connect 139.84.213.185:443 -servername mantrapath.com
```

## Production Checklist

- [ ] Domain name configured and pointing to server
- [ ] Firewall allows ports 80 and 443
- [ ] Let's Encrypt certificate installed
- [ ] Auto-renewal cron job configured
- [ ] HTTPS redirect enabled (HTTP → HTTPS)
- [ ] HSTS header configured
- [ ] Certificate valid for all required domains

## Additional Resources

- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)
- [SSL Labs Server Test](https://www.ssllabs.com/ssltest/)
- [Mozilla SSL Configuration Generator](https://ssl-config.mozilla.org/)
