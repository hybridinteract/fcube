# Plugin System

FCube's plugin system for extending projects with pre-built features.

---

## Overview

Plugins are self-contained packages that add functionality to your FCube project. Each plugin includes:

- Models and schemas
- Services and CRUD operations
- Routes and dependencies
- Configuration templates
- Documentation

---

## Available Plugins

### referral

**Multi-tier referral system with configurable levels and rewards.**

```bash
fcube addplugin referral
```

Features:

- Multi-level referral tracking
- Configurable reward tiers
- Milestone-based rewards
- Reward distribution strategies
- Complete API for referral management

Generated files:

```
app/
├── models/referral/
│   ├── referral.py
│   ├── referral_level.py
│   ├── referral_reward.py
│   └── referral_milestone.py
├── schemas/referral/
├── crud/referral/
├── services/referral/
└── routes/referral/
```

---

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

### Install a Plugin

```bash
# List available plugins
fcube plugins

# Install with default settings
fcube addplugin <plugin_name>

# Preview changes first
fcube addplugin <plugin_name> --dry-run

# Force overwrite existing files
fcube addplugin <plugin_name> --force
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
  ✓ app/models/referral/referral.py
  ✓ app/models/referral/referral_level.py
  ✓ app/schemas/referral/referral.py
  ✓ app/services/referral/referral_service.py
  ✓ app/routes/referral/referral.py

Would modify files:
  ~ app/apis/v1.py (add router)
  ~ app/core/alembic_models_import.py (add model imports)

No files will be changed (dry run mode)
```

### Post-Installation

After installing a plugin:

1. **Run migrations** to create database tables:
   ```bash
   alembic revision --autogenerate -m "add referral system"
   alembic upgrade head
   ```

2. **Configure** plugin-specific settings in `.env`

3. **Review** the plugin's README for usage instructions

---

## Creating Plugins

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

### Don't

- **Modify core files** — Except for router registration
- **Hardcode values** — Use configuration
- **Break existing code** — Check for conflicts
- **Skip migrations** — Always include model changes

---

## Contributing Plugins

See [Contributing](contributing.md) for guidelines on submitting new plugins to FCube.
