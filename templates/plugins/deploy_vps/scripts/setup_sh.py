"""
Setup script template.
Complete initial setup wizard for deploy-vps.
"""


def generate_setup_sh() -> str:
    """Generate scripts/setup.sh file content."""
    return '''#!/usr/bin/env bash

##############################################################################
# Setup Script
# Complete initial setup wizard for deploy-vps
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
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Complete setup wizard for deploy-vps:"
    echo "  1. Check system prerequisites"
    echo "  2. Collect configuration interactively"
    echo "  3. Generate all configuration files"
    echo ""
    echo "Options:"
    echo "  --force       Force regenerate existing configuration"
    echo "  --help        Show this help message"
    echo ""
}

# Parse arguments
FORCE=false
while [[ $# -gt 0 ]]; do
    case $1 in
        --force)
            FORCE=true
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

print_header "Deploy-VPS Setup Wizard"

# Step 1: System Checks
print_info "Step 1/4: Checking system prerequisites..."
print_separator

check_docker
check_docker_compose
check_disk_space 5
check_port 80
check_port 443

print_success "System checks passed"
echo ""

# Step 2: Check for existing configuration
if [[ -f "$DEPLOY_ROOT/config.env" ]] && [[ "$FORCE" != "true" ]]; then
    print_warning "config.env already exists"
    if ! confirm_action "Overwrite existing configuration?"; then
        print_info "Setup cancelled. Use --force to regenerate."
        exit 0
    fi
fi

# Step 3: Collect Configuration
print_info "Step 2/4: Collecting project configuration..."
print_separator

# Project Name
read -p "$(echo -e "${CYAN}Project name (e.g., myhotel): ${NC}")" PROJECT_NAME
PROJECT_NAME="${PROJECT_NAME:-myproject}"

# Base Domain
read -p "$(echo -e "${CYAN}Base domain (e.g., example.com): ${NC}")" BASE_DOMAIN
BASE_DOMAIN="${BASE_DOMAIN:-example.com}"

# Subdomains
read -p "$(echo -e "${CYAN}API subdomain [api]: ${NC}")" API_SUBDOMAIN
API_SUBDOMAIN="${API_SUBDOMAIN:-api}"

read -p "$(echo -e "${CYAN}Flower subdomain [flower]: ${NC}")" FLOWER_SUBDOMAIN
FLOWER_SUBDOMAIN="${FLOWER_SUBDOMAIN:-flower}"

# Admin Email
read -p "$(echo -e "${CYAN}Admin email for SSL notifications: ${NC}")" ACME_EMAIL
ACME_EMAIL="${ACME_EMAIL:-admin@$BASE_DOMAIN}"

echo ""
print_info "Configure environments (production/staging)..."

# Production Configuration
read -p "$(echo -e "${CYAN}Production API workers [4]: ${NC}")" PRODUCTION_API_WORKERS
PRODUCTION_API_WORKERS="${PRODUCTION_API_WORKERS:-4}"

read -p "$(echo -e "${CYAN}Production Celery workers [4]: ${NC}")" PRODUCTION_CELERY_WORKERS
PRODUCTION_CELERY_WORKERS="${PRODUCTION_CELERY_WORKERS:-4}"

read -p "$(echo -e "${CYAN}Production PostgreSQL host: ${NC}")" PRODUCTION_POSTGRES_HOST
read -p "$(echo -e "${CYAN}Production PostgreSQL port [25060]: ${NC}")" PRODUCTION_POSTGRES_PORT
PRODUCTION_POSTGRES_PORT="${PRODUCTION_POSTGRES_PORT:-25060}"

read -p "$(echo -e "${CYAN}Production PostgreSQL database: ${NC}")" PRODUCTION_POSTGRES_DB
read -p "$(echo -e "${CYAN}Production PostgreSQL user: ${NC}")" PRODUCTION_POSTGRES_USER
read -sp "$(echo -e "${CYAN}Production PostgreSQL password: ${NC}")" PRODUCTION_POSTGRES_PASSWORD
echo ""

# Staging Configuration
read -p "$(echo -e "${CYAN}Staging API workers [1]: ${NC}")" STAGING_API_WORKERS
STAGING_API_WORKERS="${STAGING_API_WORKERS:-1}"

read -p "$(echo -e "${CYAN}Staging PostgreSQL database [staging_db]: ${NC}")" STAGING_POSTGRES_DB
STAGING_POSTGRES_DB="${STAGING_POSTGRES_DB:-staging_db}"

read -sp "$(echo -e "${CYAN}Staging PostgreSQL password: ${NC}")" STAGING_POSTGRES_PASSWORD
echo ""

# Flower Credentials
read -p "$(echo -e "${CYAN}Flower username [admin]: ${NC}")" FLOWER_USERNAME
FLOWER_USERNAME="${FLOWER_USERNAME:-admin}"

read -sp "$(echo -e "${CYAN}Flower password: ${NC}")" FLOWER_PASSWORD
echo ""

print_success "Configuration collected"
echo ""

# Step 4: Generate config.env
print_info "Step 3/4: Writing configuration..."
print_separator

cat > "$DEPLOY_ROOT/config.env" << EOF
# Deploy-VPS Configuration
# Generated: $(date)

PROJECT_NAME=$PROJECT_NAME
BASE_DOMAIN=$BASE_DOMAIN

API_SUBDOMAIN=$API_SUBDOMAIN
FLOWER_SUBDOMAIN=$FLOWER_SUBDOMAIN

ACME_EMAIL=$ACME_EMAIL

# Production
PRODUCTION_API_WORKERS=$PRODUCTION_API_WORKERS
PRODUCTION_CELERY_WORKERS=$PRODUCTION_CELERY_WORKERS
PRODUCTION_POSTGRES_HOST=$PRODUCTION_POSTGRES_HOST
PRODUCTION_POSTGRES_PORT=$PRODUCTION_POSTGRES_PORT
PRODUCTION_POSTGRES_DB=$PRODUCTION_POSTGRES_DB
PRODUCTION_POSTGRES_USER=$PRODUCTION_POSTGRES_USER
PRODUCTION_POSTGRES_PASSWORD=$PRODUCTION_POSTGRES_PASSWORD
PRODUCTION_DB_SSL_MODE=require

# Staging
STAGING_API_WORKERS=$STAGING_API_WORKERS
STAGING_CELERY_WORKERS=1
STAGING_POSTGRES_HOST=postgres
STAGING_POSTGRES_PORT=5432
STAGING_POSTGRES_DB=$STAGING_POSTGRES_DB
STAGING_POSTGRES_USER=staging_user
STAGING_POSTGRES_PASSWORD=$STAGING_POSTGRES_PASSWORD
STAGING_DB_SSL_MODE=disable

# Flower
FLOWER_USERNAME=$FLOWER_USERNAME
FLOWER_PASSWORD=$FLOWER_PASSWORD
EOF

print_success "Created config.env"

# Step 5: Generate secrets and templates
print_info "Step 4/4: Generating configuration files..."
print_separator

# Load the configuration
source "$DEPLOY_ROOT/config.env"

# Generate secrets
SECRET_KEY=$(generate_secret 64)
JWT_SECRET_KEY=$(generate_secret 64)
REDIS_PASSWORD=$(generate_secret 32)

export SECRET_KEY JWT_SECRET_KEY REDIS_PASSWORD

# Generate production configuration
set_derived_variables "production"
process_templates "$DEPLOY_ROOT/templates" "$DEPLOY_ROOT/generated"

# Copy .env file to root
cp "$DEPLOY_ROOT/generated/env/production.env" "$DEPLOY_ROOT/.env.production"
print_success "Created .env.production"

# Generate staging configuration
set_derived_variables "staging"
process_templates "$DEPLOY_ROOT/templates" "$DEPLOY_ROOT/generated"
cp "$DEPLOY_ROOT/generated/env/staging.env" "$DEPLOY_ROOT/.env.staging"
print_success "Created .env.staging"

print_separator
print_success "Setup complete!"
echo ""
print_info "Next steps:"
echo "  1. Review and add API keys to .env.production"
echo "     nano .env.production"
echo ""
echo "  2. Validate configuration:"
echo "     ./scripts/validate.sh --env production"
echo ""
echo "  3. Deploy:"
echo "     ./scripts/deploy.sh init --env production"
echo ""
echo "  4. Setup SSL:"
echo "     ./scripts/ssl.sh setup --env production"
echo ""
'''
