# Plugin System

The plugin system allows adding pre-built feature modules to any FCube-generated project. Plugins are **self-contained** with their own models, services, routes, and installation logic.

---

## Overview

Plugins provide a way to extend FCube projects with common features without having to implement them from scratch. Each plugin includes:

- **Models and schemas** - Database entities and validation
- **Services and CRUD operations** - Business logic and data access
- **Routes and dependencies** - API endpoints and DI configuration
- **Configuration templates** - Environment variables and settings
- **Documentation** - Usage instructions and examples

---

## Available Plugins

### referral

**User referral system with strategies.**

```bash
fcube addplugin referral
```

Features:

- Referral tracking and management
- Configurable referral strategies
- Referral code generation
- Complete API for referral management
- Integration with user module

Generated files:

```
app/referral/
├── __init__.py
├── models.py
├── config.py
├── strategies.py
├── exceptions.py
├── dependencies.py
├── tasks.py
├── schemas/
│   ├── __init__.py
│   └── referral_schemas.py
├── crud/
│   ├── __init__.py
│   └── referral_crud.py
├── services/
│   ├── __init__.py
│   └── referral_service.py
└── routes/
    ├── __init__.py
    ├── referral_routes.py
    └── referral_admin_routes.py
```

### deploy_vps

**Complete VPS deployment with Docker, Nginx, SSL, and monitoring.**

```bash
fcube addplugin deploy_vps
```

Features:

- Docker Compose configuration
- Nginx reverse proxy with SSL
- Let's Encrypt certificate management
- Redis + Celery setup
- Flower monitoring dashboard
- Environment-specific configs (production/staging)
- Backup and security scripts

Generated structure:

```
deploy-vps/
├── config.env.example       # Configuration template
├── docker/
│   ├── docker-compose.production.yml
│   └── docker-compose.staging.yml
├── nginx/
│   ├── nginx.conf
│   ├── api.conf
│   └── flower.conf
├── redis/
│   └── redis.conf
├── scripts/
│   ├── setup.sh            # Initial setup wizard
│   ├── deploy.sh           # Deployment commands
│   ├── ssl.sh              # SSL certificate management
│   ├── backup.sh           # Backup utilities
│   └── security.sh         # Server hardening
└── README.md
```

---

## Using Plugins

### List Available Plugins

```bash
fcube addplugin --list
```

### Install a Plugin

```bash
# Install with default settings
fcube addplugin <plugin_name>

# Preview changes first (dry run)
fcube addplugin <plugin_name> --dry-run

# Force overwrite existing files
fcube addplugin <plugin_name> --force

# Specify app directory
fcube addplugin <plugin_name> --dir app
```

### Dry Run Mode

Preview what a plugin will do before installing:

```bash
fcube addplugin referral --dry-run
```

Output:

```
Dry Run: referral plugin
────────────────────────────────────────────────
Would create files:
  ✓ app/referral/__init__.py
  ✓ app/referral/models.py
  ✓ app/referral/config.py
  ✓ app/referral/strategies.py
  ✓ app/referral/exceptions.py
  ✓ app/referral/dependencies.py
  ✓ app/referral/tasks.py
  ✓ app/referral/schemas/__init__.py
  ✓ app/referral/schemas/referral_schemas.py
  ✓ app/referral/crud/__init__.py
  ✓ app/referral/crud/referral_crud.py
  ✓ app/referral/services/__init__.py
  ✓ app/referral/services/referral_service.py
  ✓ app/referral/routes/__init__.py
  ✓ app/referral/routes/referral_routes.py
  ✓ app/referral/routes/referral_admin_routes.py
Would modify files:
  ~ app/apis/v1.py (add router)
  ~ app/core/alembic_models_import.py (add model imports)
No files will be changed (dry run mode)
```

### Post-Installation Steps

After installing a plugin:

1. **Run migrations** to create database tables:
   ```bash
   alembic revision --autogenerate -m "add referral system"
   alembic upgrade head
   ```

2. **Configure** plugin-specific settings in `.env`

3. **Review** the plugin's README for usage instructions

### Post-Installation for Referral Plugin

1. Add `referral_code` field to User model
2. Update `app/apis/v1.py` to include referral routes
3. Update `app/core/alembic_models_import.py`
4. Run migrations: `alembic revision --autogenerate && alembic upgrade head`

---

## Plugin Architecture

Plugins are discovered dynamically from the `templates/plugins/` directory. Each plugin must have:

### Plugin Structure

```
templates/plugins/<plugin_name>/
├── __init__.py              # Plugin metadata and installer
├── <template_files>.py      # Template generators
└── README.md                # Plugin documentation
```

### Plugin Metadata

```python
# __init__.py
from dataclasses import dataclass, field
from typing import Callable, List, Tuple
from pathlib import Path


@dataclass
class PluginMetadata:
    name: str
    description: str
    version: str
    dependencies: List[str]
    files_generated: List[str]
    config_required: bool
    post_install_notes: str
    installer: Callable[[Path], List[Tuple[Path, str]]]


def install_my_plugin(app_dir: Path) -> List[Tuple[Path, str]]:
    """Install plugin files."""
    files: List[Tuple[Path, str]] = []
    
    # Generate model
    model_content = generate_model()
    files.append((app_dir / "models" / "my_module.py", model_content))
    
    # Generate schema
    schema_content = generate_schema()
    files.append((app_dir / "schemas" / "my_module.py", schema_content))
    
    # ... more files
    
    return files


PLUGIN_METADATA = PluginMetadata(
    name="my_plugin",
    description="Description of what this plugin does",
    version="1.0.0",
    dependencies=[],  # External pip packages needed
    files_generated=[
        "app/models/my_module.py",
        "app/schemas/my_module.py",
    ],
    config_required=False,
    post_install_notes="""
After installation:
1. Run migrations
2. Configure settings
    """,
    installer=install_my_plugin,
)
```

### Template Generators

Templates are Python functions that return file content:

```python
# templates.py
def generate_model() -> str:
    return '''from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class MyModel(Base):
    __tablename__ = "my_models"
    
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
'''


def generate_schema() -> str:
    return '''from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field


class MyModelBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)


class MyModelCreate(MyModelBase):
    pass


class MyModelResponse(MyModelBase):
    id: UUID
    created_at: datetime
    
    model_config = {"from_attributes": True}
'''
```

### Registering Plugins

Add your plugin to the discovery function:

```python
# templates/plugins/__init__.py
def _discover_plugins() -> None:
    from .referral import PLUGIN_METADATA as referral_metadata
    from .deploy_vps import PLUGIN_METADATA as deploy_vps_metadata
    from .my_plugin import PLUGIN_METADATA as my_plugin_metadata  # Add this
    
    register_plugin(referral_metadata)
    register_plugin(deploy_vps_metadata)
    register_plugin(my_plugin_metadata)  # And this
```

---

## Plugin Guidelines

### Do

- **Self-contained** — Include all necessary files
- **Well-documented** — README with usage instructions
- **Validated** — Test with fresh FCube project
- **Versioned** — Follow semantic versioning
- **Configurable** — Use environment variables for settings

### Don't

- **Modify core files** — Except for router registration
- **Hardcode values** — Use configuration
- **Break existing code** — Check for conflicts
- **Skip migrations** — Always include model changes
- **Duplicate functionality** — Check if existing plugins cover the use case

---

## Contributing Plugins

See [Contributing](contributing.md) for guidelines on submitting new plugins to FCube.
