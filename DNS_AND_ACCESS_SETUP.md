# MantraPath DNS and Access Setup Guide

## 🌐 Current Architecture Overview

```
Internet Users
     ↓
Your Server IP: 139.84.213.185
     ↓
Nginx (Port 80) - Reverse Proxy
     ↓
Docker Services (localhost:port)
     ↓
├── API Gateway (localhost:8000)
├── Frontend (localhost:3000)  
├── WebSocket (localhost:8080)
└── Other Services (localhost:8001-8081)
```

## 🔍 Why `localhost` is Correct in Nginx Config

The `localhost` in the upstream configuration is **correct** because:

1. **Nginx runs on the host system** (not in Docker)
2. **Docker services expose ports to the host** via port mapping
3. **From Nginx's perspective**, the services are available at `localhost:PORT`

Example Docker port mapping:
```yaml
api-gateway:
  ports:
    - "8000:8000"  # Host port 8000 → Container port 8000
```

## 🌍 How Users Access Your Application

### Current Access Methods:

1. **Direct IP Access**: `http://139.84.213.185`
2. **With Domain** (if configured): `http://your-domain.com`

### Access Flow:
```
User Browser → 139.84.213.185:80 → Nginx → localhost:3000 (Frontend)
User API Call → 139.84.213.185/api → Nginx → localhost:8000 (API Gateway)
WebSocket → 139.84.213.185/ws → Nginx → localhost:8080 (WebSocket)
```

## 🔧 DNS Configuration Options

### Option 1: IP-Only Access (Current Setup)
Users access via: `http://139.84.213.185`

**Pros:**
- No DNS setup needed
- Works immediately
- Good for development/testing

**Cons:**
- Not user-friendly
- No SSL certificate options
- Looks unprofessional

### Option 2: Domain Name Setup (Recommended)

#### Step 1: Purchase/Configure Domain
- Buy domain: `mantrapath.com` (example)
- Or use subdomain: `mantrapath.yourdomain.com`

#### Step 2: DNS Records
Add these DNS records to your domain:

```
Type: A
Name: @
Value: 139.84.213.185
TTL: 3600

Type: A  
Name: www
Value: 139.84.213.185
TTL: 3600

Type: CNAME
Name: api
Value: mantrapath.com
TTL: 3600
```

#### Step 3: Update Nginx Configuration
The configuration is already updated to handle domains:

```nginx
server_name 139.84.213.185 mantrapath.com www.mantrapath.com;
```

### Option 3: Subdomain Setup
For different services on subdomains:

```
mantrapath.com → Frontend
api.mantrapath.com → API Gateway  
ws.mantrapath.com → WebSocket
docs.mantrapath.com → API Documentation
```

## 🔒 SSL/HTTPS Setup (Recommended for Production)

### Using Let's Encrypt (Free SSL)

1. **Install Certbot:**
```bash
sudo apt update
sudo apt install certbot python3-certbot-nginx
```

2. **Get SSL Certificate:**
```bash
sudo certbot --nginx -d mantrapath.com -d www.mantrapath.com
```

3. **Auto-renewal:**
```bash
sudo crontab -e
# Add this line:
0 12 * * * /usr/bin/certbot renew --quiet
```

### Manual SSL Configuration
If you have your own SSL certificates:

```nginx
server {
    listen 443 ssl http2;
    server_name mantrapath.com www.mantrapath.com;
    
    ssl_certificate /path/to/your/certificate.crt;
    ssl_certificate_key /path/to/your/private.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    
    # Your existing configuration...
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name mantrapath.com www.mantrapath.com;
    return 301 https://$server_name$request_uri;
}
```

## 🔄 Alternative Architecture: Docker Internal Network

If you want to avoid port mapping, you could use Docker's internal network:

### Modified Nginx Configuration:
```nginx
upstream api_gateway {
    server api-gateway:8000;  # Docker service name
    keepalive 32;
}

upstream frontend {
    server frontend:3000;     # Docker service name  
    keepalive 32;
}
```

### Run Nginx in Docker:
```yaml
nginx:
  image: nginx:alpine
  ports:
    - "80:80"
    - "443:443"
  networks:
    - mantrapath-network
  # Remove port mappings from other services
```

## 🌐 Complete Access URLs

After proper DNS setup, users can access:

### Frontend Application:
- `http://139.84.213.185` (IP access)
- `http://mantrapath.com` (domain access)
- `https://mantrapath.com` (with SSL)

### API Endpoints:
- `http://139.84.213.185/api/health`
- `http://mantrapath.com/api/health`
- `https://mantrapath.com/api/health`

### API Documentation:
- `http://139.84.213.185/docs`
- `http://mantrapath.com/docs`
- `https://mantrapath.com/docs`

### WebSocket Connection:
- `ws://139.84.213.185/ws`
- `ws://mantrapath.com/ws`
- `wss://mantrapath.com/ws` (secure WebSocket)

## 🔧 Quick Setup Commands

### 1. Update Environment Variables
```bash
# Update your GitHub secrets or .env files
DOMAIN=mantrapath.com
PROTOCOL=https
APP_URL=https://mantrapath.com
```

### 2. Update Frontend Environment
```bash
# frontend/.env
VITE_API_BASE_URL=https://mantrapath.com:8000
VITE_WS_URL=wss://mantrapath.com/ws
VITE_API_URL=https://mantrapath.com/api
```

### 3. Test DNS Resolution
```bash
# Test if your domain points to your server
nslookup mantrapath.com
dig mantrapath.com

# Should return: 139.84.213.185
```

### 4. Test Nginx Configuration
```bash
sudo nginx -t
sudo systemctl reload nginx
```

## 🧪 Testing Access

### Test Frontend Access:
```bash
curl -I http://139.84.213.185
curl -I http://mantrapath.com  # if domain configured
```

### Test API Access:
```bash
curl http://139.84.213.185/api/health
curl http://mantrapath.com/api/health
```

### Test WebSocket:
```bash
# Use browser console or WebSocket testing tool
const ws = new WebSocket('ws://mantrapath.com/ws');
```

## 📋 Recommended Production Setup

1. **Purchase Domain**: Get `mantrapath.com` or similar
2. **Configure DNS**: Point domain to `139.84.213.185`
3. **Setup SSL**: Use Let's Encrypt for free SSL
4. **Update Environment**: Change all localhost references to domain
5. **Test Everything**: Verify all endpoints work with domain

## 🚨 Security Considerations

1. **Use HTTPS**: Always use SSL in production
2. **Domain Validation**: Ensure your domain is properly validated
3. **Rate Limiting**: Configure appropriate rate limits in Nginx
4. **Firewall**: Only expose necessary ports (80, 443)
5. **Headers**: Use security headers (already configured)

## 🔍 Troubleshooting

### Domain Not Resolving:
```bash
# Check DNS propagation
dig mantrapath.com
nslookup mantrapath.com 8.8.8.8
```

### SSL Issues:
```bash
# Check certificate
sudo certbot certificates
openssl s_client -connect mantrapath.com:443
```

### Nginx Issues:
```bash
# Check configuration
sudo nginx -t

# Check logs
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

### Service Connection Issues:
```bash
# Test if services are running
curl http://localhost:8000/health
docker-compose -f backend/docker-compose.prod.yml ps
```

---

The current `localhost` configuration is **correct** for the architecture, but setting up a proper domain and SSL is **highly recommended** for production use!
