"""
User Route Templates.

Generates base route aggregator for User module.
"""


def generate_user_routes() -> str:
    """Generate user/routes.py."""
    return '''"""
User module routes aggregator.
"""

from fastapi import APIRouter

from .auth_management.routes import router as auth_router

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Include authentication routes
router.include_router(auth_router)
'''
