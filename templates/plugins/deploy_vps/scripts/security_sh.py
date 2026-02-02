"""
Security setup script template.
Hardens server security (run once on fresh server).
"""


def generate_security_setup_sh() -> str:
    """Generate scripts/optional/security-setup.sh file content."""
    return '''#!/usr/bin/env bash

##############################################################################
# Security Setup Script
# Hardens server security (run once on fresh server)
##############################################################################

set -e

# Get script directory and source utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEPLOY_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"

source "$DEPLOY_ROOT/scripts/common/common.sh"

# Check for root
if [[ $EUID -ne 0 ]]; then
    print_error "This script must be run as root (sudo)"
    exit 1
fi

print_header "Server Security Setup"

print_warning "This script will:"
echo "  - Configure UFW firewall"
echo "  - Install and configure fail2ban"
echo "  - Enable automatic security updates"
echo "  - Harden SSH configuration"
echo ""

if ! confirm_action "Continue with security setup?"; then
    print_info "Setup cancelled"
    exit 0
fi

# Step 1: Update system
print_info "Updating system packages..."
apt update && apt upgrade -y

# Step 2: Configure UFW Firewall
print_info "Configuring UFW firewall..."
apt install -y ufw

ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow http
ufw allow https
ufw --force enable

print_success "UFW firewall configured"

# Step 3: Install fail2ban
print_info "Installing fail2ban..."
apt install -y fail2ban

cat > /etc/fail2ban/jail.local << 'EOF'
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
EOF

systemctl enable fail2ban
systemctl restart fail2ban

print_success "fail2ban configured"

# Step 4: Enable automatic security updates
print_info "Enabling automatic security updates..."
apt install -y unattended-upgrades
dpkg-reconfigure -plow unattended-upgrades

print_success "Automatic updates enabled"

# Step 5: Harden SSH
print_info "Hardening SSH configuration..."
sed -i 's/#PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config
sed -i 's/#PasswordAuthentication.*/PasswordAuthentication yes/' /etc/ssh/sshd_config
sed -i 's/X11Forwarding yes/X11Forwarding no/' /etc/ssh/sshd_config

systemctl reload sshd

print_success "SSH configuration hardened"

# Summary
print_separator
print_success "Security setup complete!"
echo ""
print_info "Active protections:"
echo "  - UFW firewall (SSH, HTTP, HTTPS allowed)"
echo "  - fail2ban (SSH brute-force protection)"
echo "  - Automatic security updates"
echo "  - SSH hardening (no root login)"
echo ""
print_warning "Make sure you have a non-root user with sudo access before logging out!"
'''
