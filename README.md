# 🧊 FCube CLI

> Modern FastAPI Project & Module Generator

FCube CLI is a powerful code generation tool that creates production-ready FastAPI projects and modules following clean architecture principles, dependency injection patterns, and role-based access control.

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![FastAPI](https://img.shields.io/badge/Framework-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)

---

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Commands](#commands)
  - [startproject](#startproject---create-new-project)
  - [adduser](#adduser---add-user-module)
  - [addplugin](#addplugin---add-plugin-modules)
  - [startmodule](#startmodule---create-custom-module)
  - [addentity](#addentity---add-entity-to-module)
  - [listmodules](#listmodules---list-all-modules)
- [Generated Architecture](#generated-architecture)
- [Plugin System](#plugin-system)
- [Contributing](#contributing)
- [CLI Architecture](#cli-architecture)

---

## Features

- **Complete Project Scaffolding** - Generate full FastAPI projects with core infrastructure
- **Modular User System** - Add user module with configurable authentication (email, phone, or both)
- **Plugin Architecture** - Pre-built feature modules with automatic validation
- **Modern Module Structure** - Organized directories for models, schemas, crud, services, routes
- **Docker Support** - docker-compose with PostgreSQL, Redis, Celery, and Flower
- **Alembic Migrations** - Pre-configured async migrations
- **Dependency Injection** - `@lru_cache` singleton services with factory functions
- **Role-Based Routes** - Separate public and admin route directories
- **Permission System** - RBAC with configurable permissions
- **Transaction Management** - "No Commit in CRUD" pattern
- **Rich CLI** - Beautiful terminal output with progress indicators

---

## Installation

### Option 1: Install from GitHub (Recommended)

```bash
# Using pip
pip install git+https://github.com/amal-babu-git/fcube.git

# Using uv (faster)
uv tool install git+https://github.com/amal-babu-git/fcube.git
```

### Option 2: Install from Local Source

```bash
git clone https://github.com/amal-babu-git/fcube.git
cd fcube

# Install globally
pip install .

# Or install in editable mode for development
pip install -e .

# Using uv (recommended for development)
uv sync
source .venv/bin/activate
```

### Option 3: Run Without Installation

```bash
git clone https://github.com/amal-babu-git/fcube.git
cd fcube

# Run using uv
uv run fcube --help

# Or using python module syntax
python -m fcube --help
```

### Verify Installation

```bash
fcube --version
fcube --help
```

---

## Quick Start

```bash
# 1. Create a new project
fcube startproject MyApp

# 2. Navigate to project
cd MyApp

# 3. Add user module with email authentication
fcube adduser --auth-type email

# 4. Add referral plugin
fcube addplugin referral

# 5. Create a custom module
fcube startmodule product

# 6. Start the server
docker compose up -d
```

---

## Commands

| Command | Description |
|---------|-------------|
| `startproject` | Create new FastAPI project with core infrastructure |
| `adduser` | Add user module with configurable authentication |
| `addplugin` | Add pre-built plugin modules |
| `startmodule` | Create a new custom module |
| `addentity` | Add entity to existing module |
| `listmodules` | List all existing modules |
| `version` | Show CLI version |

---

### `startproject` - Create New Project

Creates a new FastAPI project with core infrastructure. User module is **not included by default**.

```bash
# Basic usage
fcube startproject MyProject

# Specify directory
fcube startproject MyApi --dir projects

# Without Celery
fcube startproject SimpleApi --no-celery

# Without Docker
fcube startproject LightApi --no-docker

# Force overwrite
fcube startproject MyProject --force
```

**Options:**
| Option | Description | Default |
|--------|-------------|---------|
| `--dir, -d` | Directory for project | `.` |
| `--celery/--no-celery` | Include Celery | `yes` |
| `--docker/--no-docker` | Include Docker | `yes` |
| `--force, -f` | Overwrite existing files | `no` |

**Generated Structure:**
```
my_project/
├── app/
│   ├── apis/
│   │   └── v1.py
│   └── core/
│       ├── __init__.py
│       ├── database.py
│       ├── models.py
│       ├── settings.py
│       ├── crud.py
│       ├── exceptions.py
│       ├── logging.py
│       ├── main.py
│       ├── dependencies.py
│       ├── alembic_models_import.py
│       └── celery_app.py
├── migrations/
├── docker/
│   ├── Dockerfile
│   └── docker-entrypoint.sh
├── docker-compose.yml
├── alembic.ini
├── pyproject.toml
├── .env.example
├── .gitignore
└── README.md
```

---

### `adduser` - Add User Module

Adds user module with configurable authentication methods.

```bash
# Email/password authentication (default)
fcube adduser

# Phone OTP authentication
fcube adduser --auth-type phone

# Both email and phone authentication
fcube adduser --auth-type both

# Force overwrite
fcube adduser --force
```

**Options:**
| Option | Description | Default |
|--------|-------------|---------|
| `--auth-type, -a` | `email`, `phone`, or `both` | `email` |
| `--dir, -d` | App directory | `app` |
| `--force, -f` | Overwrite existing | `no` |

**Authentication Types:**
| Type | Description | User Fields |
|------|-------------|-------------|
| `email` | Email + password with JWT | `email`, `hashed_password` |
| `phone` | Phone OTP with SMS | `phone_number`, `otp_code` |
| `both` | Combined authentication | All fields + `primary_auth_method` |

**Generated Structure:**
```
app/user/
├── __init__.py
├── models.py
├── schemas.py
├── crud.py
├── exceptions.py
├── auth_management/
│   ├── __init__.py
│   ├── routes.py
│   ├── service.py
│   └── utils.py
├── permission_management/
│   ├── __init__.py
│   ├── utils.py
│   └── scoped_access.py
└── services/
    ├── __init__.py
    └── user_referral_integration.py
```

---

### `addplugin` - Add Plugin Modules

Adds pre-built feature modules to your project.

```bash
# List available plugins
fcube addplugin --list

# Preview plugin (dry run)
fcube addplugin referral --dry-run

# Install plugin
fcube addplugin referral

# Force overwrite
fcube addplugin referral --force
```

**Options:**
| Option | Description | Default |
|--------|-------------|---------|
| `--list, -l` | Show available plugins | - |
| `--dry-run` | Preview without creating files | `no` |
| `--dir, -d` | App directory | `app` |
| `--force, -f` | Overwrite existing | `no` |

**Available Plugins:**
| Plugin | Description | Dependencies |
|--------|-------------|--------------|
| `referral` | User referral system with strategies | `user` |

**Referral Plugin Structure:**
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

**Post-Installation Steps:**
1. Add `referral_code` field to User model
2. Update `app/apis/v1.py` to include referral routes
3. Update `app/core/alembic_models_import.py`
4. Run migrations: `alembic revision --autogenerate && alembic upgrade head`

---

### `startmodule` - Create Custom Module

Creates a new module with complete folder structure.

```bash
# Basic usage
fcube startmodule product

# Without admin routes
fcube startmodule review --no-admin

# Without public routes
fcube startmodule internal_report --no-public

# Force overwrite
fcube startmodule product --force
```

**Options:**
| Option | Description | Default |
|--------|-------------|---------|
| `--dir, -d` | App directory | `app` |
| `--admin/--no-admin` | Include admin routes | `yes` |
| `--public/--no-public` | Include public routes | `yes` |
| `--force, -f` | Overwrite existing | `no` |

**Generated Structure:**
```
app/product/
├── __init__.py
├── dependencies.py
├── exceptions.py
├── permissions.py
├── tasks.py
├── README.md
├── models/
│   ├── __init__.py
│   └── product.py
├── schemas/
│   ├── __init__.py
│   └── product_schemas.py
├── crud/
│   ├── __init__.py
│   └── product_crud.py
├── services/
│   ├── __init__.py
│   └── product_service.py
├── routes/
│   ├── __init__.py
│   ├── public/
│   │   ├── __init__.py
│   │   └── product.py
│   └── admin/
│       ├── __init__.py
│       └── product_management.py
├── utils/
│   └── __init__.py
└── integrations/
    └── __init__.py
```

---

### `addentity` - Add Entity to Module

Adds a new entity to an existing module.

```bash
fcube addentity service_provider availability

fcube addentity booking payment --force
```

Creates model, schema, and CRUD files for a new entity within an existing module.

---

### `listmodules` - List All Modules

```bash
fcube listmodules

fcube listmodules --dir app
```

Shows all existing modules with their structure.

---

## Generated Architecture

FCube follows the **Layered Architecture** pattern:

```
┌─────────────────────────────────────┐
│          Routes (HTTP Layer)        │
│  - Request validation               │
│  - Authentication/Authorization     │
│  - Response serialization           │
└───────────────┬─────────────────────┘
                │
┌───────────────▼─────────────────────┐
│        Services (Business Logic)    │
│  - Business rules                   │
│  - Transaction boundaries           │
│  - Orchestration                    │
└───────────────┬─────────────────────┘
                │
┌───────────────▼─────────────────────┐
│         CRUD (Data Access)          │
│  - Pure database operations         │
│  - NO session.commit()              │
│  - flush() and refresh() only       │
└───────────────┬─────────────────────┘
                │
┌───────────────▼─────────────────────┐
│        Models (Database Schema)     │
│  - SQLAlchemy ORM models            │
│  - Relationships                    │
└─────────────────────────────────────┘
```

### Key Patterns

#### Dependency Injection
```python
# dependencies.py
@lru_cache()
def get_product_service() -> ProductService:
    return ProductService()

# In routes
@router.get("/")
async def list_products(
    service: ProductService = Depends(get_product_service)
):
    ...
```

#### Transaction Management
```python
# CRUD: No commit
async def create(self, session, obj_in):
    db_obj = self.model(**obj_in.model_dump())
    session.add(db_obj)
    await session.flush()
    await session.refresh(db_obj)
    # NO commit here
    return db_obj

# Service: Owns commit
async def create_product(self, session, data):
    product = await product_crud.create(session, obj_in=data)
    await session.commit()
    await session.refresh(product)
    return product
```

#### Permission System
```python
# permissions.py
PRODUCTS_READ = "products:read"
PRODUCTS_WRITE = "products:write"

def require_product_write_permission():
    return require_permission(PRODUCTS_WRITE)

# In routes
@router.post("/", dependencies=[Depends(require_product_write_permission)])
async def create_product(...):
    ...
```

---

## Plugin System

### Overview

The plugin system allows adding pre-built feature modules to any FCube-generated project. Plugins are **self-contained** with their own models, services, routes, and installation logic.

### Architecture

```
plugins/
├── __init__.py          # Registry + validation
└── referral/            # Example plugin
    ├── __init__.py      # PLUGIN_METADATA + installer
    ├── model_templates.py
    ├── schema_templates.py
    ├── crud_templates.py
    ├── service_templates.py
    └── route_templates.py
```

### Plugin Metadata

Each plugin defines its metadata:

```python
PLUGIN_METADATA = PluginMetadata(
    name="referral",
    description="User referral system",
    version="1.0.0",
    dependencies=["user"],
    files_generated=["app/referral/models.py", ...],
    config_required=True,
    post_install_notes="...",
    installer=install_referral_plugin
)
```

### Plugin Validation

Plugins are automatically validated on registration:
- ✅ Name must be valid Python identifier
- ✅ Version must follow semantic versioning (X.Y.Z)
- ✅ Description must be provided
- ✅ Installer function must be callable
- ✅ Post-install notes must be provided
- ✅ Files list must not be empty

### Dry-Run Mode

Preview plugin installation before committing:

```bash
fcube addplugin referral --dry-run
```

Shows:
- All files that would be created
- File sizes
- Whether files would overwrite existing ones
- Post-install steps preview

---

## Contributing

### Adding New Commands

1. Create command file: `fcube/commands/mycommand.py`

```python
from rich.console import Console

console = Console()

def mycommand_command(arg: str):
    console.print(f"Running with: {arg}")
```

2. Register in `fcube/cli.py`:

```python
from .commands.mycommand import mycommand_command

@app.command("mycommand")
def mycommand(arg: str):
    """My custom command."""
    mycommand_command(arg)
```

### Adding New Plugins

1. Create folder: `fcube/templates/plugins/my_plugin/`

2. Add template files:

```python
# model_templates.py
def generate_my_plugin_model() -> str:
    return '''"""MyPlugin model."""
from app.core.models import Base

class MyPlugin(Base):
    __tablename__ = "my_plugins"
'''
```

3. Create `__init__.py` with metadata and installer:

```python
from pathlib import Path
from typing import List, Tuple
from .. import PluginMetadata
from .model_templates import generate_my_plugin_model

def install_my_plugin(app_dir: Path) -> List[Tuple[Path, str]]:
    """Self-contained installer."""
    plugin_dir = app_dir / "my_plugin"
    return [
        (plugin_dir / "__init__.py", '"""MyPlugin module."""'),
        (plugin_dir / "models.py", generate_my_plugin_model()),
    ]

PLUGIN_METADATA = PluginMetadata(
    name="my_plugin",
    description="My awesome plugin",
    version="1.0.0",
    dependencies=[],
    files_generated=[
        "app/my_plugin/__init__.py",
        "app/my_plugin/models.py",
    ],
    config_required=False,
    post_install_notes="Run migrations and start using!",
    installer=install_my_plugin,
)
```

4. Register in `fcube/templates/plugins/__init__.py`:

```python
def _discover_plugins() -> None:
    from .referral import PLUGIN_METADATA as referral_metadata
    from .my_plugin import PLUGIN_METADATA as my_plugin_metadata
    
    register_plugin(referral_metadata)
    register_plugin(my_plugin_metadata)
```

5. Done! Run `fcube addplugin my_plugin`

---

## CLI Architecture

### Design Philosophy

FCube uses **Python functions returning f-strings** for code generation:

- **Simple** - No complex templating engines like Jinja2
- **Fast** - Pure Python, no external template parsing
- **Type-safe** - Full IDE support with type hints
- **Easy to debug** - Just print the function output

### Directory Structure

```
fcube/
├── __init__.py           # Package metadata, version
├── __main__.py           # Entry point for python -m
├── cli.py                # Typer CLI app, command registration
├── commands/             # Command implementations
│   ├── startproject.py   # Project scaffolding
│   ├── adduser.py        # User module generation
│   ├── addplugin.py      # Plugin installation
│   ├── startmodule.py    # Module generation
│   ├── addentity.py      # Entity addition
│   └── listmodules.py    # Module listing
├── templates/            # Code generation templates
│   ├── model_templates.py
│   ├── schema_templates.py
│   ├── crud_templates.py
│   ├── service_templates.py
│   ├── route_templates.py
│   ├── module_templates.py
│   ├── project/          # Project-specific templates
│   │   ├── core/         # Core module templates
│   │   ├── user/         # User module templates
│   │   └── infra/        # Docker, Alembic templates
│   └── plugins/          # Plugin templates
│       ├── __init__.py   # Plugin registry
│       └── referral/     # Referral plugin
└── utils/                # Helper utilities
    └── helpers.py        # File ops, case conversion
```

### How Templates Work

Each template is a Python function that returns a string:

```python
# fcube/templates/model_templates.py

def generate_model(module_snake: str, class_name: str) -> str:
    """Generate a SQLAlchemy model file."""
    return f'''"""
{class_name} database model.
"""

from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.core.models import Base


class {class_name}(Base):
    __tablename__ = "{module_snake}s"
    
    name: Mapped[str] = mapped_column(String(255), nullable=False)
'''
```

Commands import and use these functions:

```python
# fcube/commands/startmodule.py

from ..templates import generate_model

def startmodule_command(module_name: str):
    model_content = generate_model(module_snake, class_name)
    write_file(module_dir / "models.py", model_content)
```

### Plugin System Internal Flow

```
1. Registration (_discover_plugins)
   ↓
2. Validation (validate_plugin_metadata)
   ↓
3. Storage (PLUGIN_REGISTRY)
   ↓
4. Installation (install_plugin → plugin.installer)
   ↓
5. File Creation (write_file)
```

---

## License

MIT License - see [LICENSE](LICENSE) for details.

---

## Author

**Amal Babu**
- GitHub: [@amal-babu-git](https://github.com/amal-babu-git)
- Email: amalbabu1200@gmail.com

---

## Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - The web framework
- [Typer](https://typer.tiangolo.com/) - CLI framework
- [Rich](https://rich.readthedocs.io/) - Terminal formatting
