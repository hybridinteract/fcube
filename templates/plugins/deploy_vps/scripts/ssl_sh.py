"""
SSL script template.
Manages Let's Encrypt SSL certificates.
"""


def generate_ssl_sh() -> str:
    """Generate scripts/ssl.sh file content."""
    return '''#!/usr/bin/env bash

##############################################################################
# SSL Certificate Management Script
# Manages Let's Encrypt SSL certificates
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
    echo "Usage: $0 <command> --env <environment> [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  setup         Request new SSL certificates"
    echo "  renew         Force certificate renewal"
    echo "  check         Check certificate expiry"
    echo "  test          Test SSL configuration"
    echo ""
    echo "Options:"
    echo "  --env         Environment (production|staging)"
    echo "  --staging     Use Let's Encrypt staging server (for testing)"
    echo "  --help        Show this help message"
    echo ""
}

# Parse arguments
COMMAND=""
ENV=""
USE_STAGING=""

while [[ $# -gt 0 ]]; do
    case $1 in
        setup|renew|check|test)
            COMMAND="$1"
            shift
            ;;
        --env)
            ENV="$2"
            shift 2
            ;;
        --staging)
            USE_STAGING="--staging"
            shift
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

# Paths
COMPOSE_FILE="$DEPLOY_ROOT/generated/docker-compose.$ENV.yml"
ENV_FILE="$DEPLOY_ROOT/.env.$ENV"
CERTBOT_DIR="$DEPLOY_ROOT/certbot"
COMPOSE_CMD=$(get_docker_compose_cmd)

# Functions
do_setup() {
    print_header "SSL Certificate Setup: $ENV"
    
    # Check DNS first
    print_info "Checking DNS resolution..."
    if ! check_dns "$API_DOMAIN"; then
        print_error "DNS must resolve before requesting certificates"
        exit 1
    fi
    
    if ! check_dns "$FLOWER_DOMAIN"; then
        print_error "DNS must resolve before requesting certificates"
        exit 1
    fi
    
    # Create certbot directories
    mkdir -p "$CERTBOT_DIR/conf" "$CERTBOT_DIR/www"
    
    # Request certificates
    print_info "Requesting SSL certificates..."
    
    docker run --rm \\
        -v "$CERTBOT_DIR/conf:/etc/letsencrypt" \\
        -v "$CERTBOT_DIR/www:/var/www/certbot" \\
        certbot/certbot:v5.1.0 certonly \\
        --webroot --webroot-path=/var/www/certbot \\
        --email "$ACME_EMAIL" \\
        --agree-tos --no-eff-email \\
        $USE_STAGING \\
        -d "$API_DOMAIN" \\
        -d "$FLOWER_DOMAIN"
    
    if [[ $? -eq 0 ]]; then
        print_success "SSL certificates obtained successfully"
        
        # Reload nginx
        print_info "Reloading nginx..."
        $COMPOSE_CMD -f "$COMPOSE_FILE" --env-file "$ENV_FILE" exec -T nginx nginx -s reload || true
        
        print_success "SSL setup complete!"
        print_info "Your API is now available at: https://$API_DOMAIN"
        print_info "Flower dashboard at: https://$FLOWER_DOMAIN"
    else
        print_error "Failed to obtain SSL certificates"
        exit 1
    fi
}

do_renew() {
    print_header "SSL Certificate Renewal: $ENV"
    
    docker run --rm \\
        -v "$CERTBOT_DIR/conf:/etc/letsencrypt" \\
        -v "$CERTBOT_DIR/www:/var/www/certbot" \\
        certbot/certbot:v5.1.0 renew
    
    # Reload nginx
    print_info "Reloading nginx..."
    $COMPOSE_CMD -f "$COMPOSE_FILE" --env-file "$ENV_FILE" exec -T nginx nginx -s reload || true
    
    print_success "Renewal complete"
}

do_check() {
    print_header "SSL Certificate Status: $ENV"
    
    docker run --rm \\
        -v "$CERTBOT_DIR/conf:/etc/letsencrypt" \\
        certbot/certbot:v5.1.0 certificates
}

do_test() {
    print_header "Testing SSL Configuration: $ENV"
    
    print_info "Testing $API_DOMAIN..."
    if curl -sI "https://$API_DOMAIN/health" | grep -q "200\\|301\\|302"; then
        print_success "API HTTPS is working"
    else
        print_warning "Could not verify API HTTPS"
    fi
    
    print_info "Testing $FLOWER_DOMAIN..."
    if curl -sI "https://$FLOWER_DOMAIN/" | grep -q "200\\|301\\|302\\|401"; then
        print_success "Flower HTTPS is working"
    else
        print_warning "Could not verify Flower HTTPS"
    fi
}

# Execute command
case $COMMAND in
    setup)
        do_setup
        ;;
    renew)
        do_renew
        ;;
    check)
        do_check
        ;;
    test)
        do_test
        ;;
esac
'''
