"""
User Permission Templates.

Generates permission_management submodule templates:
- __init__.py
- utils.py (RBAC utilities)
- scoped_access.py (Scoped access framework)
"""


def generate_user_permission_init() -> str:
    """Generate user/permission_management/__init__.py."""
    return '''"""
Permission Management Module

Provides RBAC functionality and Scoped Access Control.
"""

from .utils import (
    require_permission,
    require_any_permission,
    require_all_permissions,
    has_permission,
    is_super_admin,
    PermissionChecker,
    SUPER_ADMIN_ROLE,
    BasePermissionChecker,
)
from .scoped_access import (
    AdminScope,
    ScopeProvider,
    ScopeRegistry,
    ScopedPermissionChecker,
    require_scoped_permission
)

__all__ = [
    # Utilities
    "require_permission",
    "require_any_permission",
    "require_all_permissions",
    "has_permission",
    "is_super_admin",
    "PermissionChecker",
    "SUPER_ADMIN_ROLE",
    "BasePermissionChecker",

    # Scoped Access Framework
    "AdminScope",
    "ScopeProvider",
    "ScopeRegistry",
    "ScopedPermissionChecker",
    "require_scoped_permission",
]
'''


def generate_user_permission_utils() -> str:
    """Generate user/permission_management/utils.py with PermissionChecker."""
    return '''"""
Permission Management Utilities

Comprehensive RBAC utilities and PermissionChecker.
"""

from typing import List, Set, Optional, Union
from uuid import UUID
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, exists as sql_exists
from app.core.database import get_session
from app.core.logging import get_logger
from app.user.auth_management.utils import get_current_user_validated
from app.user.models import User as UserModel, Permission, Role, UserRole, RolePermission

logger = get_logger(__name__)

SUPER_ADMIN_ROLE = "super_admin"


class BasePermissionChecker:
    """Base permission checker for super admin + basic RBAC authorization."""

    def __init__(
        self,
        required_permissions: Optional[Union[str, List[str]]] = None,
        require_all: bool = True
    ):
        if required_permissions:
            if isinstance(required_permissions, str):
                required_permissions = [required_permissions]
            self.required_permissions = required_permissions
        else:
            self.required_permissions = []
        self.require_all = require_all

    async def __call__(
        self,
        current_user: UserModel = Depends(get_current_user_validated),
        session: AsyncSession = Depends(get_session)
    ) -> UserModel:
        if await self.is_super_admin(session, current_user.id):
            return current_user

        if self.required_permissions:
            user_permissions = await self.get_user_permissions(session, current_user.id)
            has_access = False
            if self.require_all:
                has_access = all(
                    perm in user_permissions for perm in self.required_permissions)
            else:
                has_access = any(
                    perm in user_permissions for perm in self.required_permissions)
            if has_access:
                return current_user

        self.handle_authorization_failure(current_user)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    def handle_authorization_failure(self, current_user: UserModel) -> None:
        logger.warning(
            f"Permission denied for user {current_user.id}. Required: {self.required_permissions}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Missing required permission(s): {', '.join(self.required_permissions)}"
        )

    @staticmethod
    async def is_super_admin(session: AsyncSession, user_id: Union[str, UUID]) -> bool:
        query = select(
            sql_exists()
            .where(UserRole.user_id == user_id)
            .where(Role.name == SUPER_ADMIN_ROLE)
            .where(UserRole.role_id == Role.id)
            .correlate(UserRole, Role)
        )
        result = await session.execute(query)
        return result.scalar()

    @staticmethod
    async def get_user_permissions(session: AsyncSession, user_id: Union[str, UUID]) -> Set[str]:
        query = (
            select(Permission.name.distinct())
            .join(RolePermission, RolePermission.permission_id == Permission.id)
            .join(UserRole, UserRole.role_id == RolePermission.role_id)
            .where(UserRole.user_id == user_id)
        )
        result = await session.execute(query)
        return set(result.scalars().all())


class PermissionChecker(BasePermissionChecker):
    """Standard permission checker for pure RBAC authorization."""
    pass


def require_permission(permission: str) -> PermissionChecker:
    return PermissionChecker(permission)


def require_any_permission(*permissions: str) -> PermissionChecker:
    return PermissionChecker(list(permissions), require_all=False)


def require_all_permissions(*permissions: str) -> PermissionChecker:
    return PermissionChecker(list(permissions), require_all=True)


async def has_permission(user: UserModel, permission: str, session: AsyncSession) -> bool:
    if await BasePermissionChecker.is_super_admin(session, user.id):
        return True
    user_permissions = await BasePermissionChecker.get_user_permissions(session, user.id)
    return permission in user_permissions


async def is_super_admin(user: UserModel, session: AsyncSession) -> bool:
    return await BasePermissionChecker.is_super_admin(session, user.id)
'''


def generate_user_permission_scoped_access() -> str:
    """Generate user/permission_management/scoped_access.py."""
    return '''"""
Generic Scoped Access Framework.

Provides plugin-based scope infrastructure for data access control.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any, Union
from uuid import UUID
from pydantic import BaseModel
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select
from sqlalchemy.orm import InstrumentedAttribute

from app.core.database import get_session
from app.user.models import User
from app.user.auth_management.utils import get_current_user_validated
from app.user.permission_management.utils import BasePermissionChecker


# ============== Scope Schema ==============

class AdminScope(BaseModel):
    """Generic admin scope - represents data access boundaries."""
    scope_type: str  # "global", "team", "department", etc.
    scope_id: Optional[UUID] = None
    metadata: Dict[str, Any] = {}

    @property
    def is_global(self) -> bool:
        return self.scope_type == "global"

    def is_scoped(self, scope_name: str) -> bool:
        return self.scope_type == scope_name


# ============== Scope Provider Interface ==============

class ScopeProvider(ABC):
    """Abstract interface for scope providers."""

    @property
    @abstractmethod
    def scope_name(self) -> str:
        """Unique name for this scope type."""
        pass

    @property
    @abstractmethod
    def permissions(self) -> List[str]:
        """Permissions that grant this scope."""
        pass

    @abstractmethod
    async def resolve_scope(
        self,
        session: AsyncSession,
        user: User
    ) -> AdminScope:
        """Resolve scope for a user."""
        pass

    @abstractmethod
    def apply_to_query(
        self,
        query: Select,
        scope: AdminScope,
        model: Any,
        user_id_column: str = "user_id",
        join_via: str = "direct",
        customer_columns: Optional[Dict[str, InstrumentedAttribute]] = None
    ) -> Select:
        """Apply scope filter to a SQLAlchemy query."""
        pass


# ============== Scope Registry ==============

class ScopeRegistry:
    """Registry for scope providers."""

    _providers: Dict[str, ScopeProvider] = {}

    @classmethod
    def register(cls, provider: ScopeProvider) -> None:
        cls._providers[provider.scope_name] = provider

    @classmethod
    def get(cls, scope_name: str) -> Optional[ScopeProvider]:
        return cls._providers.get(scope_name)

    @classmethod
    def get_by_permission(cls, permission: str) -> Optional[ScopeProvider]:
        for provider in cls._providers.values():
            if permission in provider.permissions:
                return provider
        return None

    @classmethod
    def all_scoped_permissions(cls) -> List[str]:
        perms = []
        for provider in cls._providers.values():
            perms.extend(provider.permissions)
        return perms

    @classmethod
    def clear(cls) -> None:
        cls._providers = {}


# ============== Scoped Permission Checker ==============

class ScopedPermissionChecker(BasePermissionChecker):
    """Permission checker that resolves admin scope."""

    def __init__(
        self,
        global_permissions: List[str],
        scoped_permissions: List[str]
    ):
        all_perms = global_permissions + scoped_permissions
        super().__init__(all_perms, require_all=False)
        self.global_permissions = global_permissions
        self.scoped_permissions = scoped_permissions

    async def __call__(
        self,
        current_user: User = Depends(get_current_user_validated),
        session: AsyncSession = Depends(get_session)
    ) -> tuple[User, AdminScope]:
        if await self.is_super_admin(session, current_user.id):
            return current_user, AdminScope(scope_type="global")

        user_perms = await self.get_user_permissions(session, current_user.id)

        if any(p in user_perms for p in self.global_permissions):
            return current_user, AdminScope(scope_type="global")

        for perm in self.scoped_permissions:
            if perm in user_perms:
                provider = ScopeRegistry.get_by_permission(perm)
                if provider:
                    scope = await provider.resolve_scope(session, current_user)
                    return current_user, scope

        self.handle_authorization_failure(current_user)
        raise Exception("Unreachable code")


def require_scoped_permission(
    global_permissions: List[str],
    scoped_permissions: List[str]
) -> ScopedPermissionChecker:
    return ScopedPermissionChecker(global_permissions, scoped_permissions)
'''
