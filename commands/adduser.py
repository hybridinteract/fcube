"""
Add User Command - Adds user module with configurable authentication.

Supports different authentication strategies:
- email: Email + Password authentication (JWT tokens)
- phone: Phone + OTP authentication (SMS verification)
- both: Combined email and phone authentication

Creates the user module structure:
app/user/
├── __init__.py
├── models.py
├── schemas.py
├── crud.py
├── exceptions.py
├── routes.py
├── auth_management/
│   ├── __init__.py
│   ├── routes.py
│   ├── service.py
│   └── utils.py
└── permission_management/
    ├── __init__.py
    ├── utils.py
    └── scoped_access.py
"""

import typer
from pathlib import Path
from enum import Enum
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from typing import List, Tuple

from ..utils.helpers import (
    to_snake_case,
    to_pascal_case,
    ensure_directory,
    write_file,
)

console = Console()


class AuthType(str, Enum):
    """Authentication type options."""
    EMAIL = "email"
    PHONE = "phone"
    BOTH = "both"


# ============== EMAIL AUTH TEMPLATES ==============

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


# ============== SHARED TEMPLATES ==============

def _generate_user_init() -> str:
    """Generate user/__init__.py"""
    return '''"""
User module for authentication and user management.
"""

from .models import User
from .routes import router

__all__ = ["User", "router"]
'''


def _generate_user_schemas(auth_type: AuthType) -> str:
    """Generate user/schemas.py based on auth type."""
    email_schemas = '''
class UserCreate(UserBase):
    """Schema for creating a user with email/password."""
    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    """Login request schema."""
    email: EmailStr
    password: str
''' if auth_type in [AuthType.EMAIL, AuthType.BOTH] else ''

    phone_schemas = '''
class PhoneLoginRequest(BaseModel):
    """Request OTP for phone login."""
    phone_number: str = Field(..., pattern=r"^\\+?[1-9]\\d{1,14}$")


class OTPVerifyRequest(BaseModel):
    """Verify OTP code."""
    phone_number: str
    otp_code: str = Field(..., min_length=4, max_length=6)
''' if auth_type in [AuthType.PHONE, AuthType.BOTH] else ''

    return f'''"""
User Pydantic schemas.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserBase(BaseModel):
    """Base user schema."""
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    full_name: Optional[str] = None


{email_schemas}
{phone_schemas}

class UserUpdate(BaseModel):
    """Schema for updating a user."""
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    """User response schema."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    email: Optional[str] = None
    phone_number: Optional[str] = None
    full_name: Optional[str] = None
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime


class TokenResponse(BaseModel):
    """Token response schema."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefresh(BaseModel):
    """Token refresh request schema."""
    refresh_token: str
'''


def _generate_user_crud() -> str:
    """Generate user/crud.py"""
    return '''"""
User CRUD operations.
"""

from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.crud import CRUDBase
from .models import User
from .schemas import UserUpdate


class UserCRUD(CRUDBase[User, UserUpdate, UserUpdate]):
    """CRUD operations for User model."""
    
    def __init__(self):
        super().__init__(User)
    
    async def get_by_email(self, session: AsyncSession, email: str) -> Optional[User]:
        """Get user by email."""
        query = select(self.model).where(self.model.email == email)
        result = await session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_phone(self, session: AsyncSession, phone_number: str) -> Optional[User]:
        """Get user by phone number."""
        query = select(self.model).where(self.model.phone_number == phone_number)
        result = await session.execute(query)
        return result.scalar_one_or_none()


user_crud = UserCRUD()
'''


def _generate_user_exceptions() -> str:
    """Generate user/exceptions.py"""
    return '''"""
User module exceptions.
"""

from fastapi import HTTPException, status


class UserNotFoundError(HTTPException):
    def __init__(self, identifier: str):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=f"User not found: {identifier}")


class UserAlreadyExistsError(HTTPException):
    def __init__(self, identifier: str):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=f"User already exists: {identifier}")


class InvalidCredentialsError(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials", headers={"WWW-Authenticate": "Bearer"})


class InactiveUserError(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail="User account is inactive")


class InvalidTokenError(HTTPException):
    def __init__(self, message: str = "Invalid token"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=message, headers={"WWW-Authenticate": "Bearer"})


class InvalidOTPError(HTTPException):
    def __init__(self, message: str = "Invalid or expired OTP"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=message)


class OTPExpiredError(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail="OTP has expired")


class OTPMaxAttemptsError(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Maximum OTP attempts exceeded")
'''


def _generate_user_routes() -> str:
    """Generate user/routes.py"""
    return '''"""
User module routes aggregator.
"""

from fastapi import APIRouter

from .auth_management.routes import router as auth_router

router = APIRouter(prefix="/auth", tags=["Authentication"])
router.include_router(auth_router)
'''


def _generate_apis_v1_with_user() -> str:
    """Generate apis/v1.py with user module."""
    return '''"""
API Version 1 Router.
"""

from fastapi import APIRouter

from app.user.routes import router as user_router

router = APIRouter(prefix="/v1")
router.include_router(user_router)

# Add more module routers:
# from app.product.routes import router as product_router
# router.include_router(product_router)
'''


def adduser_command(
    directory: str = "app",
    auth_type: AuthType = AuthType.EMAIL,
    force: bool = False,
):
    """
    Add user module with configurable authentication.
    """
    console.print(f"\n[bold blue]🧊 FCube CLI - Adding User Module...[/bold blue]\n")
    console.print(f"[cyan]Authentication Type:[/cyan] [bold]{auth_type.value}[/bold]\n")
    
    # Define paths
    base_dir = Path.cwd()
    app_dir = base_dir / directory
    user_dir = app_dir / "user"
    
    # Check if app directory exists
    if not app_dir.exists():
        console.print(f"[bold red]❌ Error:[/bold red] Directory '{directory}' not found.")
        console.print(f"[yellow]💡 Tip:[/yellow] Make sure you're in the project root directory.")
        raise typer.Exit(1)
    
    # Check if user module already exists
    if user_dir.exists() and not force:
        console.print(f"[bold red]❌ Error:[/bold red] User module already exists at {user_dir}")
        console.print(f"[yellow]💡 Tip:[/yellow] Use --force to overwrite existing files")
        raise typer.Exit(1)
    
    # Create directories
    console.print(f"[cyan]📁 Creating user module structure...[/cyan]")
    
    directories = [
        user_dir,
        user_dir / "auth_management",
        user_dir / "permission_management",
    ]
    
    for dir_path in directories:
        ensure_directory(dir_path)
    
    # Select model template based on auth type
    if auth_type == AuthType.EMAIL:
        models_content = _generate_user_models_email()
    elif auth_type == AuthType.PHONE:
        models_content = _generate_user_models_phone()
    else:
        models_content = _generate_user_models_both()
    
    # Import shared templates
    from ..templates.project.user import (
        generate_user_auth_init,
        generate_user_auth_routes,
        generate_user_auth_service,
        generate_user_auth_utils,
        generate_user_permission_init,
        generate_user_permission_utils,
        generate_user_permission_scoped_access,
    )
    
    # Generate files
    files_to_create: List[Tuple[Path, str]] = [
        (user_dir / "__init__.py", _generate_user_init()),
        (user_dir / "models.py", models_content),
        (user_dir / "schemas.py", _generate_user_schemas(auth_type)),
        (user_dir / "crud.py", _generate_user_crud()),
        (user_dir / "exceptions.py", _generate_user_exceptions()),
        (user_dir / "routes.py", _generate_user_routes()),
        # Auth management
        (user_dir / "auth_management" / "__init__.py", generate_user_auth_init()),
        (user_dir / "auth_management" / "routes.py", generate_user_auth_routes()),
        (user_dir / "auth_management" / "service.py", generate_user_auth_service()),
        (user_dir / "auth_management" / "utils.py", generate_user_auth_utils()),
        # Permission management
        (user_dir / "permission_management" / "__init__.py", generate_user_permission_init()),
        (user_dir / "permission_management" / "utils.py", generate_user_permission_utils()),
        (user_dir / "permission_management" / "scoped_access.py", generate_user_permission_scoped_access()),
    ]
    
    # Create files
    console.print(f"[cyan]📝 Generating files...[/cyan]\n")
    
    created_files = []
    for file_path, content in files_to_create:
        relative_path = file_path.relative_to(base_dir)
        if write_file(file_path, content, overwrite=force):
            created_files.append(str(relative_path))
            console.print(f"  [green]✓[/green] Created: {relative_path}")
    
    # Update apis/v1.py
    v1_path = app_dir / "apis" / "v1.py"
    if v1_path.exists():
        write_file(v1_path, _generate_apis_v1_with_user(), overwrite=True)
        console.print(f"  [green]✓[/green] Updated: {v1_path.relative_to(base_dir)}")
    
    # Summary
    console.print()
    
    summary_table = Table(title="📊 User Module Summary", show_header=False, box=None)
    summary_table.add_row("[bold]Auth Type:[/bold]", f"[cyan]{auth_type.value}[/cyan]")
    summary_table.add_row("[bold]Location:[/bold]", f"[cyan]{user_dir}[/cyan]")
    summary_table.add_row("[bold]Files Created:[/bold]", f"[green]{len(created_files)}[/green]")
    
    if auth_type == AuthType.EMAIL:
        summary_table.add_row("[bold]Features:[/bold]", "Email + Password, JWT tokens")
    elif auth_type == AuthType.PHONE:
        summary_table.add_row("[bold]Features:[/bold]", "Phone + OTP, SMS verification")
    else:
        summary_table.add_row("[bold]Features:[/bold]", "Email + Password, Phone + OTP")
    
    console.print(summary_table)
    console.print()
    
    # Next steps
    next_steps = f"""
[bold cyan]1. Update alembic_models_import.py[/bold cyan]
   [dim]Add: from app.user.models import User, Role, Permission[/dim]

[bold cyan]2. Generate migration[/bold cyan]
   [dim]alembic revision --autogenerate -m "Add user module"
   alembic upgrade head[/dim]

[bold cyan]3. API Endpoints[/bold cyan]
   [dim]POST /api/v1/auth/register - Register user
   POST /api/v1/auth/login - Login user
   GET  /api/v1/auth/me - Get current user[/dim]
"""
    if auth_type in [AuthType.PHONE, AuthType.BOTH]:
        next_steps += """
[bold cyan]4. Configure SMS Provider[/bold cyan]
   [dim]Add SMS_API_KEY, SMS_SENDER_ID to .env
   Implement SMS service in auth_management/sms.py[/dim]
"""
    
    console.print(Panel(next_steps, title="[bold green]✨ Next Steps[/bold green]", border_style="green"))
    console.print(f"\n[bold green]✅ User module added successfully![/bold green]\n")
