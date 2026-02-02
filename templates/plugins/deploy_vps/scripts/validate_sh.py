"""
Validate script template.
Validates all configuration before deployment.
"""


def generate_validate_sh() -> str:
    """Generate scripts/validate.sh file content."""
    return '''#!/usr/bin/env bash

##############################################################################
# Validation Script
# Validates all configuration before deployment
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
    echo "Usage: $0 --env <environment>"
    echo ""
    echo "Validate configuration for deployment"
    echo ""
    echo "Options:"
    echo "  --env         Environment (production|staging)"
    echo "  --help        Show this help message"
    echo ""
}

# Parse arguments
ENV=""
while [[ $# -gt 0 ]]; do
    case $1 in
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

if [[ -z "$ENV" ]]; then
    print_error "Environment is required"
    show_help
    exit 1
fi

if [[ "$ENV" != "production" && "$ENV" != "staging" ]]; then
    print_error "Invalid environment: $ENV"
    print_info "Must be 'production' or 'staging'"
    exit 1
fi

print_header "Validating $ENV Configuration"

errors=0
warnings=0

# Check config.env
print_info "Checking config.env..."
if [[ ! -f "$DEPLOY_ROOT/config.env" ]]; then
    print_error "config.env not found"
    print_info "Run './scripts/setup.sh' first"
    exit 1
fi
print_success "config.env exists"

# Load configuration
if ! load_config "$DEPLOY_ROOT"; then
    exit 1
fi

# Set derived variables
set_derived_variables "$ENV"

# Check environment file
print_info "Checking .env.$ENV..."
ENV_FILE="$DEPLOY_ROOT/.env.$ENV"
if ! validate_env_file "$ENV_FILE"; then
    ((warnings++))
fi

# Check Docker
print_info "Checking Docker..."
if ! check_docker; then
    ((errors++))
fi

if ! check_docker_compose; then
    ((errors++))
fi

# Check generated files
print_info "Checking generated files..."
COMPOSE_FILE="$DEPLOY_ROOT/generated/docker-compose.$ENV.yml"
if [[ -f "$COMPOSE_FILE" ]]; then
    if ! validate_compose_file "$COMPOSE_FILE"; then
        ((errors++))
    fi
else
    print_warning "Docker Compose file not found: $COMPOSE_FILE"
    print_info "Run './scripts/setup.sh' to generate"
    ((warnings++))
fi

# Check DNS (optional)
print_info "Checking DNS resolution..."
if ! check_dns "$API_DOMAIN"; then
    print_warning "DNS not resolving - ensure DNS is configured before deploying"
    ((warnings++))
fi

if ! check_dns "$FLOWER_DOMAIN"; then
    print_warning "DNS not resolving - ensure DNS is configured before deploying"
    ((warnings++))
fi

# Summary
echo ""
print_separator

if [[ $errors -gt 0 ]]; then
    print_error "Validation failed with $errors error(s) and $warnings warning(s)"
    print_info "Fix the errors above before deploying"
    exit 1
elif [[ $warnings -gt 0 ]]; then
    print_warning "Validation passed with $warnings warning(s)"
    print_info "You can proceed with deployment, but review the warnings"
    exit 2
else
    print_success "All validation checks passed!"
    print_info "Ready to deploy with: ./scripts/deploy.sh init --env $ENV"
    exit 0
fi
'''
