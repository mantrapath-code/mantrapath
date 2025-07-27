# MantraPath Backend Development Setup

## Quick Start

1. **Clone and Setup**
```bash
cd backend
cp .env.example .env
# Edit .env with your configuration
```

2. **Start All Services**
```bash
docker-compose up -d
```

3. **Check Service Health**
```bash
curl http://localhost:8000/health
```

## Environment Variables

Create a `.env` file in the backend directory:

```bash
# Database
DATABASE_URL=postgresql://mantrapath_user:mantrapath_password@postgres:5432/mantrapath
REDIS_URL=redis://redis:6379/0
MONGODB_URL=mongodb://mantrapath_user:mantrapath_password@mongodb:27017/mantrapath
INFLUXDB_URL=http://influxdb:8086
INFLUXDB_TOKEN=your_influxdb_token
INFLUXDB_ORG=mantrapath
INFLUXDB_BUCKET=mood_analytics

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# External APIs
OPENAI_API_KEY=your_openai_api_key

# Email Configuration
SMTP_HOST=your_smtp_host
SMTP_PORT=587
SMTP_USERNAME=your_smtp_username
SMTP_PASSWORD=your_smtp_password

# File Upload
UPLOAD_DIR=/app/uploads
MAX_FILE_SIZE=10485760  # 10MB
```

## Service URLs

- **API Gateway**: http://localhost:8000
- **Auth Service**: http://localhost:8001
- **Profile Service**: http://localhost:8002
- **Mood Service**: http://localhost:8003
- **Chatbot Service**: http://localhost:8004
- **Content Service**: http://localhost:8005
- **Community Service**: http://localhost:8006
- **Notification Service**: http://localhost:8007
- **Media Service**: http://localhost:8009
- **Analytics Service**: http://localhost:8010

## Database Access

### PostgreSQL
```bash
docker exec -it backend_postgres_1 psql -U mantrapath_user -d mantrapath
```

### MongoDB
```bash
docker exec -it backend_mongodb_1 mongosh --username mantrapath_user --password mantrapath_password
```

### Redis
```bash
docker exec -it backend_redis_1 redis-cli
```

## Development Commands

### Start Individual Service
```bash
cd services/auth_service
python -m uvicorn main:app --reload --port 8001
```

### Run Tests
```bash
cd services/auth_service
pytest tests/
```

### Database Migrations
```bash
cd services/auth_service
alembic upgrade head
```

### View Logs
```bash
docker-compose logs -f auth_service
```

## API Documentation

Each service exposes interactive API documentation:

- Auth Service: http://localhost:8001/docs
- Mood Service: http://localhost:8003/docs
- Community Service: http://localhost:8006/docs
- etc.

## Testing the Backend

### User Registration and Login
```bash
# Register a new user
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "testpassword123"
  }'

# Login
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpassword123"
  }'
```

### Create Mood Entry
```bash
# Use the access_token from login response
curl -X POST "http://localhost:8000/api/v1/mood/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "mood_value": 8,
    "energy_level": 7,
    "stress_level": 3,
    "notes": "Feeling great today!"
  }'
```

### Create Journal Entry
```bash
curl -X POST "http://localhost:8000/api/v1/journal/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Today was amazing",
    "content": "I had a wonderful day with lots of positive energy and great conversations with friends.",
    "tags": ["positive", "social", "energy"]
  }'
```

## Frontend Integration

Update your frontend configuration to use the backend:

```typescript
// src/config/api.ts
export const API_BASE_URL = 'http://localhost:8000'

// Example API call
const response = await fetch(`${API_BASE_URL}/api/v1/mood/`, {
  method: 'GET',
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json'
  }
})
```

## Production Deployment

### Docker Swarm
```bash
docker swarm init
docker stack deploy -c docker-compose.prod.yml mantrapath
```

### Kubernetes
```bash
kubectl apply -f k8s/
```

### Environment-specific Configurations

1. **Development**: All services on localhost
2. **Staging**: Services on internal network
3. **Production**: Load balancer + multiple instances

## Monitoring

### Health Checks
```bash
# Check all services
for port in 8000 8001 8002 8003 8004 8005 8006 8007 8009 8010; do
  echo "Checking port $port:"
  curl -s http://localhost:$port/health | jq .
done
```

### Metrics
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   ```bash
   docker-compose down
   docker volume prune
   docker-compose up -d postgres
   # Wait for postgres to be ready
   docker-compose up -d
   ```

2. **Redis Connection Failed**
   ```bash
   docker-compose restart redis
   ```

3. **Service Won't Start**
   ```bash
   docker-compose logs service_name
   ```

### Reset Everything
```bash
docker-compose down -v
docker system prune -a
docker-compose up -d
```

## Security Considerations

1. **Change Default Passwords**: Update all default passwords in production
2. **JWT Secret**: Use a strong, random JWT secret key
3. **HTTPS**: Enable HTTPS in production
4. **Rate Limiting**: Configure appropriate rate limits
5. **CORS**: Restrict CORS origins to your frontend domains
6. **Environment Variables**: Never commit secrets to version control

## Performance Tuning

1. **Database Indexing**: Ensure proper indexes on frequently queried columns
2. **Redis Caching**: Cache frequently accessed data
3. **Connection Pooling**: Optimize database connection pools
4. **Load Balancing**: Use multiple instances of services
5. **CDN**: Use CDN for static assets

This backend provides a robust, scalable foundation for the MantraPath application with comprehensive mood tracking, journaling, community features, and real-time analytics.