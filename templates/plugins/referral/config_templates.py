"""
Referral config and strategy templates.
"""


def generate_referral_config() -> str:
    """Generate referral/config.py"""
    return '''"""
Referral completion strategy configuration.

Central registry for mapping user types to their completion strategies.
To add a new user type:
1. Create integration service in the relevant module
2. Create a strategy class in strategies.py
3. Add it to get_referral_strategies() function below
"""

from typing import Dict, TYPE_CHECKING
from app.user.models import UserType
from app.referral.strategies import (
    ReferralCompletionStrategy,
    # Add your strategies here:
    # CustomerFirstOrderStrategy,
    # ProviderFirstServiceStrategy,
)

if TYPE_CHECKING:
    pass  # Add integration service type hints here


def get_referral_strategies(
    # Add integration service parameters here
    # customer_integration: "CustomerReferralIntegration",
) -> Dict[UserType, ReferralCompletionStrategy]:
    """
    Get referral strategies with integration services injected.

    Returns:
        Dictionary mapping user types to their strategies
    """
    return {
        # UserType.CUSTOMER: CustomerFirstOrderStrategy(customer_integration),
        # UserType.SERVICE_PROVIDER: ProviderFirstServiceStrategy(provider_integration),
    }


def get_strategy_for_user_type(
    user_type: UserType,
    strategies: Dict[UserType, ReferralCompletionStrategy]
) -> ReferralCompletionStrategy | None:
    """
    Get the completion strategy for a user type.

    Args:
        user_type: UserType enum value
        strategies: Dictionary of strategies

    Returns:
        ReferralCompletionStrategy instance or None if not configured
    """
    return strategies.get(user_type)
'''


def generate_referral_strategies() -> str:
    """Generate referral/strategies.py"""
    return '''"""
Referral completion strategies using the Strategy Pattern.

Each user type has a specific strategy that defines:
- What milestone completes a referral
- How to check if the milestone is reached
- What event types trigger the check

Strategies receive integration service dependencies to maintain loose coupling.
"""

from abc import ABC, abstractmethod
from typing import Optional, TYPE_CHECKING
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger

if TYPE_CHECKING:
    pass  # Add integration service type hints here

logger = get_logger(__name__)


class ReferralCompletionStrategy(ABC):
    """Base class for referral completion strategies."""

    @abstractmethod
    def get_milestone_name(self) -> str:
        """Return the milestone identifier for this strategy."""
        pass

    @abstractmethod
    async def check_completion(
        self,
        session: AsyncSession,
        user_id: UUID,
        event_data: dict
    ) -> Optional[dict]:
        """
        Check if referral should be marked complete.

        Args:
            session: Database session
            user_id: UUID of the user who triggered the event
            event_data: Data about the event

        Returns:
            dict with milestone context if complete, None otherwise
        """
        pass

    @abstractmethod
    def is_eligible_event(self, event_type: str) -> bool:
        """Check if this event type is relevant for this strategy."""
        pass


# ============================================================================
# EXAMPLE STRATEGIES - Customize for your project
# ============================================================================


class CustomerFirstOrderStrategy(ReferralCompletionStrategy):
    """
    Customer completes referral when their first order is completed.
    
    To use:
    1. Create CustomerReferralIntegration service
    2. Add UserType.CUSTOMER to config.py
    """

    def __init__(self, customer_integration=None):
        self.customer_integration = customer_integration

    def get_milestone_name(self) -> str:
        return "first_order_completed"

    def is_eligible_event(self, event_type: str) -> bool:
        return event_type == "order_completed"

    async def check_completion(
        self,
        session: AsyncSession,
        user_id: UUID,
        event_data: dict
    ) -> Optional[dict]:
        """Check if this is the user's first completed order."""
        order_id = event_data.get("order_id")

        logger.info(f"Checking first order completion for user {user_id}")

        try:
            if not self.customer_integration:
                logger.error("CustomerReferralIntegration not injected!")
                return None

            # Use integration service to get order count
            count = await self.customer_integration.get_completed_order_count(
                session, user_id
            )

            if count >= 1:
                logger.info(f"First order milestone reached for user {user_id}")
                return {
                    "order_id": str(order_id) if order_id else None,
                    "order_total": event_data.get("total_amount"),
                    "total_orders": count
                }

            return None

        except Exception as e:
            logger.error(f"Error checking first order for user {user_id}: {e}")
            return None


class ProviderFirstServiceStrategy(ReferralCompletionStrategy):
    """
    Provider completes referral when they complete their first service.
    
    To use:
    1. Create ProviderReferralIntegration service
    2. Add UserType.SERVICE_PROVIDER to config.py
    """

    def __init__(self, provider_integration=None):
        self.provider_integration = provider_integration

    def get_milestone_name(self) -> str:
        return "first_service_completed"

    def is_eligible_event(self, event_type: str) -> bool:
        return event_type == "service_completed"

    async def check_completion(
        self,
        session: AsyncSession,
        user_id: UUID,
        event_data: dict
    ) -> Optional[dict]:
        """Check if this is the provider's first completed service."""
        service_id = event_data.get("service_id")

        logger.info(f"Checking first service completion for provider {user_id}")

        try:
            if not self.provider_integration:
                logger.error("ProviderReferralIntegration not injected!")
                return None

            count = await self.provider_integration.get_completed_service_count(
                session, user_id
            )

            if count >= 1:
                logger.info(f"First service milestone reached for provider {user_id}")
                return {
                    "service_id": str(service_id) if service_id else None,
                    "earnings": event_data.get("earnings"),
                    "total_services": count
                }

            return None

        except Exception as e:
            logger.error(f"Error checking first service for provider {user_id}: {e}")
            return None


# Add more strategies as needed:
# class SubscriptionFirstMonthStrategy(ReferralCompletionStrategy):
#     """User completes referral after first subscription month."""
#     pass
'''
