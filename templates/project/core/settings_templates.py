"""
Core Settings Templates.

Generates Pydantic-based application settings.
"""


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
    CORS_ALLOW_CREDENTIALS: bool = Field(
        default=True,
        description="Allow credentials in CORS requests"
    )
    CORS_ALLOW_METHODS: List[str] = Field(
        default=["*"],
        description="Allowed HTTP methods for CORS"
    )
    CORS_ALLOW_HEADERS: List[str] = Field(
        default=["*"],
        description="Allowed headers for CORS"
    )
    CORS_ORIGIN_REGEX: str = Field(
        default="",
        description="Regex pattern for CORS origin matching"
    )

    # ==================== Security Settings (Middleware) ====================
    TRUSTED_HOSTS: List[str] = Field(
        default=["*"],
        description="Trusted hosts for production (use specific domains in production)"
    )

    # ==================== Compression Settings ====================
    ENABLE_GZIP: bool = Field(
        default=True,
        description="Enable GZip compression for responses"
    )
    GZIP_MINIMUM_SIZE: int = Field(
        default=1000,
        ge=0,
        description="Minimum response size in bytes to trigger GZip compression"
    )

    # ==================== Redis Settings ====================
    REDIS_HOST: str = Field(default="localhost", description="Redis host")
    REDIS_PORT: int = Field(default=6379, description="Redis port")
    REDIS_DB: int = Field(default=0, description="Redis database")
    REDIS_PASSWORD: str = Field(default="", description="Redis password")

    # ==================== Logging Settings ====================
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    ENABLE_FILE_LOGGING: bool = Field(
        default=True,
        description="Enable logging to files"
    )
    LOG_FILE_MAX_SIZE: int = Field(
        default=10485760,  # 10MB
        description="Maximum size of log file in bytes before rotation"
    )
    LOG_FILE_BACKUP_COUNT: int = Field(
        default=5,
        description="Number of backup log files to keep"
    )

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
