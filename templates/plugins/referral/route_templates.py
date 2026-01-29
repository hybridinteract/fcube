"""
Referral route templates.
"""


def generate_referral_routes() -> str:
    """Generate referral/routes/referral_routes.py"""
    return '''"""
Referral routes - Public user endpoints.

API endpoints for referral system.
"""

from typing import Optional
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.user.models import User
from app.user.auth_management.utils import get_current_user_validated
from app.referral.schemas import (
    ReferralCodeResponse,
    ReferralStats,
    ReferralListResponse,
    ReferralCodeValidation
)
from app.referral.services import ReferralService
from app.referral.dependencies import get_referral_service

router = APIRouter(prefix="/referrals", tags=["Referrals"])


@router.get(
    "/my-code",
    response_model=ReferralCodeResponse,
    summary="Get my referral code"
)
async def get_my_referral_code(
    current_user: User = Depends(get_current_user_validated),
    session: AsyncSession = Depends(get_session),
    service: ReferralService = Depends(get_referral_service)
):
    """
    Get the current user's referral code.

    If the user doesn't have a code yet, one will be automatically generated.
    """
    referral_code = await service.get_or_create_referral_code(session, current_user.id)
    return ReferralCodeResponse(referral_code=referral_code)


@router.get(
    "/stats",
    response_model=ReferralStats,
    summary="Get my referral statistics"
)
async def get_my_referral_stats(
    current_user: User = Depends(get_current_user_validated),
    session: AsyncSession = Depends(get_session),
    service: ReferralService = Depends(get_referral_service)
):
    """
    Get comprehensive referral statistics for the current user.

    Returns:
    - referral_code: User's referral code
    - total_referrals: Total number of users referred
    - pending_referrals: Referrals not yet completed
    - completed_referrals: Successfully completed referrals
    - milestones_breakdown: Breakdown by milestone type
    - success_rate: Percentage of completed referrals
    """
    stats = await service.get_user_referral_stats(session, current_user.id)
    return ReferralStats(**stats)


@router.get(
    "/my-referrals",
    response_model=ReferralListResponse,
    summary="Get list of my referrals"
)
async def get_my_referrals(
    status_filter: Optional[str] = Query(
        None,
        alias="status",
        description="Filter by status (pending, completed, cancelled)"
    ),
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    limit: int = Query(20, ge=1, le=100, description="Results per page"),
    current_user: User = Depends(get_current_user_validated),
    session: AsyncSession = Depends(get_session),
    service: ReferralService = Depends(get_referral_service)
):
    """
    Get a paginated list of users referred by the current user.

    Query Parameters:
    - status: Filter by referral status (pending, completed, cancelled)
    - page: Page number (default: 1)
    - limit: Results per page (default: 20, max: 100)
    """
    result = await service.get_user_referrals_list(
        session=session,
        user_id=current_user.id,
        status=status_filter,
        page=page,
        limit=limit
    )
    return ReferralListResponse(**result)


@router.get(
    "/validate/{code}",
    response_model=ReferralCodeValidation,
    summary="Validate a referral code",
    status_code=status.HTTP_200_OK
)
async def validate_referral_code(
    code: str,
    session: AsyncSession = Depends(get_session),
    service: ReferralService = Depends(get_referral_service)
):
    """
    Validate if a referral code exists and is valid.

    Use this from signup forms to validate referral codes in real-time.

    Path Parameters:
    - code: Referral code to validate

    Returns:
    - valid: Boolean indicating if code is valid
    - referrer_name: Full name of the referrer (if valid)
    - referrer_id: ID of the referrer (if valid)

    Authentication: Not required (public endpoint)
    """
    result = await service.validate_code(session, code)
    return ReferralCodeValidation(**result)
'''


def generate_referral_admin_routes() -> str:
    """Generate referral/routes/referral_admin_routes.py"""
    return '''"""
Referral admin routes.

Admin-only endpoints for managing referrals.
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.user.models import User
from app.user.auth_management.utils import get_current_user_validated
from app.user.permission_management.utils import require_permission
from app.referral.schemas import (
    AdminReferralListResponse,
    AdminReferralSystemStats,
)
from app.referral.crud import referral_crud
from app.referral.models import ReferralStatus

router = APIRouter(prefix="/admin/referrals", tags=["Admin - Referrals"])


@router.get(
    "/",
    response_model=AdminReferralListResponse,
    summary="List all referrals (Admin)"
)
async def list_all_referrals(
    status_filter: Optional[str] = Query(None, alias="status"),
    user_type: Optional[str] = Query(None, description="Filter by user type"),
    search: Optional[str] = Query(None, description="Search referral codes"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_permission("referral", "read"))
):
    """
    Get paginated list of all referrals with filtering.

    Requires: referral:read permission
    """
    # Convert status string to enum
    status_enum = None
    if status_filter:
        try:
            status_enum = ReferralStatus(status_filter)
        except ValueError:
            pass

    skip = (page - 1) * limit

    referrals, total_count = await referral_crud.get_all_referrals_paginated(
        session=session,
        skip=skip,
        limit=limit,
        status_filter=status_enum,
        user_type_filter=user_type,
        search_term=search
    )

    # TODO: Enrich with user data via integration service

    return AdminReferralListResponse(
        referrals=[],  # TODO: Map to AdminReferralDetail
        total_count=total_count,
        page=page,
        limit=limit,
        filters_applied={
            "status": status_filter,
            "user_type": user_type,
            "search": search
        }
    )


@router.get(
    "/stats",
    response_model=AdminReferralSystemStats,
    summary="Get system-wide referral statistics"
)
async def get_system_stats(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_permission("referral", "read"))
):
    """
    Get comprehensive system-wide referral statistics.

    Returns:
    - Total referrals, pending, completed, cancelled
    - Breakdown by user type and milestone
    - Top 10 referrers
    - Recent activity (last 24h)

    Requires: referral:read permission
    """
    stats = await referral_crud.get_system_stats_aggregated(session)

    total = stats["total_count"]
    status_counts = stats["status_counts"]
    pending = status_counts.get("pending", 0)
    completed = status_counts.get("completed", 0)
    cancelled = status_counts.get("cancelled", 0)
    success_rate = (completed / total * 100) if total > 0 else 0.0

    return AdminReferralSystemStats(
        total_referrals=total,
        pending_referrals=pending,
        completed_referrals=completed,
        cancelled_referrals=cancelled,
        overall_success_rate=round(success_rate, 2),
        referrals_by_user_type=stats["user_type_counts"],
        referrals_by_milestone=stats["milestone_counts"],
        top_referrers=stats["top_referrers"],
        avg_time_to_completion_hours=stats.get("avg_time_to_completion_hours"),
        referrals_last_24h=stats["referrals_last_24h"],
        completions_last_24h=stats["completions_last_24h"]
    )
'''


def generate_referral_routes_init() -> str:
    """Generate referral/routes/__init__.py"""
    return '''"""
Referral routes package.
"""

from .referral_routes import router as referral_router
from .referral_admin_routes import router as referral_admin_router

__all__ = [
    "referral_router",
    "referral_admin_router",
]
'''
