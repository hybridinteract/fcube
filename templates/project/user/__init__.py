"""
User Module Templates Package.

Contains modular template generators for the user module:
- Models (User, Role, Permission)
- Schemas (Pydantic models)
- CRUD operations
- Exceptions
- Routes
- Auth management
- Permission management
"""

# Model templates
from .model_templates import (
    generate_user_init,
    generate_user_models,
)

# Schema templates
from .schema_templates import (
    generate_user_schemas,
)

# CRUD templates
from .crud_templates import (
    generate_user_crud,
)

# Exception templates
from .exception_templates import (
    generate_user_exceptions,
)

# Route templates
from .route_templates import (
    generate_user_routes,
)

# Auth management templates
from .auth_templates import (
    generate_user_auth_init,
    generate_user_auth_routes,
    generate_user_auth_service,
    generate_user_auth_utils,
)

# Permission management templates
from .permission_templates import (
    generate_user_permission_init,
    generate_user_permission_utils,
    generate_user_permission_scoped_access,
)

__all__ = [
    # Model
    "generate_user_init",
    "generate_user_models",
    # Schema
    "generate_user_schemas",
    # CRUD
    "generate_user_crud",
    # Exception
    "generate_user_exceptions",
    # Route
    "generate_user_routes",
    # Auth
    "generate_user_auth_init",
    "generate_user_auth_routes",
    "generate_user_auth_service",
    "generate_user_auth_utils",
    # Permission
    "generate_user_permission_init",
    "generate_user_permission_utils",
    "generate_user_permission_scoped_access",
]
