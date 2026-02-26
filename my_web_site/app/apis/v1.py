"""
API Version 1 Router.

Aggregates all module routers for API v1.
"""

from fastapi import APIRouter

# Version 1 API Router
router = APIRouter(prefix="/v1")

# Add module routers as you create them:
# from app.product.routes import router as product_router
# router.include_router(product_router)

# To add user authentication, run:
# fcube adduser --auth-type email
