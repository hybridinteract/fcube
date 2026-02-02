"""
Validation utilities script template.
Functions for validating configuration and system prerequisites.
"""


def generate_validation_sh() -> str:
    """Generate scripts/common/validation.sh file content."""
    return '''#!/usr/bin/env bash

##############################################################################
# Validation Utilities
# Functions for validating configuration and system prerequisites
##############################################################################

# Source common utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

# Check if Docker is installed and running
check_docker() {
    if ! command_exists docker; then
        print_error "Docker is not installed"
        print_info "Install Docker: https://docs.docker.com/get-docker/"
        return 1
    fi
    
    if ! docker info &>/dev/null; then
        print_error "Docker daemon is not running"
        print_info "Start Docker with: sudo systemctl start docker"
        return 1
    fi
    
    print_success "Docker is available and running"
    return 0
}

# Check if Docker Compose is available
check_docker_compose() {
    local compose_cmd
    if ! compose_cmd=$(get_docker_compose_cmd); then
        return 1
    fi
    
    print_success "Docker Compose is available: $compose_cmd"
    return 0
}

# Check disk space
check_disk_space() {
    local required_gb="${1:-5}"
    local mount_point="${2:-/}"
    
    local available_kb=$(df "$mount_point" | awk 'NR==2 {print $4}')
    local available_gb=$((available_kb / 1024 / 1024))
    
    if [[ $available_gb -lt $required_gb ]]; then
        print_warning "Low disk space: ${available_gb}GB available (recommended: ${required_gb}GB+)"
        return 1
    fi
    
    print_success "Disk space OK: ${available_gb}GB available"
    return 0
}

# Check if ports are available
check_port() {
    local port="$1"
    
    if command_exists lsof; then
        if lsof -i ":$port" &>/dev/null; then
            local process=$(lsof -i ":$port" | awk 'NR==2 {print $1}')
            print_warning "Port $port is in use by: $process"
            return 1
        fi
    elif command_exists netstat; then
        if netstat -tuln | grep -q ":$port "; then
            print_warning "Port $port is in use"
            return 1
        fi
    elif command_exists ss; then
        if ss -tuln | grep -q ":$port "; then
            print_warning "Port $port is in use"
            return 1
        fi
    fi
    
    print_success "Port $port is available"
    return 0
}

# Validate DNS resolution
check_dns() {
    local domain="$1"
    
    if command_exists dig; then
        if dig +short "$domain" | grep -q '[0-9]'; then
            local ip=$(dig +short "$domain" | head -1)
            print_success "DNS resolves: $domain -> $ip"
            return 0
        fi
    elif command_exists nslookup; then
        if nslookup "$domain" &>/dev/null; then
            print_success "DNS resolves: $domain"
            return 0
        fi
    elif command_exists host; then
        if host "$domain" &>/dev/null; then
            print_success "DNS resolves: $domain"
            return 0
        fi
    fi
    
    print_warning "DNS does not resolve for: $domain"
    return 1
}

# Validate environment file
validate_env_file() {
    local env_file="$1"
    local errors=0
    
    if [[ ! -f "$env_file" ]]; then
        print_error "Environment file not found: $env_file"
        return 1
    fi
    
    # Check for placeholder values
    if grep -q "CHANGE_THIS" "$env_file"; then
        print_warning "Found placeholder values in $env_file"
        grep "CHANGE_THIS" "$env_file" | head -5
        ((errors++))
    fi
    
    # Check secret key length
    local secret_key=$(grep "^SECRET_KEY=" "$env_file" | cut -d= -f2)
    if [[ ${#secret_key} -lt 32 ]]; then
        print_warning "SECRET_KEY is too short (${#secret_key} chars, should be 32+)"
        ((errors++))
    fi
    
    if [[ $errors -gt 0 ]]; then
        return 1
    fi
    
    print_success "Environment file validated: $env_file"
    return 0
}

# Validate Docker Compose file syntax
validate_compose_file() {
    local compose_file="$1"
    local compose_cmd=$(get_docker_compose_cmd)
    
    if [[ ! -f "$compose_file" ]]; then
        print_error "Compose file not found: $compose_file"
        return 1
    fi
    
    if ! $compose_cmd -f "$compose_file" config --quiet 2>/dev/null; then
        print_error "Invalid Docker Compose syntax in: $compose_file"
        return 1
    fi
    
    print_success "Docker Compose syntax is valid: $compose_file"
    return 0
}

# Validate nginx configuration
validate_nginx_config() {
    local nginx_dir="$1"
    
    if ! docker run --rm -v "$nginx_dir:/etc/nginx:ro" nginx:alpine nginx -t 2>/dev/null; then
        print_error "Invalid nginx configuration"
        return 1
    fi
    
    print_success "Nginx configuration is valid"
    return 0
}
'''
