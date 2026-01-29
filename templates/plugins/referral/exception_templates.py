"""
Referral exception templates.
"""


def generate_referral_exceptions() -> str:
    """Generate referral/exceptions.py"""
    return '''"""
Custom exceptions for the referral module.
"""

from fastapi import HTTPException, status


class ReferralException(HTTPException):
    """Base exception for all referral-related errors."""

    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(status_code=status_code, detail=detail)


class ReferralNotFoundError(ReferralException):
    """Raised when a referral is not found."""

    def __init__(self, identifier: str):
        self.identifier = identifier
        super().__init__(
            detail=f"Referral with identifier '{identifier}' not found",
            status_code=status.HTTP_404_NOT_FOUND
        )


class InvalidReferralCodeError(ReferralException):
    """Raised when referral code is invalid."""

    def __init__(self, code: str):
        super().__init__(
            detail=f"Invalid or non-existent referral code: '{code}'",
            status_code=status.HTTP_400_BAD_REQUEST
        )


class SelfReferralError(ReferralException):
    """Raised when user tries to refer themselves."""

    def __init__(self):
        super().__init__(
            detail="Users cannot refer themselves",
            status_code=status.HTTP_400_BAD_REQUEST
        )


class DuplicateReferralError(ReferralException):
    """Raised when user already has a referral record."""

    def __init__(self, user_id: str):
        super().__init__(
            detail=f"User '{user_id}' already has a referral record",
            status_code=status.HTTP_409_CONFLICT
        )


class ReferralAlreadyCompletedError(ReferralException):
    """Raised when trying to update a completed referral."""

    def __init__(self, referral_id: str):
        super().__init__(
            detail=f"Referral '{referral_id}' is already completed",
            status_code=status.HTTP_400_BAD_REQUEST
        )


class ReferralCodeGenerationError(ReferralException):
    """Raised when unable to generate unique referral code."""

    def __init__(self):
        super().__init__(
            detail="Unable to generate unique referral code. Please try again.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
'''
