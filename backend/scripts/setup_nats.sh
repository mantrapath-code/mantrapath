#!/bin/bash
# NATS Server Setup Script for BK-004 Development and Testing
# This script sets up NATS server with JetStream enabled for MantraPath

set -e

echo "🚀 Setting up NATS Server with JetStream for BK-004"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if NATS server is already installed
check_nats_installation() {
    if command -v nats-server &> /dev/null; then
        print_status "NATS server is already installed"
        nats-server --version
        return 0
    else
        print_warning "NATS server not found"
        return 1
    fi
}

# Install NATS server
install_nats() {
    print_info "Installing NATS server..."
    
    # Detect OS
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            brew install nats-server
            print_status "NATS server installed via Homebrew"
        else
            print_error "Homebrew not found. Please install Homebrew first or install NATS manually"
            exit 1
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        print_info "Downloading NATS server for Linux..."
        wget https://github.com/nats-io/nats-server/releases/download/v2.10.4/nats-server-v2.10.4-linux-amd64.zip
        unzip nats-server-v2.10.4-linux-amd64.zip
        sudo mv nats-server-v2.10.4-linux-amd64/nats-server /usr/local/bin/
        rm -rf nats-server-v2.10.4-linux-amd64*
        print_status "NATS server installed"
    else
        print_error "Unsupported OS. Please install NATS server manually from https://nats.io/download/"
        exit 1
    fi
}

# Create NATS configuration file
create_nats_config() {
    print_info "Creating NATS configuration file..."
    
    CONFIG_DIR="$(dirname "$0")/../config"
    mkdir -p "$CONFIG_DIR"
    
    cat > "$CONFIG_DIR/nats-server.conf" << 'EOF'
# NATS Server Configuration for MantraPath BK-004
# Optimized for development and testing with production-ready settings

# Server settings
server_name: mantrapath-nats
host: 127.0.0.1
port: 4222

# HTTP monitoring
http_port: 8222

# Logging
log_file: "./logs/nats-server.log"
logtime: true
debug: false
trace: false

# JetStream Configuration
jetstream {
    # Store directory
    store_dir: "./data/jetstream"
    
    # Memory and storage limits
    max_memory_store: 1GB
    max_file_store: 10GB
    
    # Domain (optional)
    # domain: "mantrapath"
}

# Limits
max_connections: 1000
max_control_line: 4KB
max_payload: 1MB
max_pending: 64MB
max_subscriptions: 0

# Authentication (disable for development)
# accounts {
#     DEV: {
#         users: [
#             {user: "mantrapath", password: "dev-password"}
#         ]
#     }
# }

# TLS (disable for development)
# tls {
#     cert_file: "./certs/server-cert.pem"
#     key_file: "./certs/server-key.pem"
#     ca_file: "./certs/ca.pem"
#     verify: true
# }

# Clustering (for production)
# cluster {
#     name: mantrapath
#     host: 127.0.0.1
#     port: 6222
#     routes: [
#         nats://127.0.0.1:6222
#     ]
# }
EOF

    print_status "NATS configuration created: $CONFIG_DIR/nats-server.conf"
}

# Create directories for NATS
create_directories() {
    print_info "Creating necessary directories..."
    
    BASE_DIR="$(dirname "$0")/.."
    mkdir -p "$BASE_DIR/logs"
    mkdir -p "$BASE_DIR/data/jetstream"
    
    print_status "Directories created"
}

# Start NATS server
start_nats_server() {
    print_info "Starting NATS server with JetStream..."
    
    CONFIG_FILE="$(dirname "$0")/../config/nats-server.conf"
    
    if [[ -f "$CONFIG_FILE" ]]; then
        print_info "Using configuration file: $CONFIG_FILE"
        nats-server -c "$CONFIG_FILE" &
    else
        print_info "Using command line options"
        nats-server --jetstream --http_port 8222 &
    fi
    
    NATS_PID=$!
    sleep 3
    
    # Check if NATS started successfully
    if kill -0 $NATS_PID 2>/dev/null; then
        print_status "NATS server started successfully (PID: $NATS_PID)"
        echo $NATS_PID > "$(dirname "$0")/../nats-server.pid"
    else
        print_error "Failed to start NATS server"
        exit 1
    fi
}

# Verify NATS and JetStream
verify_setup() {
    print_info "Verifying NATS and JetStream setup..."
    
    # Wait for server to be ready
    sleep 2
    
    # Check NATS connectivity
    if curl -s http://127.0.0.1:8222/healthz > /dev/null; then
        print_status "NATS server is responding"
    else
        print_error "NATS server is not responding"
        return 1
    fi
    
    # Check JetStream
    if curl -s http://127.0.0.1:8222/jsz | grep -q '"config"'; then
        print_status "JetStream is enabled and responding"
    else
        print_warning "JetStream status unclear - check manually"
    fi
    
    # Show server info
    print_info "NATS Server Information:"
    curl -s http://127.0.0.1:8222/varz | python3 -m json.tool | head -20
}

# Create test streams for BK-004
create_test_streams() {
    print_info "Creating test streams for BK-004..."
    
    # Install NATS CLI if not present
    if ! command -v nats &> /dev/null; then
        print_info "Installing NATS CLI..."
        if [[ "$OSTYPE" == "darwin"* ]]; then
            brew install nats-io/nats-tools/nats
        else
            print_warning "Please install NATS CLI manually for stream management"
            return 0
        fi
    fi
    
    # Create streams
    STREAMS=(
        "mantrapath-voice:voice.*"
        "mantrapath-ai:ai.*,intelligence.*"
        "mantrapath-mood:mood.*"
        "mantrapath-journal:journal.*"
        "mantrapath-cultural:cultural.*,regional.*"
    )
    
    for stream_def in "${STREAMS[@]}"; do
        IFS=':' read -r stream_name subjects <<< "$stream_def"
        
        print_info "Creating stream: $stream_name"
        nats stream add "$stream_name" \
            --subjects="$subjects" \
            --storage=file \
            --retention=limits \
            --max-msgs=1000000 \
            --max-age=168h \
            --max-msg-size=1MB \
            --discard=old \
            --replicas=1 \
            --no-ack \
            || print_warning "Stream $stream_name might already exist"
    done
    
    print_status "Test streams created"
}

# Stop existing NATS server
stop_existing_nats() {
    print_info "Checking for existing NATS processes..."
    
    # Check for PID file
    PID_FILE="$(dirname "$0")/../nats-server.pid"
    if [[ -f "$PID_FILE" ]]; then
        PID=$(cat "$PID_FILE")
        if kill -0 $PID 2>/dev/null; then
            print_info "Stopping existing NATS server (PID: $PID)"
            kill $PID
            sleep 2
        fi
        rm -f "$PID_FILE"
    fi
    
    # Kill any remaining NATS processes
    pkill -f nats-server || true
    sleep 1
}

# Main setup function
main() {
    echo
    print_info "Starting NATS setup for BK-004..."
    
    # Stop any existing NATS
    stop_existing_nats
    
    # Check installation
    if ! check_nats_installation; then
        install_nats
    fi
    
    # Create configuration and directories
    create_nats_config
    create_directories
    
    # Start server
    start_nats_server
    
    # Verify setup
    verify_setup
    
    # Create test streams
    create_test_streams
    
    echo
    print_status "NATS setup complete!"
    echo
    print_info "NATS Server Details:"
    echo "   📡 Server: nats://127.0.0.1:4222"
    echo "   🌐 Monitoring: http://127.0.0.1:8222"
    echo "   💾 JetStream: Enabled"
    echo "   📁 Data Directory: ./data/jetstream"
    echo "   📄 Config File: ./config/nats-server.conf"
    echo
    print_info "To stop NATS server:"
    echo "   kill \$(cat nats-server.pid)"
    echo
    print_info "To test BK-004:"
    echo "   python3 scripts/comprehensive_bk004_test.py"
    echo
}

# Handle script arguments
case "${1:-}" in
    "stop")
        print_info "Stopping NATS server..."
        stop_existing_nats
        print_status "NATS server stopped"
        ;;
    "restart")
        print_info "Restarting NATS server..."
        stop_existing_nats
        main
        ;;
    "status")
        print_info "Checking NATS status..."
        if curl -s http://127.0.0.1:8222/healthz > /dev/null; then
            print_status "NATS server is running"
            curl -s http://127.0.0.1:8222/varz | python3 -c "
import json, sys
data = json.load(sys.stdin)
print(f'Version: {data.get(\"version\", \"unknown\")}')
print(f'Uptime: {data.get(\"uptime\", \"unknown\")}')
print(f'Connections: {data.get(\"connections\", 0)}')
print(f'JetStream: {\"enabled\" if data.get(\"jetstream\") else \"disabled\"}')
"
        else
            print_error "NATS server is not running"
        fi
        ;;
    "help"|"-h"|"--help")
        echo "NATS Setup Script for BK-004"
        echo "Usage: $0 [command]"
        echo
        echo "Commands:"
        echo "  (none)    - Install and start NATS with JetStream"
        echo "  stop      - Stop NATS server"
        echo "  restart   - Restart NATS server"
        echo "  status    - Check NATS server status"
        echo "  help      - Show this help message"
        ;;
    *)
        main
        ;;
esac
