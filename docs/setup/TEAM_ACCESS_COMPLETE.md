# 🚀 MantraPath Team Access - SETUP COMPLETE!

## ✅ Security Architecture Implemented

We've successfully enhanced the MantraPath application security by implementing a **secure tunnel architecture** where:

1. **Only the API Gateway is exposed** externally via ngrok (port 8000)
2. **All microservices are internal-only** and not directly accessible from outside
3. **API Gateway handles all routing** to internal services securely
4. **Authentication and authorization** are enforced through the gateway

## 🌐 **Team Access URLs**

### **Production URL (External Access)**
- **HTTPS**: `https://af7865e29409.ngrok-free.app`
- **HTTP**: `http://af7865e29409.ngrok-free.app`

### **Local Development URL**
- **API Gateway**: `http://localhost:8000`

## 📋 **Available API Endpoints**

### **Public Endpoints (No Authentication Required)**
```bash
# Health Check
GET https://af7865e29409.ngrok-free.app/health

# User Registration
POST https://af7865e29409.ngrok-free.app/auth/register

# User Login
POST https://af7865e29409.ngrok-free.app/auth/login
```

### **Protected Endpoints (Require Authentication)**
```bash
# User Profile
GET https://af7865e29409.ngrok-free.app/profile/me

# Mood Tracking
POST https://af7865e29409.ngrok-free.app/mood/entries
GET https://af7865e29409.ngrok-free.app/mood/analytics

# Memory/Journal
POST https://af7865e29409.ngrok-free.app/memory/entries
GET https://af7865e29409.ngrok-free.app/memory/patterns

# AI Chat
POST https://af7865e29409.ngrok-free.app/chat/message

# Community
GET https://af7865e29409.ngrok-free.app/community/posts
```

## 🔐 **Authentication Process**

### 1. **Register a New User**
```bash
curl -X POST https://af7865e29409.ngrok-free.app/auth/register \
  -H "Content-Type: application/json" \
  -H "ngrok-skip-browser-warning: true" \
  -d '{
    "email": "test@example.com",
    "password": "password123",
    "full_name": "Test User"
  }'
```

### 2. **Login to Get Access Token**
```bash
curl -X POST https://af7865e29409.ngrok-free.app/auth/login \
  -H "Content-Type: application/json" \
  -H "ngrok-skip-browser-warning: true" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

### 3. **Use Token for Protected Requests**
```bash
curl -X GET https://af7865e29409.ngrok-free.app/mood/analytics \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "ngrok-skip-browser-warning: true"
```

## 🛠️ **Development Commands**

### **Start the Application**
```bash
# Start secure Docker setup
cd backend
docker compose -f docker-compose.secure.yml up -d

# Start ngrok tunnel
cd ..
./start-ngrok.sh
```

### **Monitoring & Testing**
```bash
# Check service status
docker compose -f backend/docker-compose.secure.yml ps

# Run validation tests
./validate-complete-setup.sh

# Test API flow
./test-api-gateway-flow.sh

# Monitor ngrok dashboard
open http://localhost:4040
```

## 🏗️ **Architecture Summary**

```
[Internet] 
    ↓
[ngrok tunnel: af7865e29409.ngrok-free.app]
    ↓
[API Gateway: localhost:8000] ⟵ Only externally exposed service
    ↓
[Internal Network]
    ├── Auth Service (8001)
    ├── Profile Service (8002)
    ├── Mood Service (8003)
    ├── Chatbot Service (8004)
    ├── Content Service (8005)
    ├── Community Service (8006)
    ├── Memory Service (8017)
    └── [Other Services...]
```

## 🔒 **Security Features**

✅ **Only API Gateway exposed externally**  
✅ **All internal services protected**  
✅ **JWT authentication required for protected endpoints**  
✅ **Request routing through secure gateway**  
✅ **SSL/TLS encryption via ngrok HTTPS**  
✅ **Rate limiting and request validation**  

## 📚 **Documentation**

- **Setup Guide**: `NGROK_SETUP_GUIDE.md`
- **Team Access Guide**: `TEAM_ACCESS_GUIDE.md`
- **API Documentation**: Available at `https://af7865e29409.ngrok-free.app/docs`

---

**🎉 Ready for team collaboration!** Share the ngrok URL with your team members and they can start testing the application immediately.

**⚠️ Note**: The ngrok URL changes when restarted. Use `./start-ngrok.sh` to get the current URL.
