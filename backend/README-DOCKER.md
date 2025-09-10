# MantraPath Docker Setup

This guide helps team members quickly start and access the MantraPath application using Docker Compose.

## Quick Start

### Prerequisites
- Docker and Docker Compose installed
- Git (to clone the repository)

### Starting the Application

1. **Navigate to the backend directory:**
   ```bash
   cd backend
   ```

2. **Run the startup script:**
   ```bash
   ./start-mantrapath.sh
   ```

   This script will:
   - Check Docker is running
   - Create `.env` file if it doesn't exist
   - Start all services with Docker Compose
   - Display access URLs for all services

### Manual Start (Alternative)

If you prefer to start manually:

```bash
# Start all services
docker compose up -d --build

# View logs
docker compose logs -f

# Stop services
docker compose down
```

## Access URLs

Once started, you can access:

### Frontend (Main Application)
- **Server:** http://139.84.213.185:5173
- **Team Access:** http://139.84.213.185:5173

### Backend Services
- **API Gateway:** http://139.84.213.185:8000
- **API Documentation:** http://139.84.213.185:8000/docs
- **WebSocket:** ws://139.84.213.185:8080

### Database & Cache
- **PostgreSQL:** localhost:5432
- **Redis:** localhost:6379
- **NATS:** localhost:4222

### AI Services
- **Models Service:** http://139.84.213.185:8081
- **Voice Service:** http://139.84.213.185:8011
- **Translation Service:** http://139.84.213.185:8010

## Team Access

To allow team members to access your running instance:

1. **Find your local IP address:**
   ```bash
   # Linux/Mac
   hostname -I | awk '{print $1}'
   
   # Or use the script output
   ./start-mantrapath.sh
   ```

2. **Share the team access URLs:**
   - Frontend: `http://[YOUR_IP]:5173`
   - API: `http://[YOUR_IP]:8000`
   - WebSocket: `ws://[YOUR_IP]:8080`

3. **Ensure firewall allows connections:**
   ```bash
   # Ubuntu/Debian
   sudo ufw allow 5173
   sudo ufw allow 8000
   sudo ufw allow 8080
   ```

## Troubleshooting

### Services won't start
```bash
# Check logs
docker compose logs

# Restart specific service
docker compose restart [service-name]

# Rebuild and restart
docker compose up -d --build --force-recreate
```

### Port conflicts
If ports are already in use, edit the `.env` file and change the port numbers:
```bash
nano .env
# Change FRONTEND_PORT=5173 to FRONTEND_PORT=5174
# Change API_GATEWAY_PORT=8000 to API_GATEWAY_PORT=8001
```

### Database issues
```bash
# Reset database
docker compose down -v
docker compose up -d --build
```

### Frontend not loading
1. Check if frontend container is running: `docker compose ps`
2. Check frontend logs: `docker compose logs frontend`
3. Verify port mapping in `.env` file

## Development

### Making changes
- **Frontend changes:** The frontend will auto-reload in development mode
- **Backend changes:** Restart the specific service: `docker compose restart [service-name]`

### Adding new services
1. Add service definition to `docker-compose.yml`
2. Add port to `.env` file
3. Update startup script if needed

## Production Notes

- Change `JWT_SECRET_KEY` in `.env` for production
- Update `APP_URL` to your production domain
- Configure proper SMTP settings for email notifications
- Set `ENVIRONMENT=production` in `.env`

## Support

If you encounter issues:
1. Check the logs: `docker compose logs`
2. Verify all services are running: `docker compose ps`
3. Check port availability: `netstat -tulpn | grep :5173`
4. Contact the development team
