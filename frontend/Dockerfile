# Multi-stage build for React frontend
FROM node:18-alpine as builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies (include dev dependencies for build tools like tsc and vite)
# Use npm ci when a lockfile is present; otherwise fall back to npm install
RUN if [ -f package-lock.json ]; then \
			npm ci --no-audit --no-fund; \
		else \
			npm install --no-audit --no-fund; \
		fi

# Copy source code
COPY . .

# Build the application
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
