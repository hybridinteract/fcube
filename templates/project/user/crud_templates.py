"""
User CRUD Templates.

Generates CRUD operations for User model.
"""


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
