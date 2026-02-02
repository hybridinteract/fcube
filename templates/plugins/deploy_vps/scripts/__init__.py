"""
Script templates for deploy-vps plugin.

This module organizes all shell script templates into separate files
for better maintainability and readability.

Structure:
- common_sh.py: Common utilities library
- template_engine_sh.py: Template processing engine
- validation_sh.py: Configuration validation utilities
- setup_sh.py: Initial setup wizard
- validate_sh.py: Pre-deployment validation
- deploy_sh.py: Deployment management
- ssl_sh.py: SSL certificate management
- backup_sh.py: Backup and restore (optional)
- security_sh.py: Server hardening (optional)
"""

from .common_sh import generate_common_sh
from .template_engine_sh import generate_template_engine_sh
from .validation_sh import generate_validation_sh
from .setup_sh import generate_setup_sh
from .validate_sh import generate_validate_sh
from .deploy_sh import generate_deploy_sh
from .ssl_sh import generate_ssl_sh
from .backup_sh import generate_backup_sh
from .security_sh import generate_security_setup_sh

__all__ = [
    "generate_common_sh",
    "generate_template_engine_sh",
    "generate_validation_sh",
    "generate_setup_sh",
    "generate_validate_sh",
    "generate_deploy_sh",
    "generate_ssl_sh",
    "generate_backup_sh",
    "generate_security_setup_sh",
]
