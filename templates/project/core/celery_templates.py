"""
Core Celery Templates.

Generates Celery app configuration and Alembic models import.
"""


def generate_core_celery() -> str:
    """Generate core/celery_app.py for background tasks."""
    return '''"""
Celery Application Configuration

This module configures the Celery application for background task processing.
It follows the application factory pattern and integrates with FastAPI settings.

Task Discovery:
    Tasks are auto-discovered from tasks.py files in each app module.
    Each module should define tasks using @celery_app.task decorator.
"""

import os
from celery import Celery
from celery.signals import worker_ready, worker_shutdown, worker_process_init
from kombu import Exchange, Queue

from .settings import settings
from .logging import get_logger

logger = get_logger(__name__)


def get_installed_apps() -> list:
    """
    Discover all app modules that have tasks.py files.

    Scans the app directory for modules containing tasks.py and returns
    a list of module paths for Celery autodiscovery.

    Returns:
        list: List of app module paths (e.g., ['app.user', 'app.product'])
    """
    app_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)))
    apps = []

    # Scan for directories in app/ that have tasks.py
    for item in os.listdir(app_dir):
        item_path = os.path.join(app_dir, item)
        if os.path.isdir(item_path) and not item.startswith('_'):
            # Check if tasks.py exists in this module
            tasks_file = os.path.join(item_path, 'tasks.py')
            if os.path.exists(tasks_file):
                apps.append(f"app.{item}")
                logger.debug(f"Found tasks in: app.{item}")

    return apps


def create_celery_app() -> Celery:
    """
    Create and configure Celery application.

    Returns:
        Celery: Configured Celery application instance
    """
    celery_app = Celery(
        "worker",
        broker=settings.redis_url,
        backend=settings.redis_url,
    )

    # Configure Celery with settings
    celery_app.conf.update(
        # Task serialization
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="UTC",
        enable_utc=True,

        # Task tracking and execution
        task_track_started=True,
        task_time_limit=300,
        task_soft_time_limit=240,
        task_acks_late=True,
        task_reject_on_worker_lost=True,

        # Worker settings
        worker_prefetch_multiplier=4,
        worker_max_tasks_per_child=1000,
        worker_send_task_events=True,

        # Broker settings
        broker_connection_retry_on_startup=True,
        broker_connection_retry=True,
        broker_pool_limit=10,

        # Result backend settings
        result_expires=3600,
        result_extended=True,

        # Queue configuration
        task_default_queue="default",
        task_default_exchange="default",
        task_default_routing_key="default",

        # Define task queues
        task_queues=(
            Queue("default", Exchange("default"), routing_key="default"),
            Queue("high_priority", Exchange("high_priority"), routing_key="high_priority"),
            Queue("low_priority", Exchange("low_priority"), routing_key="low_priority"),
        ),

        # Task routes - map tasks to specific queues
        task_routes={
            # High priority tasks (emails, notifications)
            "*.tasks.send_*_email": {"queue": "high_priority"},
            "*.tasks.send_notification": {"queue": "high_priority"},
            # Low priority tasks (cleanup, batch operations)
            "*.tasks.cleanup_*": {"queue": "low_priority"},
            "*.tasks.bulk_*": {"queue": "low_priority"},
        },
    )

    # Auto-discover tasks from all app modules that have tasks.py
    installed_apps = get_installed_apps()
    if installed_apps:
        logger.info(f"Auto-discovering tasks from: {', '.join(installed_apps)}")
        celery_app.autodiscover_tasks(installed_apps)
    else:
        logger.warning("No app modules with tasks.py found")

    return celery_app


# Create Celery application instance
celery_app = create_celery_app()


# ==================== Celery Signals ====================

@worker_ready.connect
def on_worker_ready(sender=None, conf=None, **kwargs):
    """Signal handler called when Celery worker is ready."""
    logger.info("=" * 60)
    logger.info("Celery Worker Started Successfully")
    logger.info(f"Broker: {settings.redis_url}")
    logger.info(f"Registered tasks: {list(celery_app.tasks.keys())}")
    logger.info("=" * 60)


@worker_shutdown.connect
def on_worker_shutdown(sender=None, **kwargs):
    """Signal handler called when Celery worker is shutting down."""
    logger.info("=" * 60)
    logger.info("Celery Worker Shutting Down...")
    logger.info("=" * 60)


@worker_process_init.connect
def init_worker_process(**kwargs):
    """
    Reinitialize database engine after worker process fork.

    This is critical for async drivers like asyncpg which are not fork-safe.
    """
    import asyncio
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.pool import NullPool
    from app.core import database

    worker_pid = kwargs.get('pid', os.getpid())
    logger.info(f"Initializing database engine for worker process {worker_pid}")

    try:
        # Dispose of the engine from the parent process
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(database.engine.dispose())

        # Create new engine for this worker process with NullPool
        new_engine = create_async_engine(
            database.get_database_url(),
            echo=settings.DB_ECHO,
            poolclass=NullPool,
            pool_pre_ping=True,
        )

        # Create new session factory
        new_session_factory = sessionmaker(
            new_engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

        # Replace the global engine and session factory
        database.engine = new_engine
        database.async_session_factory = new_session_factory

        logger.info(f"Database engine successfully reinitialized for worker {worker_pid}")

    except Exception as e:
        logger.error(f"Failed to reinitialize database engine for worker {worker_pid}: {e}", exc_info=True)
        raise


# ==================== Helper Functions ====================

def get_task_info(task_id: str) -> dict:
    """
    Get information about a specific task.

    Args:
        task_id: The task ID to query

    Returns:
        dict: Task information including state, result, and metadata
    """
    from celery.result import AsyncResult

    task_result = AsyncResult(task_id, app=celery_app)

    return {
        "task_id": task_id,
        "state": task_result.state,
        "result": task_result.result if task_result.ready() else None,
        "info": task_result.info,
        "successful": task_result.successful() if task_result.ready() else None,
        "failed": task_result.failed() if task_result.ready() else None,
    }


def revoke_task(task_id: str, terminate: bool = False, signal: str = "SIGTERM") -> dict:
    """
    Revoke/cancel a running task.

    Args:
        task_id: The task ID to revoke
        terminate: If True, terminate the task immediately
        signal: Signal to send when terminating (default: SIGTERM)

    Returns:
        dict: Status of the revocation
    """
    celery_app.control.revoke(task_id, terminate=terminate, signal=signal)

    return {
        "task_id": task_id,
        "revoked": True,
        "terminated": terminate,
    }


# Export for convenience
__all__ = ["celery_app", "create_celery_app", "get_task_info", "revoke_task"]
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

