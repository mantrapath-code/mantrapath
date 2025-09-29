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

# Copy built files to nginx
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Expose port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
