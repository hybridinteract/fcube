"""
Deploy script template.
Manages Docker Compose deployments.
"""


def generate_deploy_sh() -> str:
    """Generate scripts/deploy.sh file content."""
    return '''#!/usr/bin/env bash

##############################################################################
# Deployment Script
# Manages Docker Compose deployments
##############################################################################

set -e

# Get script directory and source utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEPLOY_ROOT="$(dirname "$SCRIPT_DIR")"

source "$SCRIPT_DIR/common/common.sh"
source "$SCRIPT_DIR/common/validation.sh"
source "$SCRIPT_DIR/common/template-engine.sh"

# Help message
show_help() {
    echo "Usage: $0 <command> --env <environment>"
    echo ""
    echo "Commands:"
    echo "  init          Initial deployment (first time)"
    echo "  update        Update deployment (pull, rebuild, restart)"
    echo "  restart       Restart all services"
    echo "  stop          Stop all services"
    echo "  status        Show service status"
    echo "  logs          View logs (live tail)"
    echo ""
    echo "Options:"
    echo "  --env         Environment (production|staging)"
    echo "  --help        Show this help message"
    echo ""
}

# Parse arguments
COMMAND=""
ENV=""
while [[ $# -gt 0 ]]; do
    case $1 in
        init|update|restart|stop|status|logs)
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
            print_error "Unknown option: $1"
            show_help
            exit 1
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
COMPOSE_FILE="$DEPLOY_ROOT/generated/docker-compose.$ENV.yml"
ENV_FILE="$DEPLOY_ROOT/.env.$ENV"
COMPOSE_CMD=$(get_docker_compose_cmd)

# Verify files exist
if [[ ! -f "$COMPOSE_FILE" ]]; then
    print_error "Compose file not found: $COMPOSE_FILE"
    print_info "Run './scripts/setup.sh' first"
    exit 1
fi

if [[ ! -f "$ENV_FILE" ]]; then
    print_error "Environment file not found: $ENV_FILE"
    print_info "Run './scripts/setup.sh' first"
    exit 1
fi

# Functions
do_init() {
    print_header "Initial Deployment: $ENV"
    
    # Validate prerequisites
    check_docker
    check_docker_compose
    
    # Generate Redis password config
    print_info "Generating Redis password configuration..."
    mkdir -p "$DEPLOY_ROOT/generated/redis"
    echo "requirepass $REDIS_PASSWORD" > "$DEPLOY_ROOT/generated/redis/redis-password.conf"
    
    # Build and start services
    print_info "Building and starting services..."
    $COMPOSE_CMD -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d --build
    
    print_success "Services started successfully"
    do_status
}

do_update() {
    print_header "Updating Deployment: $ENV"
    
    # Pull latest code
    print_info "Pulling latest code..."
    cd "$DEPLOY_ROOT/.."
    git pull origin main || git pull origin master || true
    
    # Rebuild and restart
    print_info "Rebuilding containers..."
    $COMPOSE_CMD -f "$COMPOSE_FILE" --env-file "$ENV_FILE" build
    
    print_info "Restarting services..."
    $COMPOSE_CMD -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d
    
    print_success "Update complete"
    do_status
}

do_restart() {
    print_header "Restarting Services: $ENV"
    $COMPOSE_CMD -f "$COMPOSE_FILE" --env-file "$ENV_FILE" restart
    print_success "Services restarted"
    do_status
}

do_stop() {
    print_header "Stopping Services: $ENV"
    $COMPOSE_CMD -f "$COMPOSE_FILE" --env-file "$ENV_FILE" down
    print_success "Services stopped"
}

do_status() {
    print_header "Service Status: $ENV"
    $COMPOSE_CMD -f "$COMPOSE_FILE" --env-file "$ENV_FILE" ps
}

do_logs() {
    print_header "Logs: $ENV (Ctrl+C to exit)"
    $COMPOSE_CMD -f "$COMPOSE_FILE" --env-file "$ENV_FILE" logs -f
}

# Execute command
case $COMMAND in
    init)
        do_init
        ;;
    update)
        do_update
        ;;
    restart)
        do_restart
        ;;
    stop)
        do_stop
        ;;
    status)
        do_status
        ;;
    logs)
        do_logs
        ;;
esac
'''
