"""
User Model Templates.

Generates User, Role, Permission, and association models.
Supports different authentication strategies:
- email: Email + Password authentication
- phone: Phone + OTP authentication  
- both: Combined email and phone authentication
"""

from enum import Enum


class AuthType(str, Enum):
    """Authentication type options."""
    EMAIL = "email"
    PHONE = "phone"
    BOTH = "both"


def generate_user_init() -> str:
    """Generate user/__init__.py"""
    return '''"""
User module for authentication and user management.

This module provides:
- User model and schemas
- Authentication (login, register, token refresh)
- User CRUD operations
"""

from .models import User
from .routes import router

__all__ = [
    "User",
    "router",
]
'''


def generate_user_models(auth_type: AuthType = AuthType.EMAIL) -> str:
    """Generate user/models.py with User and RBAC models.
    
    Args:
        auth_type: The authentication type - email, phone, or both.
    """
    if auth_type == AuthType.EMAIL:
        return _generate_user_models_email()
    elif auth_type == AuthType.PHONE:
        return _generate_user_models_phone()
    else:
        return _generate_user_models_both()


def _generate_user_models_email() -> str:
    """Generate user models with email authentication."""
    return '''"""
User database models.
"""

from datetime import datetime, timezone
from uuid import uuid4, UUID as UUIDType
from typing import Optional, List
from enum import Enum

from sqlalchemy import String, DateTime, Boolean, Text, Enum as SQLEnum, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.models import Base


def utc_now():
    """Reusable function for UTC timestamp defaults."""
    return datetime.now(timezone.utc)


class UserType(str, Enum):
    """Enum for different user types.
    
    Add project-specific user types below ADMIN_STAFF.
    Examples: SERVICE_PROVIDER, B2B_CLIENT, B2C_CLIENT, etc.
    """
    ADMIN_STAFF = "admin_staff"
    # Add your project-specific user types here:
    # CUSTOMER = "customer"
    # SERVICE_PROVIDER = "service_provider"


class UserStatus(str, Enum):
    """Enum for user account status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING_VERIFICATION = "pending_verification"


class User(Base):
    """User model with email/password authentication."""
    
    __tablename__ = "users"
    __table_args__ = (
        Index('ix_users_type_status', 'user_type', 'status'),
    )
    
    id: Mapped[UUIDType] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )
    
    # Email authentication
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    email_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
    
    # Basic details
    full_name: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True
    )
    user_type: Mapped[UserType] = mapped_column(
        SQLEnum(UserType, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=UserType.ADMIN_STAFF
    )
    status: Mapped[UserStatus] = mapped_column(
        SQLEnum(UserStatus, values_callable=lambda x: [e.value for e in x]),
        default=UserStatus.ACTIVE,
        nullable=False
    )
    
    # Status flags
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )
    is_superuser: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False
    )
    
    # Relationships
    roles: Mapped[List["Role"]] = relationship(
        "Role",
        secondary="user_roles",
        back_populates="users",
        lazy="selectin"
    )
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email})>"


class Permission(Base):
    """Permission model for RBAC."""

    __tablename__ = "permissions"
    __table_args__ = (
        Index('ix_permissions_resource_action', 'resource', 'action'),
    )

    id: Mapped[UUIDType] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )

    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False
    )

    resource: Mapped[str] = mapped_column(String(50), nullable=False)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False
    )

    roles: Mapped[List["Role"]] = relationship(
        "Role",
        secondary="role_permissions",
        back_populates="permissions",
        lazy="noload"
    )


class Role(Base):
    """Role model for RBAC."""

    __tablename__ = "roles"

    id: Mapped[UUIDType] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )

    name: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False
    )
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_system: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False
    )

    permissions: Mapped[List["Permission"]] = relationship(
        "Permission",
        secondary="role_permissions",
        back_populates="roles",
        lazy="selectin"
    )
    users: Mapped[List["User"]] = relationship(
        "User",
        secondary="user_roles",
        back_populates="roles",
        lazy="noload"
    )


class RolePermission(Base):
    """Association table for Role-Permission."""

    __tablename__ = "role_permissions"

    role_id: Mapped[UUIDType] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True
    )
    permission_id: Mapped[UUIDType] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("permissions.id", ondelete="CASCADE"),
        primary_key=True
    )
    granted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False
    )


class UserRole(Base):
    """Association table for User-Role."""

    __tablename__ = "user_roles"

    user_id: Mapped[UUIDType] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True
    )
    role_id: Mapped[UUIDType] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True
    )
    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False
    )
'''


def _generate_user_models_phone() -> str:
    """Generate user models with phone OTP authentication."""
    return '''"""
User database models with Phone OTP authentication.
"""

from datetime import datetime, timezone
from uuid import uuid4, UUID as UUIDType
from typing import Optional, List
from enum import Enum

from sqlalchemy import String, DateTime, Boolean, Text, Enum as SQLEnum, ForeignKey, Index, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.models import Base


def utc_now():
    """Reusable function for UTC timestamp defaults."""
    return datetime.now(timezone.utc)


class UserType(str, Enum):
    """Enum for different user types."""
    ADMIN_STAFF = "admin_staff"
    # Add your project-specific user types here


class UserStatus(str, Enum):
    """Enum for user account status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING_VERIFICATION = "pending_verification"


class User(Base):
    """User model with phone OTP authentication."""
    
    __tablename__ = "users"
    __table_args__ = (
        Index('ix_users_type_status', 'user_type', 'status'),
    )
    
    id: Mapped[UUIDType] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )
    
    # Phone authentication
    phone_number: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        index=True,
        nullable=False
    )
    phone_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
    
    # Basic details
    full_name: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True
    )
    user_type: Mapped[UserType] = mapped_column(
        SQLEnum(UserType, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=UserType.ADMIN_STAFF
    )
    status: Mapped[UserStatus] = mapped_column(
        SQLEnum(UserStatus, values_callable=lambda x: [e.value for e in x]),
        default=UserStatus.PENDING_VERIFICATION,
        nullable=False
    )
    
    # Status flags
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )
    is_superuser: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False
    )
    
    # Relationships
    roles: Mapped[List["Role"]] = relationship(
        "Role",
        secondary="user_roles",
        back_populates="users",
        lazy="selectin"
    )
    otp_codes: Mapped[List["OTPCode"]] = relationship(
        "OTPCode",
        back_populates="user",
        lazy="noload"
    )
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, phone={self.phone_number})>"


class OTPCode(Base):
    """OTP code for phone verification."""
    
    __tablename__ = "otp_codes"
    
    id: Mapped[UUIDType] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )
    user_id: Mapped[UUIDType] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    code: Mapped[str] = mapped_column(
        String(6),
        nullable=False
    )
    purpose: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="login"  # login, register, reset, etc.
    )
    attempts: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )
    max_attempts: Mapped[int] = mapped_column(
        Integer,
        default=3,
        nullable=False
    )
    is_used: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False
    )
    
    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="otp_codes"
    )
    
    @property
    def is_expired(self) -> bool:
        return datetime.now(timezone.utc) > self.expires_at
    
    @property
    def is_valid(self) -> bool:
        return not self.is_used and not self.is_expired and self.attempts < self.max_attempts


class Permission(Base):
    """Permission model for RBAC."""
    __tablename__ = "permissions"
    __table_args__ = (
        Index('ix_permissions_resource_action', 'resource', 'action'),
    )

    id: Mapped[UUIDType] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    resource: Mapped[str] = mapped_column(String(50), nullable=False)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    roles: Mapped[List["Role"]] = relationship("Role", secondary="role_permissions", back_populates="permissions", lazy="noload")


class Role(Base):
    """Role model for RBAC."""
    __tablename__ = "roles"

    id: Mapped[UUIDType] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_system: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)
    permissions: Mapped[List["Permission"]] = relationship("Permission", secondary="role_permissions", back_populates="roles", lazy="selectin")
    users: Mapped[List["User"]] = relationship("User", secondary="user_roles", back_populates="roles", lazy="noload")


class RolePermission(Base):
    """Association table for Role-Permission."""
    __tablename__ = "role_permissions"
    role_id: Mapped[UUIDType] = mapped_column(UUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True)
    permission_id: Mapped[UUIDType] = mapped_column(UUID(as_uuid=True), ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True)
    granted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)


class UserRole(Base):
    """Association table for User-Role."""
    __tablename__ = "user_roles"
    user_id: Mapped[UUIDType] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    role_id: Mapped[UUIDType] = mapped_column(UUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True)
    assigned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
'''


def _generate_user_models_both() -> str:
    """Generate user models with both email and phone authentication."""
    return '''"""
User database models with Email + Phone OTP authentication.
"""

from datetime import datetime, timezone
from uuid import uuid4, UUID as UUIDType
from typing import Optional, List
from enum import Enum

from sqlalchemy import String, DateTime, Boolean, Text, Enum as SQLEnum, ForeignKey, Index, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.models import Base


def utc_now():
    return datetime.now(timezone.utc)


class UserType(str, Enum):
    """Enum for different user types."""
    ADMIN_STAFF = "admin_staff"


class UserStatus(str, Enum):
    """Enum for user account status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING_VERIFICATION = "pending_verification"


class User(Base):
    """User model with both email and phone authentication."""
    
    __tablename__ = "users"
    __table_args__ = (
        Index('ix_users_type_status', 'user_type', 'status'),
    )
    
    id: Mapped[UUIDType] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # Email authentication (optional)
    email: Mapped[Optional[str]] = mapped_column(String(255), unique=True, index=True, nullable=True)
    hashed_password: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Phone authentication (optional)
    phone_number: Mapped[Optional[str]] = mapped_column(String(20), unique=True, index=True, nullable=True)
    phone_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Basic details
    full_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    user_type: Mapped[UserType] = mapped_column(
        SQLEnum(UserType, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=UserType.ADMIN_STAFF
    )
    status: Mapped[UserStatus] = mapped_column(
        SQLEnum(UserStatus, values_callable=lambda x: [e.value for e in x]),
        default=UserStatus.ACTIVE,
        nullable=False
    )
    
    # Status flags
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)
    
    # Relationships
    roles: Mapped[List["Role"]] = relationship("Role", secondary="user_roles", back_populates="users", lazy="selectin")
    otp_codes: Mapped[List["OTPCode"]] = relationship("OTPCode", back_populates="user", lazy="noload")
    
    def __repr__(self) -> str:
        identifier = self.email or self.phone_number
        return f"<User(id={self.id}, identifier={identifier})>"


class OTPCode(Base):
    """OTP code for phone verification."""
    __tablename__ = "otp_codes"
    
    id: Mapped[UUIDType] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUIDType] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    code: Mapped[str] = mapped_column(String(6), nullable=False)
    purpose: Mapped[str] = mapped_column(String(50), nullable=False, default="login")
    attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    max_attempts: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    is_used: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    
    user: Mapped["User"] = relationship("User", back_populates="otp_codes")
    
    @property
    def is_expired(self) -> bool:
        return datetime.now(timezone.utc) > self.expires_at
    
    @property
    def is_valid(self) -> bool:
        return not self.is_used and not self.is_expired and self.attempts < self.max_attempts


class Permission(Base):
    __tablename__ = "permissions"
    __table_args__ = (Index('ix_permissions_resource_action', 'resource', 'action'),)
    id: Mapped[UUIDType] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    resource: Mapped[str] = mapped_column(String(50), nullable=False)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    roles: Mapped[List["Role"]] = relationship("Role", secondary="role_permissions", back_populates="permissions", lazy="noload")


class Role(Base):
    __tablename__ = "roles"
    id: Mapped[UUIDType] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_system: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)
    permissions: Mapped[List["Permission"]] = relationship("Permission", secondary="role_permissions", back_populates="roles", lazy="selectin")
    users: Mapped[List["User"]] = relationship("User", secondary="user_roles", back_populates="roles", lazy="noload")


class RolePermission(Base):
    __tablename__ = "role_permissions"
    role_id: Mapped[UUIDType] = mapped_column(UUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True)
    permission_id: Mapped[UUIDType] = mapped_column(UUID(as_uuid=True), ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True)
    granted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)


class UserRole(Base):
    __tablename__ = "user_roles"
    user_id: Mapped[UUIDType] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    role_id: Mapped[UUIDType] = mapped_column(UUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True)
    assigned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
'''
