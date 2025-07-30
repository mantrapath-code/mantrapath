#!/bin/bash

# Docker Compose Services Validation Script
echo "=== MantraPath Backend Services Validation ==="
echo ""

# Check if docker and docker-compose are available
echo "1. Checking Docker installation..."
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed"
    exit 1
else
    echo "✅ Docker is available"
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed"
    exit 1
else
    echo "✅ Docker Compose is available"
fi

echo ""
echo "2. Validating docker-compose.yml syntax..."
if docker-compose config > /dev/null 2>&1; then
    echo "✅ Docker Compose configuration is valid"
else
    echo "❌ Docker Compose configuration has errors"
    docker-compose config
    exit 1
fi

echo ""
echo "3. Checking service directories and Dockerfiles..."

# List of all services
services=("api_gateway" "auth_service" "profile_service" "mood_service" "chatbot_service" "content_service" "community_service" "notification_service" "media_service")

for service in "${services[@]}"; do
    service_dir="./services/$service"
    dockerfile="$service_dir/Dockerfile"
    requirements="$service_dir/requirements.txt"
    main_file="$service_dir/main.py"
    
    echo "Checking $service:"
    
    if [ -d "$service_dir" ]; then
        echo "  ✅ Service directory exists"
    else
        echo "  ❌ Service directory missing"
        continue
    fi
    
    if [ -f "$dockerfile" ]; then
        echo "  ✅ Dockerfile exists"
    else
        echo "  ❌ Dockerfile missing"
    fi
    
    if [ -f "$requirements" ]; then
        echo "  ✅ requirements.txt exists"
    else
        echo "  ❌ requirements.txt missing"
    fi
    
    if [ -f "$main_file" ]; then
        echo "  ✅ main.py exists"
    else
        echo "  ❌ main.py missing"
    fi
    
    echo ""
done

echo "4. Checking shared directory..."
if [ -d "./shared" ]; then
    echo "✅ Shared directory exists"
else
    echo "❌ Shared directory missing"
fi

echo ""
echo "5. Checking database initialization..."
if [ -f "./database/init.sql" ]; then
    echo "✅ Database init.sql exists"
else
    echo "❌ Database init.sql missing"
fi

echo ""
echo "6. Service port allocation:"
echo "  - API Gateway:     8000"
echo "  - Auth Service:    8001"
echo "  - Profile Service: 8002"
echo "  - Mood Service:    8003"
echo "  - Chatbot Service: 8004"
echo "  - Content Service: 8005"
echo "  - Community Service: 8006"
echo "  - Notification Service: 8007"
echo "  - Media Service:   8008"
echo "  - PostgreSQL:      5432"
echo "  - Redis:           6379"

echo ""
echo "=== Validation Complete ==="
echo ""
echo "To build and start all services:"
echo "  docker-compose up --build"
echo ""
echo "To start specific services:"
echo "  docker-compose up --build api-gateway auth-service"
echo ""
echo "To view logs:"
echo "  docker-compose logs -f [service-name]"
echo ""
echo "To stop all services:"
echo "  docker-compose down"
