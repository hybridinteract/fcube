"""
User Exception Templates.

Generates custom HTTP exceptions for User module.
"""


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
