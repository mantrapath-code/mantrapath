#!/bin/bash

# MantraPath Data Management Script
# Provides easy commands for data backup, restore, and cleanup

set -e

DATA_DIR="/home/sachin/mantrapath/data"
BACKUP_DIR="/home/sachin/mantrapath/backups"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
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

# Check if running as root for certain operations
check_root() {
    if [[ $EUID -eq 0 ]]; then
        log_warning "Running as root. Some operations may affect file permissions."
    fi
}

# Create backup directory
create_backup_dir() {
    if [[ ! -d "$BACKUP_DIR" ]]; then
        mkdir -p "$BACKUP_DIR"
        log_info "Created backup directory: $BACKUP_DIR"
    fi
}

# Backup all data
backup_data() {
    local backup_name="mantrapath-backup-$(date +%Y%m%d-%H%M%S)"
    local backup_path="$BACKUP_DIR/$backup_name.tar.gz"
    
    log_info "Creating backup: $backup_name"
    
    if [[ ! -d "$DATA_DIR" ]]; then
        log_error "Data directory not found: $DATA_DIR"
        exit 1
    fi
    
    create_backup_dir
    
    # Create backup
    tar -czf "$backup_path" -C "$(dirname "$DATA_DIR")" "$(basename "$DATA_DIR")"
    
    if [[ -f "$backup_path" ]]; then
        local size=$(du -h "$backup_path" | cut -f1)
        log_success "Backup created: $backup_path (Size: $size)"
    else
        log_error "Backup failed!"
        exit 1
    fi
}

# Restore data from backup
restore_data() {
    local backup_file="$1"
    
    if [[ -z "$backup_file" ]]; then
        log_error "Please provide backup file path"
        echo "Usage: $0 restore <backup-file.tar.gz>"
        exit 1
    fi
    
    if [[ ! -f "$backup_file" ]]; then
        log_error "Backup file not found: $backup_file"
        exit 1
    fi
    
    log_warning "This will replace all current data!"
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Restore cancelled"
        exit 0
    fi
    
    # Stop services
    log_info "Stopping services..."
    cd "$PROJECT_DIR/backend"
    docker-compose down || true
    
    # Backup current data
    if [[ -d "$DATA_DIR" ]]; then
        log_info "Backing up current data..."
        backup_data
    fi
    
    # Remove current data
    log_info "Removing current data..."
    sudo rm -rf "$DATA_DIR"
    
    # Restore from backup
    log_info "Restoring from backup..."
    tar -xzf "$backup_file" -C "$(dirname "$DATA_DIR")"
    
    # Fix permissions
    log_info "Fixing permissions..."
    sudo chown -R 999:999 "$DATA_DIR/postgres" 2>/dev/null || true
    sudo chown -R 1001:1001 "$DATA_DIR/redis" 2>/dev/null || true
    
    log_success "Data restored successfully!"
    log_info "You can now start services with: docker-compose up -d"
}

# Clean data (reset application)
clean_data() {
    log_warning "This will delete ALL data and reset the application!"
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Clean cancelled"
        exit 0
    fi
    
    # Stop services
    log_info "Stopping services..."
    cd "$PROJECT_DIR/backend"
    docker-compose down || true
    
    # Remove data
    log_info "Removing all data..."
    sudo rm -rf "$DATA_DIR"/*
    
    # Recreate directories
    mkdir -p "$DATA_DIR"/{postgres,redis,nats,ai-models,voice-models,voice-audio,models-data,models-cache}
    
    log_success "Data cleaned! Fresh data will be created on next startup."
}

# Clean cache only
clean_cache() {
    log_info "Cleaning cache data (keeping user data)..."
    
    # Stop services
    cd "$PROJECT_DIR/backend"
    docker-compose down || true
    
    # Clean cache directories
    rm -rf "$DATA_DIR"/redis/*
    rm -rf "$DATA_DIR"/nats/*
    rm -rf "$DATA_DIR"/ai-models/*
    rm -rf "$DATA_DIR"/models-cache/*
    
    log_success "Cache cleaned!"
    log_info "Starting services..."
    docker-compose up -d
}

# Show data status
show_status() {
    log_info "MantraPath Data Status"
    echo "======================"
    
    if [[ ! -d "$DATA_DIR" ]]; then
        log_error "Data directory not found: $DATA_DIR"
        exit 1
    fi
    
    echo "Data Directory: $DATA_DIR"
    echo "Backup Directory: $BACKUP_DIR"
    echo ""
    
    # Show directory sizes
    echo "Directory Sizes:"
    du -sh "$DATA_DIR"/* 2>/dev/null | while read size dir; do
        echo "  $size $(basename "$dir")"
    done
    
    echo ""
    
    # Show disk usage
    echo "Disk Usage:"
    df -h "$DATA_DIR" | tail -1 | awk '{print "  " $5 " used (" $3 " of " $2 ")"}'
    
    echo ""
    
    # Show recent backups
    if [[ -d "$BACKUP_DIR" ]]; then
        echo "Recent Backups:"
        ls -lt "$BACKUP_DIR"/*.tar.gz 2>/dev/null | head -5 | while read line; do
            echo "  $line"
        done
    fi
}

# List available backups
list_backups() {
    if [[ ! -d "$BACKUP_DIR" ]]; then
        log_info "No backup directory found"
        exit 0
    fi
    
    log_info "Available Backups:"
    ls -lt "$BACKUP_DIR"/*.tar.gz 2>/dev/null | while read line; do
        echo "  $line"
    done
}

# Show help
show_help() {
    echo "MantraPath Data Management Script"
    echo "================================="
    echo ""
    echo "Usage: $0 <command> [options]"
    echo ""
    echo "Commands:"
    echo "  backup                    Create a backup of all data"
    echo "  restore <backup-file>     Restore data from backup"
    echo "  clean                     Clean all data (reset application)"
    echo "  clean-cache               Clean cache data only (keep user data)"
    echo "  status                    Show data status and disk usage"
    echo "  list-backups              List available backups"
    echo "  help                      Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 backup"
    echo "  $0 restore /home/sachin/mantrapath/backups/mantrapath-backup-20241023.tar.gz"
    echo "  $0 clean-cache"
    echo "  $0 status"
}

# Main script logic
main() {
    check_root
    
    case "${1:-help}" in
        backup)
            backup_data
            ;;
        restore)
            restore_data "$2"
            ;;
        clean)
            clean_data
            ;;
        clean-cache)
            clean_cache
            ;;
        status)
            show_status
            ;;
        list-backups)
            list_backups
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            log_error "Unknown command: $1"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"

