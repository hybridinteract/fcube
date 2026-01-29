"""
Referral Celery task templates.
"""


def generate_referral_tasks() -> str:
    """Generate referral/tasks.py"""
    return '''"""
Referral background tasks (Celery).

Async tasks for processing referral events and promotions.
"""

from app.core.celery_app import celery_app
from app.core.logging import get_logger

logger = get_logger(__name__)


@celery_app.task(
    name="check_business_executive_promotion",
    bind=True,
    max_retries=3,
    default_retry_delay=60
)
def check_business_executive_promotion(self, user_id: str):
    """
    Check if user should be promoted to business_executive role.
    
    This task is triggered after a referral is completed.
    It checks if the referrer has reached the promotion threshold.
    
    Args:
        user_id: UUID string of the user to check
    """
    import asyncio
    from app.core.database import async_session_factory
    
    async def _check_promotion():
        async with async_session_factory() as session:
            try:
                from app.referral.services import ReferralService
                from app.referral.dependencies import get_referral_service
                from uuid import UUID
                
                service = get_referral_service()
                
                # Get user's referral stats
                stats = await service.get_user_referral_stats(session, UUID(user_id))
                completed = stats.get("completed_referrals", 0)
                
                # Get promotion threshold from settings
                from app.referral.crud import referral_settings_crud
                threshold_setting = await referral_settings_crud.get_by_key(
                    session, "business_executive_threshold"
                )
                threshold = threshold_setting.value if threshold_setting else 10
                
                logger.info(
                    f"User {user_id} has {completed} completed referrals "
                    f"(threshold: {threshold})"
                )
                
                if completed >= threshold:
                    # TODO: Implement role assignment
                    # call user integration to add business_executive role
                    logger.info(
                        f"User {user_id} eligible for business_executive promotion!"
                    )
                
            except Exception as e:
                logger.error(f"Error checking promotion for {user_id}: {e}")
                raise
    
    try:
        asyncio.run(_check_promotion())
    except Exception as exc:
        logger.error(f"Task failed for user {user_id}: {exc}")
        raise self.retry(exc=exc)


@celery_app.task(name="process_referral_event")
def process_referral_event(
    event_type: str,
    user_id: str,
    event_data: dict
):
    """
    Process a referral event asynchronously.
    
    Use this when you want to process referral events without
    blocking the main request.
    
    Args:
        event_type: Type of event (e.g., "order_completed")
        user_id: UUID string of the user
        event_data: Additional event context
    """
    import asyncio
    from app.core.database import async_session_factory
    from uuid import UUID
    
    async def _process_event():
        async with async_session_factory() as session:
            try:
                from app.referral.dependencies import get_referral_service
                
                service = get_referral_service()
                await service.process_event(
                    session=session,
                    event_type=event_type,
                    user_id=UUID(user_id),
                    event_data=event_data
                )
                await session.commit()
                
                logger.info(
                    f"Processed referral event {event_type} for user {user_id}"
                )
                
            except Exception as e:
                await session.rollback()
                logger.error(f"Error processing event for {user_id}: {e}")
                raise
    
    asyncio.run(_process_event())
'''
