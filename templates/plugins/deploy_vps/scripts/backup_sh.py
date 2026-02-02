"""
Backup script template.
Creates and manages backups.
"""


def generate_backup_sh() -> str:
    """Generate scripts/optional/backup.sh file content."""
    return '''#!/usr/bin/env bash

##############################################################################
# Backup Script
# Creates and manages backups
##############################################################################

set -e

# Get script directory and source utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEPLOY_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"

source "$DEPLOY_ROOT/scripts/common/common.sh"
source "$DEPLOY_ROOT/scripts/common/template-engine.sh"

# Help message
show_help() {
    echo "Usage: $0 <command> --env <environment>"
    echo ""
    echo "Commands:"
    echo "  full          Full backup (database, Redis, config)"
    echo "  db            Database only backup"
    echo "  restore       Restore from backup file"
    echo ""
    echo "Options:"
    echo "  --env         Environment (production|staging)"
    echo "  --help        Show this help message"
    echo ""
}

# Parse arguments
COMMAND=""
ENV=""
BACKUP_FILE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        full|db|restore)
            COMMAND="$1"
            shift
            ;;
        --env)
            ENV="$2"
            shift 2
            ;;
        --help|-h)
            show_help
            exit 0
            ;;
        *)
            if [[ "$COMMAND" == "restore" && -z "$BACKUP_FILE" ]]; then
                BACKUP_FILE="$1"
                shift
            else
                print_error "Unknown option: $1"
                show_help
                exit 1
            fi
            ;;
    esac
done

if [[ -z "$COMMAND" ]]; then
    print_error "Command is required"
    show_help
    exit 1
fi

if [[ -z "$ENV" ]]; then
    print_error "Environment is required"
    show_help
    exit 1
fi

# Load configuration
if ! load_config "$DEPLOY_ROOT"; then
    exit 1
fi

set_derived_variables "$ENV"

# Setup paths
BACKUP_DIR="$DEPLOY_ROOT/backups"
TIMESTAMP=$(get_timestamp)
BACKUP_NAME="${PROJECT_PREFIX}_${ENV}_${TIMESTAMP}"

mkdir -p "$BACKUP_DIR"

# Functions
do_full_backup() {
    print_header "Full Backup: $ENV"
    
    local backup_path="$BACKUP_DIR/$BACKUP_NAME"
    mkdir -p "$backup_path"
    
    # Database backup
    print_info "Backing up database..."
    do_db_backup_internal "$backup_path/database.sql"
    
    # Config backup
    print_info "Backing up configuration..."
    cp "$DEPLOY_ROOT/config.env" "$backup_path/" 2>/dev/null || true
    cp "$DEPLOY_ROOT/.env.$ENV" "$backup_path/" 2>/dev/null || true
    
    # Create archive
    print_info "Creating archive..."
    tar -czf "$BACKUP_DIR/$BACKUP_NAME.tar.gz" -C "$BACKUP_DIR" "$BACKUP_NAME"
    rm -rf "$backup_path"
    
    print_success "Backup created: $BACKUP_DIR/$BACKUP_NAME.tar.gz"
}

do_db_backup() {
    print_header "Database Backup: $ENV"
    do_db_backup_internal "$BACKUP_DIR/${BACKUP_NAME}_db.sql"
    print_success "Database backup: $BACKUP_DIR/${BACKUP_NAME}_db.sql"
}

do_db_backup_internal() {
    local output_file="$1"
    
    # Use docker to run pg_dump if database is containerized
    if [[ "$POSTGRES_HOST" == "postgres" ]]; then
        docker exec "${CONTAINER_PREFIX}_postgres" pg_dump \\
            -U "$POSTGRES_USER" -d "$POSTGRES_DB" > "$output_file"
    else
        # For external database
        PGPASSWORD="$POSTGRES_PASSWORD" pg_dump \\
            -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" \\
            -U "$POSTGRES_USER" -d "$POSTGRES_DB" > "$output_file"
    fi
}

do_restore() {
    if [[ -z "$BACKUP_FILE" ]]; then
        print_error "Backup file is required for restore"
        exit 1
    fi
    
    if [[ ! -f "$BACKUP_FILE" ]]; then
        print_error "Backup file not found: $BACKUP_FILE"
        exit 1
    fi
    
    print_header "Restore: $ENV"
    print_warning "This will overwrite existing data!"
    
    if ! confirm_action "Continue with restore?"; then
        print_info "Restore cancelled"
        exit 0
    fi
    
    # Extract archive
    local temp_dir=$(mktemp -d)
    tar -xzf "$BACKUP_FILE" -C "$temp_dir"
    
    # Find database file
    local db_file=$(find "$temp_dir" -name "*.sql" | head -1)
    if [[ -n "$db_file" ]]; then
        print_info "Restoring database..."
        if [[ "$POSTGRES_HOST" == "postgres" ]]; then
            docker exec -i "${CONTAINER_PREFIX}_postgres" psql \\
                -U "$POSTGRES_USER" -d "$POSTGRES_DB" < "$db_file"
        else
            PGPASSWORD="$POSTGRES_PASSWORD" psql \\
                -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" \\
                -U "$POSTGRES_USER" -d "$POSTGRES_DB" < "$db_file"
        fi
    fi
    
    # Cleanup
    rm -rf "$temp_dir"
    
    print_success "Restore complete"
}

# Execute command
case $COMMAND in
    full)
        do_full_backup
        ;;
    db)
        do_db_backup
        ;;
    restore)
        do_restore
        ;;
esac
'''
