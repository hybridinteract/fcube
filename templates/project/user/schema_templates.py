"""
User Schema Templates.

Generates Pydantic schemas for User operations.
Supports different authentication strategies:
- email: Email + Password authentication
- phone: Phone + OTP authentication  
- both: Combined email and phone authentication
"""

from .model_templates import AuthType


def generate_user_schemas(auth_type: AuthType = AuthType.EMAIL) -> str:
    """Generate user/schemas.py with Pydantic schemas.
    
    Args:
        auth_type: The authentication type - email, phone, or both.
    """
    # Build auth-specific schemas
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


# ==================== BASE SCHEMAS ====================

class UserBase(BaseModel):
    """Base user schema."""
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    full_name: Optional[str] = None

{email_schemas}
{phone_schemas}

# ==================== UPDATE SCHEMAS ====================

class UserUpdate(BaseModel):
    """Schema for updating a user."""
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None


# ==================== RESPONSE SCHEMAS ====================

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


class UserMinimal(BaseModel):
    """Minimal user schema for nested responses."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    email: Optional[str] = None
    phone_number: Optional[str] = None
    full_name: Optional[str] = None


# ==================== TOKEN SCHEMAS ====================

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
