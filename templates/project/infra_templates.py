"""
Infrastructure templates for Docker, Alembic, and project configuration.
"""


def generate_docker_compose(project_name: str, with_celery: bool = True) -> str:
    """Generate docker-compose.yml"""
    celery_services = ""
    if with_celery:
        celery_services = f'''
  # ==================== Celery Worker ====================
  celery_worker:
    build:
      context: .
      dockerfile: docker/Dockerfile
    container_name: {project_name}_celery_worker
    env_file:
      - .env
    environment:
      POSTGRES_HOST: postgres
      POSTGRES_PORT: 5432
      REDIS_HOST: redis
      REDIS_PORT: 6379
    volumes:
      - ./app:/app/app:ro
      - ./logs:/app/logs
    networks:
      - {project_name}_network
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    command: >
      celery -A app.core.celery_app:celery_app worker
      --loglevel=${{LOG_LEVEL:-info}}
      --concurrency=4
    restart: unless-stopped

  # ==================== Flower Monitoring ====================
  flower:
    build:
      context: .
      dockerfile: docker/Dockerfile
    container_name: {project_name}_flower
    env_file:
      - .env
    environment:
      REDIS_HOST: redis
      REDIS_PORT: 6379
    ports:
      - "${{FLOWER_PORT:-5555}}:5555"
    networks:
      - {project_name}_network
    depends_on:
      redis:
        condition: service_healthy
    entrypoint: ["/app/docker/flower-entrypoint.sh"]
    command: >
      celery -A app.core.celery_app:celery_app flower
      --port=5555
      --broker=redis://redis:6379/0
      --basic_auth=${{FLOWER_USERNAME:-admin}}:${{FLOWER_PASSWORD:-flower_password}}
    restart: unless-stopped
'''

    return f'''services:
  # ==================== PostgreSQL Database ====================
  postgres:
    image: postgres:16-alpine
    container_name: {project_name}_postgres
    env_file:
      - .env
    environment:
      POSTGRES_DB: ${{POSTGRES_DB}}
      POSTGRES_USER: ${{POSTGRES_USER}}
      POSTGRES_PASSWORD: ${{POSTGRES_PASSWORD}}
      PGDATA: /var/lib/postgresql/data/pgdata
    ports:
      - "${{POSTGRES_PORT:-5432}}:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - {project_name}_network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${{POSTGRES_USER}} -d ${{POSTGRES_DB}}"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 10s
    restart: unless-stopped

  # ==================== Redis ====================
  redis:
    image: redis:7-alpine
    container_name: {project_name}_redis
    ports:
      - "${{REDIS_PORT:-6379}}:6379"
    volumes:
      - redis_data:/data
    networks:
      - {project_name}_network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped
    command: redis-server --appendonly yes

  # ==================== FastAPI Application ====================
  api:
    build:
      context: .
      dockerfile: docker/Dockerfile
    container_name: {project_name}_api
    env_file:
      - .env
    environment:
      POSTGRES_HOST: postgres
      POSTGRES_PORT: 5432
      REDIS_HOST: redis
      REDIS_PORT: 6379
    ports:
      - "${{API_PORT:-8000}}:8000"
    volumes:
      - ./app:/app/app:ro
      - ./logs:/app/logs
      - ./migrations:/app/migrations
    networks:
      - {project_name}_network
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    command: >
      uvicorn app.core.main:app
      --host 0.0.0.0
      --port 8000
      --reload
      --reload-dir /app/app
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    restart: unless-stopped
{celery_services}
# ==================== Networks ====================
networks:
  {project_name}_network:
    driver: bridge
    name: {project_name}_network

# ==================== Volumes ====================
volumes:
  postgres_data:
    name: {project_name}_postgres_data
  redis_data:
    name: {project_name}_redis_data
'''


def generate_dockerfile() -> str:
    """Generate docker/Dockerfile"""
    return '''# ==================== Multi-stage Dockerfile ====================
# Stage 1: Builder
FROM python:3.13-slim AS builder

ENV PYTHONUNBUFFERED=1 \\
    PYTHONDONTWRITEBYTECODE=1 \\
    PIP_NO_CACHE_DIR=1

RUN apt-get update && apt-get install -y --no-install-recommends \\
    build-essential \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

RUN pip install uv

WORKDIR /app

COPY pyproject.toml ./

RUN uv pip install --system -r pyproject.toml


# ==================== Stage 2: Runtime ====================
FROM python:3.13-slim AS runtime

ENV PYTHONUNBUFFERED=1 \\
    PYTHONDONTWRITEBYTECODE=1

RUN apt-get update && apt-get install -y --no-install-recommends \\
    libpq5 \\
    curl \\
    netcat-openbsd \\
    redis-tools \\
    && rm -rf /var/lib/apt/lists/*

RUN groupadd -r appuser && \\
    useradd -r -g appuser -u 1000 -m appuser

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY --chown=appuser:appuser . .

RUN mkdir -p /app/logs /app/migrations/versions && \\
    chown -R appuser:appuser /app/logs /app/migrations

USER root
RUN chmod +x /app/docker/*.sh 2>/dev/null || true
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=15s --timeout=5s --start-period=60s --retries=10 \\
    CMD curl -f http://localhost:8000/health || exit 1

ENTRYPOINT ["/app/docker/docker-entrypoint.sh"]

CMD ["uvicorn", "app.core.main:app", "--host", "0.0.0.0", "--port", "8000"]
'''


def generate_docker_entrypoint() -> str:
    """Generate docker/docker-entrypoint.sh"""
    return '''#!/bin/bash
# Docker Entrypoint Script

set -e

echo "=========================================="
echo "FastAPI Application Starting..."
echo "Environment: ${ENVIRONMENT:-development}"
echo "=========================================="

# Wait for PostgreSQL
echo "⏳ Waiting for PostgreSQL..."

wait_for_postgres() {
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if python <<END
import asyncio
import asyncpg
import sys

async def check():
    try:
        conn = await asyncpg.connect(
            host='${POSTGRES_HOST}',
            port=${POSTGRES_PORT},
            user='${POSTGRES_USER}',
            password='${POSTGRES_PASSWORD}',
            database='${POSTGRES_DB}',
            timeout=5
        )
        await conn.close()
        return True
    except:
        return False

sys.exit(0 if asyncio.run(check()) else 1)
END
        then
            echo "✓ PostgreSQL is ready!"
            return 0
        fi
        
        echo "  Attempt $attempt/$max_attempts..."
        attempt=$((attempt + 1))
        sleep 2
    done
    
    echo "✗ PostgreSQL connection failed"
    return 1
}

wait_for_postgres || exit 1

# Run migrations
echo ""
echo "🔄 Running database migrations..."

if [ -f "alembic.ini" ] && [ -d "migrations/versions" ]; then
    alembic upgrade head
    echo "✓ Migrations completed"
else
    echo "⚠ No migrations found, skipping"
fi

# Create logs directory
mkdir -p /app/logs || true

echo ""
echo "=========================================="
echo "🚀 Starting application..."
echo "=========================================="

exec "$@"
'''


def generate_celery_entrypoint() -> str:
    """Generate docker/celery-worker-entrypoint.sh"""
    return '''#!/bin/bash
# Celery Worker Entrypoint

set -e

echo "=========================================="
echo "Celery Worker Starting..."
echo "=========================================="

# Wait for Redis
echo "⏳ Waiting for Redis..."
until redis-cli -h ${REDIS_HOST:-redis} -p ${REDIS_PORT:-6379} ping; do
    echo "  Redis not ready, waiting..."
    sleep 2
done
echo "✓ Redis is ready!"

echo ""
echo "🚀 Starting Celery worker..."

exec "$@"
'''


def generate_flower_entrypoint() -> str:
    """Generate docker/flower-entrypoint.sh"""
    return '''#!/bin/bash
# Flower Monitoring Entrypoint

set -e

echo "=========================================="
echo "Flower Monitoring Starting..."
echo "=========================================="

# Wait for Redis
echo "⏳ Waiting for Redis..."
until redis-cli -h ${REDIS_HOST:-redis} -p ${REDIS_PORT:-6379} ping; do
    echo "  Redis not ready, waiting..."
    sleep 2
done
echo "✓ Redis is ready!"

echo ""
echo "🌸 Starting Flower..."

exec "$@"
'''


def generate_alembic_ini() -> str:
    """Generate alembic.ini"""
    return '''# Alembic Configuration

[alembic]
script_location = %(here)s/migrations
file_template = %%(year)d_%%(month).2d_%%(day).2d_%%(hour).2d%%(minute).2d-%%(rev)s_%%(slug)s
prepend_sys_path = .
path_separator = os

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARNING
handlers = console
qualname =

[logger_sqlalchemy]
level = WARNING
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
'''


def generate_alembic_env() -> str:
    """Generate migrations/env.py"""
    return '''"""
Alembic migration environment configuration.
"""

import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context
from dotenv import load_dotenv

from app.core.models import Base
from app.core.alembic_models_import import *
from app.core.database import get_database_url

load_dotenv()

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

DATABASE_URL = get_database_url()
config.set_main_option("sqlalchemy.url", DATABASE_URL)


def run_migrations_offline() -> None:
    """Run migrations in offline mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in online mode with async engine."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
'''


def generate_alembic_script_mako() -> str:
    """Generate migrations/script.py.mako"""
    return '''"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

# revision identifiers, used by Alembic.
revision: str = ${repr(up_revision)}
down_revision: Union[str, None] = ${repr(down_revision)}
branch_labels: Union[str, Sequence[str], None] = ${repr(branch_labels)}
depends_on: Union[str, Sequence[str], None] = ${repr(depends_on)}


def upgrade() -> None:
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    ${downgrades if downgrades else "pass"}
'''


def generate_pyproject_toml(project_name: str, with_celery: bool = True) -> str:
    """Generate pyproject.toml"""
    celery_deps = ""
    if with_celery:
        celery_deps = '''
    "celery>=5.4.0",
    "redis>=5.0.1",
    "flower>=2.0.1",'''

    return f'''[project]
name = "{project_name}"
version = "0.1.0"
description = "FastAPI application generated by FCube CLI"
readme = "README.md"
requires-python = ">=3.11"
dependencies = [
    "alembic>=1.16.0",
    "asyncpg>=0.30.0",
    "fastapi>=0.115.0",
    "pydantic-settings>=2.0.0",
    "python-dotenv>=1.0.0",
    "python-multipart>=0.0.20",
    "sqlalchemy>=2.0.0",
    "uvicorn[standard]>=0.30.0",
    "python-jose[cryptography]>=3.3.0",
    "passlib[bcrypt]>=1.7.4",
    "bcrypt>=4.0.1,<5.0.0",{celery_deps}
    "typer>=0.12.0",
    "rich>=13.0.0",
]
'''


def generate_env_example(project_name: str, with_celery: bool = True) -> str:
    """Generate .env.example"""
    celery_env = ""
    if with_celery:
        celery_env = '''
# ==================== Celery Configuration ====================
CELERY_BROKER_URL=
CELERY_RESULT_BACKEND=

# ==================== Flower Configuration ====================
FLOWER_PORT=5555
FLOWER_USERNAME=admin
FLOWER_PASSWORD=change_me_flower_password
'''

    return f'''# ==================== Environment Configuration ====================
# Copy this file to .env and update with your actual values

# ==================== Application Settings ====================
APP_NAME={project_name.replace("_", " ").title()}
APP_VERSION=0.1.0
ENVIRONMENT=development
DEBUG=true

# ==================== API Settings ====================
API_V1_PREFIX=/api/v1
API_PORT=8000
HOST=0.0.0.0

# ==================== Database Configuration ====================
POSTGRES_USER=fastapi_user
POSTGRES_PASSWORD=change_me_secure_password
POSTGRES_DB={project_name}_db
POSTGRES_HOST=postgres  # Use 'postgres' for Docker, 'localhost' for local
POSTGRES_PORT=5432

# Database Pool Settings
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10
DB_POOL_TIMEOUT=30
DB_ECHO=false

# ==================== Security Settings ====================
# IMPORTANT: Generate strong keys using: python -c "import secrets; print(secrets.token_urlsafe(32))"
SECRET_KEY=your-secret-key-must-be-at-least-32-characters-long
JWT_SECRET_KEY=your-jwt-secret-must-be-at-least-32-characters-long

# ==================== CORS Settings ====================
CORS_ORIGINS=http://localhost:3000,http://localhost:8000

# ==================== Logging ====================
LOG_LEVEL=INFO

# ==================== Redis Configuration ====================
REDIS_HOST=redis  # Use 'redis' for Docker, 'localhost' for local
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=
{celery_env}'''


def generate_gitignore() -> str:
    """Generate .gitignore"""
    return '''# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
.venv/
venv/
ENV/
env/

# IDE
.idea/
.vscode/
*.swp
*.swo
*~

# Environment
.env
.env.local
.env.*.local

# Logs
logs/
*.log

# Database
*.db
*.sqlite3

# Celery
celerybeat-schedule
celerybeat-schedule.*

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/

# Mypy
.mypy_cache/

# Jupyter
.ipynb_checkpoints/

# OS
.DS_Store
Thumbs.db

# Project specific
migrations/versions/*.pyc
'''


def generate_project_readme(
    project_name: str,
    project_pascal: str,
    with_celery: bool = True,
    with_docker: bool = True
) -> str:
    """Generate README.md"""
    docker_section = ""
    if with_docker:
        docker_section = '''
## 🐳 Docker

### Start with Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down
```

### Services

| Service | Port | Description |
|---------|------|-------------|
| API | 8000 | FastAPI application |
| PostgreSQL | 5432 | Database |
| Redis | 6379 | Cache/Celery broker |'''

        if with_celery:
            docker_section += '''
| Celery Worker | - | Background tasks |
| Flower | 5555 | Task monitoring |'''

    celery_section = ""
    if with_celery:
        celery_section = '''
## ⚡ Background Tasks

This project uses Celery for background task processing.

### Start Celery Worker (without Docker)

```bash
celery -A app.core.celery_app:celery_app worker --loglevel=info
```

### Flower Monitoring

Access Flower at: http://localhost:5555
'''

    return f'''# {project_pascal}

> FastAPI application generated by FCube CLI

## 🚀 Quick Start

### 1. Setup Environment

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 2. Install Dependencies

```bash
pip install uv
uv pip install -r pyproject.toml
```

### 3. Start Services

```bash
# With Docker (recommended)
docker-compose up -d postgres redis

# Or run PostgreSQL and Redis locally
```

### 4. Run Migrations

```bash
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

### 5. Start Application

```bash
# Development
uvicorn app.core.main:app --reload

# With Docker
docker-compose up -d
```

### 6. Access API

- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health
{docker_section}
{celery_section}
## 📁 Project Structure

```
{project_name}/
├── app/
│   ├── apis/           # API routers
│   │   └── v1.py       # Version 1 routes
│   ├── core/           # Core infrastructure
│   │   ├── database.py # Database setup
│   │   ├── settings.py # Configuration
│   │   ├── crud.py     # Base CRUD operations
│   │   └── main.py     # FastAPI app
│   └── user/           # User module
│       ├── models.py   # User model
│       ├── schemas.py  # Pydantic schemas
│       ├── crud.py     # User CRUD
│       └── auth_management/
├── migrations/         # Alembic migrations
├── docker/            # Docker configuration
├── docker-compose.yml
└── fcube.py           # Module generator
```

## 🛠️ Creating New Modules

Use FCube CLI to create new modules:

```bash
# Create a new module
python fcube.py startmodule Product

# List all modules
python fcube.py listmodules
```

## 📝 API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register new user |
| POST | `/api/v1/auth/login` | Login user |
| POST | `/api/v1/auth/refresh` | Refresh token |
| GET | `/api/v1/auth/me` | Get current user |

---

Generated by [FCube CLI](https://github.com/your-repo/fcube)
'''


def generate_fcube_script() -> str:
    """Generate fcube.py script for the new project."""
    return '''#!/usr/bin/env python
"""
FCube CLI - Module Generator

Usage:
    python fcube.py startmodule <ModuleName>
    python fcube.py listmodules
"""

# Note: To use FCube CLI in this project, you need to have
# the fcube package installed or available in your path.
#
# For now, you can copy the fcube/ directory from the parent project
# or install it as a package.

try:
    from fcube.cli import app
    
    if __name__ == "__main__":
        app()
except ImportError:
    print("FCube CLI not found. Please install it or copy the fcube/ directory.")
    print("For module generation, use the FCube CLI from your main project.")
'''
