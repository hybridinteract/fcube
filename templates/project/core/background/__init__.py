"""
Background Task Framework Templates Package.

Contains modular template generators for the background task module:
- Main module files (celery_app.py, tasks.py, README.md)
- Internals directory (base, context, decorators, exceptions, etc.)
- Extras directory (circuit_breaker)
"""

from pathlib import Path
from typing import List, Tuple

# Import all template generators
from .background_templates import (
    generate_background_init,
    generate_background_celery_app,
    generate_background_tasks,
    generate_background_readme,
)

from .internals_templates import (
    generate_internals_init,
    generate_internals_base,
    generate_internals_context,
    generate_internals_decorators,
    generate_internals_exceptions,
    generate_internals_retry,
    generate_internals_session,
    generate_internals_event_loop,
    generate_internals_logging,
    generate_internals_monitoring,
    generate_internals_testing,
)

from .extras_templates import (
    generate_extras_init,
    generate_extras_circuit_breaker,
)


def generate_background_module_files(
    background_dir: Path,
    project_snake: str,
    project_pascal: str
) -> List[Tuple[Path, str]]:
    """
    Generate all files for the background module.

    This is a convenience function that generates all files needed
    for the complete background task framework.

    Args:
        background_dir: Path to app/core/background directory
        project_snake: Project name in snake_case
        project_pascal: Project name in PascalCase

    Returns:
        List of (path, content) tuples for all files to create
    """
    files = []

    # Main module files
    files.extend([
        (background_dir / "__init__.py", generate_background_init()),
        (background_dir / "celery_app.py", generate_background_celery_app(project_snake)),
        (background_dir / "tasks.py", generate_background_tasks()),
        (background_dir / "README.md", generate_background_readme()),
    ])

    # Internals directory
    internals_dir = background_dir / "internals"
    files.extend([
        (internals_dir / "__init__.py", generate_internals_init()),
        (internals_dir / "base.py", generate_internals_base()),
        (internals_dir / "context.py", generate_internals_context()),
        (internals_dir / "decorators.py", generate_internals_decorators()),
        (internals_dir / "exceptions.py", generate_internals_exceptions()),
        (internals_dir / "retry.py", generate_internals_retry()),
        (internals_dir / "session.py", generate_internals_session()),
        (internals_dir / "event_loop.py", generate_internals_event_loop()),
        (internals_dir / "logging.py", generate_internals_logging()),
        (internals_dir / "monitoring.py", generate_internals_monitoring()),
        (internals_dir / "testing.py", generate_internals_testing()),
    ])

    # Extras directory
    extras_dir = background_dir / "extras"
    files.extend([
        (extras_dir / "__init__.py", generate_extras_init()),
        (extras_dir / "circuit_breaker.py", generate_extras_circuit_breaker()),
    ])

    return files


__all__ = [
    # Convenience function
    "generate_background_module_files",
    # Main module templates
    "generate_background_init",
    "generate_background_celery_app",
    "generate_background_tasks",
    "generate_background_readme",
    # Internals templates
    "generate_internals_init",
    "generate_internals_base",
    "generate_internals_context",
    "generate_internals_decorators",
    "generate_internals_exceptions",
    "generate_internals_retry",
    "generate_internals_session",
    "generate_internals_event_loop",
    "generate_internals_logging",
    "generate_internals_monitoring",
    "generate_internals_testing",
    # Extras templates
    "generate_extras_init",
    "generate_extras_circuit_breaker",
]
