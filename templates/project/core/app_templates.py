"""
Core App Templates.

Generates main FastAPI application and middleware.
"""


def generate_core_main(project_name: str, project_pascal: str) -> str:
    """Generate core/main.py - the main FastAPI application."""
    return f'''"""
FastAPI Application Entry Point.

This module initializes and configures the FastAPI application.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI

from .settings import settings
from .database import verify_db_connection, shutdown_db
from .exceptions import register_exception_handlers
from .middleware import setup_middleware
from .logging import setup_logging, get_logger
from ..apis.v1 import router as api_v1_router

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    setup_logging()
    logger.info(f"Starting {{settings.APP_NAME}} v{{settings.APP_VERSION}}")
    logger.info(f"Environment: {{settings.ENVIRONMENT}}")
    
    # Verify database connection
    await verify_db_connection()
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    await shutdown_db()
    logger.info("Application shutdown complete")


def create_application() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="{project_pascal} API",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )
    
    # Setup all middleware (CORS, GZip, TrustedHost, Request Timing)
    setup_middleware(app)
    
    # Register exception handlers
    register_exception_handlers(app)
    
    # Include API routers
    app.include_router(api_v1_router, prefix=settings.API_V1_PREFIX)
    
    # Health check endpoint
    @app.get("/health", tags=["Health"])
    async def health_check():
        """Health check endpoint."""
        return {{"status": "healthy", "service": settings.APP_NAME}}
    
    # Root endpoint
    @app.get("/", tags=["Root"])
    async def root():
        """Root endpoint with API information."""
        return {{
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
            "docs": "/docs",
        }}
    
    return app


# Create the application instance
app = create_application()
'''


def generate_core_middleware() -> str:
    """Generate core/middleware.py with common middleware."""
    return '''"""
Middleware configuration for the FastAPI application.

This module contains all middleware setup including CORS, compression,
security headers, and custom request processing middleware.
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from .settings import settings
from .logging import get_logger
import time

logger = get_logger(__name__)


def setup_middleware(app: FastAPI) -> None:
    """
    Configure all application middleware.

    Note: Middleware is executed in reverse order of addition.

    Args:
        app: FastAPI application instance
    """

    # 1. Trusted Host Middleware (Security) - Only in production
    if settings.is_production:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=settings.TRUSTED_HOSTS
        )
        logger.info(
            f"✓ Trusted Host Middleware enabled: {settings.TRUSTED_HOSTS}")

    # 2. CORS Middleware - Allow cross-origin requests
    cors_kwargs = {
        "allow_origins": settings.cors_origins_list,
        "allow_credentials": settings.CORS_ALLOW_CREDENTIALS,
        "allow_methods": settings.CORS_ALLOW_METHODS,
        "allow_headers": settings.CORS_ALLOW_HEADERS,
    }

    # Add regex pattern if configured
    if settings.CORS_ORIGIN_REGEX:
        cors_kwargs["allow_origin_regex"] = settings.CORS_ORIGIN_REGEX
        logger.info(f"✓ CORS Middleware enabled with regex: {settings.CORS_ORIGIN_REGEX}")

    app.add_middleware(CORSMiddleware, **cors_kwargs)
    logger.info(f"✓ CORS Middleware enabled: {settings.cors_origins_list}")

    # 3. GZip Middleware - Response compression
    if settings.ENABLE_GZIP:
        app.add_middleware(
            GZipMiddleware,
            minimum_size=settings.GZIP_MINIMUM_SIZE
        )
        logger.info(
            f"✓ GZip Middleware enabled (min size: {settings.GZIP_MINIMUM_SIZE} bytes)")

    # 4. Custom Request Timing Middleware
    @app.middleware("http")
    async def process_time_middleware(request: Request, call_next):
        """
        Add X-Process-Time header to track request processing time.
        Also logs slow requests for monitoring.
        """
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time

        # Add processing time to response headers
        response.headers["X-Process-Time"] = f"{process_time:.4f}"

        # Log slow requests (> 1 second)
        if process_time > 1.0:
            logger.warning(
                f"Slow request: {request.method} {request.url.path} "
                f"took {process_time:.4f}s"
            )

        return response

    logger.info("✓ All middleware configured successfully")
'''
