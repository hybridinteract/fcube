"""
Referral CRUD templates.
"""


def generate_referral_crud() -> str:
    """Generate referral/crud/referral_crud.py"""
    return '''"""
Referral CRUD operations.

Handles all database operations for referrals including:
- Basic CRUD operations (get, create, update, delete)
- Filtering by referrer, status, user type
- Advanced queries with pagination
- Aggregated statistics
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import datetime, timezone, timedelta

from app.core.crud import CRUDBase
from app.core.logging import get_logger
from app.referral.models import Referral, ReferralStatus, ReferralEvent, ReferralSettings
from app.referral.schemas import ReferralCreate, ReferralUpdate

logger = get_logger(__name__)


class ReferralCRUD(CRUDBase[Referral, ReferralCreate, ReferralUpdate]):
    """CRUD operations for Referral model with advanced queries."""

    def __init__(self):
        super().__init__(Referral)

    async def get_by_referred_user_id(
        self,
        session: AsyncSession,
        user_id: UUID
    ) -> Optional[Referral]:
        """Get referral record for a referred user."""
        result = await session.execute(
            select(self.model).where(self.model.referred_user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_by_referrer(
        self,
        session: AsyncSession,
        referrer_id: UUID,
        status: Optional[ReferralStatus] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Referral]:
        """Get all referrals by a specific referrer."""
        query = select(self.model).where(self.model.referrer_id == referrer_id)

        if status:
            query = query.where(self.model.status == status)

        query = query.order_by(self.model.created_at.desc()).offset(skip).limit(limit)
        result = await session.execute(query)
        return list(result.scalars().all())

    async def count_by_referrer(
        self,
        session: AsyncSession,
        referrer_id: UUID,
        status: Optional[ReferralStatus] = None
    ) -> int:
        """Count referrals by a specific referrer."""
        query = select(func.count()).select_from(self.model).where(
            self.model.referrer_id == referrer_id
        )

        if status:
            query = query.where(self.model.status == status)

        result = await session.execute(query)
        return result.scalar_one()

    async def update_status(
        self,
        session: AsyncSession,
        referral_id: UUID,
        status: ReferralStatus,
        milestone: Optional[str] = None,
        context: Optional[dict] = None,
        completed_at: Optional[datetime] = None
    ) -> Optional[Referral]:
        """Update referral status and completion details."""
        referral = await self.get(session, referral_id)
        if not referral:
            return None

        referral.status = status
        if milestone:
            referral.completion_milestone = milestone
        if context:
            referral.milestone_context = context
        if completed_at:
            referral.completed_at = completed_at

        await session.flush()
        await session.refresh(referral)
        return referral

    async def get_all_referrals_paginated(
        self,
        session: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        status_filter: Optional[ReferralStatus] = None,
        user_type_filter: Optional[str] = None,
        search_term: Optional[str] = None,
        referrer_id: Optional[UUID] = None
    ) -> tuple[List[Referral], int]:
        """Get all referrals with advanced filtering (admin only)."""
        query = select(self.model)
        count_query = select(func.count()).select_from(self.model)

        filters = []
        if status_filter:
            filters.append(self.model.status == status_filter)
        if user_type_filter:
            filters.append(self.model.referred_user_type == user_type_filter)
        if search_term:
            filters.append(self.model.referral_code.ilike(f"%{search_term}%"))
        if referrer_id:
            filters.append(self.model.referrer_id == referrer_id)

        if filters:
            query = query.where(and_(*filters))
            count_query = count_query.where(and_(*filters))

        count_result = await session.execute(count_query)
        total_count = count_result.scalar_one()

        query = query.order_by(self.model.created_at.desc()).offset(skip).limit(limit)
        result = await session.execute(query)
        referrals = list(result.scalars().all())

        return referrals, total_count

    async def get_user_stats_aggregated(
        self,
        session: AsyncSession,
        user_id: UUID
    ) -> Dict[str, Any]:
        """Get referral statistics for a specific user using database aggregation."""
        # Get counts by status
        status_counts_query = select(
            self.model.status,
            func.count(self.model.id).label('count')
        ).where(
            self.model.referrer_id == user_id
        ).group_by(self.model.status)

        status_result = await session.execute(status_counts_query)
        status_counts = {str(row.status.value): row.count for row in status_result}

        # Get counts by milestone
        milestone_counts_query = select(
            self.model.completion_milestone,
            func.count(self.model.id).label('count')
        ).where(
            and_(
                self.model.referrer_id == user_id,
                self.model.status == ReferralStatus.COMPLETED,
                self.model.completion_milestone.isnot(None)
            )
        ).group_by(self.model.completion_milestone)

        milestone_result = await session.execute(milestone_counts_query)
        milestone_counts = {row.completion_milestone: row.count for row in milestone_result}

        # Get total count
        total_count_query = select(func.count(self.model.id)).where(
            self.model.referrer_id == user_id
        )
        total_result = await session.execute(total_count_query)
        total_count = total_result.scalar_one()

        return {
            "total_count": total_count,
            "status_counts": status_counts,
            "milestone_counts": milestone_counts
        }

    async def get_system_stats_aggregated(
        self,
        session: AsyncSession
    ) -> Dict[str, Any]:
        """Get system-wide referral statistics using database aggregation."""
        # Status counts
        status_counts_query = select(
            self.model.status,
            func.count(self.model.id).label('count')
        ).group_by(self.model.status)
        status_result = await session.execute(status_counts_query)
        status_counts = {str(row.status.value): row.count for row in status_result}

        # User type counts
        user_type_counts_query = select(
            self.model.referred_user_type,
            func.count(self.model.id).label('count')
        ).group_by(self.model.referred_user_type)
        user_type_result = await session.execute(user_type_counts_query)
        user_type_counts = {row.referred_user_type: row.count for row in user_type_result}

        # Milestone counts
        milestone_counts_query = select(
            self.model.completion_milestone,
            func.count(self.model.id).label('count')
        ).where(
            and_(
                self.model.status == ReferralStatus.COMPLETED,
                self.model.completion_milestone.isnot(None)
            )
        ).group_by(self.model.completion_milestone)
        milestone_result = await session.execute(milestone_counts_query)
        milestone_counts = {row.completion_milestone: row.count for row in milestone_result}

        # Top referrers
        top_referrers_query = select(
            self.model.referrer_id,
            func.count(self.model.id).label('count')
        ).where(
            self.model.status == ReferralStatus.COMPLETED
        ).group_by(
            self.model.referrer_id
        ).order_by(
            func.count(self.model.id).desc()
        ).limit(10)
        top_referrers_result = await session.execute(top_referrers_query)
        top_referrers = [
            {"user_id": str(row.referrer_id), "successful_referrals": row.count}
            for row in top_referrers_result
        ]

        # Recent activity
        now = datetime.now(timezone.utc)
        yesterday = now - timedelta(hours=24)

        referrals_last_24h_query = select(func.count(self.model.id)).where(
            self.model.created_at >= yesterday
        )
        referrals_last_24h_result = await session.execute(referrals_last_24h_query)
        referrals_last_24h = referrals_last_24h_result.scalar_one()

        completions_last_24h_query = select(func.count(self.model.id)).where(
            and_(
                self.model.completed_at >= yesterday,
                self.model.completed_at.isnot(None)
            )
        )
        completions_last_24h_result = await session.execute(completions_last_24h_query)
        completions_last_24h = completions_last_24h_result.scalar_one()

        total_count_query = select(func.count(self.model.id))
        total_result = await session.execute(total_count_query)
        total_count = total_result.scalar_one()

        return {
            "total_count": total_count,
            "status_counts": status_counts,
            "user_type_counts": user_type_counts,
            "milestone_counts": milestone_counts,
            "top_referrers": top_referrers,
            "referrals_last_24h": referrals_last_24h,
            "completions_last_24h": completions_last_24h
        }


class ReferralEventCRUD(CRUDBase[ReferralEvent, Dict, Dict]):
    """CRUD operations for ReferralEvent model."""

    def __init__(self):
        super().__init__(ReferralEvent)

    async def get_by_referral(
        self,
        session: AsyncSession,
        referral_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[ReferralEvent]:
        """Get all events for a specific referral."""
        query = select(self.model).where(
            self.model.referral_id == referral_id
        ).order_by(self.model.created_at.desc()).offset(skip).limit(limit)

        result = await session.execute(query)
        return list(result.scalars().all())

    async def create_event(
        self,
        session: AsyncSession,
        referral_id: UUID,
        event_type: str,
        event_data: Optional[dict] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        triggered_by_user_id: Optional[UUID] = None
    ) -> ReferralEvent:
        """Create a new referral event."""
        event = ReferralEvent(
            referral_id=referral_id,
            event_type=event_type,
            event_data=event_data or {},
            entity_type=entity_type,
            entity_id=entity_id,
            triggered_by_user_id=triggered_by_user_id
        )

        session.add(event)
        await session.flush()
        await session.refresh(event)
        return event


class ReferralSettingsCRUD(CRUDBase[ReferralSettings, Dict, Dict]):
    """CRUD operations for ReferralSettings model."""

    def __init__(self):
        super().__init__(ReferralSettings)

    async def get_by_key(
        self,
        session: AsyncSession,
        key: str
    ) -> Optional[ReferralSettings]:
        """Get setting by key."""
        result = await session.execute(
            select(self.model).where(self.model.key == key)
        )
        return result.scalar_one_or_none()

    async def upsert(
        self,
        session: AsyncSession,
        key: str,
        value: int,
        description: Optional[str] = None,
        updated_by: Optional[UUID] = None
    ) -> ReferralSettings:
        """Insert or update a setting."""
        setting = await self.get_by_key(session, key)

        if setting:
            setting.value = value
            if description:
                setting.description = description
            setting.updated_by = updated_by
        else:
            setting = ReferralSettings(
                key=key,
                value=value,
                description=description,
                updated_by=updated_by
            )
            session.add(setting)

        await session.flush()
        await session.refresh(setting)
        return setting


# Singleton instances
referral_crud = ReferralCRUD()
referral_event_crud = ReferralEventCRUD()
referral_settings_crud = ReferralSettingsCRUD()
'''


def generate_referral_crud_init() -> str:
    """Generate referral/crud/__init__.py"""
    return '''"""
Referral CRUD package.
"""

from .referral_crud import (
    referral_crud,
    referral_event_crud,
    referral_settings_crud,
    ReferralCRUD,
    ReferralEventCRUD,
    ReferralSettingsCRUD,
)

__all__ = [
    "referral_crud",
    "referral_event_crud",
    "referral_settings_crud",
    "ReferralCRUD",
    "ReferralEventCRUD",
    "ReferralSettingsCRUD",
]
'''
