"""
Referral service templates.
"""


def generate_referral_service() -> str:
    """Generate referral/services/referral_service.py"""
    return '''"""
Referral service - Business logic for referral system.

Handles:
- Processing referral signups
- Generic event processing for milestone tracking
- Referral statistics and analytics
- Referral listing and details
"""

from typing import Optional, Dict, TYPE_CHECKING
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone

from app.core.logging import get_logger
from app.referral.models import Referral, ReferralStatus
from app.referral.crud import referral_crud, referral_event_crud
from app.referral.config import get_strategy_for_user_type
from app.referral.strategies import ReferralCompletionStrategy
from app.referral.exceptions import (
    InvalidReferralCodeError,
    SelfReferralError,
    DuplicateReferralError,
)

if TYPE_CHECKING:
    from app.user.services import UserReferralIntegration
    from app.user.models import UserType

logger = get_logger(__name__)


def utc_now():
    """Get current UTC timestamp."""
    return datetime.now(timezone.utc)


class ReferralService:
    """
    Service layer for referral business logic.

    All external dependencies are injected via constructor (Dependency Injection).
    """

    def __init__(
        self,
        user_integration: "UserReferralIntegration",
        strategies: Optional[Dict["UserType", ReferralCompletionStrategy]] = None
    ):
        """
        Initialize referral service with injected dependencies.

        Args:
            user_integration: User referral integration service (injected)
            strategies: Dictionary mapping user types to completion strategies
        """
        self.user_integration = user_integration
        self.strategies = strategies or {}
        logger.debug(f"ReferralService initialized with {len(self.strategies)} strategies")

    async def process_referral_signup(
        self,
        session: AsyncSession,
        user_id: UUID,
        referral_code: str
    ) -> Optional[Referral]:
        """
        Create referral record when user signs up with a code.

        Args:
            session: Database session
            user_id: UUID of the new user
            referral_code: Referral code used during signup

        Returns:
            Created Referral instance

        Raises:
            InvalidReferralCodeError: If code is invalid
            SelfReferralError: If user tries to refer themselves
            DuplicateReferralError: If referral already exists
        """
        logger.info(f"Processing referral signup for user {user_id} with code {referral_code}")

        # Validate referral code and get referrer
        referrer_data = await self.user_integration.validate_referral_code(session, referral_code)
        if not referrer_data:
            logger.warning(f"Invalid referral code: {referral_code}")
            raise InvalidReferralCodeError(referral_code)

        # Prevent self-referral
        if referrer_data["id"] == user_id:
            logger.warning(f"User {user_id} attempted self-referral")
            raise SelfReferralError()

        # Get referred user
        user_data = await self.user_integration.get_user_by_id(session, user_id)
        if not user_data:
            logger.error(f"User not found: {user_id}")
            raise ValueError(f"User not found: {user_id}")

        # Check if referral already exists
        existing = await referral_crud.get_by_referred_user_id(session, user_id)
        if existing:
            logger.info(f"Referral already exists for user {user_id}")
            raise DuplicateReferralError(str(user_id))

        # Create referral record
        referral = Referral(
            referrer_id=referrer_data["id"],
            referred_user_id=user_id,
            referral_code=referral_code,
            status=ReferralStatus.PENDING,
            referred_user_type=user_data["user_type"],
            created_at=utc_now()
        )

        session.add(referral)
        await session.flush()
        await session.refresh(referral)

        logger.info(
            f"Referral created: {referral.id} "
            f"(referrer: {referrer_data['id']}, referred: {user_id})"
        )

        return referral

    async def process_event(
        self,
        session: AsyncSession,
        event_type: str,
        user_id: UUID,
        event_data: dict
    ):
        """
        Generic event processor - handles any event type.
        Uses strategy pattern to determine completion.

        Args:
            session: Database session
            event_type: Type of event (e.g., "order_completed")
            user_id: UUID of the user who triggered the event
            event_data: Data about the event
        """
        logger.info(f"Processing event {event_type} for user {user_id}")

        # Get user and their referral
        referral = await referral_crud.get_by_referred_user_id(session, user_id)
        if not referral:
            logger.debug(f"No referral found for user {user_id}")
            return

        if referral.status == ReferralStatus.COMPLETED:
            logger.debug(f"Referral {referral.id} already completed")
            return

        # Log the event
        await self._log_event(
            session=session,
            referral_id=referral.id,
            event_type=event_type,
            event_data=event_data
        )

        # Get user to determine strategy
        user_data = await self.user_integration.get_user_by_id(session, user_id)
        if not user_data:
            logger.error(f"User not found: {user_id}")
            return

        # Find matching strategy
        user_type_str = user_data["user_type"]
        strategy = None
        for ut, strat in self.strategies.items():
            if ut.value == user_type_str:
                strategy = strat
                break

        if not strategy:
            logger.warning(f"No strategy found for user type {user_type_str}")
            return

        if not strategy.is_eligible_event(event_type):
            logger.debug(f"Event {event_type} not eligible for strategy")
            return

        # Check if this event completes the referral
        milestone_context = await strategy.check_completion(session, user_id, event_data)

        if milestone_context:
            await self._mark_completed(
                session=session,
                referral=referral,
                milestone=strategy.get_milestone_name(),
                context=milestone_context
            )

    async def _mark_completed(
        self,
        session: AsyncSession,
        referral: Referral,
        milestone: str,
        context: dict
    ):
        """Mark referral as completed with milestone data."""
        referral.status = ReferralStatus.COMPLETED
        referral.completed_at = utc_now()
        referral.completion_milestone = milestone
        referral.milestone_context = context

        await session.flush()
        await session.refresh(referral)

        logger.info(f"Referral {referral.id} marked as completed (milestone: {milestone})")

        # Trigger async promotion check
        self._trigger_promotion_check(referral.referrer_id)

    def _trigger_promotion_check(self, user_id: UUID):
        """Trigger async promotion check via Celery."""
        try:
            from app.referral.tasks import check_business_executive_promotion
            check_business_executive_promotion.delay(str(user_id))
            logger.debug(f"Triggered promotion check for user {user_id}")
        except Exception as e:
            logger.error(f"Failed to trigger promotion check: {e}")

    async def _log_event(
        self,
        session: AsyncSession,
        referral_id: UUID,
        event_type: str,
        event_data: dict
    ):
        """Log event for audit trail."""
        await referral_event_crud.create_event(
            session=session,
            referral_id=referral_id,
            event_type=event_type,
            event_data=event_data,
            entity_type=event_data.get("entity_type"),
            entity_id=event_data.get("entity_id"),
            triggered_by_user_id=event_data.get("triggered_by_user_id")
        )

    async def get_user_referral_stats(
        self,
        session: AsyncSession,
        user_id: UUID
    ) -> dict:
        """Get referral statistics for a user."""
        referral_code = await self.get_or_create_referral_code(session, user_id)

        aggregated_stats = await referral_crud.get_user_stats_aggregated(session, user_id)

        status_counts = aggregated_stats["status_counts"]
        total = aggregated_stats["total_count"]
        pending = status_counts.get("pending", 0)
        completed = status_counts.get("completed", 0)

        success_rate = (completed / total * 100) if total > 0 else 0.0

        return {
            "referral_code": referral_code,
            "total_referrals": total,
            "pending_referrals": pending,
            "completed_referrals": completed,
            "milestones_breakdown": aggregated_stats["milestone_counts"],
            "success_rate": round(success_rate, 2)
        }

    async def get_user_referrals_list(
        self,
        session: AsyncSession,
        user_id: UUID,
        status: Optional[str] = None,
        page: int = 1,
        limit: int = 20
    ) -> dict:
        """Get list of referrals with filtering and pagination."""
        status_enum = None
        if status:
            try:
                status_enum = ReferralStatus(status)
            except ValueError:
                logger.warning(f"Invalid status filter: {status}")

        skip = (page - 1) * limit

        referrals = await referral_crud.get_by_referrer(
            session=session,
            referrer_id=user_id,
            status=status_enum,
            skip=skip,
            limit=limit
        )

        total_count = await referral_crud.count_by_referrer(
            session=session,
            referrer_id=user_id,
            status=status_enum
        )

        # Batch load referred user data
        referred_user_ids = [r.referred_user_id for r in referrals]
        users_dict = await self.user_integration.get_users_by_ids(session, referred_user_ids)

        results = []
        for referral in referrals:
            user_data = users_dict.get(referral.referred_user_id)
            if user_data:
                results.append({
                    "id": str(referral.id),
                    "user_id": str(user_data["id"]),
                    "user_name": user_data["full_name"],
                    "user_type": referral.referred_user_type,
                    "phone_number": user_data.get("phone_number"),
                    "email": user_data.get("email"),
                    "status": referral.status.value,
                    "completion_milestone": referral.completion_milestone,
                    "milestone_context": referral.milestone_context,
                    "signed_up_at": referral.created_at,
                    "completed_at": referral.completed_at
                })

        return {
            "referrals": results,
            "total_count": total_count,
            "page": page,
            "limit": limit
        }

    async def validate_code(
        self,
        session: AsyncSession,
        code: str
    ) -> dict:
        """Validate a referral code."""
        referrer_data = await self.user_integration.validate_referral_code(session, code)

        if referrer_data:
            return {
                "valid": True,
                "referrer_name": referrer_data["full_name"],
                "referrer_id": str(referrer_data["id"])
            }
        else:
            return {
                "valid": False,
                "referrer_name": None,
                "referrer_id": None
            }

    async def get_or_create_referral_code(
        self,
        session: AsyncSession,
        user_id: UUID
    ) -> str:
        """Get user's referral code, generating one if it doesn't exist."""
        referral_code = await self.user_integration.get_user_referral_code(session, user_id)

        if referral_code:
            return referral_code

        # Generate new code
        logger.info(f"User {user_id} missing referral code - auto-generating")

        try:
            referral_code = await self.user_integration.generate_unique_referral_code(session)

            success = await self.user_integration.update_user_referral_code(
                session, user_id, referral_code
            )

            if not success:
                raise ValueError(f"Failed to update user {user_id} with referral code")

            await session.commit()
            logger.info(f"Generated referral code {referral_code} for user {user_id}")
            return referral_code

        except Exception as e:
            await session.rollback()
            logger.error(f"Failed to generate referral code for user {user_id}: {e}")
            raise
'''


def generate_referral_service_init() -> str:
    """Generate referral/services/__init__.py"""
    return '''"""
Referral services package.
"""

from .referral_service import ReferralService

__all__ = [
    "ReferralService",
]
'''
