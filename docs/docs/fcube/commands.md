# Commands Reference

Complete reference for all FCube CLI commands.

---

## Global Options

These options are available for all commands:

| Option | Description |
|--------|-------------|
| `--help` | Show help message |
| `--version` | Show FCube version |

---

## startproject

Create a new FastAPI project.

```bash
fcube startproject <project_name> [OPTIONS]
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `project_name` | Yes | Name of the project (creates directory) |

### Options

| Option | Default | Description |
|--------|---------|-------------|
| `--no-git` | False | Skip Git initialization |
| `--no-venv` | False | Skip virtual environment creation |

### Examples

```bash
# Basic project
fcube startproject myapp

# Without Git
fcube startproject myapp --no-git

# Custom location
cd /path/to/projects
fcube startproject myapp
```

### Generated Structure

```
myapp/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── apis/
│   │   ├── __init__.py
│   │   └── v1.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── dependencies.py
│   │   └── security.py
│   ├── models/
│   │   └── __init__.py
│   ├── schemas/
│   │   └── __init__.py
│   ├── services/
│   │   └── __init__.py
│   ├── crud/
│   │   └── __init__.py
│   └── routes/
│       └── __init__.py
├── alembic/
│   ├── versions/
│   ├── env.py
│   └── script.py.mako
├── tests/
│   ├── __init__.py
│   └── conftest.py
├── .env.example
├── .gitignore
├── alembic.ini
├── pyproject.toml
├── requirements.txt
└── README.md
```

---

## addmodule

Add a new module (feature) to the project.

```bash
fcube addmodule <module_name> [OPTIONS]
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `module_name` | Yes | Name of the module (e.g., `products`) |

### Options

| Option | Default | Description |
|--------|---------|-------------|
| `--no-routes` | False | Skip route generation |
| `--no-crud` | False | Skip CRUD generation |
| `--no-service` | False | Skip service generation |

### Examples

```bash
# Full module with all components
fcube addmodule products

# Model and schema only
fcube addmodule products --no-routes --no-crud --no-service

# Multiple modules
fcube addmodule products
fcube addmodule categories
fcube addmodule orders
```

### Generated Files

```
app/
├── models/products.py       # SQLAlchemy model
├── schemas/products.py      # Pydantic schemas
├── crud/products.py         # CRUD operations
├── services/products.py     # Business logic
└── routes/products.py       # API endpoints
```

### Auto-Registration

Routes are automatically added to `app/apis/v1.py`:

```python
from app.routes import products

router.include_router(products.router, prefix="/products", tags=["products"])
```

---

## adduser

Add user authentication module.

```bash
fcube adduser [OPTIONS]
```

### Options

| Option | Default | Description |
|--------|---------|-------------|
| `--jwt` | True | Use JWT authentication |
| `--roles` | True | Include role-based permissions |
| `--refresh` | True | Include refresh token support |

### Examples

```bash
# Full authentication
fcube adduser

# Basic JWT without roles
fcube adduser --no-roles

# JWT only (no refresh tokens)
fcube adduser --no-refresh
```

### Generated Files

```
app/
├── models/user.py           # User model with password hashing
├── schemas/user.py          # Auth schemas (login, register, tokens)
├── crud/user.py             # User CRUD
├── services/user.py         # Auth logic (login, register)
├── routes/auth.py           # Auth endpoints
└── core/
    └── security.py          # JWT utilities, password hashing
```

### Endpoints Added

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/auth/register` | POST | Register new user |
| `/auth/login` | POST | Login and get tokens |
| `/auth/refresh` | POST | Refresh access token |
| `/auth/me` | GET | Get current user |

---

## addplugin

Add a plugin to the project.

```bash
fcube addplugin <plugin_name> [OPTIONS]
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `plugin_name` | Yes | Name of the plugin to install |

### Options

| Option | Default | Description |
|--------|---------|-------------|
| `--dry-run` | False | Preview changes without applying |
| `--force` | False | Overwrite existing files |

### Examples

```bash
# List available plugins
fcube plugins

# Install a plugin
fcube addplugin referral

# Preview what would be installed
fcube addplugin deploy_vps --dry-run

# Force overwrite existing files
fcube addplugin referral --force
```

### Available Plugins

| Plugin | Description |
|--------|-------------|
| `referral` | Referral system with levels and rewards |
| `deploy_vps` | VPS deployment with Docker, Nginx, SSL |

---

## plugins

List available plugins.

```bash
fcube plugins
```

### Output

```
Available Plugins:
──────────────────────────────────────────────────────────────

  referral (v1.0.0)
  Multi-tier referral system with configurable levels and rewards
  
  deploy_vps (v1.0.0)
  Complete VPS deployment with Docker, Nginx, SSL, Redis, Celery

──────────────────────────────────────────────────────────────
Install a plugin with: fcube addplugin <plugin_name>
```

---

## Common Workflows

### New Project Setup

```bash
# Create project
fcube startproject myapp
cd myapp

# Add authentication
fcube adduser --jwt

# Add modules
fcube addmodule products
fcube addmodule orders
fcube addmodule customers

# Set up environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure database
cp .env.example .env
# Edit .env with your settings

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload
```

### Adding Features to Existing Project

```bash
# Navigate to project
cd myapp

# Add new module
fcube addmodule reviews

# Add referral system
fcube addplugin referral

# Run new migrations
alembic revision --autogenerate -m "add reviews and referral"
alembic upgrade head
```

### Preparing for Deployment

```bash
# Add deployment plugin
fcube addplugin deploy_vps

# Configure deployment
cd deploy-vps
./scripts/setup.sh

# Deploy
./scripts/deploy.sh init
```
