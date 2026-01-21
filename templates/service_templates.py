"""
Service template generators.

Generates service layer following the business logic patterns.
Services own transaction boundaries and call commit().
"""


def generate_service(module_name: str, class_name: str) -> str:
    """
    Generate service layer file.
    
    Follows the pattern from app/service_provider/services/provider_service.py
    Services own transaction boundaries (commit happens here, not in CRUD).
    """
    return f'''"""
{class_name} Service - Business Logic Layer.

This service handles all business logic for {module_name} operations.

Responsibilities:
- Orchestrate business operations
- Enforce business rules and validations
- Control transaction boundaries (call commit)
- Coordinate between CRUD operations
- Handle post-commit operations (notifications, tasks)

Pattern:
- CRUD operations do NOT commit
- Service calls session.commit() after all operations
- Use session.refresh() after commit for fresh data
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from ..models import {class_name}
from ..schemas import {class_name}Create, {class_name}CreateRequest, {class_name}Update
from ..crud import {module_name}_crud
from ..exceptions import {class_name}NotFoundError, {class_name}AlreadyExistsError

logger = get_logger(__name__)


class {class_name}Service:
    """
    Service layer for {module_name} business logic.
    
    This service follows the Single Responsibility Principle,
    handling only {module_name}-related operations.
    """
    
    # ==================== READ OPERATIONS ====================
    
    @staticmethod
    async def get_all_{module_name}s(
        session: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = True
    ) -> List[{class_name}]:
        """
        Get all {module_name}s with pagination.
        
        Args:
            session: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            active_only: If True, return only active records
            
        Returns:
            List of {class_name} instances
        """
        logger.info(f"Fetching {module_name}s (skip={{skip}}, limit={{limit}}, active_only={{active_only}})")
        
        if active_only:
            return await {module_name}_crud.get_active(session, skip, limit)
        return await {module_name}_crud.get_multi(session, skip=skip, limit=limit)
    
    @staticmethod
    async def get_{module_name}_by_id(
        session: AsyncSession,
        {module_name}_id: UUID,
        include_relationships: bool = False
    ) -> {class_name}:
        """
        Get a {module_name} by ID.
        
        Args:
            session: Database session
            {module_name}_id: UUID of the {module_name}
            include_relationships: If True, load all relationships
            
        Returns:
            {class_name} instance
            
        Raises:
            {class_name}NotFoundError: If {module_name} not found
        """
        if include_relationships:
            {module_name} = await {module_name}_crud.get_with_relationships(
                session, {module_name}_id
            )
        else:
            {module_name} = await {module_name}_crud.get(session, {module_name}_id)
        
        if not {module_name}:
            logger.warning(f"{class_name} not found: {{{module_name}_id}}")
            raise {class_name}NotFoundError(str({module_name}_id))
        
        return {module_name}
    
    @staticmethod
    async def get_{module_name}_by_name(
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
        return await {module_name}_crud.get_by_name(session, name)
    
    # ==================== WRITE OPERATIONS ====================
    
    @staticmethod
    async def create_{module_name}(
        session: AsyncSession,
        {module_name}_data: {class_name}CreateRequest,
        # current_user = None  # Add if needed for ownership
    ) -> {class_name}:
        """
        Create a new {module_name}.
        
        Args:
            session: Database session
            {module_name}_data: Data for creating the {module_name}
            
        Returns:
            Created {class_name} instance
            
        Raises:
            {class_name}AlreadyExistsError: If {module_name} with same name exists
        """
        logger.info(f"Creating {module_name}: {{{module_name}_data.name}}")
        
        # 1. Business validation - check for duplicates
        existing = await {module_name}_crud.get_by_name(session, {module_name}_data.name)
        if existing:
            logger.warning(f"{class_name} already exists: {{{module_name}_data.name}}")
            raise {class_name}AlreadyExistsError({module_name}_data.name)
        
        # 2. Create internal schema with any system-generated fields
        create_data = {class_name}Create(**{module_name}_data.model_dump())
        
        # 3. Data operation
        {module_name} = await {module_name}_crud.create(session, obj_in=create_data)
        
        # 4. Commit the transaction (service layer owns this)
        await session.commit()
        
        # 5. Refresh for fresh data after commit
        await session.refresh({module_name})
        
        # 6. Post-commit operations (background tasks, notifications)
        # Example: trigger background task
        # from .tasks import process_{module_name}_created
        # process_{module_name}_created.delay(str({module_name}.id))
        
        logger.info(f"{class_name} created successfully: {{{module_name}.id}}")
        return {module_name}
    
    @staticmethod
    async def update_{module_name}(
        session: AsyncSession,
        {module_name}_id: UUID,
        {module_name}_data: {class_name}Update
    ) -> {class_name}:
        """
        Update an existing {module_name}.
        
        Args:
            session: Database session
            {module_name}_id: UUID of the {module_name} to update
            {module_name}_data: Update data
            
        Returns:
            Updated {class_name} instance
            
        Raises:
            {class_name}NotFoundError: If {module_name} not found
        """
        # 1. Get existing record
        {module_name} = await {class_name}Service.get_{module_name}_by_id(
            session, {module_name}_id
        )
        
        logger.info(f"Updating {module_name}: {{{module_name}_id}}")
        
        # 2. Business validation
        if {module_name}_data.name:
            existing = await {module_name}_crud.get_by_name(session, {module_name}_data.name)
            if existing and existing.id != {module_name}_id:
                raise {class_name}AlreadyExistsError({module_name}_data.name)
        
        # 3. Update record
        updated_{module_name} = await {module_name}_crud.update(
            session,
            db_obj={module_name},
            obj_in={module_name}_data
        )
        
        # 4. Commit the transaction
        await session.commit()
        
        # 5. Refresh for fresh data
        await session.refresh(updated_{module_name})
        
        logger.info(f"{class_name} updated successfully: {{{module_name}_id}}")
        return updated_{module_name}
    
    @staticmethod
    async def delete_{module_name}(
        session: AsyncSession,
        {module_name}_id: UUID,
        soft_delete: bool = True
    ) -> None:
        """
        Delete a {module_name} (soft or hard delete).
        
        Args:
            session: Database session
            {module_name}_id: UUID of the {module_name} to delete
            soft_delete: If True, set is_active=False; if False, remove from DB
            
        Raises:
            {class_name}NotFoundError: If {module_name} not found
        """
        # 1. Verify record exists
        {module_name} = await {class_name}Service.get_{module_name}_by_id(
            session, {module_name}_id
        )
        
        logger.info(f"Deleting {module_name}: {{{module_name}_id}} (soft={{soft_delete}})")
        
        # 2. Delete or deactivate
        if soft_delete:
            await {module_name}_crud.deactivate(session, {module_name}_id)
        else:
            await {module_name}_crud.remove(session, id={module_name}_id)
        
        # 3. Commit the transaction
        await session.commit()
        
        logger.info(f"{class_name} deleted successfully: {{{module_name}_id}}")
    
    # ==================== COUNT/STATS OPERATIONS ====================
    
    @staticmethod
    async def get_{module_name}_count(
        session: AsyncSession,
        active_only: bool = True
    ) -> int:
        """
        Get total count of {module_name}s.
        
        Args:
            session: Database session
            active_only: If True, count only active records
            
        Returns:
            Count of records
        """
        if active_only:
            return await {module_name}_crud.count_active(session)
        return await {module_name}_crud.count(session)
'''


def generate_service_init(module_name: str, class_name: str) -> str:
    """
    Generate services/__init__.py file.
    
    Follows the pattern from app/service_provider/services/__init__.py
    """
    return f'''"""
{class_name} Services Package.

This module exports all services for the {module_name} module.

Services handle business logic and own transaction boundaries.
"""

from .{module_name}_service import {class_name}Service

__all__ = [
    "{class_name}Service",
]
'''
