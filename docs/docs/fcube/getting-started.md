# Getting Started

!!! warning "Under Development"
    The FCube CLI is currently under active development. Please do not use it for production projects at this time.

Install FCube and create your first project.

---

## Installation

### Prerequisites

- **Python 3.9+** — Check with `python --version`
- **pip** — Usually included with Python
- **Git** — For version control
- **Docker** — For containerized development (optional but recommended)

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
# FCube CLI v1.0.0

fcube --help
```

---

## Create Your First Project

### 1. Generate Project

```bash
# Basic usage
fcube startproject MyApp

# Specify directory
fcube startproject MyApi --dir projects

# Without Celery
fcube startproject SimpleApi --no-celery

# Without Docker
fcube startproject LightApi --no-docker

# Force overwrite
fcube startproject MyProject --force
```

This creates:

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

### 2. Set Up Environment

```bash
cd my_project

# Create virtual environment (optional if using Docker)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: .\venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Database

```bash
# Copy example env
cp .env.example .env

# Edit .env with your database URL
# DATABASE_URL=postgresql://user:pass@localhost:5432/myapp
```

### 4. Run with Docker (Recommended)

```bash
# Start all services
docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs -f
```

### 5. Run Migrations

```bash
# If using Docker
docker compose exec app alembic upgrade head

# If running locally
alembic upgrade head
```

### 6. Start the Server

```bash
# If using Docker
# Server is already running

# If running locally
uvicorn app.main:app --reload
```

Open [http://localhost:8000/docs](http://localhost:8000/docs) — you'll see the Swagger UI!

---

## Add User Module

Add authentication and user management:

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

This adds:

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

## Add a Plugin

Plugins add pre-built features to your project:

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

Learn more in the [Plugin System](plugins.md) guide.

---

## Create a Custom Module

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

This generates:

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

## Add Entity to Module

Add a new entity to an existing module:

```bash
fcube addentity service_provider availability

fcube addentity booking payment --force
```

---

## List Modules

```bash
fcube listmodules

fcube listmodules --dir app
```

Shows all existing modules with their structure.

---

## Next Steps

1. **Learn the commands** — See [Commands Reference](commands.md)
2. **Understand the architecture** — Read [Generated Architecture](architecture.md)
3. **Explore plugins** — Check [Plugin System](plugins.md)
4. **Deploy your app** — Use the `deploy-vps` plugin

---

## Common Issues

### Can't connect to database

```bash
# Check PostgreSQL is running
pg_isready

# Verify DATABASE_URL format
postgresql://user:password@host:port/database
```

### Module not found after generation

```bash
# Ensure you're in virtual environment
source venv/bin/activate

# Reinstall in development mode
pip install -e .
```

### Migrations fail

```bash
# Check alembic.ini has correct sqlalchemy.url
# Or set env variable and run:
alembic upgrade head
```
