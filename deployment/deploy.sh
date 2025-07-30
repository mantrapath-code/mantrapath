#!/bin/bash

# MantraPath Production Deployment Script

set -e

echo "🚀 Starting MantraPath deployment..."

# Check if Docker and Docker Compose are installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p backend/monitoring/grafana/{dashboards,datasources}
mkdir -p backend/nginx/ssl
mkdir -p backend/logs

# Copy environment file
if [ ! -f "backend/.env" ]; then
    echo "📝 Copying environment configuration..."
    cp backend/.env.production backend/.env
    echo "⚠️  Please edit backend/.env with your actual configuration values"
    echo "   - Set OPENAI_API_KEY"
    echo "   - Update JWT_SECRET_KEY"
    echo "   - Configure email settings"
    echo "   - Set your domain in CORS_ORIGINS"
fi

# Create nginx configuration
echo "🌐 Setting up nginx configuration..."
cat > backend/nginx/nginx.conf << EOF
events {
    worker_connections 1024;
}

http {
    upstream frontend {
        server frontend:3000;
    }

    upstream api_gateway {
        server api-gateway:8000;
    }

    upstream notification_ws {
        server notification-service:8007;
    }

    server {
        listen 80;
        server_name localhost;

        # Security headers
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header X-Content-Type-Options "nosniff" always;

        # Frontend
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
        }

        # API routes
        location /api/ {
            proxy_pass http://api_gateway;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
        }

        # WebSocket for notifications
        location /ws/ {
            proxy_pass http://notification_ws;
            proxy_http_version 1.1;
            proxy_set_header Upgrade \$http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
            proxy_read_timeout 86400;
        }
    }
}
EOF

# Create monitoring configuration
echo "📊 Setting up monitoring..."
cat > backend/monitoring/prometheus.yml << EOF
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'mantrapath-services'
    static_configs:
      - targets: ['api-gateway:8000', 'auth-service:8001', 'mood-service:8003']
    metrics_path: /metrics
    scrape_interval: 30s
EOF

# Create Grafana datasource
cat > backend/monitoring/grafana/datasources/prometheus.yml << EOF
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
EOF

# Build and start services
echo "🔨 Building Docker images..."
cd backend

# Pull latest base images
docker-compose pull

# Build services
docker-compose build

# Start the infrastructure first
echo "🗄️  Starting databases..."
docker-compose up -d postgres redis mongodb influxdb

# Wait for databases to be ready
echo "⏳ Waiting for databases to be ready..."
sleep 30

# Start backend services
echo "🔧 Starting backend services..."
docker-compose up -d auth-service profile-service mood-service chatbot-service content-service community-service notification-service media-service

# Wait for backend services
echo "⏳ Waiting for backend services to be ready..."
sleep 20

# Start API gateway
echo "🚪 Starting API gateway..."
docker-compose up -d api-gateway

# Start frontend
echo "🖥️  Starting frontend..."
docker-compose up -d frontend

# Start nginx proxy
echo "🌐 Starting nginx proxy..."
docker-compose up -d nginx

# Start monitoring
echo "📊 Starting monitoring services..."
docker-compose up -d prometheus grafana

echo "✅ MantraPath deployment completed!"
echo ""
echo "🌐 Application URLs:"
echo "   Frontend: http://localhost"
echo "   API Gateway: http://localhost:8000"
echo "   Grafana Dashboard: http://localhost:3001 (admin/mantrapath123)"
echo "   Prometheus: http://localhost:9090"
echo ""
echo "📋 Service Status:"
docker-compose ps

echo ""
echo "📝 Next Steps:"
echo "1. Edit backend/.env with your actual configuration"
echo "2. Set up SSL certificates in backend/nginx/ssl/ for production"
echo "3. Configure your domain in nginx configuration"
echo "4. Set up backup strategy for databases"
echo "5. Configure monitoring alerts"
echo ""
echo "🔍 To view logs: docker-compose logs -f [service-name]"
echo "🛑 To stop all services: docker-compose down"
echo "🔄 To update services: ./scripts/update.sh"