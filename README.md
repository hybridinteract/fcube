# 🧊 FCube CLI

> Modern FastAPI Project & Module Generator following Korab Backend Architecture Patterns

FCube CLI is a powerful code generation tool that creates production-ready FastAPI projects and modules following clean architecture principles, dependency injection patterns, and role-based access control.

## ✨ Features

- **Complete Project Scaffolding**: Generate full FastAPI projects with core infrastructure
- **Modern Module Structure**: Organized directories for models, schemas, crud, services, routes
- **User Authentication**: Built-in user module with JWT authentication
- **Docker Support**: docker-compose with PostgreSQL, Redis, Celery, and Flower
- **Alembic Migrations**: Pre-configured async migrations
- **Dependency Injection**: `@lru_cache` singleton services with factory functions
- **Role-Based Routes**: Separate public and admin route directories
- **Permission System**: RBAC with configurable permissions
- **Transaction Management**: "No Commit in CRUD" pattern
- **Rich CLI**: Beautiful terminal output with progress indicators

## 🚀 Installation & Usage

You can install FCube directly from the source or run it as a script.

### Option 1: Install as a Tool (Recommended)

```bash
# From within the directory
pip install .

# Then use the command directly
fcube startproject MyProject
```

### Option 2: Run without Installation

```bash
# Run using python module syntax
python -m fcube startproject MyProject
```

## 📖 Commands

### `startproject` - Create New Project

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
│   ├── apis/           # API routers
│   │   └── v1.py       # Version 1 routes
│   ├── core/           # Core infrastructure
│   │   ├── database.py # Async SQLAlchemy
│   │   ├── settings.py # Pydantic settings
│   │   ├── crud.py     # Base CRUD operations
│   │   ├── main.py     # FastAPI application
│   │   └── ...
│   └── user/           # User module
│       ├── models.py   # User model
│       ├── schemas.py  # Pydantic schemas
│       ├── crud.py     # User CRUD
│       └── auth_management/
│           ├── routes.py   # Auth endpoints
│           ├── service.py  # Auth service
│           └── utils.py    # JWT utilities
├── migrations/         # Alembic migrations
├── docker/            # Docker configuration
│   ├── Dockerfile
│   ├── docker-entrypoint.sh
│   └── ...
├── docker-compose.yml
├── alembic.ini
├── pyproject.toml
├── .env.example
├── .gitignore
├── README.md
└── fcube.py           # Module generator script
```

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

### `addentity` - Add Entity to Module

```bash
# Add a new entity to existing module
fcube addentity service_provider availability

# Force overwrite
fcube addentity booking payment --force
```

Creates model, schema, and CRUD files for a new entity within an existing module.

### `listmodules` - List All Modules

```bash
fcube listmodules
```

Shows all existing modules with their structure (modern vs flat).

### `version` - Show Version

```bash
fcube version
```

## 🏗️ Architecture

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

## 📦 What Gets Generated

### Project Level (`startproject`)

| Component | Description |
|-----------|-------------|
| **Core Module** | Database, settings, logging, CRUD base, exceptions |
| **User Module** | User model, auth routes, JWT utilities |
| **Docker** | Dockerfile, docker-compose, entrypoint scripts |
| **Alembic** | Async migration configuration |
| **Config Files** | pyproject.toml, .env.example, .gitignore |

### Module Level (`startmodule`)

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

## 🔧 Customization

### Adding Custom Templates

Edit files in `fcube/templates/`:

- `templates/project/` - Project templates (core, user, infra)
- `templates/model_templates.py` - SQLAlchemy models
- `templates/schema_templates.py` - Pydantic schemas
- `templates/crud_templates.py` - CRUD operations
- `templates/service_templates.py` - Service layer
- `templates/route_templates.py` - API routes
- `templates/module_templates.py` - Module-level files

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

## 📚 Related Documentation

- [PROJECT_ARCHITECTURE_GUIDE.md](../docs/PROJECT_ARCHITECTURE_GUIDE.md) - Full architecture reference
- [ARCHITECTURE.md](../ARCHITECTURE.md) - High-level design principles

## 🤝 Contributing

When adding new templates or commands:

1. Follow existing code patterns
2. Add proper type hints
3. Include docstrings
4. Test with various names (singular, plural, camelCase, snake_case)

---

**Happy coding! 🚀**

Created by the Korab Development Team
