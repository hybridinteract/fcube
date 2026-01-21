"""
CRUD template generators.

Generates CRUD operations following the "No Commit in CRUD" pattern.
"""


def generate_crud(module_name: str, class_name: str) -> str:
    """
    Generate CRUD operations file.
    
    Follows the pattern from app/service_provider/crud/provider_crud.py
    with the "No Commit in CRUD" principle.
    """
    return f'''"""
{class_name} CRUD operations.

This module provides data access operations for the {class_name} model.

IMPORTANT: CRUD methods do NOT commit transactions.
The service layer owns transaction boundaries.

Pattern:
- Use session.flush() to get database-generated IDs
- Use session.refresh() to load relationships
- NEVER call session.commit() - let service layer handle it
"""

from typing import Optional, List
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.crud import CRUDBase
from ..models import {class_name}
from ..schemas import {class_name}Create, {class_name}Update


class {class_name}CRUD(CRUDBase[{class_name}, {class_name}Create, {class_name}Update]):
    """
    CRUD operations for {class_name} model.
    
    Extends CRUDBase with custom query methods.
    All methods follow the "No Commit in CRUD" pattern.
    """
    
    def __init__(self):
        super().__init__({class_name})
    
    # ==================== READ OPERATIONS ====================
    
    async def get_by_name(
        self,
        session: AsyncSession,
        name: str
    ) -> Optional[{class_name}]:
        """
        Get a {module_name} by name.
        
        Args:
            session: Database session
            name: Name to search for
            
        Returns:
            {class_name} instance or None if not found
        """
        query = select(self.model).where(self.model.name == name)
        result = await session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_active(
        self,
        session: AsyncSession,
        skip: int = 0,
        limit: int = 100
    ) -> List[{class_name}]:
        """
        Get all active {module_name}s.
        
        Args:
            session: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of active {class_name} instances
        """
        query = (
            select(self.model)
            .where(self.model.is_active == True)
            .offset(skip)
            .limit(limit)
            .order_by(self.model.created_at.desc())
        )
        result = await session.execute(query)
        return list(result.scalars().all())
    
    async def get_with_relationships(
        self,
        session: AsyncSession,
        id: UUID
    ) -> Optional[{class_name}]:
        """
        Get a {module_name} with all relationships loaded.
        
        Args:
            session: Database session
            id: Primary key UUID
            
        Returns:
            {class_name} instance with relationships or None
        """
        query = (
            select(self.model)
            .where(self.model.id == id)
            # Add selectinload for relationships:
            # .options(selectinload(self.model.user))
        )
        result = await session.execute(query)
        return result.scalar_one_or_none()
    
    # ==================== WRITE OPERATIONS ====================
    
    async def create(
        self,
        session: AsyncSession,
        *,
        obj_in: {class_name}Create
    ) -> {class_name}:
        """
        Create a new {module_name}.
        
        Note: Does NOT commit. Call session.commit() from service layer.
        
        Args:
            session: Database session
            obj_in: Create schema with input data
            
        Returns:
            Created {class_name} instance
        """
        obj_data = obj_in.model_dump()
        db_obj = self.model(**obj_data)
        session.add(db_obj)
        await session.flush()      # Get database-generated ID
        await session.refresh(db_obj)  # Ensure object is fully loaded
        # NO session.commit() - service layer owns transactions
        return db_obj
    
    async def deactivate(
        self,
        session: AsyncSession,
        id: UUID
    ) -> Optional[{class_name}]:
        """
        Soft delete a {module_name} by setting is_active to False.
        
        Note: Does NOT commit. Call session.commit() from service layer.
        
        Args:
            session: Database session
            id: Primary key UUID
            
        Returns:
            Updated {class_name} instance or None if not found
        """
        db_obj = await self.get(session, id)
        if db_obj:
            db_obj.is_active = False
            await session.flush()
            await session.refresh(db_obj)
        return db_obj
    
    # ==================== COUNT OPERATIONS ====================
    
    async def count_active(self, session: AsyncSession) -> int:
        """
        Count total number of active {module_name}s.
        
        Args:
            session: Database session
            
        Returns:
            Count of active records
        """
        query = select(func.count(self.model.id)).where(
            self.model.is_active == True
        )
        result = await session.execute(query)
        return result.scalar() or 0


# Singleton instance for dependency injection
{module_name}_crud = {class_name}CRUD()
'''


def generate_crud_init(module_name: str, class_name: str) -> str:
    """
    Generate crud/__init__.py file.
    
    Follows the pattern from app/service_provider/crud/__init__.py
    """
    return f'''"""
{class_name} CRUD Package.

This module exports all CRUD operations for the {module_name} module.
"""

from .{module_name}_crud import {class_name}CRUD, {module_name}_crud

__all__ = [
    "{class_name}CRUD",
    "{module_name}_crud",
]
'''
