"""
Referral dependency injection templates.
"""


def generate_referral_dependencies() -> str:
    """Generate referral/dependencies.py"""
    return '''"""
Referral module dependency injection.

This file wires up all service dependencies for the referral module.
Uses FastAPI's Depends() for proper dependency injection.
"""

from typing import TYPE_CHECKING
from app.referral.services import ReferralService
from app.referral.config import get_referral_strategies

if TYPE_CHECKING:
    from fastapi import Request


# Singleton instance - created once on module load
_referral_service: ReferralService | None = None


def _create_referral_service() -> ReferralService:
    """
    Create and configure the ReferralService with all dependencies.
    
    This is where you wire up:
    1. UserReferralIntegration service
    2. Completion strategies for each user type
    """
    # Import integration services here to avoid circular imports
    from app.user.services import user_referral_integration
    
    # TODO: Add your module integration services
    # from app.customer.services import customer_referral_integration
    # from app.provider.services import provider_referral_integration
    
    # Build strategies dictionary
    strategies = get_referral_strategies(
        # customer_integration=customer_referral_integration,
        # provider_integration=provider_referral_integration,
    )
    
    return ReferralService(
        user_integration=user_referral_integration,
        strategies=strategies
    )


def get_referral_service() -> ReferralService:
    """
    Get or create the ReferralService singleton.
    
    Use with FastAPI Depends():
        @router.get("/referrals")
        async def get_referrals(service: ReferralService = Depends(get_referral_service)):
            ...
    """
    global _referral_service
    if _referral_service is None:
        _referral_service = _create_referral_service()
    return _referral_service


# For testing - allows resetting the singleton
def reset_referral_service() -> None:
    """Reset the service singleton (useful for testing)."""
    global _referral_service
    _referral_service = None
'''
