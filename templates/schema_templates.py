"""
Schema template generators.

Generates Pydantic schemas following the project patterns.
"""


def generate_schemas(module_name: str, class_name: str) -> str:
    """
    Generate Pydantic schemas file.
    
    Follows the pattern from app/service_provider/schemas/provider_schemas.py
    """
    return f'''"""
{class_name} Pydantic schemas.

This module contains all Pydantic schemas for the {module_name} entity:
- {class_name}Base: Base schema with common fields
- {class_name}Create: Schema for creating new {module_name}s
- {class_name}CreateRequest: Client-facing create request
- {class_name}Update: Schema for updating existing {module_name}s
- {class_name}: Response schema for API responses
- {class_name}InDB: Database representation schema
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


# ==================== BASE SCHEMAS ====================

class {class_name}Base(BaseModel):
    """
    Base {class_name} schema with common fields.
    
    This schema contains fields that are shared across
    create, update, and response schemas.
    """
    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Name of the {module_name}"
    )
    description: Optional[str] = Field(
        None,
        max_length=2000,
        description="Optional description"
    )


# ==================== CREATE SCHEMAS ====================

class {class_name}CreateRequest({class_name}Base):
    """
    Schema for client-side create requests.
    
    This is what the API client sends. Does not include
    system-generated fields like user_id.
    """
    pass


class {class_name}Create({class_name}Base):
    """
    Internal schema for creating a new {module_name}.
    
    Includes system-generated fields that are set by the service layer.
    """
    # Add system-generated fields here if needed
    # user_id: UUID
    pass


# ==================== UPDATE SCHEMAS ====================

class {class_name}Update(BaseModel):
    """
    Schema for updating an existing {module_name}.
    
    All fields are optional to support partial updates.
    """
    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255,
        description="Name of the {module_name}"
    )
    description: Optional[str] = Field(
        None,
        max_length=2000,
        description="Optional description"
    )
    is_active: Optional[bool] = Field(
        None,
        description="Whether the {module_name} is active"
    )


# ==================== RESPONSE SCHEMAS ====================

class {class_name}({class_name}Base):
    """
    Full {class_name} response schema for API responses.
    
    Includes all fields that should be returned to the client.
    """
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    # Add nested relationship schemas here if needed
    # Example:
    # user: Optional["UserMinimal"] = None


class {class_name}Minimal(BaseModel):
    """
    Minimal {class_name} schema for nested responses.
    
    Use when including {module_name} data in other schemas
    to avoid circular dependencies and reduce payload size.
    """
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    name: str


class {class_name}InDB({class_name}):
    """
    Schema for {module_name} as stored in database.
    
    Extends the response schema with any database-only fields.
    """
    pass


# ==================== LIST RESPONSE SCHEMAS ====================

class {class_name}ListResponse(BaseModel):
    """
    Paginated list response for {module_name}s.
    """
    items: list[{class_name}]
    total: int
    skip: int
    limit: int
'''


def generate_schema_init(module_name: str, class_name: str) -> str:
    """
    Generate schemas/__init__.py file.
    
    Follows the pattern from app/service_provider/schemas/__init__.py
    """
    return f'''"""
{class_name} Schemas Package.

This module exports all Pydantic schemas for the {module_name} module.
"""

from .{module_name}_schemas import (
    {class_name}Base,
    {class_name}CreateRequest,
    {class_name}Create,
    {class_name}Update,
    {class_name},
    {class_name}Minimal,
    {class_name}InDB,
    {class_name}ListResponse,
)

__all__ = [
    "{class_name}Base",
    "{class_name}CreateRequest",
    "{class_name}Create",
    "{class_name}Update",
    "{class_name}",
    "{class_name}Minimal",
    "{class_name}InDB",
    "{class_name}ListResponse",
]
'''
