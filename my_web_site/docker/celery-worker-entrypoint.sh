#!/bin/bash
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
