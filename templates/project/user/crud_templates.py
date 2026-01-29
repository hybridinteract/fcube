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
