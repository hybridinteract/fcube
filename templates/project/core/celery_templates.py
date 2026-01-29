"""
Core Celery Templates.

Generates Celery app configuration and Alembic models import.
"""


def generate_core_celery() -> str:
    """Generate core/celery_app.py for background tasks."""
    return '''"""
Celery application configuration.

Provides background task processing with Redis as broker.
"""

from celery import Celery

from .settings import settings

celery_app = Celery(
    "worker",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,
    task_soft_time_limit=240,
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
)

# Auto-discover tasks from all modules
# Add your module names here
celery_app.autodiscover_tasks([
    "app.user",
    # Add more modules as you create them
])
'''


def generate_core_alembic_models() -> str:
    """Generate core/alembic_models_import.py for migration auto-generation."""
    return '''"""
Alembic Models Import

This file imports all models for Alembic autogenerate to detect.
Add imports for all your models here.
"""

# Import Base for metadata
from app.core.models import Base

# Import all models for Alembic autogenerate
from app.user.models import User

# Add more model imports as you create modules:
# from app.product.models import Product
# from app.order.models import Order
'''
