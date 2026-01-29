"""
Referral model templates.
"""


def generate_referral_models() -> str:
    """Generate referral/models.py"""
    return '''"""
Referral system models for tracking user referrals and milestones.
"""

from datetime import datetime, timezone
from uuid import uuid4, UUID as UUIDType
from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, Text, Integer, Enum as SQLEnum, ForeignKey, Index, CheckConstraint, JSON
from sqlalchemy.dialects.postgresql import UUID
from enum import Enum

from app.core.database import Base


def utc_now():
    """Reusable function for UTC timestamp defaults."""
    return datetime.now(timezone.utc)


class ReferralStatus(str, Enum):
    """Status of the referral."""
    PENDING = "pending"      # Referred user signed up, no milestone reached yet
    COMPLETED = "completed"  # Success milestone reached
    CANCELLED = "cancelled"  # Optional: referral invalidated


class Referral(Base):
    """
    Core referral tracking - GENERIC for all user types.
    Tracks who referred whom and completion status.
    """
    __tablename__ = "referrals"
    __table_args__ = (
        Index('ix_referral_referrer_id', 'referrer_id'),
        Index('ix_referral_referred_user_id', 'referred_user_id'),
        Index('ix_referral_status', 'status'),
        Index('ix_referral_code', 'referral_code'),
        Index('ix_referral_created_at', 'created_at'),
        Index('ix_referral_user_type', 'referred_user_type'),
        CheckConstraint('referrer_id != referred_user_id', name='check_no_self_referral'),
    )

    id: Mapped[UUIDType] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )

    # Referral Participants
    referrer_id: Mapped[UUIDType] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        comment="User who shared the referral code"
    )
    referred_user_id: Mapped[UUIDType] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        comment="User who signed up using the code"
    )
    referral_code: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="The code that was used during signup"
    )

    # Status
    status: Mapped[ReferralStatus] = mapped_column(
        SQLEnum(ReferralStatus, values_callable=lambda x: [e.value for e in x]),
        default=ReferralStatus.PENDING,
        nullable=False
    )

    # Generic Completion Tracking
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="When referral became successful"
    )
    completion_milestone: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="Generic milestone identifier (e.g., 'first_booking', 'first_order')"
    )
    milestone_context: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
        comment="Additional milestone data (flexible schema)"
    )

    # Metadata
    referred_user_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="User type at time of signup (for analytics)"
    )
    extra_metadata: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
        comment="Extensible metadata field"
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
        comment="When referred user signed up"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False
    )

    # Relationships
    referrer: Mapped["User"] = relationship(
        "User",
        foreign_keys=[referrer_id],
        lazy="noload"
    )
    referred_user: Mapped["User"] = relationship(
        "User",
        foreign_keys=[referred_user_id],
        lazy="noload"
    )

    def __repr__(self) -> str:
        return f"<Referral(id={self.id}, status={self.status}, milestone={self.completion_milestone})>"


class ReferralEvent(Base):
    """
    Detailed event log for referral milestones.
    Tracks ALL significant events, not just completion.
    """
    __tablename__ = "referral_events"
    __table_args__ = (
        Index('ix_event_referral_id', 'referral_id'),
        Index('ix_event_type', 'event_type'),
        Index('ix_event_created_at', 'created_at'),
    )

    id: Mapped[UUIDType] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )

    referral_id: Mapped[UUIDType] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("referrals.id", ondelete="CASCADE"),
        nullable=False
    )

    event_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Type of event (e.g., 'order_completed', 'profile_verified')"
    )
    event_data: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
        comment="Contextual data about the event"
    )
    entity_type: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="What entity triggered this (e.g., 'order', 'booking')"
    )
    entity_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="ID of the triggering entity"
    )

    triggered_by_user_id: Mapped[Optional[UUIDType]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="Who caused this event"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False
    )

    referral: Mapped["Referral"] = relationship("Referral", lazy="noload")
    triggered_by_user: Mapped[Optional["User"]] = relationship("User", lazy="noload")

    def __repr__(self) -> str:
        return f"<ReferralEvent(id={self.id}, type={self.event_type}, entity={self.entity_type})>"


class ReferralSettings(Base):
    """
    Referral module configuration settings.
    Stores configurable parameters like promotion thresholds.
    """
    __tablename__ = "referral_settings"
    __table_args__ = (
        Index('ix_referral_settings_key', 'key'),
    )

    id: Mapped[UUIDType] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )

    key: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
        comment="Setting key identifier"
    )
    value: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Setting value (stored as integer)"
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Description of what this setting controls"
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
        comment="When this setting was last updated"
    )
    updated_by: Mapped[Optional[UUIDType]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="User who last updated this setting"
    )

    updated_by_user: Mapped[Optional["User"]] = relationship("User", lazy="noload")

    def __repr__(self) -> str:
        return f"<ReferralSettings(key={self.key}, value={self.value})>"
'''


def generate_referral_init() -> str:
    """Generate referral/__init__.py"""
    return '''"""
Referral module.

Handles user referral system with configurable completion strategies.
"""

from .models import Referral, ReferralEvent, ReferralStatus, ReferralSettings
from .schemas import *
from .exceptions import *

__all__ = [
    "Referral",
    "ReferralEvent",
    "ReferralStatus",
    "ReferralSettings",
]
'''
