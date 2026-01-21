"""
FCube Project Templates Package.

Contains code generation templates for complete FastAPI project setup.
"""

# Core module templates
from .core_templates import (
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

# User module templates
from .user_templates import (
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
)

# API templates
from .api_templates import (
    generate_apis_init,
    generate_apis_v1,
)

# Infrastructure templates
from .infra_templates import (
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
    # API
    "generate_apis_init",
    "generate_apis_v1",
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
]
