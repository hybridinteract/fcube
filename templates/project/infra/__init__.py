"""
Infrastructure Templates Package.

Contains modular template generators for infrastructure:
- Docker configuration
- Alembic migrations
- Project files (pyproject.toml, README, etc.)
"""

# Docker templates
from .docker_templates import (
    generate_docker_compose,
    generate_dockerfile,
    generate_docker_entrypoint,
    generate_celery_entrypoint,
    generate_flower_entrypoint,
)

# Alembic templates
from .alembic_templates import (
    generate_alembic_ini,
    generate_alembic_env,
    generate_alembic_script_mako,
)

# Project templates
from .project_templates import (
    generate_pyproject_toml,
    generate_env_example,
    generate_gitignore,
    generate_project_readme,
    generate_fcube_script,
)

__all__ = [
    # Docker
    "generate_docker_compose",
    "generate_dockerfile",
    "generate_docker_entrypoint",
    "generate_celery_entrypoint",
    "generate_flower_entrypoint",
    # Alembic
    "generate_alembic_ini",
    "generate_alembic_env",
    "generate_alembic_script_mako",
    # Project
    "generate_pyproject_toml",
    "generate_env_example",
    "generate_gitignore",
    "generate_project_readme",
    "generate_fcube_script",
]
