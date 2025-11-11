# Multi-stage build for React frontend
FROM node:20-alpine as builder

# Install build tools for better ARM64 compatibility
RUN apk add --no-cache python3 make g++ libc6-compat

WORKDIR /app

# Copy package files
COPY package*.json ./

# Configure npm for better compatibility and performance
RUN npm config set cache /tmp/.npm && \
    npm config set prefer-offline true

# Install dependencies with retry logic and better ARM64 support
# Use npm ci when a lockfile is present; otherwise fall back to npm install
RUN timeout 1800 sh -c 'if [ -f package-lock.json ]; then \
        npm ci --no-audit --no-fund --ignore-scripts; \
    else \
        npm install --no-audit --no-fund --ignore-scripts; \
    fi' && \
    npm run prepare || true

# Copy source code
COPY . .

# Build the application with memory optimization
ENV NODE_OPTIONS="--max-old-space-size=4096"
RUN npm run build

# Production stage
FROM nginx:alpine

# Install openssl for certificate generation
RUN apk add --no-cache openssl

# Copy built files to nginx
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Create entrypoint script to generate SSL certs if not provided via volume
RUN echo '#!/bin/sh' > /docker-entrypoint.sh && \
    echo 'set -e' >> /docker-entrypoint.sh && \
    echo '' >> /docker-entrypoint.sh && \
    echo '# Check if SSL certificates are provided via volume mount' >> /docker-entrypoint.sh && \
    echo 'if [ -f /etc/nginx/ssl/mantrapath.crt ] && [ -f /etc/nginx/ssl/mantrapath.key ]; then' >> /docker-entrypoint.sh && \
    echo '    echo "Using mounted SSL certificates (mantrapath.crt/key)"' >> /docker-entrypoint.sh && \
    echo 'elif [ ! -f /etc/nginx/ssl/cert.pem ] || [ ! -f /etc/nginx/ssl/key.pem ]; then' >> /docker-entrypoint.sh && \
    echo '    echo "Generating self-signed SSL certificate..."' >> /docker-entrypoint.sh && \
    echo '    mkdir -p /etc/nginx/ssl' >> /docker-entrypoint.sh && \
    echo '    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \' >> /docker-entrypoint.sh && \
    echo '        -keyout /etc/nginx/ssl/key.pem \' >> /docker-entrypoint.sh && \
    echo '        -out /etc/nginx/ssl/cert.pem \' >> /docker-entrypoint.sh && \
    echo '        -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"' >> /docker-entrypoint.sh && \
    echo '    echo "SSL certificate generated successfully"' >> /docker-entrypoint.sh && \
    echo 'else' >> /docker-entrypoint.sh && \
    echo '    echo "Using existing SSL certificates"' >> /docker-entrypoint.sh && \
    echo 'fi' >> /docker-entrypoint.sh && \
    echo '' >> /docker-entrypoint.sh && \
    echo '# Start nginx' >> /docker-entrypoint.sh && \
    echo 'exec nginx -g "daemon off;"' >> /docker-entrypoint.sh && \
    chmod +x /docker-entrypoint.sh

# Expose ports
EXPOSE 80 443

# Use custom entrypoint
ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["nginx", "-g", "daemon off;"]
