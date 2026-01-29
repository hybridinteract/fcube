"""
FCube Project Templates Package.

Contains modular code generation templates for complete FastAPI project setup.

Structure:
- core/   - Core module templates (database, settings, logging, etc.)
- user/   - User module templates (models, auth, permissions)
- infra/  - Infrastructure templates (Docker, Alembic, project files)
- api_templates.py - API routing templates
"""

# Core module templates (from modular subpackage)
from .core import (
    generate_core_init,
    generate_core_models,
    generate_core_database,
    generate_core_settings,
    generate_core_crud,
    generate_core_exceptions,
    generate_core_logging,
    generate_core_main,
    generate_core_middleware,
    generate_core_celery,
    generate_core_alembic_models,
)

# User module templates (from modular subpackage)
from .user import (
    generate_user_init,
    generate_user_models,
    generate_user_schemas,
    generate_user_crud,
    generate_user_exceptions,
    generate_user_routes,
    generate_user_auth_init,
    generate_user_auth_routes,
    generate_user_auth_service,
    generate_user_auth_utils,
    generate_user_permission_init,
    generate_user_permission_utils,
    generate_user_permission_scoped_access,
)

# Infrastructure templates (from modular subpackage)
from .infra import (
    generate_docker_compose,
    generate_dockerfile,
    generate_docker_entrypoint,
    generate_celery_entrypoint,
    generate_flower_entrypoint,
    generate_alembic_ini,
    generate_alembic_env,
    generate_alembic_script_mako,
    generate_pyproject_toml,
    generate_env_example,
    generate_gitignore,
    generate_project_readme,
    generate_fcube_script,
)

# API templates
from .api_templates import (
    generate_apis_init,
    generate_apis_v1,
)

__all__ = [
    # Core
    "generate_core_init",
    "generate_core_models",
    "generate_core_database",
    "generate_core_settings",
    "generate_core_crud",
    "generate_core_exceptions",
    "generate_core_logging",
    "generate_core_main",
    "generate_core_middleware",
    "generate_core_celery",
    "generate_core_alembic_models",
    # User
    "generate_user_init",
    "generate_user_models",
    "generate_user_schemas",
    "generate_user_crud",
    "generate_user_exceptions",
    "generate_user_routes",
    "generate_user_auth_init",
    "generate_user_auth_routes",
    "generate_user_auth_service",
    "generate_user_auth_utils",
    "generate_user_permission_init",
    "generate_user_permission_utils",
    "generate_user_permission_scoped_access",
    # Infrastructure
    "generate_docker_compose",
    "generate_dockerfile",
    "generate_docker_entrypoint",
    "generate_celery_entrypoint",
    "generate_flower_entrypoint",
    "generate_alembic_ini",
    "generate_alembic_env",
    "generate_alembic_script_mako",
    "generate_pyproject_toml",
    "generate_env_example",
    "generate_gitignore",
    "generate_project_readme",
    "generate_fcube_script",
    # API
    "generate_apis_init",
    "generate_apis_v1",
]
