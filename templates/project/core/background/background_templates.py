"""
Background Task Framework - Main Module Templates.

Generates the main background/ directory files:
- __init__.py: Public API exports
- celery_app.py: Celery application configuration
- tasks.py: Core system tasks
- README.md: Module documentation
"""


def generate_background_init() -> str:
    """Generate background/__init__.py with public API exports."""
    return '''"""
Background Task Framework

A comprehensive framework for Celery background tasks with:
- Standardized task decorators (@simple_task, @db_task)
- Automatic session and event loop management
- Structured logging with task context
- Performance metrics and monitoring
- Testing utilities

Usage:
    from app.core.background import simple_task, TaskContext

    @simple_task(name="app.user.tasks.send_email", retry_policy="high_priority")
    def send_email(ctx: TaskContext, email: str):
        ctx.log_info(f"Sending email to {email}")
        # ... send email ...
        return ctx.success_result(email_sent=True)

For database tasks:
    from app.core.background import db_task, TaskContext

    @db_task(name="app.booking.tasks.process", retry_policy="standard")
    async def process_booking(ctx: TaskContext, booking_id: str):
        ctx.log_info(f"Processing booking {booking_id}")
        booking = await booking_crud.get(ctx.session, booking_id)
        # ... process booking ...
        # Auto-commit on success
        return ctx.success_result(booking_id=booking_id)

For batch operations (use @db_task with batch utilities):
    @db_task(name="app.provider.tasks.bulk_update", retry_policy="long_running", queue="low_priority")
    async def bulk_update_profiles(ctx: TaskContext, provider_ids: list[str]):
        stats = ctx.create_stats_counter()
        async for batch in ctx.iter_batches(provider_ids, provider_crud, batch_size=50):
            for provider in batch:
                # process provider
                stats.increment("processed")
            await ctx.commit_batch()
        return ctx.success_result(**stats.to_dict())

Optional extras (import separately):
    from app.core.background.extras import CircuitBreaker, CircuitBreakerOpen
"""

# Import celery_app from this module
from .celery_app import celery_app

# Re-export everything from internals for public API
from .internals import (
    # Primary decorators
    simple_task,
    db_task,

    # Core classes
    TaskContext,

    # Exceptions
    TaskException,
    TaskValidationError,
    TaskNotFoundError,
    TaskConfigurationError,
    TaskTimeoutError,
    NON_RETRIABLE_EXCEPTIONS,
    is_retriable_error,

    # Testing
    TaskTestContext,
    mock_task_session,
    run_task_sync,

    # Monitoring
    TaskMetrics,
    Timer,
    StatsCounter,
    log_metric,

    # Advanced - for special cases
    BaseTask,
    DatabaseTask,
    RETRY_POLICIES,
    get_retry_policy,
    get_task_session,
    TaskSessionManager,
    run_with_event_loop,
    get_or_create_event_loop,
    TaskLogger,
)


# Public API - what users should import
__all__ = [
    # Celery app
    "celery_app",

    # Primary decorators
    "simple_task",
    "db_task",

    # Core classes
    "TaskContext",

    # Exceptions
    "TaskException",
    "TaskValidationError",
    "TaskNotFoundError",
    "TaskConfigurationError",
    "TaskTimeoutError",
    "is_retriable_error",
    "NON_RETRIABLE_EXCEPTIONS",

    # Testing
    "TaskTestContext",
    "mock_task_session",
    "run_task_sync",

    # Monitoring
    "TaskMetrics",
    "Timer",
    "StatsCounter",
    "log_metric",

    # Advanced - for special cases
    "BaseTask",
    "DatabaseTask",
    "RETRY_POLICIES",
    "get_retry_policy",
    "get_task_session",
    "TaskSessionManager",
    "run_with_event_loop",
    "get_or_create_event_loop",
    "TaskLogger",
]


# Module version
__version__ = "1.1.0"
'''


def generate_background_celery_app(project_snake: str) -> str:
    """Generate background/celery_app.py with Celery configuration."""
    return f'''"""
Celery Application Configuration

This module configures the Celery application for background task processing.
It follows the application factory pattern and integrates with FastAPI settings.

Task Discovery:
    Tasks are auto-discovered from tasks.py files in each app module:
    - app/user/tasks.py
    - app/product/tasks.py (future)
    - app/order/tasks.py (future)

    Each module should define tasks using @celery_app.task decorator.
"""

import os
from celery import Celery
from celery.signals import worker_ready, worker_shutdown, worker_process_init
from celery.schedules import crontab
from kombu import Exchange, Queue
from app.core.settings import settings
from app.core.logging import get_logger

# Configure logging
logger = get_logger(__name__)


def get_installed_apps() -> list:
    """
    Discover all app modules that have tasks.py files.

    Scans the app directory for modules containing tasks.py and returns
    a list of module paths for Celery autodiscovery.

    Returns:
        list: List of app module paths (e.g., ['app.user', 'app.product'])
    """
    # Go up from app/core/background/celery_app.py to app/
    # __file__ = app/core/background/celery_app.py
    # dirname(__file__) = app/core/background
    # dirname(dirname(__file__)) = app/core
    # dirname(dirname(dirname(__file__))) = app
    app_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    apps = []

    # Directories to exclude from task discovery
    exclude_dirs = {{'core', 'background', '__pycache__'}}

    # Scan for directories in app/ that have tasks.py
    for item in os.listdir(app_dir):
        # Skip excluded directories and private modules
        if item.startswith('_') or item in exclude_dirs:
            continue

        item_path = os.path.join(app_dir, item)
        if os.path.isdir(item_path):
            # Check if tasks.py exists in this module
            tasks_file = os.path.join(item_path, 'tasks.py')
            if os.path.exists(tasks_file):
                apps.append(f"app.{{item}}")
                logger.debug(f"Found tasks in: app.{{item}}")

    return apps


def create_celery_app() -> Celery:
    """
    Create and configure Celery application.

    Returns:
        Celery: Configured Celery application instance
    """
    celery_app = Celery(
        "{project_snake}",
        broker=settings.celery_broker_url,
        backend=settings.celery_result_backend,
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
        task_track_started=settings.CELERY_TASK_TRACK_STARTED,
        task_time_limit=settings.CELERY_TASK_TIME_LIMIT,
        task_soft_time_limit=settings.CELERY_TASK_SOFT_TIME_LIMIT,
        task_acks_late=settings.CELERY_TASK_ACKS_LATE,
        task_reject_on_worker_lost=settings.CELERY_TASK_REJECT_ON_WORKER_LOST,

        # Task compression for large payloads
        task_compression=settings.CELERY_TASK_COMPRESSION if settings.CELERY_TASK_COMPRESSION else None,
        result_compression=settings.CELERY_TASK_COMPRESSION if settings.CELERY_TASK_COMPRESSION else None,

        # Worker settings
        worker_pool=settings.CELERY_WORKER_POOL,
        worker_prefetch_multiplier=settings.CELERY_WORKER_PREFETCH_MULTIPLIER,
        worker_max_tasks_per_child=settings.CELERY_WORKER_MAX_TASKS_PER_CHILD,
        worker_lost_wait=settings.CELERY_WORKER_LOST_WAIT,
        worker_send_task_events=True,
        worker_disable_rate_limits=False,

        # Broker settings
        broker_connection_retry_on_startup=settings.CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP,
        broker_connection_retry=True,
        broker_connection_max_retries=settings.CELERY_BROKER_CONNECTION_MAX_RETRIES,
        broker_pool_limit=10,

        # Result backend settings
        result_expires=settings.CELERY_RESULT_EXPIRES,
        result_extended=True,
        result_backend_thread_safe=settings.CELERY_RESULT_BACKEND_THREAD_SAFE,

        # Task result settings
        task_send_sent_event=True,
        task_ignore_result=False,

        # Queue configuration
        task_default_queue="default",
        task_default_exchange="default",
        task_default_routing_key="default",

        # Define task queues
        task_queues=(
            Queue("default", Exchange("default"), routing_key="default"),
            Queue("high_priority", Exchange("high_priority"),
                  routing_key="high_priority"),
            Queue("low_priority", Exchange("low_priority"),
                  routing_key="low_priority"),
        ),

        # Beat schedule for periodic tasks
        beat_schedule={{
            # Task result cleanup - prevents Redis memory growth
            "cleanup-expired-results-daily": {{
                "task": "app.core.background.tasks.cleanup_expired_task_results",
                "schedule": crontab(hour=3, minute=0),  # Run daily at 3 AM
                "args": (2,),  # Clean results older than 2 days
            }},
            # Example: Add more scheduled tasks here
            # "send-daily-report": {{
            #     "task": "app.reports.tasks.send_daily_report",
            #     "schedule": crontab(hour=9, minute=0),  # 9 AM daily
            # }},
        }},
    )

    # Auto-discover tasks from all app modules that have tasks.py
    installed_apps = get_installed_apps()

    # Also include core background tasks
    installed_apps.append("app.core.background")

    if installed_apps:
        logger.info(
            f"Auto-discovering tasks from: {{', '.join(installed_apps)}}")
        celery_app.autodiscover_tasks(installed_apps)
    else:
        logger.warning("No app modules with tasks.py found")

    return celery_app


# Create Celery application instance
celery_app = create_celery_app()


def discover_and_import_models() -> list:
    """
    Auto-discover and import all SQLAlchemy models.

    This ensures all models are properly registered with SQLAlchemy before
    database operations in worker processes. Import order matters - models
    must be imported in dependency order.

    Returns:
        list: List of imported model module paths

    Raises:
        Exception: If model imports fail
    """
    import importlib
    from pathlib import Path

    # Ordered imports to respect dependencies
    # Add your models here in dependency order (base models first)
    ordered_modules = [
        "app.core.models",              # Base
        # "app.user.models",            # User (referenced by many)
        # Add more models as you create modules
    ]

    imported = []

    for module_path in ordered_modules:
        try:
            module = importlib.import_module(module_path)
            imported.append(module_path)
            logger.debug(f"Imported models from: {{module_path}}")
        except ImportError as e:
            logger.warning(f"Could not import {{module_path}}: {{e}}")
        except Exception as e:
            logger.error(f"Error importing {{module_path}}: {{e}}", exc_info=True)
            raise

    # Auto-discover any additional models not in the ordered list
    app_dir = Path(__file__).parent.parent.parent  # Go up to /app
    for item in app_dir.iterdir():
        if item.is_dir() and not item.name.startswith('_'):
            models_file = item / "models.py"
            if models_file.exists():
                module_path = f"app.{{item.name}}.models"
                if module_path not in imported:
                    try:
                        module = importlib.import_module(module_path)
                        imported.append(module_path)
                        logger.debug(f"Auto-discovered models: {{module_path}}")
                    except ImportError as e:
                        logger.warning(f"Could not import {{module_path}}: {{e}}")
                    except Exception as e:
                        logger.error(
                            f"Error importing {{module_path}}: {{e}}", exc_info=True)

    logger.info(
        f"Imported {{len(imported)}} model modules: {{', '.join(imported)}}")
    return imported


# ==================== Celery Signals ====================

@worker_ready.connect
def on_worker_ready(sender=None, conf=None, **kwargs):
    """Signal handler called when Celery worker is ready."""
    logger.info("=" * 60)
    logger.info("Celery Worker Started Successfully")
    logger.info(f"Broker: {{settings.celery_broker_url}}")
    logger.info(f"Backend: {{settings.celery_result_backend}}")
    logger.info(f"Registered tasks: {{list(celery_app.tasks.keys())}}")
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
    When using prefork worker pool, the parent process creates the database
    engine, but after fork(), the child processes need their own engine
    with fresh connections and event loops.

    This also ensures all SQLAlchemy models are properly imported and
    configured in the worker process.

    This signal is called after each worker process is forked from the parent.
    """
    import asyncio
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    from sqlalchemy.orm import sessionmaker
    from app.core import database

    worker_pid = kwargs.get('pid', os.getpid())
    logger.info(
        f"Initializing database engine for worker process {{worker_pid}}")

    try:
        # CRITICAL: Import all models BEFORE engine initialization
        # This ensures SQLAlchemy mapper configuration works correctly
        # Import order matters - base models first, then dependent models
        try:
            discover_and_import_models()
            logger.debug(
                f"All models imported successfully in worker {{worker_pid}}")
        except Exception as e:
            logger.error(
                f"Failed to import models in worker {{worker_pid}}: {{e}}", exc_info=True)
            raise

        # Dispose of the engine from the parent process
        # This needs to be done synchronously in the forked process
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(database.engine.dispose())
            # Keep the loop open - it will be reused by tasks
            logger.debug(f"Event loop created and set for worker {{worker_pid}}")
        except Exception as e:
            logger.warning(f"Could not dispose parent engine: {{e}}")

        # Create new engine for this worker process
        # Use proper connection pooling with Celery-specific settings
        # The single event loop per worker (created above) works correctly with
        # AsyncAdaptedQueuePool since all async operations in this worker process
        # will use the same loop.
        from sqlalchemy.pool import AsyncAdaptedQueuePool

        new_engine = create_async_engine(
            database.get_database_url(),
            echo=settings.DB_ECHO,
            poolclass=AsyncAdaptedQueuePool,
            pool_size=settings.CELERY_DB_POOL_SIZE,
            max_overflow=settings.CELERY_DB_MAX_OVERFLOW,
            pool_recycle=settings.CELERY_DB_POOL_RECYCLE,
            pool_pre_ping=True,
            pool_timeout=30,
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

        logger.info(
            f"Database engine successfully reinitialized for worker {{worker_pid}}"
        )

    except Exception as e:
        logger.error(
            f"Failed to reinitialize database engine for worker {{worker_pid}}: {{e}}",
            exc_info=True
        )
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

    return {{
        "task_id": task_id,
        "state": task_result.state,
        "result": task_result.result if task_result.ready() else None,
        "info": task_result.info,
        "successful": task_result.successful() if task_result.ready() else None,
        "failed": task_result.failed() if task_result.ready() else None,
    }}


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

    return {{
        "task_id": task_id,
        "revoked": True,
        "terminated": terminate,
    }}


# Export for convenience
__all__ = ["celery_app", "create_celery_app", "get_task_info", "revoke_task"]
'''


def generate_background_tasks() -> str:
    """Generate background/tasks.py with core system tasks."""
    return '''"""
Core Background Tasks (Optional)

This file is for core-level background tasks that don't belong in any specific
app module. Examples include:
- System maintenance tasks
- Administrative tasks
- Cross-module operations
- Infrastructure monitoring

Tasks are auto-discovered by Celery, so you just need to define them here using
the framework decorators.

Example:
    from app.core.background import simple_task, db_task, TaskContext

    @simple_task(
        name="app.core.background.tasks.system_health_check",
        retry_policy="standard",
        queue="low_priority"
    )
    def system_health_check(ctx: TaskContext):
        ctx.log_info("Running system health check")
        # ... check system health ...
        return ctx.success_result(status="healthy")
"""

from app.core.background import simple_task, db_task, TaskContext
from app.core.logging import get_logger

logger = get_logger(__name__)


# ==================== Task Result Cleanup ====================

@simple_task(
    name="app.core.background.tasks.cleanup_expired_task_results",
    retry_policy="standard",
    queue="low_priority"
)
def cleanup_expired_task_results(ctx: TaskContext, days_old: int = 2):
    """
    Clean up expired task results from Redis backend.

    This task prevents Redis memory growth by removing old task results.
    Should be scheduled to run daily via Celery Beat.

    Args:
        ctx: Task context
        days_old: Delete results older than N days (default: 2)

    Returns:
        dict: Cleanup statistics

    Example:
        # Manual trigger
        cleanup_expired_task_results.delay(days_old=2)

        # Scheduled in Celery Beat (celery_app.py):
        beat_schedule = {
            "cleanup-expired-results-daily": {
                "task": "app.core.background.tasks.cleanup_expired_task_results",
                "schedule": crontab(hour=3, minute=0),
                "args": (2,),
            }
        }
    """
    ctx.log_info(f"Starting cleanup of task results older than {days_old} days")

    from datetime import datetime, timedelta
    from app.core.background import celery_app

    try:
        # Calculate cutoff timestamp
        cutoff_time = datetime.utcnow() - timedelta(days=days_old)
        cutoff_timestamp = cutoff_time.timestamp()

        ctx.log_info(f"Cleaning results before {cutoff_time.isoformat()}")

        # Use Celery's backend cleanup
        # This removes expired results efficiently
        backend = celery_app.backend

        # Get count before cleanup for metrics
        try:
            # This is backend-specific, works with Redis
            cleaned = 0
            if hasattr(backend, 'cleanup'):
                # Some backends support cleanup method
                cleaned = backend.cleanup()
            else:
                # Fallback: let expiration handle it
                ctx.log_info("Backend auto-expires results, no manual cleanup needed")
                cleaned = 0

        except Exception as e:
            ctx.log_warning(f"Cleanup method not available: {e}")
            cleaned = 0

        ctx.log_success(
            f"Task result cleanup completed",
            cleaned_count=cleaned,
            cutoff_days=days_old
        )

        return ctx.success_result(
            cleaned_count=cleaned,
            cutoff_days=days_old,
            cutoff_time=cutoff_time.isoformat()
        )

    except Exception as e:
        ctx.log_error(f"Failed to cleanup task results: {e}")
        raise


# ==================== Example Core Tasks ====================

# Uncomment and customize these examples as needed:

# @simple_task(
#     name="app.core.background.tasks.cleanup_old_logs",
#     retry_policy="standard",
#     queue="low_priority"
# )
# def cleanup_old_logs(ctx: TaskContext, days_old: int = 30):
#     """
#     Clean up old log files from the system.
#
#     Args:
#         ctx: Task context
#         days_old: Number of days after which logs should be deleted
#
#     Returns:
#         dict: Cleanup statistics
#     """
#     ctx.log_info(f"Cleaning up logs older than {days_old} days")
#
#     # TODO: Implement log cleanup logic
#     cleaned_count = 0
#
#     ctx.log_success(f"Cleaned up {cleaned_count} old log files")
#     return ctx.success_result(cleaned=cleaned_count, days_old=days_old)


# @db_task(
#     name="app.core.background.tasks.database_maintenance",
#     retry_policy="long_running",
#     queue="low_priority"
# )
# async def database_maintenance(ctx: TaskContext):
#     """
#     Perform database maintenance operations.
#
#     Args:
#         ctx: Task context with database session
#
#     Returns:
#         dict: Maintenance statistics
#     """
#     ctx.log_info("Starting database maintenance")
#
#     # TODO: Implement database maintenance
#     # - VACUUM
#     # - ANALYZE
#     # - Index rebuilding
#
#     ctx.log_success("Database maintenance completed")
#     return ctx.success_result(status="completed")


# ==================== Export Tasks ====================

# Add your tasks to __all__ for explicit exports
__all__ = [
    "cleanup_expired_task_results",
    # "cleanup_old_logs",
    # "database_maintenance",
]
'''


def generate_background_readme() -> str:
    """Generate background/README.md with module documentation."""
    return '''# Background Task Framework

A lean, production-ready Celery framework for async database operations in FastAPI.

## Quick Start

### 1. Create `tasks.py` in Your Module

```python
# app/your_module/tasks.py
from app.core.background import simple_task, db_task, TaskContext

@simple_task(name="your_module.send_notification", retry_policy="standard")
def send_notification(ctx: TaskContext, user_id: str, message: str):
    ctx.log_info(f"Sending notification to {user_id}")
    # ... your logic ...
    return ctx.success_result(sent=True)

@db_task(name="your_module.process_entity", retry_policy="standard")
async def process_entity(ctx: TaskContext, entity_id: str):
    entity = await entity_crud.get(ctx.session, entity_id)
    # ... process entity ...
    # Auto-commits on success
    return ctx.success_result(entity_id=entity_id)
```

### 2. Trigger the Task

```python
from app.your_module.tasks import send_notification
send_notification.delay(user_id="uuid", message="Hello")
```

Tasks are auto-discovered from `tasks.py` files.

---

## Decorators

### `@simple_task` - No Database Access

```python
@simple_task(
    name="module.task_name",      # Required: unique task identifier
    retry_policy="standard",       # standard|aggressive|high_priority|long_running|no_retry
    queue="default"                # default|high_priority|low_priority
)
def my_task(ctx: TaskContext, param1: str):
    ctx.log_info("Processing")
    return ctx.success_result(done=True)
```

**Use for:** Email sending, SMS, external API calls, webhooks

### `@db_task` - With Database Access

```python
@db_task(
    name="module.db_task_name",
    retry_policy="standard",
    queue="default"
)
async def my_db_task(ctx: TaskContext, entity_id: str):
    result = await some_crud.get(ctx.session, entity_id)
    # Auto-commits on success, auto-rollbacks on error
    return ctx.success_result(entity_id=entity_id)
```

**Use for:** Any task needing database read/write

---

## TaskContext API

Every task receives a `TaskContext` as the first parameter:

### Logging
```python
ctx.log_info("Message", extra_field=value)
ctx.log_success("Completed", count=10)
ctx.log_warning("Something concerning")
ctx.log_error("Failed", exc_info=True)
ctx.log_debug("Verbose info")
```

### Validation
```python
user_uuid = ctx.validate_uuid(user_id, "user_id")  # Raises TaskValidationError if invalid
```

### Exceptions (Non-Retriable)
```python
raise ctx.not_found_error("User not found", user_id=user_id)
raise ctx.validation_error("Invalid input", field="email")
raise ctx.config_error("Missing API key")
```

### Results
```python
return ctx.success_result(user_id=user_id, status="created")
# Returns: {"status": "success", "task_id": "...", "user_id": "...", "status": "created"}
```

---

## Batch Operations

Use `@db_task` with batch utilities for bulk operations:

```python
@db_task(
    name="module.bulk_update",
    retry_policy="long_running",
    queue="low_priority"
)
async def bulk_update(ctx: TaskContext, item_ids: list[str]):
    stats = ctx.create_stats_counter()

    async for batch in ctx.iter_batches(item_ids, item_crud, batch_size=50):
        for item in batch:
            # process item
            stats.increment("processed")
        await ctx.commit_batch()

    return ctx.success_result(**stats.to_dict())
```

**Batch utilities available in TaskContext:**
- `ctx.iter_batches(items, crud, batch_size=20)` - Iterate in batches
- `ctx.commit_batch()` - Commit current batch
- `ctx.create_stats_counter()` - Track processing stats
- `ctx.log_progress(**metrics)` - Log progress updates

---

## Queues & Retry Policies

### Queues

| Queue | Use For | Examples |
|-------|---------|----------|
| `high_priority` | Time-sensitive, user-facing | OTP, payment confirmation |
| `default` | Normal operations | Status updates, notifications |
| `low_priority` | Background, can wait | Cleanup, reports, batch jobs |

### Retry Policies

| Policy | Max Retries | Initial Delay | Use For |
|--------|-------------|---------------|---------|
| `standard` | 3 | 60s | Most tasks |
| `aggressive` | 5 | 30s | Critical tasks |
| `high_priority` | 3 | 120s | Time-sensitive |
| `long_running` | 2 | 300s | Batch operations |
| `no_retry` | 0 | - | Idempotency issues |

---

## Error Handling

### Non-Retriable Errors (No Retry)
- `TaskValidationError` - Invalid input
- `TaskNotFoundError` - Missing resource
- `TaskConfigurationError` - Misconfiguration
- `IntegrityError` - DB constraint violation

### Retriable Errors (Auto-Retry)
- `OperationalError` - Connection lost
- `TimeoutError` - Query timeout
- Unknown exceptions

---

## Task Deduplication

Prevent duplicate tasks using custom `task_id`:

```python
# Only one verification email per user at a time
send_verification_email.apply_async(
    args=(user_id, email, code),
    task_id=f"verify-email-{user_id}"
)
```

**Deduplication keys:**
- User notifications: `f"notify-{user_id}"`
- Entity updates: `f"update-{entity_id}"`
- Periodic tasks: `f"daily-{date}"`

---

## Testing

```python
from app.core.background import TaskTestContext, mock_task_session

async def test_my_db_task():
    ctx = TaskTestContext(
        task_id="test-123",
        session=mock_task_session()
    )

    result = await my_db_task(ctx, entity_id="uuid-here")

    assert result["status"] == "success"
    ctx.assert_logged_success()
```

---

## Optional: Circuit Breaker

For external service protection, import from extras:

```python
from app.core.background.extras import CircuitBreaker, CircuitBreakerOpen

email_breaker = CircuitBreaker(name="email_service", failure_threshold=5)

def send_email_task(ctx: TaskContext, ...):
    try:
        result = email_breaker.call(send_email, to=..., subject=...)
        return ctx.success_result(sent=True)
    except CircuitBreakerOpen:
        ctx.log_warning("Email service unavailable")
        raise
```

**Note:** Circuit breaker state is per-worker-process in multi-worker deployments.

---

## Architecture

```
app/core/background/
├── __init__.py          # Public API exports
├── celery_app.py        # Celery configuration & worker signals
├── tasks.py             # Core/system tasks
├── README.md            # <- You are here
├── internals/
│   ├── base.py          # BaseTask, DatabaseTask
│   ├── decorators.py    # @simple_task, @db_task
│   ├── context.py       # TaskContext (unified task interface)
│   ├── session.py       # Async DB session management
│   ├── event_loop.py    # Event loop handling for async in sync workers
│   ├── exceptions.py    # Retriable vs non-retriable errors
│   ├── retry.py         # Predefined retry policies
│   ├── monitoring.py    # TaskMetrics, Timer, StatsCounter
│   ├── logging.py       # TaskLogger
│   └── testing.py       # TaskTestContext, mock utilities
└── extras/
    └── circuit_breaker.py  # Optional circuit breaker pattern
```

---

## Checklist for New Tasks

- [ ] Create `tasks.py` in your module (if not exists)
- [ ] Import: `from app.core.background import simple_task, db_task, TaskContext`
- [ ] Choose decorator: `@simple_task` (no DB) or `@db_task` (with DB)
- [ ] Set unique `name` parameter
- [ ] Choose appropriate `retry_policy` and `queue`
- [ ] Use `ctx.log_*` for logging
- [ ] Use `ctx.validate_uuid()` for UUID parameters
- [ ] Use `ctx.not_found_error()` / `ctx.validation_error()` for failures
- [ ] Return `ctx.success_result(...)` on success
- [ ] Add to `__all__` for explicit exports
'''
