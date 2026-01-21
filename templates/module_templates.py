"""
Module-level template generators.

Generates files that belong at the module root:
- dependencies.py: Dependency injection factories
- permissions.py: Permission definitions and checkers
- exceptions.py: Custom HTTPException classes
- tasks.py: Celery background tasks
- __init__.py: Module exports
- README.md: Module documentation
"""


def generate_dependencies(module_name: str, class_name: str) -> str:
    """
    Generate dependencies.py file.
    
    Follows the pattern from app/service_provider/dependencies.py
    with @lru_cache for singleton services.
    """
    return f'''"""
{class_name} Module Dependencies.

This module provides dependency injection factories for {module_name} services.

Pattern:
- Use @lru_cache() to create singleton service instances
- Services receive their dependencies via factory functions
- Routes use Depends() to inject services

Usage in routes:
    from .dependencies import get_{module_name}_service
    
    @router.get("/")
    async def list_items(
        service: {class_name}Service = Depends(get_{module_name}_service)
    ):
        ...
"""

from functools import lru_cache
from typing import Optional
from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.user.auth import get_current_user_validated, UserModel
from .services import {class_name}Service
from .models import {class_name}
from .exceptions import {class_name}NotFoundError


# ==================== SERVICE FACTORIES ====================

@lru_cache()
def get_{module_name}_service() -> {class_name}Service:
    """
    Factory for {class_name}Service singleton.
    
    Uses @lru_cache to ensure only one instance is created.
    The service is stateless, so a singleton is safe.
    
    Returns:
        {class_name}Service instance
    """
    return {class_name}Service()


# ==================== ENTITY RESOLVERS ====================

async def get_{module_name}_by_id(
    {module_name}_id: UUID,
    session: AsyncSession = Depends(get_session),
    service: {class_name}Service = Depends(get_{module_name}_service),
) -> {class_name}:
    """
    Dependency to resolve a {module_name} by ID.
    
    Use in routes to automatically fetch and validate the {module_name}:
    
        @router.get("/{{{module_name}_id}}")
        async def get_item(
            {module_name}: {class_name} = Depends(get_{module_name}_by_id)
        ):
            return {module_name}
    
    Args:
        {module_name}_id: UUID path parameter
        session: Database session (injected)
        service: Service instance (injected)
        
    Returns:
        {class_name} instance
        
    Raises:
        {class_name}NotFoundError: If {module_name} not found
    """
    return await service.get_{module_name}_by_id(session, {module_name}_id)


# ==================== USER CONTEXT RESOLVERS ====================

# Uncomment and modify if this module has user-owned entities:
#
# async def get_current_user_{module_name}(
#     session: AsyncSession = Depends(get_session),
#     current_user: UserModel = Depends(get_current_user_validated),
#     service: {class_name}Service = Depends(get_{module_name}_service),
# ) -> {class_name}:
#     """
#     Get the {module_name} belonging to the current authenticated user.
#     
#     Use in routes where the user should only access their own {module_name}.
#     """
#     {module_name} = await service.get_{module_name}_by_user_id(
#         session, current_user.id
#     )
#     if not {module_name}:
#         raise {class_name}NotFoundError(f"No {module_name} for user {{current_user.id}}")
#     return {module_name}
'''


def generate_permissions(module_name: str, class_name: str) -> str:
    """
    Generate permissions.py file.
    
    Follows the pattern from app/service_provider/permissions.py
    """
    upper_name = module_name.upper()
    
    return f'''"""
{class_name} Module Permissions.

Defines permission strings and helper functions for {module_name} access control.

Permission Format: {{resource}}:{{action}}

Actions:
- read: View/list {module_name}s
- write: Create/update {module_name}s  
- delete: Delete {module_name}s

Usage in routes:
    from .permissions import require_{module_name}_write_permission
    
    @router.post("/", dependencies=[Depends(require_{module_name}_write_permission)])
    async def create_item(...):
        ...
"""

from app.user.permission_management import (
    require_permission,
    require_any_permission,
    require_all_permissions,
    has_permission,
)


# ==================== PERMISSION CONSTANTS ====================

# Base permission strings
{upper_name}_READ = "{module_name}s:read"
{upper_name}_WRITE = "{module_name}s:write"
{upper_name}_DELETE = "{module_name}s:delete"


# ==================== PERMISSION CHECKERS ====================

def require_{module_name}_read_permission():
    """
    Dependency that requires read permission for {module_name}s.
    
    Returns:
        Permission checker dependency
    """
    return require_permission({upper_name}_READ)


def require_{module_name}_write_permission():
    """
    Dependency that requires write permission for {module_name}s.
    
    Write permission implies create and update operations.
    
    Returns:
        Permission checker dependency
    """
    return require_permission({upper_name}_WRITE)


def require_{module_name}_delete_permission():
    """
    Dependency that requires delete permission for {module_name}s.
    
    Returns:
        Permission checker dependency
    """
    return require_permission({upper_name}_DELETE)


def require_{module_name}_admin_permission():
    """
    Dependency that requires full admin access to {module_name}s.
    
    Requires both write and delete permissions.
    
    Returns:
        Permission checker dependency
    """
    return require_all_permissions({upper_name}_WRITE, {upper_name}_DELETE)


# ==================== PERMISSION CHECK HELPERS ====================

async def user_can_read_{module_name}(user) -> bool:
    """
    Check if user can read {module_name}s.
    
    Args:
        user: User model instance
        
    Returns:
        True if user has read permission
    """
    return await has_permission(user, {upper_name}_READ)


async def user_can_write_{module_name}(user) -> bool:
    """
    Check if user can create/update {module_name}s.
    
    Args:
        user: User model instance
        
    Returns:
        True if user has write permission
    """
    return await has_permission(user, {upper_name}_WRITE)
'''


def generate_exceptions(module_name: str, class_name: str) -> str:
    """
    Generate exceptions.py file.
    
    Follows the pattern from app/service_provider/exceptions.py
    with HTTPException-based exceptions.
    """
    return f'''"""
{class_name} Module Exceptions.

Custom exceptions for the {module_name} module.

All exceptions extend HTTPException for automatic handling by FastAPI.
This ensures consistent API error responses.

Pattern:
- Inherit from HTTPException
- Set appropriate status_code
- Provide descriptive detail message
"""

from fastapi import HTTPException, status


# ==================== NOT FOUND EXCEPTIONS ====================

class {class_name}NotFoundError(HTTPException):
    """
    Raised when a requested {module_name} is not found.
    
    Status Code: 404 Not Found
    """
    
    def __init__(self, identifier: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{class_name} not found: {{identifier}}"
        )
        self.identifier = identifier


# ==================== CONFLICT EXCEPTIONS ====================

class {class_name}AlreadyExistsError(HTTPException):
    """
    Raised when attempting to create a {module_name} that already exists.
    
    Status Code: 409 Conflict
    """
    
    def __init__(self, identifier: str, field: str = "name"):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"{class_name} with {{field}} '{{identifier}}' already exists"
        )
        self.identifier = identifier
        self.field = field


# ==================== VALIDATION EXCEPTIONS ====================

class Invalid{class_name}DataError(HTTPException):
    """
    Raised when {module_name} data fails business validation.
    
    Use for business rule violations that aren't caught by Pydantic.
    Status Code: 400 Bad Request
    """
    
    def __init__(self, message: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid {module_name} data: {{message}}"
        )


# ==================== PERMISSION EXCEPTIONS ====================

class {class_name}AccessDeniedError(HTTPException):
    """
    Raised when user doesn't have permission for the {module_name} operation.
    
    Status Code: 403 Forbidden
    """
    
    def __init__(self, action: str = "access"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"You don't have permission to {{action}} this {module_name}"
        )


# ==================== STATE EXCEPTIONS ====================

class {class_name}InactiveError(HTTPException):
    """
    Raised when trying to operate on an inactive {module_name}.
    
    Status Code: 400 Bad Request
    """
    
    def __init__(self, identifier: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{class_name} '{{identifier}}' is inactive and cannot be modified"
        )
        self.identifier = identifier
'''


def generate_module_init(module_name: str, class_name: str) -> str:
    """
    Generate __init__.py file for the module root.
    
    Follows the pattern from app/service_provider/__init__.py
    """
    return f'''"""
{class_name} Module.

This module provides functionality for managing {module_name}s.

Exports:
- Models: {class_name} database model
- Schemas: Pydantic schemas for validation
- Services: Business logic layer
- Routes: API endpoints
- Exceptions: Custom exception classes

Usage:
    from app.{module_name} import {class_name}, {class_name}Service, {module_name}_router
"""

# Models
from .models import {class_name}

# Schemas
from .schemas import (
    {class_name}Base,
    {class_name}Create,
    {class_name}CreateRequest,
    {class_name}Update,
    {class_name} as {class_name}Response,
    {class_name}Minimal,
    {class_name}ListResponse,
)

# Services
from .services import {class_name}Service

# Routes
from .routes import {module_name}_router

# Exceptions
from .exceptions import (
    {class_name}NotFoundError,
    {class_name}AlreadyExistsError,
    Invalid{class_name}DataError,
    {class_name}AccessDeniedError,
)

# Dependencies
from .dependencies import get_{module_name}_service


__all__ = [
    # Models
    "{class_name}",
    # Schemas
    "{class_name}Base",
    "{class_name}Create",
    "{class_name}CreateRequest",
    "{class_name}Update",
    "{class_name}Response",
    "{class_name}Minimal",
    "{class_name}ListResponse",
    # Services
    "{class_name}Service",
    # Routes
    "{module_name}_router",
    # Exceptions
    "{class_name}NotFoundError",
    "{class_name}AlreadyExistsError",
    "Invalid{class_name}DataError",
    "{class_name}AccessDeniedError",
    # Dependencies
    "get_{module_name}_service",
]
'''


def generate_tasks(module_name: str, class_name: str) -> str:
    """
    Generate tasks.py file for Celery background tasks.
    """
    return f'''"""
{class_name} Module Background Tasks.

Celery tasks for {module_name} operations.

Usage:
    from .tasks import process_{module_name}_created
    
    # In service after commit:
    process_{module_name}_created.delay(str({module_name}.id))
"""

from celery import shared_task

from app.core.logging import get_logger

logger = get_logger(__name__)


@shared_task(bind=True, max_retries=3)
def process_{module_name}_created(self, {module_name}_id: str):
    """
    Background task triggered when a {module_name} is created.
    
    Use for:
    - Sending notifications
    - Updating analytics
    - External API calls
    
    Args:
        {module_name}_id: UUID string of the created {module_name}
    """
    try:
        logger.info(f"Processing {module_name} created: {{{module_name}_id}}")
        # Add your background processing logic here
        logger.info(f"Finished processing {module_name}: {{{module_name}_id}}")
    except Exception as exc:
        logger.error(f"Error processing {module_name} {{{module_name}_id}}: {{exc}}")
        raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=3)
def process_{module_name}_updated(self, {module_name}_id: str):
    """
    Background task triggered when a {module_name} is updated.
    
    Args:
        {module_name}_id: UUID string of the updated {module_name}
    """
    try:
        logger.info(f"Processing {module_name} updated: {{{module_name}_id}}")
        # Add your background processing logic here
        logger.info(f"Finished processing {module_name} update: {{{module_name}_id}}")
    except Exception as exc:
        logger.error(f"Error processing {module_name} update {{{module_name}_id}}: {{exc}}")
        raise self.retry(exc=exc, countdown=60)
'''


def generate_readme(module_name: str, class_name: str, module_kebab: str) -> str:
    """
    Generate README.md for the module.
    """
    return f'''# {class_name} Module

> Manages {module_name} entities with full CRUD operations.

## 📁 Module Structure

```
{module_name}/
├── __init__.py          # Module exports
├── dependencies.py      # Dependency injection factories
├── exceptions.py        # Custom HTTPException classes
├── permissions.py       # RBAC permission definitions
├── tasks.py             # Celery background tasks
├── models/
│   ├── __init__.py
│   └── {module_name}.py         # SQLAlchemy model
├── schemas/
│   ├── __init__.py
│   └── {module_name}_schemas.py # Pydantic schemas
├── crud/
│   ├── __init__.py
│   └── {module_name}_crud.py    # Data access layer
├── services/
│   ├── __init__.py
│   └── {module_name}_service.py # Business logic
├── routes/
│   ├── __init__.py              # Route aggregator
│   ├── public/                  # Public endpoints
│   │   ├── __init__.py
│   │   └── {module_name}.py
│   └── admin/                   # Admin endpoints
│       ├── __init__.py
│       └── {module_name}_management.py
├── utils/               # Module utilities
└── integrations/        # Cross-module facades
```

## 🔗 API Endpoints

### Public Routes (`/api/v1/{module_name}s/`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List all active {module_name}s |
| GET | `/{{id}}` | Get {module_name} by ID |

### Admin Routes (`/api/v1/{module_name}s/admin/`)

| Method | Endpoint | Description | Permission |
|--------|----------|-------------|------------|
| GET | `/` | List all {module_name}s (incl. inactive) | `{module_name}s:read` |
| GET | `/{{id}}` | Get {module_name} details | `{module_name}s:read` |
| POST | `/` | Create new {module_name} | `{module_name}s:write` |
| PATCH | `/{{id}}` | Update {module_name} | `{module_name}s:write` |
| DELETE | `/{{id}}` | Delete {module_name} | `{module_name}s:delete` |

## 🏗️ Architecture

This module follows the **Layered Architecture** pattern:

```
Routes (HTTP Layer)
    ↓
Services (Business Logic)
    ↓
CRUD (Data Access)
    ↓
Models (Database)
```

### Key Principles

1. **Routes**: Handle HTTP concerns only (validation, auth, responses)
2. **Services**: Contain business logic, own transaction boundaries
3. **CRUD**: Pure data operations, NO commits
4. **Models**: Database schema definition

### Transaction Management

```python
# Service layer owns commits
async def create_{module_name}(self, session, data):
    # 1. Business validation
    existing = await {module_name}_crud.get_by_name(session, data.name)
    if existing:
        raise {class_name}AlreadyExistsError(data.name)
    
    # 2. CRUD operation (no commit)
    {module_name} = await {module_name}_crud.create(session, obj_in=data)
    
    # 3. Commit transaction
    await session.commit()
    
    # 4. Refresh and return
    await session.refresh({module_name})
    return {module_name}
```

## 🔐 Permissions

| Permission | Description |
|------------|-------------|
| `{module_name}s:read` | View/list {module_name}s |
| `{module_name}s:write` | Create/update {module_name}s |
| `{module_name}s:delete` | Delete {module_name}s |

## 🚀 Usage Examples

### Import in other modules

```python
from app.{module_name} import {class_name}, {class_name}Service, get_{module_name}_service
```

### Register router

Add to `app/apis/v1.py`:

```python
from app.{module_name}.routes import {module_name}_router

router.include_router({module_name}_router)
```

## 📝 Development Notes

- All async operations
- Pydantic v2 schemas  
- SQLAlchemy 2.0 style
- Full type hints
'''


def generate_utils_init(module_name: str, class_name: str) -> str:
    """
    Generate utils/__init__.py file.
    """
    return f'''"""
{class_name} Module Utilities.

Helper functions and utilities specific to the {module_name} module.

Add module-specific helpers here, such as:
- Data transformation utilities
- Validation helpers
- Caching utilities
"""

# Example exports:
# from .cache import invalidate_{module_name}_cache
# from .validators import validate_{module_name}_data

__all__ = [
    # Add utility exports here
]
'''


def generate_integrations_init(module_name: str, class_name: str) -> str:
    """
    Generate integrations/__init__.py file.
    
    Follows the Integration/Facade pattern.
    """
    return f'''"""
{class_name} Module Integrations.

Provides a stable API for other modules to interact with {module_name}
functionality without depending on internal implementation details.

This follows the Anti-Corruption Layer / Facade pattern.

Example integration:
    class {class_name}Integration:
        \"\"\"Facade for {module_name} operations used by other modules.\"\"\"
        
        def __init__(self):
            self.service = {class_name}Service()
        
        async def get_{module_name}_for_display(
            self,
            session: AsyncSession,
            {module_name}_id: UUID
        ) -> Optional[{class_name}Minimal]:
            \"\"\"Get minimal {module_name} data for display in other modules.\"\"\"
            try:
                {module_name} = await self.service.get_{module_name}_by_id(
                    session, {module_name}_id
                )
                return {class_name}Minimal.model_validate({module_name})
            except {class_name}NotFoundError:
                return None

Usage in other modules:
    from app.{module_name}.integrations import {class_name}Integration
    
    {module_name}_integration = {class_name}Integration()
    {module_name}_data = await {module_name}_integration.get_{module_name}_for_display(
        session, {module_name}_id
    )
"""

# Export integration classes here
# from .{module_name}_integration import {class_name}Integration

__all__ = [
    # "{class_name}Integration",
]
'''
