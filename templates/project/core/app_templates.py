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
from fastapi.middleware.cors import CORSMiddleware

from .settings import settings
from .database import verify_db_connection, shutdown_db
from .exceptions import register_exception_handlers
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
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
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
Custom middleware for the application.

Provides request/response processing, timing, and logging.
"""

import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from .logging import get_logger

logger = get_logger(__name__)


class RequestTimingMiddleware(BaseHTTPMiddleware):
    """Middleware to log request timing."""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        response = await call_next(request)
        
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        
        # Log slow requests
        if process_time > 1.0:
            logger.warning(
                f"Slow request: {request.method} {request.url.path} "
                f"took {process_time:.2f}s"
            )
        
        return response
'''
