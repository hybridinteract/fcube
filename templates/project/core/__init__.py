"""
Core Module Templates Package.

Contains modular template generators for the core module:
- Database configuration
- Settings
- CRUD base
- Exceptions
- Logging
- Main app
- Celery
"""

# Database templates
from .database_templates import (
    generate_core_init,
    generate_core_models,
    generate_core_database,
)

# Settings templates
from .settings_templates import (
    generate_core_settings,
)

# CRUD templates
from .crud_templates import (
    generate_core_crud,
)

# Exception templates
from .exception_templates import (
    generate_core_exceptions,
)

# Logging templates
from .logging_templates import (
    generate_core_logging,
)

# App templates
from .app_templates import (
    generate_core_main,
    generate_core_middleware,
)

# Celery templates
from .celery_templates import (
    generate_core_celery,
    generate_core_alembic_models,
)

__all__ = [
    # Database
    "generate_core_init",
    "generate_core_models",
    "generate_core_database",
    # Settings
    "generate_core_settings",
    # CRUD
    "generate_core_crud",
    # Exceptions
    "generate_core_exceptions",
    # Logging
    "generate_core_logging",
    # App
    "generate_core_main",
    "generate_core_middleware",
    # Celery
    "generate_core_celery",
    "generate_core_alembic_models",
]
