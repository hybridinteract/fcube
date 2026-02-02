"""
Template engine script template.
Processes template files and replaces {{PLACEHOLDERS}} with actual values.
"""


def generate_template_engine_sh() -> str:
    """Generate scripts/common/template-engine.sh file content."""
    return '''#!/usr/bin/env bash

##############################################################################
# Template Engine
# Processes template files and replaces {{PLACEHOLDERS}} with actual values
##############################################################################

# Source common utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

# Process a single template file
# Usage: process_template <input_file> <output_file>
process_template() {
    local input_file="$1"
    local output_file="$2"
    
    if [[ ! -f "$input_file" ]]; then
        print_error "Template file not found: $input_file"
        return 1
    fi
    
    # Create output directory if needed
    mkdir -p "$(dirname "$output_file")"
    
    # Read template and replace placeholders
    local content
    content=$(cat "$input_file")
    
    # Replace all {{PLACEHOLDER}} patterns with environment variables
    while [[ "$content" =~ \\{\\{([A-Z_][A-Z0-9_]*)\\}\\} ]]; do
        local placeholder="${BASH_REMATCH[0]}"
        local var_name="${BASH_REMATCH[1]}"
        local var_value="${!var_name:-}"
        
        if [[ -z "$var_value" ]]; then
            print_warning "Placeholder $placeholder has no value set"
        fi
        
        # Replace placeholder with value
        content="${content//$placeholder/$var_value}"
    done
    
    # Write processed content
    echo "$content" > "$output_file"
    
    print_debug "Processed: $input_file -> $output_file"
    return 0
}

# Process all templates in a directory
# Usage: process_templates <template_dir> <output_dir>
process_templates() {
    local template_dir="$1"
    local output_dir="$2"
    
    if [[ ! -d "$template_dir" ]]; then
        print_error "Template directory not found: $template_dir"
        return 1
    fi
    
    local count=0
    while IFS= read -r -d '' template; do
        local relative_path="${template#$template_dir/}"
        local output_path="$output_dir/${relative_path%.template}"
        
        if process_template "$template" "$output_path"; then
            ((count++))
        else
            return 1
        fi
    done < <(find "$template_dir" -name "*.template" -type f -print0)
    
    print_success "Processed $count template files"
    return 0
}

# Set derived variables from base configuration
set_derived_variables() {
    local env="${1:-production}"
    
    # Derived domain variables
    export API_DOMAIN="${API_SUBDOMAIN}.${BASE_DOMAIN}"
    export FLOWER_DOMAIN="${FLOWER_SUBDOMAIN}.${BASE_DOMAIN}"
    
    # Sanitize project name for Docker naming
    export PROJECT_PREFIX=$(sanitize_project_name "$PROJECT_NAME")
    
    # Environment-specific variables
    if [[ "$env" == "production" ]]; then
        export ENVIRONMENT="production"
        export DEBUG="false"
        export API_WORKERS="${PRODUCTION_API_WORKERS:-4}"
        export CELERY_WORKERS="${PRODUCTION_CELERY_WORKERS:-4}"
        export POSTGRES_HOST="${PRODUCTION_POSTGRES_HOST:-localhost}"
        export POSTGRES_PORT="${PRODUCTION_POSTGRES_PORT:-5432}"
        export POSTGRES_DB="${PRODUCTION_POSTGRES_DB:-defaultdb}"
        export POSTGRES_USER="${PRODUCTION_POSTGRES_USER:-postgres}"
        export POSTGRES_PASSWORD="${PRODUCTION_POSTGRES_PASSWORD:-}"
        export DB_SSL_MODE="${PRODUCTION_DB_SSL_MODE:-require}"
        export CONTAINER_PREFIX="${PROJECT_PREFIX}"
        export VOLUME_PREFIX="${PROJECT_PREFIX}"
        export NETWORK_PREFIX="${PROJECT_PREFIX}"
        export NETWORK_SUBNET="172.20.0.0/16"
        export LOG_LEVEL="warning"
        export ENABLE_DOCS="false"
    else
        export ENVIRONMENT="staging"
        export DEBUG="true"
        export API_WORKERS="${STAGING_API_WORKERS:-2}"
        export CELERY_WORKERS="${STAGING_CELERY_WORKERS:-2}"
        export POSTGRES_HOST="${STAGING_POSTGRES_HOST:-postgres}"
        export POSTGRES_PORT="${STAGING_POSTGRES_PORT:-5432}"
        export POSTGRES_DB="${STAGING_POSTGRES_DB:-staging_db}"
        export POSTGRES_USER="${STAGING_POSTGRES_USER:-staging_user}"
        export POSTGRES_PASSWORD="${STAGING_POSTGRES_PASSWORD:-}"
        export DB_SSL_MODE="${STAGING_DB_SSL_MODE:-disable}"
        export CONTAINER_PREFIX="${PROJECT_PREFIX}_staging"
        export VOLUME_PREFIX="${PROJECT_PREFIX}_staging"
        export NETWORK_PREFIX="${PROJECT_PREFIX}_staging"
        export NETWORK_SUBNET="172.21.0.0/16"
        export LOG_LEVEL="info"
        export ENABLE_DOCS="true"
    fi
    
    # Trusted hosts (used for FastAPI security)
    export TRUSTED_HOSTS="localhost,127.0.0.1,${API_DOMAIN},${BASE_DOMAIN},*.${BASE_DOMAIN}"
    
    # CORS Origins
    export CORS_ORIGINS="http://localhost:3000,https://${BASE_DOMAIN},https://www.${BASE_DOMAIN},https://app.${BASE_DOMAIN}"
    
    print_debug "Derived variables set for $env environment"
}

# Generate secure secrets if not already set
generate_secrets() {
    if [[ -z "${SECRET_KEY:-}" ]]; then
        export SECRET_KEY=$(generate_secret 64)
        print_info "Generated new SECRET_KEY"
    fi
    
    if [[ -z "${JWT_SECRET_KEY:-}" ]]; then
        export JWT_SECRET_KEY=$(generate_secret 64)
        print_info "Generated new JWT_SECRET_KEY"
    fi
    
    if [[ -z "${REDIS_PASSWORD:-}" ]]; then
        export REDIS_PASSWORD=$(generate_secret 32)
        print_info "Generated new REDIS_PASSWORD"
    fi
}
'''
