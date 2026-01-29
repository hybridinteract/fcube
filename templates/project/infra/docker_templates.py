"""
Infrastructure Docker Templates.

Generates Docker-related configuration files:
- docker-compose.yml
- Dockerfile
- Entrypoint scripts
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
