"""
API templates for routing.
"""


def generate_apis_init() -> str:
    """Generate apis/__init__.py"""
    return '''"""
API Routes Package.

Contains versioned API routers.
"""
'''


def generate_apis_v1() -> str:
    """Generate apis/v1.py with version 1 router."""
    return '''"""
API Version 1 Router.

Aggregates all module routers for API v1.
"""

from fastapi import APIRouter

from app.user.routes import router as user_router

# Version 1 API Router
router = APIRouter(prefix="/v1")

# Include module routers
router.include_router(user_router)

# Add more module routers as you create them:
# from app.product.routes import product_router
# router.include_router(product_router)
'''
