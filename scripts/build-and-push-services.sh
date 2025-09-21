#!/bin/bash

# MantraPath Services - Automated Build and Push Script
# This script builds and pushes Docker images for all services to Vultr Container Registry

set -e  # Exit on any error

# Configuration
REGISTRY_URL="${VULTR_REGISTRY:-blr.vultrcr.com/mantrapath}"
REGISTRY_USERNAME="${VULTR_REGISTRY_USERNAME:-}"
REGISTRY_PASSWORD="${VULTR_REGISTRY_PASSWORD:-}"
SERVICES_DIR="/home/sachin/mantrapath/backend/services"
PROJECT_PREFIX="mantrapath"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check if Docker is installed and running
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed or not in PATH"
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        log_error "Docker daemon is not running"
        exit 1
    fi
    
    # Check if services directory exists
    if [ ! -d "$SERVICES_DIR" ]; then
        log_error "Services directory not found: $SERVICES_DIR"
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

# Function to login to registry
login_to_registry() {
    log_info "Logging into Vultr Container Registry..."
    
    if echo "$REGISTRY_PASSWORD" | docker login "$REGISTRY_URL" --username "$REGISTRY_USERNAME" --password-stdin; then
        # Re-login with https scheme to be explicit
        echo "$REGISTRY_PASSWORD" | docker login "https://$REGISTRY_URL" --username "$REGISTRY_USERNAME" --password-stdin
        log_success "Successfully logged into registry"
    else
        log_error "Failed to login to registry"
        exit 1
    fi
}

# Function to get commit SHA (if in git repo)
get_commit_sha() {
    if git rev-parse --git-dir > /dev/null 2>&1; then
        git rev-parse --short HEAD
    else
        date +%Y%m%d-%H%M%S
    fi
}

# Function to build and push a single service
build_and_push_service() {
    local service_name=$1
    local service_path=$2
    local dockerfile_path="$service_path/Dockerfile"
    
    log_info "Processing service: $service_name"
    
    # Check if Dockerfile exists
    if [ ! -f "$dockerfile_path" ]; then
        log_warning "Dockerfile not found for $service_name, skipping..."
        return 1
    fi
    
    # Generate image names
    local image_name="$PROJECT_PREFIX-$service_name"
    local temp_tag="temp-$image_name:latest"
    local latest_tag="$REGISTRY_URL/$image_name:latest"
    local commit_sha=$(get_commit_sha)
    local sha_tag="$REGISTRY_URL/$image_name:$commit_sha"
    
    log_info "Building image for $service_name..."
    
    # Build the image from backend directory (correct context)
    local backend_dir="$(dirname "$SERVICES_DIR")"
    if docker build -f "$dockerfile_path" -t "$temp_tag" "$backend_dir"; then
        log_success "Successfully built $service_name"
    else
        log_error "Failed to build $service_name"
        return 1
    fi
    
    # Tag the image
    log_info "Tagging image for $service_name..."
    docker tag "$temp_tag" "$latest_tag"
    docker tag "$temp_tag" "$sha_tag"
    
    # Push the images
    log_info "Pushing images for $service_name..."
    
    if docker push "$latest_tag"; then
        log_success "Successfully pushed $latest_tag"
    else
        log_error "Failed to push $latest_tag"
        return 1
    fi
    
    if docker push "$sha_tag"; then
        log_success "Successfully pushed $sha_tag"
    else
        log_error "Failed to push $sha_tag"
        return 1
    fi
    
    # Clean up temporary image
    docker rmi "$temp_tag" > /dev/null 2>&1 || true
    
    log_success "Completed processing $service_name"
    return 0
}

# Function to get all services with Dockerfiles
get_services_with_dockerfiles() {
    local services=()
    
    # Find all directories with Dockerfiles
    while IFS= read -r -d '' dockerfile; do
        local service_dir=$(dirname "$dockerfile")
        local service_name=$(basename "$service_dir")
        services+=("$service_name:$service_dir")
    done < <(find "$SERVICES_DIR" -name "Dockerfile" -type f -print0)
    
    printf '%s\n' "${services[@]}"
}

# Function to display service summary
display_service_summary() {
    log_info "Found services with Dockerfiles:"
    local services=($(get_services_with_dockerfiles))
    
    for service_info in "${services[@]}"; do
        local service_name="${service_info%%:*}"
        echo "  - $service_name"
    done
    
    echo ""
    log_info "Total services to build: ${#services[@]}"
}

# Function to build all services
build_all_services() {
    local services=($(get_services_with_dockerfiles))
    local successful_builds=0
    local failed_builds=0
    local failed_services=()
    
    log_info "Starting build process for all services..."
    echo "========================================"
    
    for service_info in "${services[@]}"; do
        local service_name="${service_info%%:*}"
        local service_path="${service_info##*:}"
        
        echo ""
        log_info "Building service $((successful_builds + failed_builds + 1))/${#services[@]}: $service_name"
        echo "----------------------------------------"
        
        if build_and_push_service "$service_name" "$service_path"; then
            ((successful_builds++))
        else
            ((failed_builds++))
            failed_services+=("$service_name")
        fi
    done
    
    # Display summary
    echo ""
    echo "========================================"
    log_info "Build Summary:"
    log_success "Successful builds: $successful_builds"
    
    if [ $failed_builds -gt 0 ]; then
        log_error "Failed builds: $failed_builds"
        log_error "Failed services:"
        for failed_service in "${failed_services[@]}"; do
            echo "  - $failed_service"
        done
    fi
    
    echo ""
    if [ $failed_builds -eq 0 ]; then
        log_success "All services built and pushed successfully!"
        return 0
    else
        log_error "Some services failed to build. Check the logs above for details."
        return 1
    fi
}

# Function to build specific services
build_specific_services() {
    local service_names=("$@")
    local successful_builds=0
    local failed_builds=0
    local failed_services=()
    
    log_info "Building specific services: ${service_names[*]}"
    echo "========================================"
    
    for service_name in "${service_names[@]}"; do
        local service_path="$SERVICES_DIR/$service_name"
        
        if [ ! -d "$service_path" ]; then
            log_error "Service directory not found: $service_path"
            ((failed_builds++))
            failed_services+=("$service_name")
            continue
        fi
        
        echo ""
        log_info "Building service: $service_name"
        echo "----------------------------------------"
        
        if build_and_push_service "$service_name" "$service_path"; then
            ((successful_builds++))
        else
            ((failed_builds++))
            failed_services+=("$service_name")
        fi
    done
    
    # Display summary
    echo ""
    echo "========================================"
    log_info "Build Summary:"
    log_success "Successful builds: $successful_builds"
    
    if [ $failed_builds -gt 0 ]; then
        log_error "Failed builds: $failed_builds"
        log_error "Failed services:"
        for failed_service in "${failed_services[@]}"; do
            echo "  - $failed_service"
        done
    fi
    
    echo ""
    if [ $failed_builds -eq 0 ]; then
        log_success "All specified services built and pushed successfully!"
        return 0
    else
        log_error "Some services failed to build. Check the logs above for details."
        return 1
    fi
}

# Function to display help
show_help() {
    echo "MantraPath Services - Automated Build and Push Script"
    echo ""
    echo "Usage:"
    echo "  $0 [OPTIONS] [SERVICE_NAMES...]"
    echo ""
    echo "Options:"
    echo "  -h, --help     Show this help message"
    echo "  -l, --list     List all available services"
    echo "  -a, --all      Build all services (default if no services specified)"
    echo "  -c, --check    Check prerequisites only"
    echo ""
    echo "Examples:"
    echo "  $0                           # Build all services"
    echo "  $0 --all                     # Build all services"
    echo "  $0 models_service api_gateway # Build specific services"
    echo "  $0 --list                    # List all available services"
    echo "  $0 --check                   # Check prerequisites only"
    echo ""
    echo "Registry: $REGISTRY_URL"
}

# Main function
main() {
    local build_all=false
    local check_only=false
    local list_only=false
    local specific_services=()
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -l|--list)
                list_only=true
                shift
                ;;
            -a|--all)
                build_all=true
                shift
                ;;
            -c|--check)
                check_only=true
                shift
                ;;
            -*)
                log_error "Unknown option: $1"
                show_help
                exit 1
                ;;
            *)
                specific_services+=("$1")
                shift
                ;;
        esac
    done
    
    # Show header
    echo "========================================"
    echo "MantraPath Services Build & Push Script"
    echo "========================================"
    echo "Registry: $REGISTRY_URL"
    echo "Services Directory: $SERVICES_DIR"
    echo ""
    
    # Check prerequisites
    check_prerequisites
    
    if [ "$check_only" = true ]; then
        log_success "Prerequisites check completed successfully"
        exit 0
    fi
    
    if [ "$list_only" = true ]; then
        display_service_summary
        exit 0
    fi
    
    # Login to registry
    login_to_registry
    
    # Determine what to build
    if [ ${#specific_services[@]} -gt 0 ]; then
        build_specific_services "${specific_services[@]}"
    else
        display_service_summary
        echo ""
        read -p "Do you want to continue building all services? (y/N): " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            build_all_services
        else
            log_info "Build cancelled by user"
            exit 0
        fi
    fi
}

# Run main function with all arguments
main "$@"
