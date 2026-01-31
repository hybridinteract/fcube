# 🧊 FCube CLI

> Modern FastAPI Project & Module Generator following Korab Backend Architecture Patterns

FCube CLI is a powerful code generation tool that creates production-ready FastAPI projects and modules following clean architecture principles, dependency injection patterns, and role-based access control.

## Features

- **Complete Project Scaffolding**: Generate full FastAPI projects with core infrastructure
- **Modular User System**: Add user module separately with configurable authentication (email, phone, or both)
- **Plugin Architecture**: Pre-built feature modules (referral system, and more coming)
- **Modern Module Structure**: Organized directories for models, schemas, crud, services, routes
- **Docker Support**: docker-compose with PostgreSQL, Redis, Celery, and Flower
- **Alembic Migrations**: Pre-configured async migrations
- **Dependency Injection**: `@lru_cache` singleton services with factory functions
- **Role-Based Routes**: Separate public and admin route directories
- **Permission System**: RBAC with configurable permissions
- **Transaction Management**: "No Commit in CRUD" pattern
- **Rich CLI**: Beautiful terminal output with progress indicators

## Installation & Usage

FCube can be installed globally on your system for easy access from anywhere, or run directly from source.

### Option 1: Install from GitHub (Recommended)

Install the latest version directly from the GitHub repository:

```bash
# Using pip
pip install git+https://github.com/amal-babu-git/fcube.git

# Using uv (faster)
uv tool install git+https://github.com/amal-babu-git/fcube.git

# Then use the command globally
fcube startproject MyProject
fcube --help
```

### Option 2: Install from Local Source

Clone the repository and install locally:

```bash
# Clone the repository
git clone https://github.com/amal-babu-git/fcube.git
cd fcube

# Install globally using pip
pip install .

# Or install in editable mode for development
pip install -e .

# Using uv (recommended for development)
uv sync  # Creates venv and installs dependencies
source .venv/bin/activate  # Activate the environment
fcube --help
```

### Option 3: Run Without Installation

Run directly as a Python module without global installation:

```bash
# Clone the repository first
git clone https://github.com/amal-babu-git/fcube.git
cd fcube

# Run using uv (handles dependencies automatically)
uv run fcube startproject MyProject

# Or using python module syntax
python -m fcube startproject MyProject
```

### Option 4: Install from PyPI (Coming Soon)

Once published to PyPI, you'll be able to install with:

```bash
# Using pip
pip install fcube

# Using uv
uv tool install fcube
```

### Verify Installation

```bash
fcube --version
fcube --help
```


## Commands Overview

| Command | Description |
|---------|-------------|
| `startproject` | Create new FastAPI project (core infrastructure only) |
| `adduser` | Add user module with configurable authentication |
| `addplugin` | Add pre-built plugin modules (referral, etc.) |
| `startmodule` | Create a new custom module |
| `addentity` | Add entity to existing module |
| `listmodules` | List all existing modules |
| `version` | Show CLI version |

---

## Commands

### `startproject` - Create New Project

Creates a new FastAPI project with core infrastructure. The user module is **not included by default** to give you full control over authentication setup.

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
- `--dir, -d`: Directory for project (default: `.`)
- `--celery/--no-celery`: Include Celery (default: yes)
- `--docker/--no-docker`: Include Docker (default: yes)
- `--force, -f`: Overwrite existing files

**Generated Project Structure:**
```
my_project/
├── app/
│   ├── apis/                 # API routers
│   │   └── v1.py             # Version 1 routes (minimal)
│   └── core/                 # Core infrastructure
│       ├── __init__.py
│       ├── database.py       # Async SQLAlchemy
│       ├── models.py         # Base model classes
│       ├── settings.py       # Pydantic settings
│       ├── crud.py           # Base CRUD operations
│       ├── exceptions.py     # Exception handlers
│       ├── logging.py        # Logging configuration
│       ├── main.py           # FastAPI application
│       ├── dependencies.py   # Shared dependencies
│       ├── alembic_models_import.py
│       └── celery_app.py     # Celery configuration
├── migrations/               # Alembic migrations
├── docker/                   # Docker configuration
│   ├── Dockerfile
│   ├── docker-entrypoint.sh
│   └── ...
├── docker-compose.yml
├── alembic.ini
├── pyproject.toml
├── .env.example
├── .gitignore
├── README.md
└── fcube.py                  # Module generator script
```

**After creating a project:**
```bash
# Navigate to project
cd my_project

# Add user module with your preferred authentication
fcube adduser --auth-type email    # Email/password only
fcube adduser --auth-type phone    # Phone OTP only
fcube adduser --auth-type both     # Both methods
```

---

### `adduser` - Add User Module

Adds the user module with configurable authentication methods. This is separate from `startproject` to give you control over authentication setup.

```bash
# Add with email/password authentication (default)
fcube adduser

# Add with phone OTP authentication
fcube adduser --auth-type phone

# Add with both email and phone authentication
fcube adduser --auth-type both

# Specify directory
fcube adduser --dir my_app

# Force overwrite existing files
fcube adduser --force
```

**Options:**
- `--auth-type, -a`: Authentication type - `email`, `phone`, or `both` (default: `email`)
- `--dir, -d`: Directory containing the app (default: `app`)
- `--force, -f`: Overwrite existing files

**Authentication Types:**

| Type | Description | User Fields |
|------|-------------|-------------|
| `email` | Email + password authentication | `email`, `hashed_password` |
| `phone` | Phone OTP authentication | `phone_number`, `otp_code` |
| `both` | Combined authentication | All fields + `primary_auth_method` |

**Generated User Module Structure:**
```
app/user/
├── __init__.py
├── models.py                 # User, Role, Permission models
├── schemas.py                # Pydantic schemas
├── crud.py                   # User CRUD operations
├── exceptions.py             # User-specific exceptions
├── auth_management/
│   ├── __init__.py
│   ├── routes.py             # Auth endpoints
│   ├── service.py            # Auth business logic
│   └── utils.py              # JWT, OTP utilities
├── permission_management/
│   ├── __init__.py
│   ├── utils.py              # Permission checking
│   └── scoped_access.py      # Resource-level access
└── services/
    ├── __init__.py
    └── user_referral_integration.py  # Referral hooks
```

---

### `addplugin` - Add Plugin Modules

Adds pre-built feature modules to your project. Plugins are self-contained systems with models, services, routes, and all dependencies.

```bash
# List available plugins
fcube addplugin --list

# Add referral plugin
fcube addplugin referral

# Specify directory
fcube addplugin referral --dir my_app

# Force overwrite existing files
fcube addplugin referral --force
```

**Options:**
- `--list, -l`: Show all available plugins
- `--dir, -d`: Directory containing the app (default: `app`)
- `--force, -f`: Overwrite existing files

**Available Plugins:**

| Plugin | Description | Dependencies |
|--------|-------------|--------------|
| `referral` | User referral system with configurable completion strategies | `user` |

#### Referral Plugin

A complete referral system with:
- **Strategy Pattern**: Configurable completion strategies per user type
- **Event-Driven**: Process milestones via events (orders, bookings, etc.)
- **Admin Dashboard**: System-wide statistics and management
- **Celery Tasks**: Async promotion checks

**Generated Structure:**
```
app/referral/
├── __init__.py
├── models.py                 # Referral, ReferralEvent, ReferralSettings
├── config.py                 # Strategy configuration
├── strategies.py             # Completion strategy pattern
├── exceptions.py             # Custom exceptions
├── dependencies.py           # Dependency injection
├── tasks.py                  # Celery background tasks
├── schemas/
│   ├── __init__.py
│   └── referral_schemas.py   # Request/response schemas
├── crud/
│   ├── __init__.py
│   └── referral_crud.py      # Database operations
├── services/
│   ├── __init__.py
│   └── referral_service.py   # Business logic
└── routes/
    ├── __init__.py
    ├── referral_routes.py    # Public endpoints
    └── referral_admin_routes.py  # Admin endpoints
```

**Post-Installation Steps:**

1. Add `referral_code` field to User model:
   ```python
   referral_code: Mapped[Optional[str]] = mapped_column(String(20), unique=True, nullable=True)
   ```

2. Update `app/apis/v1.py` to include referral routes:
   ```python
   from app.referral.routes import referral_router, referral_admin_router
   
   router.include_router(referral_router)
   router.include_router(referral_admin_router)
   ```

3. Update `app/core/alembic_models_import.py`:
   ```python
   from app.referral.models import Referral, ReferralEvent, ReferralSettings
   ```

4. Run migrations:
   ```bash
   alembic revision --autogenerate -m "Add referral tables"
   alembic upgrade head
   ```

---

### `startmodule` - Create New Module

```bash
# Basic usage
fcube startmodule Product

# Specify directory
fcube startmodule Customer --dir app

# Without admin routes
fcube startmodule Review --no-admin

# Without public routes
fcube startmodule InternalReport --no-public

# Force overwrite
fcube startmodule Product --force
```

**Options:**
- `--dir, -d`: Directory for module (default: `app`)
- `--admin/--no-admin`: Include admin routes (default: yes)
- `--public/--no-public`: Include public routes (default: yes)
- `--force, -f`: Overwrite existing files

**Generated Module Structure:**
```
app/product/
├── __init__.py              # Module exports
├── dependencies.py          # DI factories with @lru_cache
├── exceptions.py            # HTTPException-based errors
├── permissions.py           # RBAC permission definitions
├── tasks.py                 # Celery background tasks
├── README.md                # Module documentation
├── models/
│   ├── __init__.py
│   └── product.py           # SQLAlchemy model
├── schemas/
│   ├── __init__.py
│   └── product_schemas.py   # Pydantic v2 schemas
├── crud/
│   ├── __init__.py
│   └── product_crud.py      # Data access (no commit)
├── services/
│   ├── __init__.py
│   └── product_service.py   # Business logic (owns commits)
├── routes/
│   ├── __init__.py          # Route aggregator
│   ├── public/              # Public endpoints
│   │   ├── __init__.py
│   │   └── product.py
│   └── admin/               # Admin endpoints
│       ├── __init__.py
│       └── product_management.py
├── utils/                   # Module utilities
│   └── __init__.py
└── integrations/            # Cross-module facades
    └── __init__.py
```

---

### `addentity` - Add Entity to Module

```bash
# Add a new entity to existing module
fcube addentity service_provider availability

# Force overwrite
fcube addentity booking payment --force
```

Creates model, schema, and CRUD files for a new entity within an existing module.

---

### `listmodules` - List All Modules

```bash
fcube listmodules
```

Shows all existing modules with their structure (modern vs flat).

---

### `version` - Show Version

```bash
fcube version
```

---

## Architecture

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

#### 1. Dependency Injection

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

#### 2. Transaction Management

```python
# CRUD: No commit
async def create(self, session, obj_in):
    db_obj = self.model(**obj_in.model_dump())
    session.add(db_obj)
    await session.flush()      # Get ID
    await session.refresh(db_obj)  # Load data
    # NO commit here
    return db_obj

# Service: Owns commit
async def create_product(self, session, data):
    product = await product_crud.create(session, obj_in=data)
    await session.commit()     # Service commits
    await session.refresh(product)
    return product
```

#### 3. Permissions

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

## CLI Internal Architecture

FCube follows a **simple, fast, and maintainable** approach for code generation:

### Design Philosophy

We use **Python functions that return f-strings** containing the file content to be generated. This approach is:

- **Simple**: No complex templating engines like Jinja2 or Cookiecutter
- **Fast**: Pure Python, no external template parsing
- **Type-safe**: Full IDE support with Python type hints
- **Easy to debug**: Just print the function output to see what will be generated

### Directory Structure

```
fcube/
├── cli.py                    # CLI entry point (Typer app)
├── commands/                 # Command implementations
│   ├── startproject.py       # Project scaffolding
│   ├── startmodule.py        # Module generation
│   ├── adduser.py            # User module (uses templates)
│   └── addplugin.py          # Plugin installer
├── templates/                # Template functions
│   ├── __init__.py           # Template exports
│   ├── model_templates.py    # Model generation functions
│   ├── schema_templates.py   # Schema generation functions
│   ├── crud_templates.py     # CRUD generation functions
│   ├── project/              # Project-specific templates
│   │   ├── core/             # Core module templates
│   │   ├── user/             # User module templates
│   │   └── infra/            # Docker, Alembic templates
│   └── plugins/              # Plugin templates
│       └── referral/         # Referral plugin
└── utils/                    # Helper utilities
    └── helpers.py            # File writing, case conversion
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

Commands import these functions and write their output to files:

```python
# fcube/commands/startmodule.py

from ..templates import generate_model, generate_schemas, generate_crud

def startmodule_command(module_name: str):
    # Generate content using template functions
    model_content = generate_model(module_snake, class_name)
    
    # Write to file
    write_file(module_dir / "models.py", model_content)
```

### Adding New Commands

1. **Create command file**: `fcube/commands/mycommand.py`
2. **Create templates** (if needed): `fcube/templates/mycommand_templates.py`
3. **Register in CLI**: `fcube/cli.py`

### Adding New Plugin Modules

Plugins are **self-contained** - each plugin folder has its own installer function.
No need to modify `addplugin.py`!

1. Create folder: `fcube/templates/plugins/my_plugin/`

2. Add template files (e.g., `model_templates.py`):
   ```python
   def generate_my_plugin_model() -> str:
       return '''"""MyPlugin model."""
   from app.core.models import Base
   
   class MyPlugin(Base):
       __tablename__ = "my_plugins"
   '''
   ```

3. Create `__init__.py` with metadata AND installer:
   ```python
   from pathlib import Path
   from typing import List, Tuple
   from .. import PluginMetadata
   from .model_templates import generate_my_plugin_model
   
   def install_my_plugin(app_dir: Path) -> List[Tuple[Path, str]]:
       """Self-contained installer - returns list of (path, content)."""
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
       files_generated=["app/my_plugin/__init__.py", "app/my_plugin/models.py"],
       config_required=False,
       post_install_notes="Run migrations and start using!",
       installer=install_my_plugin,  # <-- Self-contained!
   )
   ```

4. Register in `fcube/templates/plugins/__init__.py`:
   ```python
   def _discover_plugins() -> None:
       from .referral import PLUGIN_METADATA as referral_metadata
       from .my_plugin import PLUGIN_METADATA as my_plugin_metadata  # Add this
       register_plugin(referral_metadata)
       register_plugin(my_plugin_metadata)  # Add this
   ```

5. Done! Run `fcube addplugin my_plugin`

### Future Considerations

The current f-string approach is intentionally simple and sufficient for most use cases. In the future, we may consider:

- **Git-based templates**: `fcube addplugin --from git@github.com:org/plugin.git` for community plugins
- **Template marketplace**: Centralized registry of community-contributed plugins
- **Interactive scaffolding**: Prompt-based customization during generation

However, for maintainability and simplicity, the current approach is preferred.

---

## What Gets Generated

### Project Level (`startproject`)

| Component | Description |
|-----------|-------------|
| **Core Module** | Database, settings, logging, CRUD base, exceptions |
| **Docker** | Dockerfile, docker-compose, entrypoint scripts |
| **Alembic** | Async migration configuration |
| **Config Files** | pyproject.toml, .env.example, .gitignore |

> **Note:** User module is now added separately via `adduser` command.

### User Module (`adduser`)

| Component | Description |
|-----------|-------------|
| **Models** | User, Role, Permission with RBAC |
| **Auth Management** | JWT, OTP, authentication routes |
| **Permission Management** | RBAC utilities, scoped access |
| **Configurable Auth** | Email, phone, or both |

### Plugin Modules (`addplugin`)

| Plugin | Components |
|--------|------------|
| **Referral** | Models, strategies, services, routes, tasks |

### Custom Modules (`startmodule`)

| Component | Description |
|-----------|-------------|
| **Models** | SQLAlchemy model with timestamps |
| **Schemas** | Pydantic v2 schemas (Base, Create, Update, Response) |
| **CRUD** | Data access layer with no-commit pattern |
| **Services** | Business logic with transaction control |
| **Routes** | Public and admin route separation |
| **Dependencies** | DI factories with singleton pattern |
| **Permissions** | RBAC permission definitions |
| **Exceptions** | HTTPException-based errors |

---

## Customization

### Template Structure

```
fcube/templates/
├── project/                  # Project templates
│   ├── core/                 # Core module templates
│   │   ├── database_templates.py
│   │   ├── settings_templates.py
│   │   ├── crud_templates.py
│   │   └── ...
│   ├── user/                 # User module templates
│   │   ├── model_templates.py
│   │   ├── auth_templates.py
│   │   └── permission_templates.py
│   └── infra/                # Infrastructure templates
│       ├── docker_templates.py
│       ├── alembic_templates.py
│       └── project_templates.py
├── plugins/                  # Plugin templates
│   ├── __init__.py           # Plugin registry
│   └── referral/             # Referral plugin
│       ├── __init__.py
│       ├── model_templates.py
│       └── ...
├── model_templates.py        # Generic model templates
├── schema_templates.py       # Pydantic schemas
├── crud_templates.py         # CRUD operations
├── service_templates.py      # Service layer
├── route_templates.py        # API routes
```

### Adding New Plugins

Plugins are **self-contained**. Each plugin folder contains:
- Template files (`model_templates.py`, `schema_templates.py`, etc.)
- `__init__.py` with `PLUGIN_METADATA` **and** `install_plugin()` function

**No need to modify `addplugin.py`!** Just create your plugin folder and register it.

```
fcube/templates/plugins/your_plugin/
├── __init__.py           # PLUGIN_METADATA + install_your_plugin()
├── model_templates.py    # def generate_your_plugin_model() -> str
├── schema_templates.py   # def generate_your_plugin_schemas() -> str
├── service_templates.py  # def generate_your_plugin_service() -> str
└── route_templates.py    # def generate_your_plugin_routes() -> str
```

See `fcube/templates/plugins/referral/` for a complete example.

### Adding New Commands

1. Create `fcube/commands/mycommand.py`:

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

---

## Quick Start Guide

```bash
# 1. Create a new project
fcube startproject MyApp

# 2. Navigate to project
cd MyApp

# 3. Add user module with email authentication
fcube adduser --auth-type email

# 4. Add referral plugin (optional)
fcube addplugin referral

# 5. Create custom modules
fcube startmodule Product
fcube startmodule Order

# 6. Set up environment
cp .env.example .env
# Edit .env with your database credentials

# 7. Run migrations
alembic upgrade head

# 8. Start the application
docker-compose up -d
# or
uvicorn app.core.main:app --reload
```

---

## Related Documentation

- [PROJECT_ARCHITECTURE_GUIDE.md](../docs/PROJECT_ARCHITECTURE_GUIDE.md) - Full architecture reference
- [ARCHITECTURE.md](../ARCHITECTURE.md) - High-level design principles

## Contributing

FCube is designed to be **easy to contribute to**. The architecture follows a simple pattern that any Python developer can quickly understand.

### Design Philosophy

We use **Python functions that return f-strings** instead of complex templating engines:

```python
def generate_model(name: str) -> str:
    return f'''"""
{name} model.
"""
from app.core.models import Base

class {name}(Base):
    __tablename__ = "{name.lower()}s"
'''
```

**Why this approach?**
- **Simple**: No Jinja2, Cookiecutter, or complex template syntax
- **Fast**: Pure Python string generation
- **Type-safe**: Full IDE autocomplete and type checking
- **Debuggable**: Just `print()` the function output to see what it generates

### Adding a New Plugin (Easiest Way to Contribute)

Each plugin is **self-contained** in its own folder. You don't need to touch `addplugin.py`!

**Step 1: Create the plugin folder**

```bash
mkdir -p fcube/templates/plugins/my_plugin
```

**Step 2: Create template files**

```python
# fcube/templates/plugins/my_plugin/model_templates.py

def generate_my_plugin_model() -> str:
    return '''"""
MyPlugin database model.
"""
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from app.core.models import Base


class MyPlugin(Base):
    __tablename__ = "my_plugins"
    
    name: Mapped[str] = mapped_column(String(255))
'''

def generate_my_plugin_init() -> str:
    return '''"""MyPlugin module."""

from .models import MyPlugin

__all__ = ["MyPlugin"]
'''
```

**Step 3: Create `__init__.py` with metadata AND installer**

```python
# fcube/templates/plugins/my_plugin/__init__.py

from pathlib import Path
from typing import List, Tuple
from .. import PluginMetadata
from .model_templates import generate_my_plugin_model, generate_my_plugin_init


def install_my_plugin(app_dir: Path) -> List[Tuple[Path, str]]:
    """
    Self-contained installer function.
    Returns list of (file_path, file_content) tuples.
    """
    plugin_dir = app_dir / "my_plugin"
    
    return [
        (plugin_dir / "__init__.py", generate_my_plugin_init()),
        (plugin_dir / "models.py", generate_my_plugin_model()),
        # Add more files as needed...
    ]


PLUGIN_METADATA = PluginMetadata(
    name="my_plugin",
    description="Description shown in fcube addplugin --list",
    version="1.0.0",
    dependencies=[],  # e.g., ["user"] if it requires user module
    files_generated=[
        "app/my_plugin/__init__.py",
        "app/my_plugin/models.py",
    ],
    config_required=False,
    post_install_notes="""
1. Update alembic_models_import.py
2. Run migrations
3. Start using!
""",
    installer=install_my_plugin,  # <-- This is the key!
)
```

**Step 4: Register the plugin**

```python
# fcube/templates/plugins/__init__.py

def _discover_plugins() -> None:
    from .referral import PLUGIN_METADATA as referral_metadata
    from .my_plugin import PLUGIN_METADATA as my_plugin_metadata  # Add this line
    
    register_plugin(referral_metadata)
    register_plugin(my_plugin_metadata)  # Add this line
```

**Step 5: Test it!**

```bash
fcube addplugin --list      # Should show your plugin
fcube addplugin my_plugin   # Should install it
```

### Adding a New Command

**Step 1: Create the command file**

```python
# fcube/commands/mycommand.py

import typer
from rich.console import Console

console = Console()

def mycommand_command(
    name: str,
    force: bool = False,
):
    """My custom command implementation."""
    console.print(f"[bold blue]Running mycommand with: {name}[/bold blue]")
    
    # Your logic here...
    
    console.print("[bold green]Done![/bold green]")
```

**Step 2: Register in CLI**

```python
# fcube/cli.py

from .commands.mycommand import mycommand_command

@app.command("mycommand")
def mycommand(
    name: str = typer.Argument(..., help="Name argument"),
    force: bool = typer.Option(False, "--force", "-f", help="Force overwrite"),
):
    """My custom command description."""
    mycommand_command(name, force)
```

### Code Style Guidelines

1. **Follow existing patterns** - Look at similar files for reference
2. **Add type hints** - All functions should have proper type annotations
3. **Include docstrings** - Document what each function does
4. **Test with edge cases** - Try singular/plural, camelCase/snake_case names
5. **Use Rich for output** - `console.print()` with formatting for nice CLI output

### Project Structure Reference

```
fcube/
├── __init__.py           # Package init
├── cli.py                # Typer CLI entry point
├── commands/             # Command implementations
│   ├── startproject.py   # fcube startproject
│   ├── startmodule.py    # fcube startmodule
│   ├── adduser.py        # fcube adduser
│   ├── addplugin.py      # fcube addplugin (generic)
│   └── ...
├── templates/            # Code generation templates
│   ├── model_templates.py      # Generic model templates
│   ├── schema_templates.py     # Generic schema templates
│   ├── project/                # Project-specific templates
│   │   ├── core/               # Core module templates
│   │   ├── user/               # User module templates
│   │   └── infra/              # Docker, Alembic templates
│   └── plugins/                # Plugin templates
│       ├── __init__.py         # Plugin registry
│       └── referral/           # Example: referral plugin
│           ├── __init__.py     # PLUGIN_METADATA + installer
│           ├── model_templates.py
│           └── ...
└── utils/
    └── helpers.py        # File writing, case conversion utilities
```

### Future Roadmap

The current f-string approach is intentionally simple. Future enhancements may include:

- **Git-based templates**: `fcube addplugin --from github.com/org/plugin`
- **Template marketplace**: Community plugin registry
- **Interactive mode**: Prompt-based customization

---

## Related Documentation

- [PROJECT_ARCHITECTURE_GUIDE.md](../docs/PROJECT_ARCHITECTURE_GUIDE.md) - Full architecture reference
- [ARCHITECTURE.md](../ARCHITECTURE.md) - High-level design principles

---

**Happy coding!** 🧊

Created by the Korab Development Team
