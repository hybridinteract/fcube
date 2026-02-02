"""
Deploy VPS Plugin for FCube CLI.

A comprehensive VPS deployment system with:
- Template-based configuration (zero hardcoded values)
- Docker Compose orchestration
- Nginx reverse proxy with SSL
- Redis cache & message broker
- Celery workers for background tasks
- Flower monitoring dashboard
- Production & staging environments

This plugin generates a complete deployment structure that works on any
VPS/dedicated server. All configurations are derived from a single
config.env file (single source of truth).

Usage:
    fcube addplugin deploy_vps
"""

from pathlib import Path
from typing import List, Tuple

from .. import PluginMetadata

# Import all template generators
from .gitignore_templates import generate_gitignore
from .config_templates import generate_config_env_example
from .readme_templates import generate_readme, generate_quick_start
from .env_templates import (
    generate_production_env_template,
    generate_staging_env_template,
)
from .docker_templates import (
    generate_production_compose_template,
    generate_staging_compose_template,
)
from .nginx_templates import (
    generate_nginx_conf_template,
    generate_api_conf_template,
    generate_flower_conf_template,
)
from .redis_templates import (
    generate_redis_conf_template,
    generate_redis_password_conf_template,
)
# Import from modular scripts subpackage
from .scripts import (
    generate_common_sh,
    generate_template_engine_sh,
    generate_validation_sh,
    generate_setup_sh,
    generate_validate_sh,
    generate_deploy_sh,
    generate_ssl_sh,
    generate_backup_sh,
    generate_security_setup_sh,
)


def install_deploy_vps_plugin(app_dir: Path) -> List[Tuple[Path, str]]:
    """Generate all files for the deploy-vps plugin.
    
    This is the plugin's installer function. It returns a list of
    (file_path, content) tuples that the addplugin command will create.
    
    Note: This plugin installs to the project root, not within app/
    The plugin creates a `deploy-vps/` directory at the project root level.
    
    Args:
        app_dir: The app directory (e.g., /path/to/project/app)
    
    Returns:
        List of (Path, str) tuples representing files to create
    """
    # Deploy directory is at project root, not inside app/
    project_root = app_dir.parent
    deploy_dir = project_root / "deploy-vps"
    
    files: List[Tuple[Path, str]] = [
        # Root files
        (deploy_dir / ".gitignore", generate_gitignore()),
        (deploy_dir / "config.env.example", generate_config_env_example()),
        (deploy_dir / "README.md", generate_readme()),
        (deploy_dir / "QUICK_START.md", generate_quick_start()),
        
        # Generated directory placeholder
        (deploy_dir / "generated" / ".gitkeep", ""),
        
        # Templates - env
        (deploy_dir / "templates" / "env" / "production.env.template", generate_production_env_template()),
        (deploy_dir / "templates" / "env" / "staging.env.template", generate_staging_env_template()),
        
        # Templates - docker
        (deploy_dir / "templates" / "docker" / "production.compose.yml.template", generate_production_compose_template()),
        (deploy_dir / "templates" / "docker" / "staging.compose.yml.template", generate_staging_compose_template()),
        
        # Templates - nginx
        (deploy_dir / "templates" / "nginx" / "nginx.conf.template", generate_nginx_conf_template()),
        (deploy_dir / "templates" / "nginx" / "api.conf.template", generate_api_conf_template()),
        (deploy_dir / "templates" / "nginx" / "flower.conf.template", generate_flower_conf_template()),
        
        # Templates - redis
        (deploy_dir / "templates" / "redis" / "redis.conf.template", generate_redis_conf_template()),
        (deploy_dir / "templates" / "redis" / "redis-password.conf.template", generate_redis_password_conf_template()),
        
        # Scripts - common
        (deploy_dir / "scripts" / "common" / "common.sh", generate_common_sh()),
        (deploy_dir / "scripts" / "common" / "template-engine.sh", generate_template_engine_sh()),
        (deploy_dir / "scripts" / "common" / "validation.sh", generate_validation_sh()),
        
        # Scripts - main
        (deploy_dir / "scripts" / "setup.sh", generate_setup_sh()),
        (deploy_dir / "scripts" / "validate.sh", generate_validate_sh()),
        (deploy_dir / "scripts" / "deploy.sh", generate_deploy_sh()),
        (deploy_dir / "scripts" / "ssl.sh", generate_ssl_sh()),
        
        # Scripts - optional
        (deploy_dir / "scripts" / "optional" / "backup.sh", generate_backup_sh()),
        (deploy_dir / "scripts" / "optional" / "security-setup.sh", generate_security_setup_sh()),
    ]
    
    return files


# Plugin metadata with installer function
PLUGIN_METADATA = PluginMetadata(
    name="deploy_vps",
    description="Complete VPS deployment system with Docker, Nginx, SSL, Redis, Celery, and Flower",
    version="1.0.0",
    dependencies=[],  # No dependencies - can be used with any FCube project
    files_generated=[
        "deploy-vps/.gitignore",
        "deploy-vps/config.env.example",
        "deploy-vps/README.md",
        "deploy-vps/QUICK_START.md",
        "deploy-vps/generated/.gitkeep",
        "deploy-vps/templates/env/production.env.template",
        "deploy-vps/templates/env/staging.env.template",
        "deploy-vps/templates/docker/production.compose.yml.template",
        "deploy-vps/templates/docker/staging.compose.yml.template",
        "deploy-vps/templates/nginx/nginx.conf.template",
        "deploy-vps/templates/nginx/api.conf.template",
        "deploy-vps/templates/nginx/flower.conf.template",
        "deploy-vps/templates/redis/redis.conf.template",
        "deploy-vps/templates/redis/redis-password.conf.template",
        "deploy-vps/scripts/common/common.sh",
        "deploy-vps/scripts/common/template-engine.sh",
        "deploy-vps/scripts/common/validation.sh",
        "deploy-vps/scripts/setup.sh",
        "deploy-vps/scripts/validate.sh",
        "deploy-vps/scripts/deploy.sh",
        "deploy-vps/scripts/ssl.sh",
        "deploy-vps/scripts/optional/backup.sh",
        "deploy-vps/scripts/optional/security-setup.sh",
    ],
    config_required=True,
    post_install_notes="""
1. Navigate to the deploy-vps directory:
   cd deploy-vps

2. Copy and configure the environment file:
   cp config.env.example config.env
   nano config.env  # Edit with your project details

3. Make scripts executable (on Linux/macOS):
   chmod +x scripts/*.sh scripts/optional/*.sh scripts/common/*.sh

4. Run the setup wizard:
   ./scripts/setup.sh

5. Review the generated files and add your API keys to .env.production

6. Validate configuration:
   ./scripts/validate.sh --env production

7. Deploy:
   ./scripts/deploy.sh init --env production

8. Setup SSL:
   ./scripts/ssl.sh setup --env production

For detailed instructions, see deploy-vps/QUICK_START.md
""",
    installer=install_deploy_vps_plugin,
)


__all__ = [
    "PLUGIN_METADATA",
    "install_deploy_vps_plugin",
]
