"""
User Auth Templates.

Generates auth_management submodule templates:
- __init__.py
- routes.py  
- service.py
- utils.py
"""


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


# Alias for permission_management compatibility
get_current_user_validated = get_current_user


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
