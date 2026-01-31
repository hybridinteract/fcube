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

This plugin is self-contained with its own installer function.
To see how this works, check the install_referral_plugin() function below.
"""

from pathlib import Path
from typing import List, Tuple

from .. import PluginMetadata

# Import all template generators
from .model_templates import generate_referral_init, generate_referral_models
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


def install_referral_plugin(app_dir: Path) -> List[Tuple[Path, str]]:
    """Generate all files for the referral plugin.
    
    This is the plugin's installer function. It returns a list of
    (file_path, content) tuples that the addplugin command will create.
    
    Args:
        app_dir: The app directory (e.g., /path/to/project/app)
    
    Returns:
        List of (Path, str) tuples representing files to create
    """
    referral_dir = app_dir / "referral"
    
    files: List[Tuple[Path, str]] = [
        # Root files
        (referral_dir / "__init__.py", generate_referral_init()),
        (referral_dir / "models.py", generate_referral_models()),
        (referral_dir / "config.py", generate_referral_config()),
        (referral_dir / "strategies.py", generate_referral_strategies()),
        (referral_dir / "exceptions.py", generate_referral_exceptions()),
        (referral_dir / "dependencies.py", generate_referral_dependencies()),
        (referral_dir / "tasks.py", generate_referral_tasks()),
        # Schemas
        (referral_dir / "schemas" / "__init__.py", generate_referral_schemas_init()),
        (referral_dir / "schemas" / "referral_schemas.py", generate_referral_schemas()),
        # CRUD
        (referral_dir / "crud" / "__init__.py", generate_referral_crud_init()),
        (referral_dir / "crud" / "referral_crud.py", generate_referral_crud()),
        # Services
        (referral_dir / "services" / "__init__.py", generate_referral_service_init()),
        (referral_dir / "services" / "referral_service.py", generate_referral_service()),
        # Routes
        (referral_dir / "routes" / "__init__.py", generate_referral_routes_init()),
        (referral_dir / "routes" / "referral_routes.py", generate_referral_routes()),
        (referral_dir / "routes" / "referral_admin_routes.py", generate_referral_admin_routes()),
    ]
    
    return files


# Plugin metadata with installer function
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
""",
    installer=install_referral_plugin,  # Self-contained installer!
)


__all__ = [
    "PLUGIN_METADATA",
    "install_referral_plugin",
    # Model templates
    "generate_referral_init",
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
