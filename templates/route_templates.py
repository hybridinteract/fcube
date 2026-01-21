"""
Route template generators.

Generates FastAPI routes with proper organization:
- Public routes (no auth required)
- Admin routes (permission-based access)
"""


def generate_routes_init(
    module_name: str,
    class_name: str,
    with_public: bool = True,
    with_admin: bool = True
) -> str:
    """
    Generate routes/__init__.py file.
    
    Follows the pattern from app/service_provider/routes/__init__.py
    """
    imports = []
    includes = []
    
    if with_public:
        imports.append(f"from .public import public_router")
        includes.append(f'{module_name}_router.include_router(public_router, prefix="", tags=["{class_name}s - Public"])')
    
    if with_admin:
        imports.append(f"from .admin import admin_router")
        includes.append(f'{module_name}_router.include_router(admin_router, prefix="/admin", tags=["{class_name}s - Admin"])')
    
    imports_str = "\n".join(imports) if imports else "# No sub-routers"
    includes_str = "\n".join(includes) if includes else "# No sub-routers included"
    
    return f'''"""
{class_name} Routes Package.

This module aggregates all routers for the {module_name} module.

Route Organization:
- /                 -> Public routes (read-only, no auth)
- /admin/           -> Admin routes (requires permissions)
"""

from fastapi import APIRouter

{imports_str}

# Main module router
{module_name}_router = APIRouter(
    prefix="/{module_name}s",
    tags=["{class_name}s"]
)

# Include sub-routers
{includes_str}

__all__ = ["{module_name}_router"]
'''


def generate_public_routes_init(module_name: str, class_name: str) -> str:
    """
    Generate routes/public/__init__.py file.
    """
    return f'''"""
Public {class_name} Routes.

These routes are publicly accessible (no authentication required).
Typically used for read-only operations like listing and viewing.
"""

from fastapi import APIRouter

from .{module_name} import router as {module_name}_base_router

# Aggregate public routers
public_router = APIRouter()

# Include all public route files
public_router.include_router({module_name}_base_router)

__all__ = ["public_router"]
'''


def generate_public_routes(module_name: str, class_name: str) -> str:
    """
    Generate public route file.
    
    Follows the pattern for public read-only endpoints.
    """
    return f'''"""
Public {class_name} Routes.

These endpoints are publicly accessible without authentication.
Used for reading/listing {module_name}s.
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.logging import get_logger
from ...schemas import {class_name}, {class_name}ListResponse
from ...dependencies import get_{module_name}_service
from ...services import {class_name}Service

logger = get_logger(__name__)

router = APIRouter()


@router.get(
    "/",
    response_model={class_name}ListResponse,
    summary="List all {module_name}s",
    description="Get a paginated list of all active {module_name}s."
)
async def list_{module_name}s(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum records to return"),
    session: AsyncSession = Depends(get_session),
    service: {class_name}Service = Depends(get_{module_name}_service),
):
    """
    List all active {module_name}s with pagination.
    
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum number of records to return (default: 20, max: 100)
    """
    items = await service.get_all_{module_name}s(
        session,
        skip=skip,
        limit=limit,
        active_only=True
    )
    total = await service.get_{module_name}_count(session)
    
    return {class_name}ListResponse(
        items=items,
        total=total,
        skip=skip,
        limit=limit
    )


@router.get(
    "/{{{module_name}_id}}",
    response_model={class_name},
    summary="Get {module_name} by ID",
    description="Get detailed information about a specific {module_name}."
)
async def get_{module_name}(
    {module_name}_id: UUID = Path(..., description="{class_name} ID"),
    session: AsyncSession = Depends(get_session),
    service: {class_name}Service = Depends(get_{module_name}_service),
):
    """
    Get a specific {module_name} by ID.
    
    - **{module_name}_id**: UUID of the {module_name}
    """
    return await service.get_{module_name}_by_id(session, {module_name}_id)
'''


def generate_admin_routes_init(module_name: str, class_name: str) -> str:
    """
    Generate routes/admin/__init__.py file.
    """
    return f'''"""
Admin {class_name} Routes.

These routes require admin permissions.
Used for create, update, delete operations.
"""

from fastapi import APIRouter

from .{module_name}_management import router as management_router

# Aggregate admin routers
admin_router = APIRouter()

# Include all admin route files
admin_router.include_router(management_router)

__all__ = ["admin_router"]
'''


def generate_admin_routes(module_name: str, class_name: str) -> str:
    """
    Generate admin management route file.
    
    Follows the pattern for admin CRUD endpoints with permissions.
    """
    upper_name = module_name.upper()
    
    return f'''"""
Admin {class_name} Management Routes.

These endpoints require admin permissions for managing {module_name}s.
Includes create, update, and delete operations.
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.logging import get_logger
from app.user.auth import get_current_user_validated, UserModel
from ...schemas import (
    {class_name},
    {class_name}CreateRequest,
    {class_name}Update,
    {class_name}ListResponse,
)
from ...dependencies import get_{module_name}_service
from ...services import {class_name}Service
from ...permissions import (
    require_{module_name}_read_permission,
    require_{module_name}_write_permission,
    require_{module_name}_delete_permission,
)

logger = get_logger(__name__)

router = APIRouter()


# ==================== LIST/READ ====================

@router.get(
    "/",
    response_model={class_name}ListResponse,
    summary="[Admin] List all {module_name}s",
    description="Admin endpoint to list all {module_name}s including inactive ones.",
    dependencies=[Depends(require_{module_name}_read_permission)],
)
async def admin_list_{module_name}s(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=500, description="Maximum records to return"),
    include_inactive: bool = Query(False, description="Include inactive records"),
    session: AsyncSession = Depends(get_session),
    service: {class_name}Service = Depends(get_{module_name}_service),
    current_user: UserModel = Depends(get_current_user_validated),
):
    """
    Admin: List all {module_name}s with optional inactive records.
    """
    items = await service.get_all_{module_name}s(
        session,
        skip=skip,
        limit=limit,
        active_only=not include_inactive
    )
    total = await service.get_{module_name}_count(session, active_only=not include_inactive)
    
    return {class_name}ListResponse(
        items=items,
        total=total,
        skip=skip,
        limit=limit
    )


@router.get(
    "/{{{module_name}_id}}",
    response_model={class_name},
    summary="[Admin] Get {module_name} details",
    dependencies=[Depends(require_{module_name}_read_permission)],
)
async def admin_get_{module_name}(
    {module_name}_id: UUID = Path(..., description="{class_name} ID"),
    session: AsyncSession = Depends(get_session),
    service: {class_name}Service = Depends(get_{module_name}_service),
    current_user: UserModel = Depends(get_current_user_validated),
):
    """
    Admin: Get detailed information about a {module_name}.
    """
    return await service.get_{module_name}_by_id(
        session,
        {module_name}_id,
        include_relationships=True
    )


# ==================== CREATE ====================

@router.post(
    "/",
    response_model={class_name},
    status_code=status.HTTP_201_CREATED,
    summary="[Admin] Create {module_name}",
    dependencies=[Depends(require_{module_name}_write_permission)],
)
async def admin_create_{module_name}(
    {module_name}_data: {class_name}CreateRequest,
    session: AsyncSession = Depends(get_session),
    service: {class_name}Service = Depends(get_{module_name}_service),
    current_user: UserModel = Depends(get_current_user_validated),
):
    """
    Admin: Create a new {module_name}.
    """
    logger.info(f"Admin {{current_user.email}} creating {module_name}")
    return await service.create_{module_name}(session, {module_name}_data)


# ==================== UPDATE ====================

@router.patch(
    "/{{{module_name}_id}}",
    response_model={class_name},
    summary="[Admin] Update {module_name}",
    dependencies=[Depends(require_{module_name}_write_permission)],
)
async def admin_update_{module_name}(
    {module_name}_id: UUID = Path(..., description="{class_name} ID"),
    {module_name}_data: {class_name}Update = ...,
    session: AsyncSession = Depends(get_session),
    service: {class_name}Service = Depends(get_{module_name}_service),
    current_user: UserModel = Depends(get_current_user_validated),
):
    """
    Admin: Update an existing {module_name}.
    """
    logger.info(f"Admin {{current_user.email}} updating {module_name} {{{module_name}_id}}")
    return await service.update_{module_name}(session, {module_name}_id, {module_name}_data)


# ==================== DELETE ====================

@router.delete(
    "/{{{module_name}_id}}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="[Admin] Delete {module_name}",
    dependencies=[Depends(require_{module_name}_delete_permission)],
)
async def admin_delete_{module_name}(
    {module_name}_id: UUID = Path(..., description="{class_name} ID"),
    hard_delete: bool = Query(False, description="Permanently delete (default: soft delete)"),
    session: AsyncSession = Depends(get_session),
    service: {class_name}Service = Depends(get_{module_name}_service),
    current_user: UserModel = Depends(get_current_user_validated),
):
    """
    Admin: Delete a {module_name} (soft delete by default).
    
    - **hard_delete**: If true, permanently removes the record
    """
    logger.info(f"Admin {{current_user.email}} deleting {module_name} {{{module_name}_id}} (hard={{hard_delete}})")
    await service.delete_{module_name}(session, {module_name}_id, soft_delete=not hard_delete)
'''
