"""
FCube CLI Templates Package.

Contains code generation templates for all module components.
Each template follows the Korab Backend architecture patterns.
"""

# Model templates
from .model_templates import generate_model, generate_model_init

# Schema templates
from .schema_templates import generate_schemas, generate_schema_init

# CRUD templates
from .crud_templates import generate_crud, generate_crud_init

# Service templates
from .service_templates import generate_service, generate_service_init

# Route templates
from .route_templates import (
    generate_routes_init,
    generate_public_routes,
    generate_public_routes_init,
    generate_admin_routes,
    generate_admin_routes_init,
)

# Module-level templates
from .module_templates import (
    generate_dependencies,
    generate_permissions,
    generate_exceptions,
    generate_module_init,
    generate_tasks,
    generate_readme,
    generate_utils_init,
    generate_integrations_init,
)

__all__ = [
    # Models
    "generate_model",
    "generate_model_init",
    # Schemas
    "generate_schemas",
    "generate_schema_init",
    # CRUD
    "generate_crud",
    "generate_crud_init",
    # Services
    "generate_service",
    "generate_service_init",
    # Routes
    "generate_routes_init",
    "generate_public_routes",
    "generate_public_routes_init",
    "generate_admin_routes",
    "generate_admin_routes_init",
    # Module-level
    "generate_dependencies",
    "generate_permissions",
    "generate_exceptions",
    "generate_module_init",
    "generate_tasks",
    "generate_readme",
    "generate_utils_init",
    "generate_integrations_init",
]
