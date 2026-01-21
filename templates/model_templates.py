"""
Model template generators.

Generates SQLAlchemy ORM models following the project patterns.
"""


def generate_model(module_name: str, class_name: str) -> str:
    """
    Generate SQLAlchemy model file.
    
    Follows the pattern from app/service_provider/models/provider.py
    """
    # Simple pluralization
    table_name = module_name + 's'
    if module_name.endswith('y'):
        table_name = module_name[:-1] + 'ies'
    elif module_name.endswith(('s', 'x', 'z', 'ch', 'sh')):
        table_name = module_name + 'es'
    
    return f'''"""
{class_name} model for the {module_name} module.

This model represents the {module_name} entity in the database.
"""

from datetime import datetime, timezone
from uuid import uuid4
from typing import Optional

from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.core.models import Base


class {class_name}(Base):
    """
    {class_name} database model.
    
    Attributes:
        id: Primary key UUID
        name: Name of the {module_name}
        description: Optional description
        is_active: Soft delete flag
        created_at: Timestamp when record was created
        updated_at: Timestamp when record was last updated
    """
    
    __tablename__ = "{table_name}"
    
    # Primary Key
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True
    )
    
    # Core Fields
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )
    
    # Timestamps
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
    
    # Add relationships here as needed
    # Example:
    # user_id: Mapped[UUID] = mapped_column(
    #     UUID(as_uuid=True),
    #     ForeignKey("users.id"),
    #     nullable=False
    # )
    # user = relationship("User", back_populates="{table_name}")
    
    def __repr__(self) -> str:
        return f"<{class_name}(id={{self.id}}, name={{self.name}})>"
'''


def generate_model_init(module_name: str, class_name: str) -> str:
    """
    Generate models/__init__.py file.
    
    Follows the pattern from app/service_provider/models/__init__.py
    """
    return f'''"""
{class_name} Models Package.

This module exports all database models for the {module_name} module.
"""

from .{module_name} import {class_name}

# Add enums here if needed
# from .enums import {class_name}Status, {class_name}Type

__all__ = [
    "{class_name}",
    # Add enum exports here
]
'''
