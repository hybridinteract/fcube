"""
User module template generators.

Generates the app/user module with authentication, models, etc.
"""


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
from .schemas import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserLogin,
    TokenResponse,
)
from .routes import router

__all__ = [
    "User",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserLogin",
    "TokenResponse",
    "router",
]
'''


def generate_user_models() -> str:
    """Generate user/models.py with User model."""
    return '''"""
User database model.
"""

from datetime import datetime, timezone
from uuid import uuid4
from typing import Optional

from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.models import Base


class User(Base):
    """User database model."""
    
    __tablename__ = "users"
    
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True
    )
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
    full_name: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True
    )
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
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email})>"
'''


def generate_user_schemas() -> str:
    """Generate user/schemas.py with Pydantic schemas."""
    return '''"""
User Pydantic schemas.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, ConfigDict


# ==================== BASE SCHEMAS ====================

class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr
    full_name: Optional[str] = None


# ==================== CREATE/UPDATE SCHEMAS ====================

class UserCreate(UserBase):
    """Schema for creating a user."""
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    """Schema for updating a user."""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8)
    is_active: Optional[bool] = None


# ==================== RESPONSE SCHEMAS ====================

class UserResponse(UserBase):
    """User response schema."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime


class UserMinimal(BaseModel):
    """Minimal user schema for nested responses."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    email: str
    full_name: Optional[str] = None


# ==================== AUTH SCHEMAS ====================

class UserLogin(BaseModel):
    """Login request schema."""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Token response schema."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefresh(BaseModel):
    """Token refresh request schema."""
    refresh_token: str


class TokenPayload(BaseModel):
    """JWT token payload."""
    sub: str  # User ID
    exp: datetime
    type: str  # "access" or "refresh"
'''


def generate_user_crud() -> str:
    """Generate user/crud.py with user CRUD operations."""
    return '''"""
User CRUD operations.
"""

from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.crud import CRUDBase
from .models import User
from .schemas import UserCreate, UserUpdate


class UserCRUD(CRUDBase[User, UserCreate, UserUpdate]):
    """CRUD operations for User model."""
    
    def __init__(self):
        super().__init__(User)
    
    async def get_by_email(
        self,
        session: AsyncSession,
        email: str
    ) -> Optional[User]:
        """Get user by email."""
        query = select(self.model).where(self.model.email == email)
        result = await session.execute(query)
        return result.scalar_one_or_none()
    
    async def create_with_password(
        self,
        session: AsyncSession,
        *,
        obj_in: UserCreate,
        hashed_password: str
    ) -> User:
        """Create user with hashed password."""
        db_obj = User(
            email=obj_in.email,
            full_name=obj_in.full_name,
            hashed_password=hashed_password,
        )
        session.add(db_obj)
        await session.flush()
        await session.refresh(db_obj)
        return db_obj


user_crud = UserCRUD()
'''


def generate_user_exceptions() -> str:
    """Generate user/exceptions.py with user-related exceptions."""
    return '''"""
User module exceptions.
"""

from fastapi import HTTPException, status


class UserNotFoundError(HTTPException):
    """Raised when user is not found."""
    
    def __init__(self, identifier: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User not found: {identifier}"
        )


class UserAlreadyExistsError(HTTPException):
    """Raised when user already exists."""
    
    def __init__(self, email: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with email '{email}' already exists"
        )


class InvalidCredentialsError(HTTPException):
    """Raised when login credentials are invalid."""
    
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )


class InactiveUserError(HTTPException):
    """Raised when user account is inactive."""
    
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )


class InvalidTokenError(HTTPException):
    """Raised when token is invalid."""
    
    def __init__(self, message: str = "Invalid token"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=message,
            headers={"WWW-Authenticate": "Bearer"},
        )
'''


def generate_user_routes() -> str:
    """Generate user/routes.py."""
    return '''"""
User module routes aggregator.
"""

from fastapi import APIRouter

from .auth_management.routes import router as auth_router

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Include authentication routes
router.include_router(auth_router)
'''


def generate_user_auth_init() -> str:
    """Generate user/auth_management/__init__.py."""
    return '''"""
Authentication management submodule.

Provides authentication functionality:
- Login/logout
- Token generation and validation
- Password hashing
"""

from .service import AuthService
from .utils import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    get_current_user,
)

__all__ = [
    "AuthService",
    "get_password_hash",
    "verify_password",
    "create_access_token",
    "create_refresh_token",
    "get_current_user",
]
'''


def generate_user_auth_routes() -> str:
    """Generate user/auth_management/routes.py."""
    return '''"""
Authentication routes.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.logging import get_logger
from ..schemas import (
    UserCreate,
    UserResponse,
    UserLogin,
    TokenResponse,
    TokenRefresh,
)
from .service import AuthService
from .utils import get_current_user
from ..models import User

logger = get_logger(__name__)

router = APIRouter()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user"
)
async def register(
    user_data: UserCreate,
    session: AsyncSession = Depends(get_session),
):
    """Register a new user account."""
    return await AuthService.register(session, user_data)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login user"
)
async def login(
    credentials: UserLogin,
    session: AsyncSession = Depends(get_session),
):
    """Authenticate user and return access token."""
    return await AuthService.login(session, credentials)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token"
)
async def refresh_token(
    token_data: TokenRefresh,
    session: AsyncSession = Depends(get_session),
):
    """Refresh access token using refresh token."""
    return await AuthService.refresh_token(session, token_data.refresh_token)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user"
)
async def get_me(
    current_user: User = Depends(get_current_user),
):
    """Get current authenticated user."""
    return current_user
'''


def generate_user_auth_service() -> str:
    """Generate user/auth_management/service.py."""
    return '''"""
Authentication service.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from ..models import User
from ..schemas import UserCreate, UserLogin, TokenResponse
from ..crud import user_crud
from ..exceptions import (
    UserAlreadyExistsError,
    InvalidCredentialsError,
    InactiveUserError,
    InvalidTokenError,
)
from .utils import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)

logger = get_logger(__name__)


class AuthService:
    """Authentication service for user login and registration."""
    
    @staticmethod
    async def register(
        session: AsyncSession,
        user_data: UserCreate
    ) -> User:
        """Register a new user."""
        # Check if user exists
        existing = await user_crud.get_by_email(session, user_data.email)
        if existing:
            raise UserAlreadyExistsError(user_data.email)
        
        # Hash password and create user
        hashed_password = get_password_hash(user_data.password)
        user = await user_crud.create_with_password(
            session,
            obj_in=user_data,
            hashed_password=hashed_password
        )
        
        await session.commit()
        await session.refresh(user)
        
        logger.info(f"User registered: {user.email}")
        return user
    
    @staticmethod
    async def login(
        session: AsyncSession,
        credentials: UserLogin
    ) -> TokenResponse:
        """Authenticate user and return tokens."""
        # Get user
        user = await user_crud.get_by_email(session, credentials.email)
        if not user:
            raise InvalidCredentialsError()
        
        # Verify password
        if not verify_password(credentials.password, user.hashed_password):
            raise InvalidCredentialsError()
        
        # Check if active
        if not user.is_active:
            raise InactiveUserError()
        
        # Generate tokens
        access_token = create_access_token(str(user.id))
        refresh_token = create_refresh_token(str(user.id))
        
        logger.info(f"User logged in: {user.email}")
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token
        )
    
    @staticmethod
    async def refresh_token(
        session: AsyncSession,
        refresh_token: str
    ) -> TokenResponse:
        """Refresh access token."""
        # Decode refresh token
        payload = decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise InvalidTokenError("Invalid token type")
        
        user_id = payload.get("sub")
        if not user_id:
            raise InvalidTokenError("Invalid token payload")
        
        # Verify user exists and is active
        user = await user_crud.get(session, user_id)
        if not user or not user.is_active:
            raise InvalidTokenError("User not found or inactive")
        
        # Generate new tokens
        new_access_token = create_access_token(str(user.id))
        new_refresh_token = create_refresh_token(str(user.id))
        
        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token
        )
'''


def generate_user_auth_utils() -> str:
    """Generate user/auth_management/utils.py."""
    return '''"""
Authentication utilities.

Provides password hashing, token generation, and user retrieval.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.settings import settings
from app.core.database import get_session
from ..models import User
from ..crud import user_crud

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(subject: str) -> str:
    """Create an access token."""
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode = {
        "sub": subject,
        "exp": expire,
        "type": "access"
    }
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(subject: str) -> str:
    """Create a refresh token."""
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
    )
    to_encode = {
        "sub": subject,
        "exp": expire,
        "type": "refresh"
    }
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    """Decode and validate a JWT token."""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session),
) -> User:
    """Get current authenticated user from token."""
    payload = decode_token(token)
    
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    
    user = await user_crud.get(session, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )
    
    return user


async def get_current_active_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get current superuser."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    return current_user
'''
