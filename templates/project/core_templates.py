"""
Core module template generators.

Generates the app/core module with database, settings, logging, etc.
"""


def generate_core_init(project_name: str, project_pascal: str) -> str:
    """Generate core/__init__.py"""
    return '''"""
Core module - Shared infrastructure for the application.

This module provides:
- Database configuration and session management
- Application settings
- Logging utilities
- Base CRUD operations
- Common exceptions
- Middleware
"""
'''


def generate_core_models() -> str:
    """Generate core/models.py with Base declarative class."""
    return '''"""
SQLAlchemy Base Model.

This module provides the declarative base for all SQLAlchemy models.
All models should inherit from this Base class.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy models.
    
    All models should inherit from this class:
        from app.core.models import Base
        
        class User(Base):
            __tablename__ = "users"
            ...
    """
    pass
'''


def generate_core_database() -> str:
    """Generate core/database.py with async database setup."""
    return '''"""
Database configuration and session management.

Provides:
- Async SQLAlchemy engine configuration
- Session factory and dependency
- Database connection verification
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from typing import AsyncGenerator
import asyncio
from fastapi import HTTPException

from .models import Base
from .settings import settings
from .logging import get_logger

logger = get_logger(__name__)


def get_database_url() -> str:
    """
    Build DATABASE_URL from settings.
    
    Returns:
        str: PostgreSQL connection URL with asyncpg driver
    """
    return settings.database_url


DATABASE_URL = get_database_url()

# Create async engine with connection pooling
engine: AsyncEngine = create_async_engine(
    DATABASE_URL,
    echo=settings.DB_ECHO,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_timeout=settings.DB_POOL_TIMEOUT,
    pool_pre_ping=True,
)

# Create async session factory
async_session_factory = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to provide an async database session.
    
    Usage:
        @router.post("/user")
        async def create_user(session: AsyncSession = Depends(get_session)):
            user = await user_crud.create(session, data)
            await session.commit()
            return user
    """
    async with async_session_factory() as session:
        try:
            yield session
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Database session error: {e}")
            await session.rollback()
            raise


async def verify_db_connection(max_retries: int = 5, retry_delay: float = 2.0) -> None:
    """Verify database connectivity at startup with retry logic."""
    last_exception = None

    for attempt in range(1, max_retries + 1):
        try:
            async with engine.begin() as conn:
                result = await conn.execute(text("SELECT version()"))
                version = result.scalar()
                logger.info(f"Database connected. PostgreSQL: {version}")
                return
        except Exception as e:
            last_exception = e
            if attempt < max_retries:
                logger.warning(f"DB connection attempt {attempt}/{max_retries} failed. Retrying...")
                await asyncio.sleep(retry_delay)
            else:
                logger.error(f"Failed to connect to database after {max_retries} attempts")

    raise last_exception if last_exception else Exception("Database connection failed")


async def shutdown_db() -> None:
    """Gracefully shutdown the database engine."""
    await engine.dispose()
    logger.info("Database engine disposed")


__all__ = ["Base", "get_session", "verify_db_connection", "shutdown_db", "engine", "get_database_url"]
'''


def generate_core_settings(project_name: str, project_pascal: str) -> str:
    """Generate core/settings.py with Pydantic settings."""
    return f'''"""
Application settings and configuration.

Uses Pydantic Settings for environment-based configuration
with validation and type checking.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
from typing import Literal, List
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        env_parse_none_str="null"
    )

    # ==================== Application Settings ====================
    APP_NAME: str = Field(default="{project_pascal}", description="Application name")
    APP_VERSION: str = Field(default="0.1.0", description="Application version")
    ENVIRONMENT: Literal["development", "staging", "production"] = Field(
        default="development",
        description="Current environment"
    )
    DEBUG: bool = Field(default=False, description="Debug mode")

    # ==================== API Settings ====================
    API_V1_PREFIX: str = Field(default="/api/v1", description="API v1 prefix")
    API_PORT: int = Field(default=8000, ge=1, le=65535, description="API port")
    HOST: str = Field(default="0.0.0.0", description="API host")

    # ==================== Database Settings ====================
    POSTGRES_USER: str = Field(..., description="PostgreSQL username")
    POSTGRES_PASSWORD: str = Field(..., description="PostgreSQL password")
    POSTGRES_HOST: str = Field(default="localhost", description="PostgreSQL host")
    POSTGRES_PORT: int = Field(default=5432, ge=1, le=65535, description="PostgreSQL port")
    POSTGRES_DB: str = Field(..., description="PostgreSQL database name")

    # Database Pool Settings
    DB_POOL_SIZE: int = Field(default=5, ge=1, description="Connection pool size")
    DB_MAX_OVERFLOW: int = Field(default=10, ge=0, description="Max overflow connections")
    DB_POOL_TIMEOUT: int = Field(default=30, ge=1, description="Pool timeout in seconds")
    DB_ECHO: bool = Field(default=False, description="Echo SQL statements")

    # ==================== Security Settings ====================
    SECRET_KEY: str = Field(..., description="Secret key for signing")
    JWT_SECRET_KEY: str = Field(..., description="JWT secret key")
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=120, ge=1)
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, ge=1)

    # ==================== CORS Settings ====================
    CORS_ORIGINS: str = Field(
        default="http://localhost:3000,http://localhost:8000",
        description="Comma-separated list of allowed origins"
    )

    # ==================== Redis Settings ====================
    REDIS_HOST: str = Field(default="localhost", description="Redis host")
    REDIS_PORT: int = Field(default=6379, description="Redis port")
    REDIS_DB: int = Field(default=0, description="Redis database")
    REDIS_PASSWORD: str = Field(default="", description="Redis password")

    # ==================== Logging Settings ====================
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")

    # ==================== Computed Properties ====================
    @property
    def database_url(self) -> str:
        """Build async PostgreSQL connection URL."""
        return (
            f"postgresql+asyncpg://{{self.POSTGRES_USER}}:{{self.POSTGRES_PASSWORD}}"
            f"@{{self.POSTGRES_HOST}}:{{self.POSTGRES_PORT}}/{{self.POSTGRES_DB}}"
        )

    @property
    def redis_url(self) -> str:
        """Build Redis connection URL."""
        if self.REDIS_PASSWORD:
            return f"redis://:{{self.REDIS_PASSWORD}}@{{self.REDIS_HOST}}:{{self.REDIS_PORT}}/{{self.REDIS_DB}}"
        return f"redis://{{self.REDIS_HOST}}:{{self.REDIS_PORT}}/{{self.REDIS_DB}}"

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT == "development"

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    @field_validator("SECRET_KEY", "JWT_SECRET_KEY")
    @classmethod
    def validate_secret_keys(cls, v: str, info) -> str:
        """Validate secret keys meet minimum security requirements."""
        if not v or len(v) < 32:
            raise ValueError(f"{{info.field_name}} must be at least 32 characters")
        return v


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
'''


def generate_core_crud() -> str:
    """Generate core/crud.py with base CRUD operations."""
    return '''"""
Base CRUD operations.

Provides a reusable, type-safe interface for CRUD operations
on SQLAlchemy models using Generic types.

IMPORTANT: CRUD methods do NOT commit. Service layer owns transactions.
"""

from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from sqlalchemy.orm import DeclarativeBase
from pydantic import BaseModel

ModelType = TypeVar("ModelType", bound=DeclarativeBase)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Base CRUD class with common database operations.
    
    Pattern:
    - NO session.commit() calls - Service layer owns transaction boundaries
    - USE session.flush() to persist and get database-generated IDs
    - USE session.refresh() to ensure objects are fully loaded
    """

    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get(self, session: AsyncSession, id: Any) -> Optional[ModelType]:
        """Get a single record by ID."""
        result = await session.execute(select(self.model).where(self.model.id == id))
        return result.scalar_one_or_none()

    async def get_multi(
        self, session: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        """Get multiple records with pagination."""
        result = await session.execute(
            select(self.model).offset(skip).limit(limit).order_by(self.model.id)
        )
        return list(result.scalars().all())

    async def create(self, session: AsyncSession, *, obj_in: CreateSchemaType) -> ModelType:
        """
        Create a new record.
        Note: Does NOT commit. Call session.commit() from service layer.
        """
        obj_in_data = obj_in.model_dump()
        db_obj = self.model(**obj_in_data)
        session.add(db_obj)
        await session.flush()
        await session.refresh(db_obj)
        return db_obj

    async def update(
        self,
        session: AsyncSession,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """
        Update an existing record.
        Note: Does NOT commit. Call session.commit() from service layer.
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        if update_data:
            filtered_data = {k: v for k, v in update_data.items() if v is not None}
            for field, value in filtered_data.items():
                setattr(db_obj, field, value)
            await session.flush()
            await session.refresh(db_obj)

        return db_obj

    async def remove(self, session: AsyncSession, *, id: int) -> bool:
        """Delete a record by ID. Does NOT commit."""
        result = await session.execute(
            delete(self.model).where(self.model.id == id)
        )
        await session.flush()
        return result.rowcount > 0

    async def count(self, session: AsyncSession) -> int:
        """Count total records."""
        result = await session.execute(select(func.count(self.model.id)))
        return result.scalar() or 0

    async def exists(self, session: AsyncSession, id: Any) -> bool:
        """Check if a record exists."""
        result = await session.execute(
            select(self.model.id).where(self.model.id == id)
        )
        return result.scalar_one_or_none() is not None
'''


def generate_core_exceptions() -> str:
    """Generate core/exceptions.py with global exception handlers."""
    return '''"""
Global exception handlers and custom exceptions.

Provides centralized exception handling for the FastAPI application.
"""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from pydantic import ValidationError
import traceback

from .logging import get_logger

logger = get_logger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    """Register all exception handlers with the FastAPI app."""

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Handle Pydantic validation errors."""
        logger.warning(f"Validation error: {exc.errors()}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "detail": "Validation error",
                "errors": exc.errors()
            }
        )

    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(request: Request, exc: IntegrityError):
        """Handle database integrity errors."""
        logger.error(f"Database integrity error: {exc}")
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": "Database integrity error. Possible duplicate entry."}
        )

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_error_handler(request: Request, exc: SQLAlchemyError):
        """Handle general SQLAlchemy errors."""
        logger.error(f"Database error: {exc}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "A database error occurred."}
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle all uncaught exceptions."""
        logger.error(f"Unhandled exception: {exc}\\n{traceback.format_exc()}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "An internal server error occurred."}
        )
'''


def generate_core_logging() -> str:
    """Generate core/logging.py with structured logging."""
    return '''"""
Logging configuration.

Provides structured logging with configurable levels and formatters.
"""

import logging
import sys
from typing import Optional

from .settings import settings


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get a logger instance with standard configuration.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name or __name__)
    
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))
        
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))
    
    return logger


def setup_logging() -> None:
    """Configure root logging for the application."""
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    
    # Reduce noise from third-party libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
'''


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


def generate_core_celery() -> str:
    """Generate core/celery_app.py for background tasks."""
    return '''"""
Celery application configuration.

Provides background task processing with Redis as broker.
"""

from celery import Celery

from .settings import settings

celery_app = Celery(
    "worker",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,
    task_soft_time_limit=240,
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
)

# Auto-discover tasks from all modules
# Add your module names here
celery_app.autodiscover_tasks([
    "app.user",
    # Add more modules as you create them
])
'''


def generate_core_alembic_models() -> str:
    """Generate core/alembic_models_import.py for migration auto-generation."""
    return '''"""
Alembic Models Import

This file imports all models for Alembic autogenerate to detect.
Add imports for all your models here.
"""

# Import Base for metadata
from app.core.models import Base

# Import all models for Alembic autogenerate
from app.user.models import User

# Add more model imports as you create modules:
# from app.product.models import Product
# from app.order.models import Order
'''
