"""
Referral schema templates.
"""


def generate_referral_schemas() -> str:
    """Generate referral/schemas/referral_schemas.py"""
    return '''"""
Pydantic schemas for referral system.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field

from app.referral.models import ReferralStatus


class ReferralBase(BaseModel):
    """Base schema for referral."""
    referral_code: str = Field(..., description="The referral code that was used")
    referred_user_type: str = Field(..., description="Type of the referred user")


class ReferralCreate(BaseModel):
    """Schema for creating a referral (internal use)."""
    referrer_id: str
    referred_user_id: str
    referral_code: str
    referred_user_type: str


class ReferralUpdate(BaseModel):
    """Schema for updating a referral."""
    status: Optional[ReferralStatus] = None
    completion_milestone: Optional[str] = None
    milestone_context: Optional[dict] = None
    completed_at: Optional[datetime] = None


class ReferralResponse(ReferralBase):
    """Schema for referral response."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    referrer_id: str
    referred_user_id: str
    status: ReferralStatus
    completion_milestone: Optional[str] = None
    milestone_context: Optional[dict] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class ReferralDetail(BaseModel):
    """Detailed referral information with user details."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str = Field(..., description="ID of the referred user")
    user_name: str = Field(..., description="Full name of the referred user")
    user_type: str = Field(..., description="Type of the referred user")
    phone_number: Optional[str] = Field(None, description="Phone of referred user")
    email: Optional[str] = Field(None, description="Email of referred user")
    status: ReferralStatus
    completion_milestone: Optional[str] = Field(None, description="Milestone that completed the referral")
    milestone_context: Optional[dict] = Field(None, description="Additional context")
    signed_up_at: datetime = Field(..., description="When the user signed up")
    completed_at: Optional[datetime] = Field(None, description="When completed")


class ReferralListResponse(BaseModel):
    """Response schema for list of referrals with pagination."""
    model_config = ConfigDict(from_attributes=True)

    referrals: List[ReferralDetail]
    total_count: int
    page: int
    limit: int


class ReferralStats(BaseModel):
    """Statistics about user's referrals."""
    model_config = ConfigDict(from_attributes=True)

    referral_code: str
    total_referrals: int
    pending_referrals: int
    completed_referrals: int
    milestones_breakdown: dict = Field(
        default_factory=dict,
        description="Breakdown by milestone type"
    )
    success_rate: float = Field(..., description="Percentage of completed referrals")


class ReferralCodeResponse(BaseModel):
    """Response for user's referral code."""
    model_config = ConfigDict(from_attributes=True)
    referral_code: str


class ReferralCodeValidation(BaseModel):
    """Response for referral code validation."""
    model_config = ConfigDict(from_attributes=True)

    valid: bool
    referrer_name: Optional[str] = None
    referrer_id: Optional[str] = None


class ReferralEventSchema(BaseModel):
    """Schema for referral event tracking."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    referral_id: str
    event_type: str
    event_data: Optional[dict] = None
    entity_type: Optional[str] = None
    entity_id: Optional[str] = None
    triggered_by_user_id: Optional[str] = None
    created_at: datetime


# ============================================================================
# ADMIN SCHEMAS
# ============================================================================


class AdminUserReferralInfo(BaseModel):
    """Detailed user info for admin referral tracking."""
    model_config = ConfigDict(from_attributes=True)

    user_id: str
    full_name: str
    phone_number: Optional[str] = None
    email: Optional[str] = None
    user_type: str
    status: str
    created_at: datetime
    referral_code: Optional[str] = Field(None, description="User's own referral code")


class AdminReferralDetail(BaseModel):
    """Comprehensive referral details for admin view."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    referrer: AdminUserReferralInfo = Field(..., description="User who referred")
    referred_user: AdminUserReferralInfo = Field(..., description="User who was referred")
    referral_code_used: str = Field(..., description="Referral code that was used")
    status: ReferralStatus
    completion_milestone: Optional[str] = None
    milestone_context: Optional[dict] = None
    created_at: datetime = Field(..., description="When referred user signed up")
    completed_at: Optional[datetime] = Field(None, description="When completed")
    time_to_completion: Optional[str] = Field(None, description="Human readable time")


class AdminReferralListResponse(BaseModel):
    """Admin response for paginated referral list."""
    model_config = ConfigDict(from_attributes=True)

    referrals: List[AdminReferralDetail]
    total_count: int
    page: int
    limit: int
    filters_applied: dict = Field(default_factory=dict, description="Active filters")


class AdminReferralSystemStats(BaseModel):
    """System-wide referral statistics for admin dashboard."""
    model_config = ConfigDict(from_attributes=True)

    total_referrals: int = Field(..., description="Total referrals in system")
    pending_referrals: int = Field(..., description="Referrals not yet completed")
    completed_referrals: int = Field(..., description="Successfully completed referrals")
    cancelled_referrals: int = Field(0, description="Cancelled referrals")
    overall_success_rate: float = Field(..., description="Completion rate percentage")

    referrals_by_user_type: dict = Field(default_factory=dict, description="Breakdown by user type")
    referrals_by_milestone: dict = Field(default_factory=dict, description="Breakdown by milestone")
    top_referrers: List[dict] = Field(default_factory=list, description="Top 10 referrers")

    avg_time_to_completion_hours: Optional[float] = Field(None, description="Average completion time")
    referrals_last_24h: int = Field(0, description="New referrals in last 24 hours")
    completions_last_24h: int = Field(0, description="Completions in last 24 hours")
'''


def generate_referral_schemas_init() -> str:
    """Generate referral/schemas/__init__.py"""
    return '''"""
Referral schemas package.
"""

from .referral_schemas import (
    ReferralBase,
    ReferralCreate,
    ReferralUpdate,
    ReferralResponse,
    ReferralDetail,
    ReferralListResponse,
    ReferralStats,
    ReferralCodeResponse,
    ReferralCodeValidation,
    ReferralEventSchema,
    AdminUserReferralInfo,
    AdminReferralDetail,
    AdminReferralListResponse,
    AdminReferralSystemStats,
)

__all__ = [
    "ReferralBase",
    "ReferralCreate",
    "ReferralUpdate",
    "ReferralResponse",
    "ReferralDetail",
    "ReferralListResponse",
    "ReferralStats",
    "ReferralCodeResponse",
    "ReferralCodeValidation",
    "ReferralEventSchema",
    "AdminUserReferralInfo",
    "AdminReferralDetail",
    "AdminReferralListResponse",
    "AdminReferralSystemStats",
]
'''
