# MantraPath Deployment Guide

This guide covers deploying the complete MantraPath system with real-time notifications and WebSocket integration.

## 🏗️ Architecture Overview

### Services
- **Frontend**: React SPA with real-time notifications
- **API Gateway**: Request routing and authentication
- **Auth Service**: User authentication and authorization
- **Profile Service**: User profiles and preferences
- **Mood Service**: Mood tracking and analytics
- **Chatbot Service**: AI-powered wellness assistant
- **Content Service**: Affirmations and wellness content
- **Community Service**: Forums and social features
- **Notification Service**: Real-time notifications with WebSocket
- **Media Service**: File uploads and media management

### Databases
- **PostgreSQL**: Primary relational database
- **Redis**: Caching and session storage
- **MongoDB**: Document storage for content
- **InfluxDB**: Time-series data for mood analytics

### Infrastructure
- **Nginx**: Reverse proxy and load balancer
- **Prometheus**: Metrics collection
- **Grafana**: Monitoring dashboards

## 🚀 Quick Deployment

### Prerequisites
- Docker 20.10+
- Docker Compose 2.0+
- 4GB+ RAM
- 20GB+ disk space

### One-Command Deployment
```bash
./deploy.sh
```

This script will:
1. Set up all necessary configuration files
2. Create required directories
3. Build all Docker images
4. Start all services in the correct order
5. Set up monitoring and logging

## 📝 Configuration

### Environment Variables
Edit `backend/.env` with your settings:

```bash
# Required: Set your OpenAI API key
OPENAI_API_KEY=your-openai-api-key-here

# Required: Change the JWT secret for security
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production

# Optional: Email configuration for notifications
SMTP_HOST=smtp.gmail.com
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Optional: Push notifications
FCM_SERVER_KEY=your-firebase-server-key
```

### SSL/HTTPS Setup
For production, add SSL certificates:

```bash
# Place your SSL certificates in backend/nginx/ssl/
backend/nginx/ssl/
├── cert.pem
└── key.pem
```

Update nginx configuration to use HTTPS.

## 🔄 Real-Time Features

### WebSocket Notifications
The system includes real-time notifications via WebSocket:

- **Mood pattern alerts**: Automatic notifications when concerning patterns are detected
- **Weekly reports**: Personalized weekly mood summaries
- **Intervention prompts**: Smart timing for wellness suggestions
- **Community updates**: Real-time forum and social interactions

### Frontend Integration
The frontend automatically connects to WebSocket notifications:

```typescript
// WebSocket connection is handled automatically
import { useWebSocket } from '@/hooks/useWebSocket'

const { isConnected, lastMessage } = useWebSocket()
```

### Notification Types
- `mood_pattern`: Mood trend alerts
- `weekly_report`: Weekly mood summaries
- `intervention`: Wellness intervention prompts
- `community`: Social interaction notifications
- `crisis`: Emergency support alerts

## 📊 Monitoring

### Service Health
Check service status:
```bash
cd backend
docker-compose ps
```

### Logs
View service logs:
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f notification-service
```

### Metrics & Dashboards
- **Grafana**: http://localhost:3001 (admin/mantrapath123)
- **Prometheus**: http://localhost:9090

## 🔧 Maintenance

### Updates
Update all services:
```bash
./scripts/update.sh
```

### Backup
Backup databases:
```bash
# PostgreSQL
docker exec backend_postgres_1 pg_dump -U mantrapath mantrapath > backup.sql

# Redis
docker exec backend_redis_1 redis-cli BGSAVE
```

### Scaling
Scale specific services:
```bash
docker-compose up -d --scale mood-service=3
docker-compose up -d --scale notification-service=2
```

## 🐛 Troubleshooting

### Common Issues

**WebSocket Connection Failed**
- Check if notification-service is running
- Verify firewall allows port 8007
- Check browser WebSocket support

**Database Connection Errors**
- Ensure databases are healthy: `docker-compose ps`
- Check database logs: `docker-compose logs postgres`
- Verify connection strings in .env

**High Memory Usage**
- Monitor with Grafana dashboard
- Scale services horizontally
- Optimize database queries

### Debug Mode
Run services in debug mode:
```bash
# Single service
docker-compose up notification-service

# With debug logs
LOG_LEVEL=DEBUG docker-compose up
```

## 🔒 Security Considerations

### Production Checklist
- [ ] Change all default passwords
- [ ] Set strong JWT secret key
- [ ] Configure HTTPS with valid SSL certificates
- [ ] Set up firewall rules
- [ ] Enable database authentication
- [ ] Configure CORS for your domain
- [ ] Set up backup strategy
- [ ] Monitor security logs

### Network Security
- Services communicate only within Docker network
- API Gateway is the only external entry point
- WebSocket connections are authenticated
- Rate limiting is enabled

## 📈 Performance Optimization

### Database Performance
- Connection pooling is configured
- Redis caching reduces database load
- InfluxDB optimized for time-series data

### WebSocket Performance
- Connection management with automatic reconnection
- Heartbeat mechanism prevents dead connections
- Message queuing for offline users

### Frontend Performance
- Code splitting for faster loading
- Service worker for offline support
- Optimized bundle size

## 🌐 Production URLs

After deployment, access:
- **Application**: http://localhost (or your domain)
- **API**: http://localhost:8000
- **Monitoring**: http://localhost:3001
- **Metrics**: http://localhost:9090

## 📞 Support

For issues or questions:
1. Check the logs first
2. Review this documentation
3. Check GitHub issues
4. Contact the development team

---

**Note**: This is a complete production-ready deployment with real-time features, monitoring, and scaling capabilities. The system is designed to handle thousands of concurrent users with proper infrastructure.