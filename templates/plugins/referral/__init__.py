"""
Referral Plugin for FCube CLI.

A comprehensive user referral system with:
- Configurable completion strategies per user type
- Event-driven milestone tracking
- Admin management and statistics
- Team hierarchy support (optional)

Integration Points:
- User module: referral_code field, UserReferralIntegration service
- Booking/Order modules: trigger referral events on completion
"""

from .. import PluginMetadata

# Plugin metadata
PLUGIN_METADATA = PluginMetadata(
    name="referral",
    description="User referral system with configurable completion strategies and milestone tracking",
    version="1.0.0",
    dependencies=["user"],  # Requires user module
    files_generated=[
        "app/referral/__init__.py",
        "app/referral/models.py",
        "app/referral/config.py",
        "app/referral/strategies.py",
        "app/referral/exceptions.py",
        "app/referral/dependencies.py",
        "app/referral/tasks.py",
        "app/referral/schemas/__init__.py",
        "app/referral/schemas/referral_schemas.py",
        "app/referral/crud/__init__.py",
        "app/referral/crud/referral_crud.py",
        "app/referral/services/__init__.py",
        "app/referral/services/referral_service.py",
        "app/referral/routes/__init__.py",
        "app/referral/routes/referral_routes.py",
        "app/referral/routes/referral_admin_routes.py",
    ],
    config_required=True,
    post_install_notes="""
1. Add referral_code field to User model:
   referral_code: Mapped[Optional[str]] = mapped_column(String(20), unique=True, nullable=True)

2. Create UserReferralIntegration service in app/user/services/

3. Update alembic_models_import.py:
   from app.referral.models import Referral, ReferralEvent, ReferralSettings

4. Create a strategy for your user types in app/referral/strategies.py

5. Trigger referral events from your modules:
   await referral_service.process_event(session, "booking_completed", user_id, {"booking_id": ...})
"""
)

# Import all template generators
from .model_templates import generate_referral_models
from .config_templates import generate_referral_config, generate_referral_strategies
from .exception_templates import generate_referral_exceptions
from .dependency_templates import generate_referral_dependencies
from .task_templates import generate_referral_tasks
from .schema_templates import generate_referral_schemas, generate_referral_schemas_init
from .crud_templates import generate_referral_crud, generate_referral_crud_init
from .service_templates import generate_referral_service, generate_referral_service_init
from .route_templates import (
    generate_referral_routes,
    generate_referral_admin_routes,
    generate_referral_routes_init,
)

__all__ = [
    "PLUGIN_METADATA",
    # Model templates
    "generate_referral_models",
    # Config templates
    "generate_referral_config",
    "generate_referral_strategies",
    # Exception templates
    "generate_referral_exceptions",
    # Dependency templates
    "generate_referral_dependencies",
    # Task templates
    "generate_referral_tasks",
    # Schema templates
    "generate_referral_schemas",
    "generate_referral_schemas_init",
    # CRUD templates
    "generate_referral_crud",
    "generate_referral_crud_init",
    # Service templates
    "generate_referral_service",
    "generate_referral_service_init",
    # Route templates
    "generate_referral_routes",
    "generate_referral_admin_routes",
    "generate_referral_routes_init",
]
