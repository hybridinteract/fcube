"""
Background Task Framework - Internals Templates.

Generates the internals/ directory containing the core implementation:
- base.py: BaseTask and DatabaseTask classes
- context.py: TaskContext class
- decorators.py: @simple_task and @db_task decorators
- exceptions.py: Task exception hierarchy
- retry.py: Retry policy configurations
- session.py: Database session management
- event_loop.py: Event loop utilities
- logging.py: TaskLogger class
- monitoring.py: TaskMetrics, Timer, StatsCounter
- testing.py: TaskTestContext and mock utilities
"""


def generate_internals_init() -> str:
    """Generate internals/__init__.py with all exports."""
    return '''"""
Background Task Framework - Core Library

This module contains the internal implementation of the background task framework.
Most users should import from app.core.background instead of this module directly.
"""

# Core decorators
from .decorators import (
    simple_task,
    db_task,
)

# Task context
from .context import TaskContext

# Base task classes
from .base import (
    BaseTask,
    DatabaseTask,
)

# Exceptions
from .exceptions import (
    TaskException,
    TaskValidationError,
    TaskNotFoundError,
    TaskConfigurationError,
    TaskTimeoutError,
    NON_RETRIABLE_EXCEPTIONS,
    is_retriable_error,
)

# Retry policies
from .retry import (
    RETRY_POLICIES,
    get_retry_policy,
)

# Session management
from .session import (
    get_task_session,
    TaskSessionManager,
)

# Event loop utilities
from .event_loop import (
    run_with_event_loop,
    get_or_create_event_loop,
)

# Logging
from .logging import TaskLogger

# Monitoring
from .monitoring import (
    TaskMetrics,
    Timer,
    StatsCounter,
    log_metric,
)

# Testing utilities
from .testing import (
    TaskTestContext,
    mock_task_session,
    run_task_sync,
)


__all__ = [
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
    "NON_RETRIABLE_EXCEPTIONS",
    "is_retriable_error",

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
'''


def generate_internals_base() -> str:
    """Generate internals/base.py with BaseTask and DatabaseTask classes."""
    return '''"""
Base Task Classes

This module provides base classes for all Celery tasks with built-in:
- TaskContext injection
- Automatic metrics tracking
- Standard error handling
- Sentry integration
- Database session management (for DatabaseTask)
- Batch operation support

Hierarchy:
    celery.Task
    └── BaseTask (simple tasks, no DB)
        └── DatabaseTask (async DB operations)
"""

from typing import Any, Callable
from celery import Task
from app.core.logging import get_logger
from .context import TaskContext
from .session import get_task_session
from .event_loop import run_with_event_loop
from .exceptions import TaskException

logger = get_logger(__name__)


class BaseTask(Task):
    """
    Base class for all simple Celery tasks (no database operations).

    Provides:
    - Automatic TaskContext injection as first parameter
    - Standard failure handling with Sentry integration
    - Metrics tracking
    - Structured logging

    Tasks inheriting from this class will receive a TaskContext
    as their first parameter.

    Example:
        @celery_app.task(base=BaseTask, bind=True)
        def my_task(self, ctx: TaskContext, param1, param2):
            ctx.log_info("Processing task")
            # ... task logic ...
            return ctx.success_result(processed=True)
    """

    def __call__(self, *args, **kwargs):
        """
        Override to inject TaskContext before task execution.

        This is called when the task is executed, and we inject
        the TaskContext as the first argument.
        """
        # Create TaskContext
        ctx = TaskContext(
            task=self,
            task_id=self.request.id,
            retry_count=self.request.retries
        )

        # Call the actual task function with context injected
        try:
            ctx.log_debug(f"Task started", **kwargs)
            result = self.run(ctx, *args, **kwargs)
            ctx.metrics.mark_success()
            return result
        except Exception as exc:
            ctx.metrics.mark_failure(exc)
            ctx.log_error(f"Task failed: {exc}")
            raise

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """
        Called when task fails after all retries.

        Provides standardized failure handling and Sentry integration.

        Args:
            exc: The exception raised by the task
            task_id: Unique id of the failed task
            args: Original arguments for the task
            kwargs: Original keyword arguments for the task
            einfo: ExceptionInfo instance with traceback
        """
        logger.error(
            f"Task {self.name} failed permanently: {exc}",
            extra={
                "task_id": task_id,
                "task_name": self.name,
                "error_type": type(exc).__name__,
                "retriable": getattr(exc, "retriable", True) if isinstance(exc, TaskException) else True
            },
            exc_info=True
        )

        # Sentry will automatically capture this via exception handlers
        super().on_failure(exc, task_id, args, kwargs, einfo)

    def on_retry(self, exc, task_id, args, kwargs, einfo):
        """
        Called when task is retried.

        Args:
            exc: The exception that caused the retry
            task_id: Unique id of the task
            args: Original arguments for the task
            kwargs: Original keyword arguments for the task
            einfo: ExceptionInfo instance
        """
        logger.warning(
            f"Task {self.name} retrying due to: {exc}",
            extra={
                "task_id": task_id,
                "task_name": self.name,
                "error_type": type(exc).__name__,
                "retry_count": self.request.retries
            }
        )
        super().on_retry(exc, task_id, args, kwargs, einfo)


class DatabaseTask(BaseTask):
    """
    Base class for tasks requiring database access.

    Automatically manages:
    - Async database session lifecycle
    - Event loop reuse (prevents "attached to different loop" errors)
    - Automatic commit on success
    - Automatic rollback on failure

    The task function receives a TaskContext with `session` populated.

    Example:
        @celery_app.task(base=DatabaseTask, bind=True)
        async def my_db_task(ctx: TaskContext, user_id: str):
            ctx.log_info("Fetching user")
            user = await user_crud.get(ctx.session, user_id)
            # Session auto-commits on success, auto-rollbacks on error
            return ctx.success_result(user_id=str(user.id))
    """

    def __call__(self, *args, **kwargs):
        """
        Override to wrap task execution with async session management.

        This wraps the task function in event loop and session context.
        """
        # Wrap in event loop and session management
        return run_with_event_loop(self._execute_with_session, *args, **kwargs)

    async def _execute_with_session(self, *args, **kwargs):
        """
        Execute task with database session.

        This method:
        1. Creates async database session
        2. Creates TaskContext with session
        3. Executes task function
        4. Commits on success
        5. Rollbacks on error
        """
        async with get_task_session() as session:
            # Create TaskContext with session
            ctx = TaskContext(
                task=self,
                task_id=self.request.id,
                retry_count=self.request.retries,
                session=session
            )

            try:
                ctx.log_debug(f"DB task started", **kwargs)

                # Call the actual task function
                result = await self.run(ctx, *args, **kwargs)

                # Commit the session
                await session.commit()
                ctx.log_debug("Session committed successfully")

                ctx.metrics.mark_success()
                return result

            except Exception as exc:
                # Rollback handled by get_task_session context manager
                ctx.metrics.mark_failure(exc)

                # Check if error should be retried
                from .exceptions import is_retriable_error

                if not is_retriable_error(exc):
                    ctx.log_error(
                        f"DB task failed with non-retriable error: {exc}",
                        error_type=type(exc).__name__,
                        retriable=False
                    )
                    # Don't retry - fail permanently
                    raise
                else:
                    ctx.log_error(
                        f"DB task failed (will retry): {exc}",
                        error_type=type(exc).__name__,
                        retriable=True
                    )
                    # Let Celery retry according to retry policy
                    raise


# Export public API
__all__ = [
    "BaseTask",
    "DatabaseTask",
]
'''


def generate_internals_context() -> str:
    """Generate internals/context.py with TaskContext class."""
    return '''"""
Task Context - Unified Interface for Background Tasks

This module provides the TaskContext class, which is passed as the first
parameter to all background tasks. It provides a unified interface for:
- Structured logging with automatic task context
- Database session access (for DB tasks)
- Input validation helpers
- Result formatting
- Exception raising with clear retriable semantics
- Performance metrics and timing
- Batch operation utilities

TaskContext makes tasks:
- Easier to write (less boilerplate)
- Easier to test (mock the context)
- Easier to debug (structured logging)
- More consistent (standard patterns)
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional, List, AsyncGenerator
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from .logging import TaskLogger
from .monitoring import TaskMetrics, Timer, StatsCounter
from .exceptions import (
    TaskValidationError,
    TaskNotFoundError,
    TaskConfigurationError,
)


@dataclass
class TaskContext:
    """
    Unified context object passed to all background tasks.

    Provides utilities for logging, database access, validation,
    metrics, and error handling with consistent patterns.

    Attributes:
        task: Celery task instance
        task_id: Unique task execution ID
        retry_count: Current retry attempt number
        session: Database session (only for DB tasks)
        _logger: Task logger instance (lazy loaded)
        _metrics: Task metrics instance (lazy loaded)
    """

    task: Any  # Celery Task instance
    task_id: str
    retry_count: int
    session: Optional[AsyncSession] = None
    _logger: Optional[TaskLogger] = None
    _metrics: Optional[TaskMetrics] = None
    _timers: Dict[str, Timer] = field(default_factory=dict)

    @property
    def logger(self) -> TaskLogger:
        """
        Get task logger with automatic context.

        Lazy loaded on first access.

        Returns:
            TaskLogger instance
        """
        if self._logger is None:
            self._logger = TaskLogger(
                task_name=self.task.name,
                task_id=self.task_id,
                retry_count=self.retry_count
            )
        return self._logger

    @property
    def metrics(self) -> TaskMetrics:
        """
        Get task metrics tracker.

        Lazy loaded on first access.

        Returns:
            TaskMetrics instance
        """
        if self._metrics is None:
            self._metrics = TaskMetrics(
                task_name=self.task.name,
                task_id=self.task_id,
                retry_count=self.retry_count
            )
        return self._metrics

    # ==================== Logging Methods ====================

    def log_info(self, message: str, **extra):
        """
        Log info-level message.

        Args:
            message: Log message
            **extra: Additional context fields
        """
        self.logger.info(message, **extra)

    def log_success(self, message: str, **extra):
        """
        Log successful task completion.

        Args:
            message: Success message
            **extra: Additional context (e.g., result data)
        """
        self.logger.success(message, **extra)

    def log_error(self, message: str, exc_info: bool = True, **extra):
        """
        Log error-level message.

        Args:
            message: Error message
            exc_info: Include exception traceback
            **extra: Additional context fields
        """
        self.logger.error(message, exc_info=exc_info, **extra)

    def log_warning(self, message: str, **extra):
        """
        Log warning-level message.

        Args:
            message: Warning message
            **extra: Additional context fields
        """
        self.logger.warning(message, **extra)

    def log_debug(self, message: str, **extra):
        """
        Log debug-level message.

        Args:
            message: Debug message
            **extra: Additional context fields
        """
        self.logger.debug(message, **extra)

    def log_progress(self, **metrics):
        """
        Log progress metrics for long-running tasks.

        Args:
            **metrics: Progress metrics (processed=10, failed=2, etc.)
        """
        self.logger.info(
            f"Progress update",
            **metrics
        )

    # ==================== Result Helpers ====================

    def success_result(self, **data) -> Dict[str, Any]:
        """
        Create standardized success result dictionary.

        Args:
            **data: Additional result data

        Returns:
            Dict with status="success" and task_id

        Example:
            return ctx.success_result(user_id=123, email_sent=True)
        """
        return {
            "status": "success",
            "task_id": self.task_id,
            **data
        }

    def error_result(self, error: str, **data) -> Dict[str, Any]:
        """
        Create standardized error result dictionary.

        Args:
            error: Error message
            **data: Additional error context

        Returns:
            Dict with status="error" and task_id

        Example:
            return ctx.error_result("User not found", user_id=123)
        """
        return {
            "status": "error",
            "task_id": self.task_id,
            "error": error,
            **data
        }

    # ==================== Validation Helpers ====================

    def validate_uuid(self, value: str, field_name: str = "id") -> UUID:
        """
        Validate and convert UUID string.

        Raises TaskValidationError (non-retriable) on invalid format.

        Args:
            value: UUID string to validate
            field_name: Name of the field (for error messages)

        Returns:
            UUID object

        Raises:
            TaskValidationError: If UUID format is invalid

        Example:
            provider_uuid = ctx.validate_uuid(provider_id, "provider_id")
        """
        try:
            return UUID(value)
        except (ValueError, TypeError, AttributeError) as e:
            raise TaskValidationError(
                f"Invalid UUID format for {field_name}: {value}",
                field=field_name,
                value=value
            ) from e

    # ==================== Exception Helpers ====================

    def not_found_error(self, message: str, **context):
        """
        Raise TaskNotFoundError (non-retriable).

        Args:
            message: Error message
            **context: Additional context (entity_id, entity_type, etc.)

        Raises:
            TaskNotFoundError

        Example:
            if not user:
                raise ctx.not_found_error("User not found", user_id=123)
        """
        raise TaskNotFoundError(message, **context)

    def validation_error(self, message: str, **context):
        """
        Raise TaskValidationError (non-retriable).

        Args:
            message: Error message
            **context: Additional context (field, value, etc.)

        Raises:
            TaskValidationError

        Example:
            if age < 0:
                raise ctx.validation_error("Age must be positive", age=age)
        """
        raise TaskValidationError(message, **context)

    def config_error(self, message: str, **context):
        """
        Raise TaskConfigurationError (non-retriable).

        Args:
            message: Error message
            **context: Additional context

        Raises:
            TaskConfigurationError

        Example:
            if not api_key:
                raise ctx.config_error("Missing API key")
        """
        raise TaskConfigurationError(message, **context)

    # ==================== Monitoring/Metrics Helpers ====================

    def start_timer(self, name: str) -> Timer:
        """
        Start a named timer for measuring operation duration.

        Args:
            name: Timer name

        Returns:
            Timer instance

        Example:
            ctx.start_timer("database_query")
            # ... perform query ...
            duration = ctx.end_timer("database_query")
        """
        timer = Timer(name)
        self._timers[name] = timer
        return timer

    def end_timer(self, name: str) -> Optional[float]:
        """
        Stop a named timer and return duration.

        Args:
            name: Timer name

        Returns:
            Duration in seconds, or None if timer not found

        Example:
            duration = ctx.end_timer("database_query")
            ctx.log_info(f"Query took {duration:.2f}s")
        """
        timer = self._timers.get(name)
        if timer:
            duration = timer.stop()
            self.log_debug(f"Timer '{name}' completed", duration=duration)
            return duration
        return None

    def increment_metric(self, name: str, value: int = 1):
        """
        Increment a custom metric counter.

        Args:
            name: Metric name
            value: Amount to increment

        Example:
            ctx.increment_metric("emails_sent")
            ctx.increment_metric("processing_errors", 2)
        """
        self.metrics.add_custom_metric(name, value)

    # ==================== Batch Operation Helpers ====================

    def create_stats_counter(self) -> StatsCounter:
        """
        Create a statistics counter for batch operations.

        Returns:
            StatsCounter instance

        Example:
            stats = ctx.create_stats_counter()
            for item in items:
                if process(item):
                    stats.increment("processed")
                else:
                    stats.increment("failed")
            return ctx.success_result(**stats.to_dict())
        """
        return StatsCounter()

    async def iter_batches(
        self,
        items: Optional[List[Any]],
        crud: Any,
        batch_size: int = 20,
        all_items_query: bool = False
    ) -> AsyncGenerator[List[Any], None]:
        """
        Iterate over items in batches.

        This async generator is safe to exit early (via `break` or exception).
        The database session is managed at the task level, so partial iteration
        does not cause resource leaks.

        Args:
            items: List of items to batch, or None to fetch all
            crud: CRUD object with get_multi method
            batch_size: Number of items per batch
            all_items_query: If True and items is None, fetch all from DB

        Yields:
            List of items in each batch

        Note:
            - When `items` is provided, it slices the in-memory list (no DB calls)
            - When `all_items_query=True`, it fetches from DB using `crud.get_multi()`
            - Early exit (break) is safe - the session is managed by DatabaseTask
            - Always call `await ctx.commit_batch()` after processing each batch

        Example:
            async for batch in ctx.iter_batches(provider_ids, provider_crud, batch_size=50):
                for provider in batch:
                    # Process provider
                    pass
                await ctx.commit_batch()
        """
        if items:
            # Batch provided list
            for i in range(0, len(items), batch_size):
                yield items[i:i + batch_size]
        elif all_items_query and self.session:
            # Fetch all from database in batches
            skip = 0
            while True:
                batch = await crud.get_multi(
                    self.session,
                    skip=skip,
                    limit=batch_size
                )
                if not batch:
                    break
                yield batch
                skip += batch_size
        else:
            # No items to iterate
            return

    async def commit_batch(self):
        """
        Commit current batch to database.

        Example:
            async for batch in ctx.iter_batches(...):
                # Process batch
                await ctx.commit_batch()
        """
        if self.session:
            await self.session.commit()
            self.log_debug("Batch committed")


# Export public API
__all__ = ["TaskContext"]
'''


def generate_internals_decorators() -> str:
    """Generate internals/decorators.py with @simple_task and @db_task decorators."""
    return '''"""
Task Decorators

This module provides easy-to-use decorators for creating Celery tasks
with best practices built-in:
- Automatic retry configuration
- TaskContext injection
- Session management (for DB tasks)
- Structured logging and metrics

Two main decorators:
1. @simple_task - For tasks without database operations
2. @db_task - For tasks with async database operations (includes batch utilities)

Example:
    @simple_task(name="app.user.tasks.send_email", retry_policy="high_priority")
    def send_email(ctx: TaskContext, email: str):
        ctx.log_info(f"Sending email to {email}")
        # ... send email ...
        return ctx.success_result(email_sent=True)
"""

from functools import wraps
from typing import Callable, Any, Optional

# Import celery_app from parent background directory
from ..celery_app import celery_app
from .base import BaseTask, DatabaseTask
from .retry import get_retry_policy


def simple_task(
    name: str,
    retry_policy: str = "standard",
    queue: str = "default",
    **celery_kwargs
) -> Callable:
    """
    Decorator for simple tasks without database dependencies.

    Creates a Celery task with:
    - Automatic TaskContext injection
    - Predefined retry policy
    - Queue-based priority routing
    - Structured logging
    - Metrics tracking

    Args:
        name: Full task name (e.g., "app.user.tasks.send_email")
        retry_policy: Name of retry policy from retry.py (default: "standard")
        queue: Queue name for priority routing (default: "default")
            Options: "default", "high_priority", "low_priority"
        **celery_kwargs: Additional Celery task configuration

    Returns:
        Decorated task function

    Example:
        # High priority task (OTP, password reset)
        @simple_task(
            name="app.user.tasks.send_otp",
            retry_policy="aggressive",
            queue="high_priority"
        )
        def send_otp(ctx: TaskContext, phone: str, code: str):
            ctx.log_info(f"Sending OTP to {phone}")
            result = send_sms(phone, f"Your code: {code}")
            return ctx.success_result(sent=True)

        # Low priority task (cleanup, reports)
        @simple_task(
            name="app.reports.tasks.generate_monthly",
            queue="low_priority"
        )
        def generate_monthly_report(ctx: TaskContext, month: str):
            ctx.log_info(f"Generating report for {month}")
            # ... generate report
            return ctx.success_result(generated=True)
    """
    # Get retry configuration
    retry_config = get_retry_policy(retry_policy)

    def decorator(func: Callable) -> Callable:
        @celery_app.task(
            name=name,
            base=BaseTask,
            bind=True,
            queue=queue,
            **retry_config,
            **celery_kwargs
        )
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            # BaseTask.__call__ handles TaskContext injection
            return func(*args, **kwargs)

        return wrapper

    return decorator


def db_task(
    name: str,
    retry_policy: str = "standard",
    queue: str = "default",
    **celery_kwargs
) -> Callable:
    """
    Decorator for tasks requiring database access.

    Creates a Celery task with:
    - Automatic TaskContext injection with database session
    - Event loop management (reuses worker's loop)
    - Automatic commit on success
    - Automatic rollback on failure
    - Queue-based priority routing
    - Predefined retry policy
    - Structured logging and metrics

    The decorated function MUST be async and will receive a TaskContext
    with `session` populated.

    Args:
        name: Full task name (e.g., "app.booking.tasks.process_booking")
        retry_policy: Name of retry policy from retry.py (default: "standard")
        queue: Queue name for priority routing (default: "default")
            Options: "default", "high_priority", "low_priority"
        **celery_kwargs: Additional Celery task configuration

    Returns:
        Decorated async task function

    Example:
        # High priority booking confirmation
        @db_task(
            name="app.booking.tasks.confirm_booking",
            retry_policy="standard",
            queue="high_priority"
        )
        async def confirm_booking(ctx: TaskContext, booking_id: str):
            ctx.log_info(f"Confirming booking {booking_id}")
            booking = await booking_crud.get(ctx.session, booking_id)
            # ... update booking status
            return ctx.success_result(booking_id=booking_id)

        # Low priority profile calculation
        @db_task(
            name="app.provider.tasks.update_profile",
            queue="low_priority"
        )
        async def update_profile_completion(ctx: TaskContext, provider_id: str):
            provider_uuid = ctx.validate_uuid(provider_id, "provider_id")
            provider = await provider_crud.get(ctx.session, provider_uuid)
            if not provider:
                raise ctx.not_found_error(f"Provider not found")
            await calculate_completion(ctx.session, provider)
            return ctx.success_result(provider_id=provider_id)
    """
    # Get retry configuration
    retry_config = get_retry_policy(retry_policy)

    def decorator(func: Callable) -> Callable:
        @celery_app.task(
            name=name,
            base=DatabaseTask,
            bind=True,
            queue=queue,
            **retry_config,
            **celery_kwargs
        )
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            # DatabaseTask.__call__ handles event loop + session management
            return func(*args, **kwargs)

        return wrapper

    return decorator

# Export public API
__all__ = [
    "simple_task",
    "db_task",
]
'''


def generate_internals_exceptions() -> str:
    """Generate internals/exceptions.py with task exception hierarchy."""
    return '''"""
Background Task Exceptions

This module defines exceptions specific to Celery background tasks,
with clear distinction between retriable and non-retriable errors.

The `retriable` attribute helps the framework decide whether to retry
a failed task or mark it as permanently failed.
"""


class TaskException(Exception):
    """
    Base exception for all background task errors.

    By default, task exceptions are retriable, meaning Celery will
    attempt to retry the task according to the configured retry policy.

    Attributes:
        retriable (bool): Whether this exception should trigger a task retry.
            Default: True
    """

    retriable = True

    def __init__(self, message: str, **context):
        """
        Initialize task exception.

        Args:
            message: Error message describing what went wrong
            **context: Additional context information (entity_id, operation, etc.)
        """
        super().__init__(message)
        self.message = message
        self.context = context

    def __str__(self):
        if self.context:
            context_str = ", ".join(f"{k}={v}" for k, v in self.context.items())
            return f"{self.message} ({context_str})"
        return self.message


class TaskValidationError(TaskException):
    """
    Validation error in task input parameters.

    This error indicates that the task was called with invalid arguments
    (e.g., malformed UUID, missing required fields, invalid data format).

    These errors are NOT retriable because retrying with the same invalid
    input will always fail. The caller should fix the input and retry manually.

    Examples:
        - Invalid UUID format
        - Missing required parameter
        - Invalid email format
        - Out-of-range value
    """

    retriable = False


class TaskNotFoundError(TaskException):
    """
    Resource not found error.

    This error indicates that a required database resource (user, booking,
    provider, etc.) was not found.

    These errors are NOT retriable because retrying won't make the missing
    resource appear. The caller should verify the resource exists before
    triggering the task.

    Examples:
        - User ID doesn't exist
        - Booking not found
        - Service provider not found
    """

    retriable = False


class TaskConfigurationError(TaskException):
    """
    Task misconfiguration error.

    This error indicates that the task itself is incorrectly configured
    (e.g., missing required environment variables, invalid settings,
    missing external service credentials).

    These errors are NOT retriable because the task configuration must
    be fixed before the task can succeed.

    Examples:
        - Missing API key for external service
        - Invalid queue configuration
        - Missing required task parameter default
    """

    retriable = False


class TaskTimeoutError(TaskException):
    """
    Task execution timeout error.

    This error indicates that the task exceeded its time limit
    (soft or hard time limit configured in Celery).

    These errors ARE retriable because the task might succeed if
    executed again (e.g., if the database or external service
    responds faster on retry).

    Examples:
        - Database query timeout
        - External API timeout
        - Long-running computation exceeded limit
    """

    retriable = True


# Database-specific error handling
try:
    from sqlalchemy.exc import (
        OperationalError,
        DatabaseError,
        DisconnectionError,
        TimeoutError as SQLAlchemyTimeoutError,
        IntegrityError,
        DataError,
    )

    # Database errors that should trigger retries (transient errors)
    RETRIABLE_DB_EXCEPTIONS = (
        OperationalError,       # Connection lost, database unavailable
        DisconnectionError,     # Pool disconnection
        SQLAlchemyTimeoutError, # Query timeout
    )

    # Database errors that should NOT be retried (permanent errors)
    NON_RETRIABLE_DB_EXCEPTIONS = (
        IntegrityError,  # Constraint violation, duplicate key
        DataError,       # Data type mismatch, invalid data
    )

except ImportError:
    # SQLAlchemy not available (shouldn't happen, but handle gracefully)
    RETRIABLE_DB_EXCEPTIONS = ()
    NON_RETRIABLE_DB_EXCEPTIONS = ()


# Non-retriable exceptions tuple for easy checking
NON_RETRIABLE_EXCEPTIONS = (
    TaskValidationError,
    TaskNotFoundError,
    TaskConfigurationError,
) + NON_RETRIABLE_DB_EXCEPTIONS


def is_retriable_error(exc: Exception) -> bool:
    """
    Check if an exception should trigger a task retry.

    This function examines the exception type and determines whether
    the task should be retried or marked as permanently failed.

    Args:
        exc: Exception raised by the task

    Returns:
        bool: True if the task should be retried, False otherwise

    Examples:
        >>> is_retriable_error(TaskValidationError("Invalid UUID"))
        False

        >>> is_retriable_error(OperationalError("Connection lost"))
        True

        >>> is_retriable_error(IntegrityError("Duplicate key"))
        False

    Logic:
        1. Non-retriable task exceptions → False
        2. Non-retriable database exceptions → False
        3. Retriable database exceptions → True
        4. TaskException with retriable=False → False
        5. TaskException with retriable=True → True
        6. Unknown exceptions → True (safe default, let retry policy handle)
    """
    # Check if it's a non-retriable task exception
    if isinstance(exc, NON_RETRIABLE_EXCEPTIONS):
        return False

    # Check if it's a retriable database exception
    if RETRIABLE_DB_EXCEPTIONS and isinstance(exc, RETRIABLE_DB_EXCEPTIONS):
        return True

    # Check if it's a TaskException with explicit retriable flag
    if isinstance(exc, TaskException):
        return exc.retriable

    # Default: retry on unknown exceptions
    # This is safer - let the retry policy handle limits
    return True


# Export all exceptions
__all__ = [
    "TaskException",
    "TaskValidationError",
    "TaskNotFoundError",
    "TaskConfigurationError",
    "TaskTimeoutError",
    "NON_RETRIABLE_EXCEPTIONS",
    "RETRIABLE_DB_EXCEPTIONS",
    "NON_RETRIABLE_DB_EXCEPTIONS",
    "is_retriable_error",
]
'''


def generate_internals_retry() -> str:
    """Generate internals/retry.py with retry policy configurations."""
    return '''"""
Retry Policy Configurations

This module defines predefined retry policies for common task patterns.
These policies can be referenced by name in task decorators, making it
easy to apply consistent retry behavior across similar tasks.

Retry policies include:
- Max retry attempts
- Delay between retries
- Exponential backoff configuration
- Jitter to prevent thundering herd

Example:
    @simple_task(name="...", retry_policy="high_priority")
    def send_email(ctx: TaskContext, ...):
        pass
"""

from typing import Dict, Any
from .exceptions import NON_RETRIABLE_EXCEPTIONS


# Predefined retry policies
RETRY_POLICIES: Dict[str, Dict[str, Any]] = {
    "standard": {
        "max_retries": 3,
        "default_retry_delay": 60,  # 1 minute
        "autoretry_for": (Exception,),
        "dont_autoretry_for": NON_RETRIABLE_EXCEPTIONS,
        "retry_backoff": True,
        "retry_backoff_max": 300,  # 5 minutes max delay
        "retry_jitter": True,
    },
    "aggressive": {
        "max_retries": 5,
        "default_retry_delay": 30,  # 30 seconds
        "autoretry_for": (Exception,),
        "dont_autoretry_for": NON_RETRIABLE_EXCEPTIONS,
        "retry_backoff": True,
        "retry_backoff_max": 600,  # 10 minutes max delay
        "retry_jitter": True,
    },
    "high_priority": {
        "max_retries": 3,
        "default_retry_delay": 120,  # 2 minutes
        "autoretry_for": (Exception,),
        "dont_autoretry_for": NON_RETRIABLE_EXCEPTIONS,
        "retry_backoff": True,
        "retry_backoff_max": 600,  # 10 minutes max delay
        "retry_jitter": True,
    },
    "long_running": {
        "max_retries": 2,
        "default_retry_delay": 300,  # 5 minutes
        "autoretry_for": (Exception,),
        "dont_autoretry_for": NON_RETRIABLE_EXCEPTIONS,
        "retry_backoff": True,
        "retry_backoff_max": 900,  # 15 minutes max delay
        "retry_jitter": True,
    },
    "no_retry": {
        "max_retries": 0,
    },
}


def get_retry_policy(policy_name: str) -> Dict[str, Any]:
    """
    Get retry policy configuration by name.

    Args:
        policy_name: Name of the retry policy (e.g., "standard", "aggressive")

    Returns:
        Dict containing Celery retry configuration

    Raises:
        KeyError: If policy_name is not found

    Example:
        retry_config = get_retry_policy("standard")
        # Returns: {"max_retries": 3, "default_retry_delay": 60, ...}
    """
    if policy_name not in RETRY_POLICIES:
        available = ", ".join(RETRY_POLICIES.keys())
        raise KeyError(
            f"Unknown retry policy '{policy_name}'. "
            f"Available policies: {available}"
        )
    return RETRY_POLICIES[policy_name].copy()


# Export public API
__all__ = [
    "RETRY_POLICIES",
    "get_retry_policy",
]
'''


def generate_internals_session() -> str:
    """Generate internals/session.py with database session management."""
    return '''"""
Database Session Management for Background Tasks

This module provides session management utilities specifically designed
for Celery background tasks.

Key differences from FastAPI's get_session():
- Works with NullPool (no connection pooling for workers)
- Reuses worker's event loop (prevents "attached to different loop" errors)
- Skips rollback for validation errors (no DB changes made)
- Designed for background task context, not HTTP request context

The TaskSessionManager ensures:
1. Fresh database connections for each task
2. Proper cleanup even on exceptions
3. Compatibility with async database drivers (asyncpg)
4. No connection pool issues with forked worker processes
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import async_session_factory
from app.core.logging import get_logger
from .exceptions import TaskValidationError, TaskNotFoundError, TaskConfigurationError

logger = get_logger(__name__)


@asynccontextmanager
async def get_task_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Async context manager for database sessions in Celery tasks.

    This provides a fresh database session for each task execution,
    with automatic rollback on errors and cleanup on completion.

    Yields:
        AsyncSession: Database session for the task

    Example:
        async with get_task_session() as session:
            user = await user_crud.get(session, user_id)
            await session.commit()

    Technical Notes:
        - Uses async_session_factory (configured with NullPool in workers)
        - Reuses worker's event loop (from worker_process_init)
        - Skips rollback for validation errors (no DB modifications)
        - Always closes session properly via context manager

    Error Handling:
        - TaskValidationError: No rollback (no DB changes)
        - TaskNotFoundError: No rollback (no DB changes)
        - TaskConfigurationError: No rollback (no DB changes)
        - Other exceptions: Automatic rollback before re-raising
    """
    async with async_session_factory() as session:
        try:
            yield session
        except (TaskValidationError, TaskNotFoundError, TaskConfigurationError):
            # Don't rollback for validation errors - no DB changes were made
            # Just re-raise the exception to let the task fail with proper error type
            raise
        except Exception as e:
            # For all other exceptions, rollback any uncommitted changes
            logger.error(
                f"Task session error, rolling back: {e}",
                exc_info=True,
                extra={"error_type": type(e).__name__}
            )
            await session.rollback()
            raise
        # Note: session.close() is handled by the async_session_factory context manager


class TaskSessionManager:
    """
    Reusable session manager for background tasks.

    This class can be used directly in tasks that need more control
    over session lifecycle, or as a base for custom session managers.

    Example:
        session_manager = TaskSessionManager()
        async with session_manager() as session:
            # Use session
            pass
    """

    @asynccontextmanager
    async def __call__(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Provide async context manager interface.

        This allows TaskSessionManager instances to be used with async with.

        Yields:
            AsyncSession: Database session
        """
        async with get_task_session() as session:
            yield session


# Export public API
__all__ = [
    "get_task_session",
    "TaskSessionManager",
]
'''


def generate_internals_event_loop() -> str:
    """Generate internals/event_loop.py with event loop utilities."""
    return '''"""
Event Loop Management for Background Tasks

This module provides utilities to safely run async functions in Celery tasks.

The key insight: Celery worker processes create a single event loop during
worker_process_init (see app/core/background/celery_app.py). Reusing this loop
with proper connection pooling (AsyncAdaptedQueuePool) provides optimal performance
for async database operations.

Design:
- One event loop per worker process (created in worker_process_init)
- All tasks in the worker reuse this loop
- AsyncAdaptedQueuePool provides connection pooling (3-8 connections per worker)
- Worker process restarts after max_tasks_per_child to prevent memory leaks

IMPORTANT: Never create a new event loop in a task unless absolutely necessary.
Reusing the worker's event loop ensures all async database connections work
correctly across multiple task executions.
"""

import asyncio
from typing import Any, Callable, Coroutine, TypeVar, Union
from app.core.logging import get_logger

logger = get_logger(__name__)

T = TypeVar('T')


def run_with_event_loop(
    async_func: Union[Callable[..., Coroutine[Any, Any, T]], Coroutine[Any, Any, T]],
    *args,
    **kwargs
) -> T:
    """
    Safely run async function in Celery task.

    This function reuses the worker's event loop (created in worker_process_init)
    instead of creating a new one, preventing "attached to different loop" errors
    with async database drivers like asyncpg.

    Args:
        async_func: Either an async function (callable) or coroutine object
        *args: Arguments to pass to async_func (if it's callable)
        **kwargs: Keyword arguments to pass to async_func (if it's callable)

    Returns:
        Result of the async function

    Raises:
        Any exception raised by the async function

    Example:
        # With callable async function
        result = run_with_event_loop(my_async_function, arg1, arg2, kwarg=value)

        # With coroutine object
        coro = my_async_function(arg1, arg2)
        result = run_with_event_loop(coro)

    Technical Notes:
        - Reuses worker's event loop (one per worker process)
        - Falls back to creating new loop only if none exists (shouldn't happen)
        - Does NOT close the loop after execution (shared across all tasks in worker)
        - Works with AsyncAdaptedQueuePool (proper connection pooling)
        - Event loop is disposed when worker process exits via max_tasks_per_child
        - Async generator cleanup happens at worker shutdown, not per-task
    """
    loop = _get_event_loop()

    try:
        # If it's a callable, call it with arguments to get the coroutine
        if callable(async_func):
            coro = async_func(*args, **kwargs)
        else:
            # It's already a coroutine object
            coro = async_func

        # Run the coroutine to completion
        # Note: We do NOT call shutdown_asyncgens() here - that should only
        # happen at worker shutdown, not after each task. Calling it per-task
        # can cause issues with connection pools and async generators.
        return loop.run_until_complete(coro)

    except Exception as e:
        logger.error(
            f"Error running async task: {e}",
            exc_info=True,
            extra={"error_type": type(e).__name__}
        )
        raise


def _get_event_loop() -> asyncio.AbstractEventLoop:
    """
    Get the current event loop in a Python 3.10+ compatible way.

    This handles the deprecation of asyncio.get_event_loop() which will
    raise DeprecationWarning in Python 3.10+ when called outside an
    async context.

    Returns:
        The current or newly created event loop
    """
    try:
        # First, try to get a running loop (only works inside async context)
        return asyncio.get_running_loop()
    except RuntimeError:
        # Not in async context, try to get the current thread's event loop
        pass

    # For worker processes, there should be an event loop set up in
    # worker_process_init. Try to get it without triggering deprecation.
    try:
        # This is the Python 3.10+ safe way to get an existing loop
        loop = asyncio.get_event_loop_policy().get_event_loop()
        if loop.is_closed():
            logger.warning(
                "Event loop is closed, creating new one. "
                "This indicates a problem with worker lifecycle management."
            )
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        else:
            logger.debug(f"Reusing worker event loop: {id(loop)}")
        return loop
    except RuntimeError as e:
        # No event loop exists, create one
        logger.warning(
            f"No event loop found ({e}), creating new one. "
            "This is unexpected in a Celery worker and may indicate a configuration issue."
        )
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        logger.debug(f"Created new event loop: {id(loop)}")
        return loop


def get_or_create_event_loop() -> asyncio.AbstractEventLoop:
    """
    Get the current event loop or create a new one if none exists.

    This is useful for tasks that need direct access to the event loop
    for advanced async operations (e.g., creating tasks, managing futures).

    Returns:
        The current or newly created event loop

    Example:
        loop = get_or_create_event_loop()
        task = loop.create_task(my_coroutine())
        loop.run_until_complete(task)

    Note:
        Prefer run_with_event_loop() for simple async function execution.
        Only use this if you need direct loop access for advanced use cases.
    """
    return _get_event_loop()


# Export public API
__all__ = [
    "run_with_event_loop",
    "get_or_create_event_loop",
]
'''


def generate_internals_logging() -> str:
    """Generate internals/logging.py with TaskLogger class."""
    return '''"""
Structured Logging for Background Tasks

This module provides the TaskLogger class which automatically includes
task context (task_id, task_name, retry_count) in all log messages.

This makes it easy to:
- Track task execution through logs
- Debug production failures
- Aggregate logs by task or entity
- Correlate errors with specific task runs

Example:
    logger = TaskLogger(task_name="booking.process", task_id="123", retry_count=0)
    logger.info("Processing booking", booking_id="abc-123")
    # Output: [123] Processing booking (extra: task_id=123, booking_id=abc-123)
"""

from typing import Any, Dict, Optional
from app.core.logging import get_logger


class TaskLogger:
    """
    Structured logger for Celery tasks.

    Automatically includes task context in all log messages,
    making it easier to track and debug task execution.

    Attributes:
        task_name: Name of the Celery task
        task_id: Unique task execution ID
        retry_count: Current retry attempt number
    """

    def __init__(self, task_name: str, task_id: str, retry_count: int = 0):
        """
        Initialize task logger.

        Args:
            task_name: Name of the Celery task (e.g., "app.user.tasks.send_email")
            task_id: Unique task execution ID from Celery
            retry_count: Current retry attempt (0 for first attempt)
        """
        self.task_name = task_name
        self.task_id = task_id
        self.retry_count = retry_count
        self._logger = get_logger(task_name)

    def _build_extra(self, **kwargs) -> Dict[str, Any]:
        """
        Build extra context dict for logging.

        Combines standard task context with custom context.

        Args:
            **kwargs: Additional context to include in logs

        Returns:
            Dict with all context merged
        """
        return {
            "task_id": self.task_id,
            "task_name": self.task_name,
            "retry_count": self.retry_count,
            **kwargs
        }

    def _format_message(self, message: str) -> str:
        """
        Format log message with task_id prefix.

        Args:
            message: Original log message

        Returns:
            Formatted message with [task_id] prefix
        """
        return f"[{self.task_id}] {message}"

    def info(self, message: str, **extra):
        """
        Log info-level message with task context.

        Args:
            message: Log message
            **extra: Additional context fields
        """
        self._logger.info(
            self._format_message(message),
            extra=self._build_extra(**extra)
        )

    def success(self, message: str, **extra):
        """
        Log successful task completion.

        Args:
            message: Success message
            **extra: Additional context fields (e.g., result data)
        """
        self._logger.info(
            self._format_message(f"SUCCESS: {message}"),
            extra=self._build_extra(status="success", **extra)
        )

    def error(self, message: str, exc_info: bool = True, **extra):
        """
        Log error-level message with task context.

        Args:
            message: Error message
            exc_info: Include exception traceback (default: True)
            **extra: Additional context fields
        """
        self._logger.error(
            self._format_message(f"ERROR: {message}"),
            extra=self._build_extra(status="error", **extra),
            exc_info=exc_info
        )

    def warning(self, message: str, **extra):
        """
        Log warning-level message with task context.

        Args:
            message: Warning message
            **extra: Additional context fields
        """
        self._logger.warning(
            self._format_message(f"WARNING: {message}"),
            extra=self._build_extra(**extra)
        )

    def debug(self, message: str, **extra):
        """
        Log debug-level message with task context.

        Args:
            message: Debug message
            **extra: Additional context fields
        """
        self._logger.debug(
            self._format_message(message),
            extra=self._build_extra(**extra)
        )

    def add_breadcrumb(self, message: str, category: str = "task", **data):
        """
        Add Sentry breadcrumb for task execution tracing.

        Breadcrumbs help track the execution flow leading up to an error.

        Args:
            message: Breadcrumb message
            category: Breadcrumb category (default: "task")
            **data: Additional breadcrumb data
        """
        try:
            from app.core.sentry import add_breadcrumb as sentry_add_breadcrumb
            sentry_add_breadcrumb(
                message=message,
                category=category,
                level="info",
                data={
                    "task_id": self.task_id,
                    "task_name": self.task_name,
                    **data
                }
            )
        except Exception:
            # Don't fail task if Sentry breadcrumb fails
            pass


# Export public API
__all__ = ["TaskLogger"]
'''


def generate_internals_monitoring() -> str:
    """Generate internals/monitoring.py with TaskMetrics, Timer, StatsCounter."""
    return '''"""
Task Monitoring and Metrics

This module provides utilities for tracking task performance, success rates,
and execution patterns. This is essential for:
- Debugging production task failures
- Identifying performance bottlenecks
- Monitoring system health
- Capacity planning

Metrics tracked:
- Task execution duration
- Success/failure counts
- Retry patterns
- Validation error rates

Integration points:
- Currently logs metrics (can be parsed by log aggregation tools)
- Designed to integrate with Prometheus/StatsD/CloudWatch in the future
"""

import time
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from app.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class TaskMetrics:
    """
    Container for task execution metrics.

    Tracks various metrics during task execution that can be
    logged or exported to monitoring systems.

    Attributes:
        task_name: Name of the Celery task
        task_id: Unique task execution ID
        start_time: Task start timestamp (seconds since epoch)
        end_time: Task end timestamp (optional)
        duration: Task execution duration in seconds (optional)
        success: Whether task completed successfully
        retry_count: Number of retries before success/failure
        error_type: Type of exception if task failed
        custom_metrics: Dict of custom metrics specific to the task
    """
    task_name: str
    task_id: str
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    duration: Optional[float] = None
    success: Optional[bool] = None
    retry_count: int = 0
    error_type: Optional[str] = None
    custom_metrics: Dict[str, Any] = field(default_factory=dict)

    def mark_success(self):
        """Mark task as successfully completed and calculate duration."""
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time
        self.success = True
        self._log_completion()

    def mark_failure(self, error: Exception):
        """
        Mark task as failed and calculate duration.

        Args:
            error: The exception that caused the failure
        """
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time
        self.success = False
        self.error_type = type(error).__name__
        self._log_completion()

    def add_custom_metric(self, name: str, value: Any):
        """
        Add a custom metric specific to this task execution.

        Args:
            name: Metric name
            value: Metric value

        Example:
            metrics.add_custom_metric("emails_sent", 10)
            metrics.add_custom_metric("processing_errors", 2)
        """
        self.custom_metrics[name] = value

    def _log_completion(self):
        """Log task completion metrics."""
        status = "SUCCESS" if self.success else "FAILURE"
        logger.info(
            f"Task {status}: {self.task_name}",
            extra={
                "task_id": self.task_id,
                "task_name": self.task_name,
                "duration_seconds": self.duration,
                "success": self.success,
                "retry_count": self.retry_count,
                "error_type": self.error_type,
                "metric_type": "task_completion",
                **self.custom_metrics
            }
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Export metrics as dictionary.

        Returns:
            Dict containing all metrics

        Example:
            metrics_dict = metrics.to_dict()
            # Send to external monitoring system
        """
        return {
            "task_name": self.task_name,
            "task_id": self.task_id,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.duration,
            "success": self.success,
            "retry_count": self.retry_count,
            "error_type": self.error_type,
            **self.custom_metrics
        }


class Timer:
    """
    Simple timer for measuring operation durations within tasks.

    Example:
        timer = Timer("database_query")
        # ... perform query ...
        duration = timer.stop()
    """

    def __init__(self, name: str):
        """
        Initialize timer.

        Args:
            name: Name/label for this timer
        """
        self.name = name
        self.start_time = time.time()
        self.end_time: Optional[float] = None
        self.duration: Optional[float] = None

    def stop(self) -> float:
        """
        Stop timer and return duration.

        Returns:
            Duration in seconds
        """
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time
        return self.duration

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - automatically stop timer."""
        self.stop()
        return False


class StatsCounter:
    """
    Simple counter for tracking statistics during batch operations.

    Example:
        stats = StatsCounter()
        for item in items:
            if process(item):
                stats.increment("processed")
            else:
                stats.increment("failed")
        print(stats.to_dict())  # {"processed": 100, "failed": 5}
    """

    def __init__(self):
        """Initialize empty stats counter."""
        self._counts: Dict[str, int] = {}

    def increment(self, key: str, amount: int = 1):
        """
        Increment counter by given amount.

        Args:
            key: Counter key/name
            amount: Amount to increment (default: 1)
        """
        self._counts[key] = self._counts.get(key, 0) + amount

    def get(self, key: str, default: int = 0) -> int:
        """
        Get counter value.

        Args:
            key: Counter key
            default: Default value if key doesn't exist

        Returns:
            Counter value
        """
        return self._counts.get(key, default)

    def to_dict(self) -> Dict[str, int]:
        """
        Export all counters as dictionary.

        Returns:
            Dict of all counter values
        """
        return self._counts.copy()

    def __repr__(self):
        """String representation of stats."""
        return f"StatsCounter({self._counts})"


def log_metric(metric_name: str, value: Any, **tags):
    """
    Log a metric with optional tags.

    This is a simple metric logging function that outputs to logs.
    Can be replaced with actual metrics backend (Prometheus, StatsD) later.

    Args:
        metric_name: Name of the metric
        value: Metric value
        **tags: Additional tags/labels for the metric

    Example:
        log_metric("task.duration", 1.5, task_name="send_email", status="success")
        log_metric("task.retry_count", 2, task_name="process_payment")
    """
    logger.info(
        f"METRIC: {metric_name}={value}",
        extra={
            "metric_name": metric_name,
            "metric_value": value,
            "metric_type": "gauge",
            **tags
        }
    )


# Export public API
__all__ = [
    "TaskMetrics",
    "Timer",
    "StatsCounter",
    "log_metric",
]
'''


def generate_internals_testing() -> str:
    """Generate internals/testing.py with TaskTestContext and mock utilities."""
    return '''"""
Testing Utilities for Background Tasks

This module provides utilities to make testing Celery tasks easier:
- Mock TaskContext for unit tests
- Async task execution in synchronous tests
- Logging assertion helpers
- Session mocking utilities

Example:
    async def test_my_task():
        ctx = TaskTestContext(task_id="test-123")
        result = await my_task(ctx, param1="value")
        assert result["status"] == "success"
        ctx.assert_logged_info()
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from unittest.mock import MagicMock, AsyncMock
from uuid import UUID

from .context import TaskContext
from .monitoring import StatsCounter


@dataclass
class TaskTestContext:
    """
    Mock TaskContext for testing background tasks.

    Provides the same interface as TaskContext but stores
    log calls and metrics for assertion in tests.

    Example:
        ctx = TaskTestContext(task_id="test-123")
        my_task(ctx, user_id=123)
        ctx.assert_logged_success()
        assert ctx.info_logs[0]["message"] == "Processing user"
    """
    task_id: str = "test-task-id"
    retry_count: int = 0
    session: Optional[Any] = None

    # Mock task instance
    task: Any = field(default_factory=lambda: MagicMock(name="mock_task"))

    # Logged messages storage
    info_logs: List[Dict[str, Any]] = field(default_factory=list)
    success_logs: List[Dict[str, Any]] = field(default_factory=list)
    error_logs: List[Dict[str, Any]] = field(default_factory=list)
    warning_logs: List[Dict[str, Any]] = field(default_factory=list)
    debug_logs: List[Dict[str, Any]] = field(default_factory=list)

    # Metrics storage
    _timers: Dict[str, float] = field(default_factory=dict)
    _metrics: Dict[str, Any] = field(default_factory=dict)

    def log_info(self, message: str, **extra):
        """Mock log_info - stores call for assertion."""
        self.info_logs.append({"message": message, **extra})

    def log_success(self, message: str, **extra):
        """Mock log_success - stores call for assertion."""
        self.success_logs.append({"message": message, **extra})

    def log_error(self, message: str, exc_info: bool = True, **extra):
        """Mock log_error - stores call for assertion."""
        self.error_logs.append({"message": message, "exc_info": exc_info, **extra})

    def log_warning(self, message: str, **extra):
        """Mock log_warning - stores call for assertion."""
        self.warning_logs.append({"message": message, **extra})

    def log_debug(self, message: str, **extra):
        """Mock log_debug - stores call for assertion."""
        self.debug_logs.append({"message": message, **extra})

    def log_progress(self, **metrics):
        """Mock log_progress - stores metrics."""
        self._metrics.update(metrics)

    def success_result(self, **data) -> Dict[str, Any]:
        """Create success result - same as TaskContext."""
        return {
            "status": "success",
            "task_id": self.task_id,
            **data
        }

    def error_result(self, error: str, **data) -> Dict[str, Any]:
        """Create error result - same as TaskContext."""
        return {
            "status": "error",
            "task_id": self.task_id,
            "error": error,
            **data
        }

    def validate_uuid(self, value: str, field_name: str = "id") -> UUID:
        """Validate UUID - same as TaskContext."""
        from .exceptions import TaskValidationError
        try:
            return UUID(value)
        except (ValueError, TypeError, AttributeError) as e:
            raise TaskValidationError(
                f"Invalid UUID format for {field_name}: {value}",
                field=field_name,
                value=value
            ) from e

    def not_found_error(self, message: str, **context):
        """Raise not found error - same as TaskContext."""
        from .exceptions import TaskNotFoundError
        raise TaskNotFoundError(message, **context)

    def validation_error(self, message: str, **context):
        """Raise validation error - same as TaskContext."""
        from .exceptions import TaskValidationError
        raise TaskValidationError(message, **context)

    def config_error(self, message: str, **context):
        """Raise config error - same as TaskContext."""
        from .exceptions import TaskConfigurationError
        raise TaskConfigurationError(message, **context)

    def start_timer(self, name: str):
        """Mock start_timer."""
        import time
        self._timers[name] = time.time()

    def end_timer(self, name: str) -> Optional[float]:
        """Mock end_timer."""
        if name in self._timers:
            import time
            duration = time.time() - self._timers[name]
            return duration
        return None

    def increment_metric(self, name: str, value: int = 1):
        """Mock increment_metric."""
        self._metrics[name] = self._metrics.get(name, 0) + value

    def create_stats_counter(self) -> StatsCounter:
        """Create stats counter - same as TaskContext."""
        return StatsCounter()

    async def commit_batch(self):
        """Mock commit_batch."""
        if self.session and hasattr(self.session, 'commit'):
            await self.session.commit()

    # Assertion helpers

    def assert_logged_info(self, message: Optional[str] = None):
        """Assert that info was logged."""
        assert len(self.info_logs) > 0, "No info logs found"
        if message:
            assert any(message in log["message"] for log in self.info_logs), \\
                f"Message '{message}' not found in info logs"

    def assert_logged_success(self, message: Optional[str] = None):
        """Assert that success was logged."""
        assert len(self.success_logs) > 0, "No success logs found"
        if message:
            assert any(message in log["message"] for log in self.success_logs), \\
                f"Message '{message}' not found in success logs"

    def assert_logged_error(self, message: Optional[str] = None):
        """Assert that error was logged."""
        assert len(self.error_logs) > 0, "No error logs found"
        if message:
            assert any(message in log["message"] for log in self.error_logs), \\
                f"Message '{message}' not found in error logs"

    def assert_logged_warning(self, message: Optional[str] = None):
        """Assert that warning was logged."""
        assert len(self.warning_logs) > 0, "No warning logs found"
        if message:
            assert any(message in log["message"] for log in self.warning_logs), \\
                f"Message '{message}' not found in warning logs"


def mock_task_session():
    """
    Create a mock AsyncSession for testing.

    Returns:
        AsyncMock configured as an async database session

    Example:
        session = mock_task_session()
        ctx = TaskTestContext(session=session)
        await my_task(ctx, user_id=123)
        session.commit.assert_called_once()
    """
    session = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.close = AsyncMock()
    return session


async def run_task_sync(task_func, ctx: TaskTestContext, *args, **kwargs):
    """
    Run an async task function synchronously for testing.

    Args:
        task_func: The async task function to run
        ctx: TaskTestContext instance
        *args: Task arguments
        **kwargs: Task keyword arguments

    Returns:
        Task result

    Example:
        ctx = TaskTestContext()
        result = await run_task_sync(my_async_task, ctx, param1="value")
        assert result["status"] == "success"
    """
    return await task_func(ctx, *args, **kwargs)


# Export public API
__all__ = [
    "TaskTestContext",
    "mock_task_session",
    "run_task_sync",
]
'''
