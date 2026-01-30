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

1. Create folder: `fcube/templates/plugins/your_plugin/`

2. Add `__init__.py` with metadata:
   ```python
   from .. import PluginMetadata
   
   PLUGIN_METADATA = PluginMetadata(
       name="your_plugin",
       description="Description of your plugin",
       version="1.0.0",
       dependencies=["user"],  # Required modules
       files_generated=[...],
       config_required=True,
       post_install_notes="Instructions..."
   )
   ```

3. Create template files for each component

4. Register in `fcube/templates/plugins/__init__.py`

5. Add installer in `fcube/commands/addplugin.py`

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

When adding new templates or commands:

1. Follow existing code patterns
2. Add proper type hints
3. Include docstrings
4. Test with various names (singular, plural, camelCase, snake_case)

---

**Happy coding!**

Created by the Korab Development Team
