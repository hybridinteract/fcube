# Commands Reference

!!! warning "Under Development"
    The FCube CLI is currently under active development. Please do not use it for production projects at this time.

Complete reference for all FCube CLI commands.

---

## Global Options

These options are available for all commands:

| Option | Description |
|--------|-------------|
| `--help` | Show help message |
| `--version` | Show FCube version |

---

## startproject - Create New Project

Creates a new FastAPI project with core infrastructure. User module is **not included by default**.

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
| `--dir, -d` | `.` | Directory for project |
| `--celery/--no-celery` | `yes` | Include Celery |
| `--docker/--no-docker` | `yes` | Include Docker |
| `--force, -f` | `no` | Overwrite existing files |

### Examples

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

### Generated Structure

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

## adduser - Add User Module

Adds user module with configurable authentication methods.

```bash
fcube adduser [OPTIONS]
```

### Options

| Option | Default | Description |
|--------|---------|-------------|
| `--auth-type, -a` | `email` | `email`, `phone`, or `both` |
| `--dir, -d` | `app` | App directory |
| `--force, -f` | `no` | Overwrite existing |

### Authentication Types

| Type | Description | User Fields |
|------|-------------|-------------|
| `email` | Email + password with JWT | `email`, `hashed_password` |
| `phone` | Phone OTP with SMS | `phone_number`, `otp_code` |
| `both` | Combined authentication | All fields + `primary_auth_method` |

### Examples

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

### Generated Structure

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

## addplugin - Add Plugin Modules

Adds pre-built feature modules to your project.

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
| `--list, -l` | - | Show available plugins |
| `--dry-run` | `no` | Preview without creating files |
| `--dir, -d` | `app` | App directory |
| `--force, -f` | `no` | Overwrite existing |

### Examples

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

### Available Plugins

| Plugin | Description | Dependencies |
|--------|-------------|--------------|
| `referral` | User referral system with strategies | `user` |

### Referral Plugin Structure

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

### Post-Installation Steps (Referral Plugin)

1. Add `referral_code` field to User model
2. Update `app/apis/v1.py` to include referral routes
3. Update `app/core/alembic_models_import.py`
4. Run migrations: `alembic revision --autogenerate && alembic upgrade head`

---

## startmodule - Create Custom Module

Creates a new module with complete folder structure.

```bash
fcube startmodule <module_name> [OPTIONS]
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `module_name` | Yes | Name of the module (e.g., `products`) |

### Options

| Option | Default | Description |
|--------|---------|-------------|
| `--dir, -d` | `app` | App directory |
| `--admin/--no-admin` | `yes` | Include admin routes |
| `--public/--no-public` | `yes` | Include public routes |
| `--force, -f` | `no` | Overwrite existing |

### Examples

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

### Generated Structure

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

## addentity - Add Entity to Module

Adds a new entity to an existing module.

```bash
fcube addentity <module_name> <entity_name> [OPTIONS]
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `module_name` | Yes | Name of the existing module |
| `entity_name` | Yes | Name of the entity to add |

### Options

| Option | Default | Description |
|--------|---------|-------------|
| `--force, -f` | `no` | Overwrite existing |

### Examples

```bash
fcube addentity service_provider availability

fcube addentity booking payment --force
```

Creates model, schema, and CRUD files for a new entity within an existing module.

---

## listmodules - List All Modules

Shows all existing modules with their structure.

```bash
fcube listmodules [OPTIONS]
```

### Options

| Option | Default | Description |
|--------|---------|-------------|
| `--dir, -d` | `app` | App directory |

### Examples

```bash
fcube listmodules

fcube listmodules --dir app
```

---

## version - Show CLI Version

Shows the current FCube CLI version.

```bash
fcube version
```

### Examples

```bash
fcube version
# FCube CLI v1.0.0
```

---

## Common Workflows

### New Project Setup

```bash
# Create project
fcube startproject MyApp
cd MyApp

# Add user module with email authentication
fcube adduser --auth-type email

# Add modules
fcube startmodule products
fcube startmodule orders
fcube startmodule customers

# Add referral plugin
fcube addplugin referral

# Set up environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure database
cp .env.example .env
# Edit .env with your settings

# Run Docker services
docker compose up -d

# Run migrations
docker compose exec app alembic upgrade head

# Start server (already running with Docker)
```

### Adding Features to Existing Project

```bash
# Navigate to project
cd MyApp

# Add new module
fcube startmodule reviews

# Add referral system
fcube addplugin referral

# Run new migrations
docker compose exec app alembic revision --autogenerate -m "add reviews and referral"
docker compose exec app alembic upgrade head
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
