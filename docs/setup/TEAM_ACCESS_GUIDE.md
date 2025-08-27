# 🌐 MantraPath Team Access Guide

## ✅ Security Architecture Successfully Implemented!

We've successfully implemented a secure microservices architecture where:
- **Only API Gateway (port 8000)** is exposed externally
- **All internal services** are protected and not directly accessible
- **ngrok tunnels only the API Gateway** for team access

---

## 🔗 Developer Access Endpoints

### 🏠 Local Development Access
When running locally, developers can access the application via:

#### **Primary API Gateway Endpoint**
```
http://localhost:8000
```

#### **Alternative Gateway Ports**
```
http://localhost:8080  # Alternative gateway port
http://localhost:9090  # Monitoring/metrics port
```

---

## 🌍 Remote Team Access (via ngrok)

### Setup ngrok (One-time setup)
```bash
# 1. Sign up for ngrok account
https://dashboard.ngrok.com/signup

# 2. Get your auth token
https://dashboard.ngrok.com/get-started/your-authtoken

# 3. Install auth token
ngrok config add-authtoken YOUR_AUTH_TOKEN_HERE

# 4. Start ngrok tunnel
./start-ngrok.sh
```

### After ngrok is running:
- **Public HTTPS URL**: `https://RANDOM-ID.ngrok-free.app`
- **ngrok Dashboard**: `http://localhost:4040`
- **API Gateway through tunnel**: Routes to `localhost:8000`

---

## 🔧 Available API Endpoints

### 🔐 Authentication
```bash
# Login
POST https://YOUR-NGROK-URL/auth/login
Content-Type: application/json
{
  "email_or_username": "sa@gmail.com",
  "password": "Dev@#123"
}

# Register
POST https://YOUR-NGROK-URL/auth/register
```

### 🧠 Core Services (via API Gateway)
```bash
# Mood Service
GET https://YOUR-NGROK-URL/api/v1/mood/
Authorization: Bearer YOUR_JWT_TOKEN

# Profile Service  
GET https://YOUR-NGROK-URL/api/v1/profile/
Authorization: Bearer YOUR_JWT_TOKEN

# Memory Service
GET https://YOUR-NGROK-URL/api/v1/memory/
Authorization: Bearer YOUR_JWT_TOKEN

# Chatbot Service
POST https://YOUR-NGROK-URL/api/v1/chatbot/chat
Authorization: Bearer YOUR_JWT_TOKEN

# Voice Service
POST https://YOUR-NGROK-URL/api/v1/voice/process
Authorization: Bearer YOUR_JWT_TOKEN

# Content Service
GET https://YOUR-NGROK-URL/api/v1/content/
Authorization: Bearer YOUR_JWT_TOKEN

# Media Service
POST https://YOUR-NGROK-URL/api/v1/media/upload
Authorization: Bearer YOUR_JWT_TOKEN

# Community Service
GET https://YOUR-NGROK-URL/api/v1/community/
Authorization: Bearer YOUR_JWT_TOKEN

# Notification Service
GET https://YOUR-NGROK-URL/api/v1/notifications/
Authorization: Bearer YOUR_JWT_TOKEN

# Translation Service
POST https://YOUR-NGROK-URL/api/v1/translation/translate
Authorization: Bearer YOUR_JWT_TOKEN

# ML Service
POST https://YOUR-NGROK-URL/api/v1/ml/predict
Authorization: Bearer YOUR_JWT_TOKEN

# Models Service  
GET https://YOUR-NGROK-URL/api/v1/models/
Authorization: Bearer YOUR_JWT_TOKEN
```

### 🏥 Health & Status
```bash
# API Gateway Health
GET https://YOUR-NGROK-URL/health

# Service Status  
GET https://YOUR-NGROK-URL/status

# Metrics (if available)
GET https://YOUR-NGROK-URL:9090/metrics
```

---

## 🔒 Security Features

### ✅ What's Protected:
- **Internal Services**: Not directly accessible from outside
- **Database**: PostgreSQL only accessible internally
- **Redis**: Cache only accessible internally  
- **NATS**: Message queue only accessible internally
- **Service-to-Service**: Communication happens internally

### ✅ What's Exposed:
- **API Gateway Only**: Single point of entry (port 8000)
- **Through ngrok**: Secure HTTPS tunnel to API Gateway
- **Authentication Required**: JWT tokens for protected endpoints

---

## 🚀 Quick Start for Team Members

### 1. Get the ngrok URL from team lead
```bash
# Team lead shares the URL like:
https://abc123.ngrok-free.app
```

### 2. Test connectivity
```bash
curl https://abc123.ngrok-free.app/health
```

### 3. Login to get access token
```bash
curl -X POST https://abc123.ngrok-free.app/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email_or_username": "sa@gmail.com", "password": "Dev@#123"}'
```

### 4. Use the token for API calls
```bash
export TOKEN="YOUR_JWT_TOKEN_HERE"
curl -H "Authorization: Bearer $TOKEN" \
  https://abc123.ngrok-free.app/api/v1/mood/?limit=5
```

---

## 🛠️ Development Scripts

### For Local Development:
```bash
# Start secure backend services
cd backend && docker-compose -f docker-compose.secure.yml up -d

# Start frontend
cd frontend && npm run dev

# Validate setup
./validate-complete-setup.sh
```

### For Team Sharing:
```bash
# Start ngrok tunnel (requires auth token)
./start-ngrok.sh

# Test ngrok setup
./test-ngrok-setup.sh

# Test complete API flow
./test-api-gateway-flow.sh
```

---

## 📊 Monitoring & Debugging

### ngrok Dashboard
- **URL**: `http://localhost:4040`
- **Features**: Request inspection, replay, traffic analysis

### Docker Logs
```bash
# View all service logs
docker-compose -f backend/docker-compose.secure.yml logs

# View specific service
docker-compose -f backend/docker-compose.secure.yml logs api-gateway
```

### Service Health
```bash
# Check all container status
docker-compose -f backend/docker-compose.secure.yml ps

# Run health validation
./validate-complete-setup.sh
```

---

## ❓ Troubleshooting

### Common Issues:

1. **ngrok auth token missing**:
   ```bash
   ngrok config add-authtoken YOUR_TOKEN
   ```

2. **Services not starting**:
   ```bash
   docker-compose -f backend/docker-compose.secure.yml down
   docker-compose -f backend/docker-compose.secure.yml up -d
   ```

3. **API Gateway not responding**:
   ```bash
   curl http://localhost:8000/health
   ```

4. **Authentication failing**:
   - Check if user exists: `sa@gmail.com` / `Dev@#123`
   - Verify JWT token format

---

## 🎯 Next Steps

1. **Team Lead**: Set up ngrok auth token and share public URL
2. **Developers**: Use the shared ngrok URL for API testing
3. **Frontend**: Update API base URL to ngrok URL for team testing
4. **Production**: Replace ngrok with proper domain and SSL certificates

---

*This setup ensures secure, scalable access to the MantraPath application for distributed team development! 🚀*
