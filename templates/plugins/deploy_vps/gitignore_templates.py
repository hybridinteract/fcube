"""
Gitignore template for deploy-vps plugin.
"""


def generate_gitignore() -> str:
    """Generate .gitignore file content."""
    return '''# Generated files
generated/*
!generated/.gitkeep

# Environment files (actual, not templates)
*.env
!*.env.example
!*.env.template
.env.staging

# Secrets
config.env
config.env.*

# Runtime directories
ssl/
certbot/
backups/

# Logs
*.log
logs/

# Temporary files
*.tmp
.DS_Store
'''
