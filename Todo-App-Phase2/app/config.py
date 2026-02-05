"""
Phase 2 Configuration - Traditional REST API.

This configuration is for Phase 2 only (Auth + Todo CRUD).
NO OpenAI / AI chatbot configuration is included.
Phase 3 (AI chatbot) has its own separate configuration.
"""

from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import Optional, List, Union
import logging
import os
from pathlib import Path

# Load .env file BEFORE Settings instantiation
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Determine .env file path (backend/.env)
env_path = Path(__file__).parent.parent / ".env"

# Load .env with verification
if env_path.exists():
    load_dotenv(dotenv_path=env_path, override=False)
    logger.info(f"✓ Environment variables loaded from: {env_path}")
else:
    logger.warning(f"⚠ .env file not found at: {env_path} - using system environment only")


class Settings(BaseSettings):
    """
    Phase 2 Application Settings.

    Required for:
    - User authentication (JWT)
    - Todo CRUD operations
    - PostgreSQL database connection
    - OAuth (Google, GitHub) - optional

    NOT required (Phase 3 only):
    - OPENAI_API_KEY (separate deployment)
    - MCP configuration (separate deployment)
    """

    # Core
    APP_NAME: str = "Todo Web API - Phase 2"
    APP_ENV: str = "production"
    LOG_LEVEL: str = "info"

    # Database - Optional at startup, required for DB operations
    DATABASE_URL: Optional[str] = None

    # CORS - List of allowed origins
    # Accepts: JSON array, comma-separated string, or single string
    CORS_ORIGINS: Union[str, List[str]] = ["http://localhost:3000"]

    # Auth - JWT - Optional at startup, required for auth operations
    JWT_SECRET_KEY: Optional[str] = None
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 15

    # Frontend URL - defaults to allow app to start
    FRONTEND_URL: str = "http://localhost:3000"

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, v: Optional[str]) -> Optional[str]:
        """
        Normalize DATABASE_URL to use psycopg driver.

        Supports Neon, Supabase, Railway, and other PostgreSQL providers.
        Normalizes postgres:// and postgresql:// to postgresql+psycopg://.
        """
        if not v:
            logger.warning("DATABASE_URL not set - database operations will fail")
            return None

        if not v.startswith(("postgresql://", "postgresql+psycopg://", "postgresql+psycopg2://", "postgres://")):
            logger.error("DATABASE_URL must be a PostgreSQL connection string")
            return None

        # Normalize postgres:// to postgresql+psycopg:// (psycopg v3)
        if v.startswith("postgres://"):
            v = v.replace("postgres://", "postgresql+psycopg://", 1)
            logger.info("Normalized postgres:// to postgresql+psycopg://")
        # Also normalize postgresql:// to postgresql+psycopg://
        elif v.startswith("postgresql://") and "+psycopg" not in v:
            v = v.replace("postgresql://", "postgresql+psycopg://", 1)
            logger.info("Normalized postgresql:// to postgresql+psycopg://")

        return v

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def validate_cors_origins(cls, v) -> List[str]:
        """
        Ensure CORS_ORIGINS is a list of strings.
        Accepts: JSON array, comma-separated string, or single string
        """
        if v is None or v == "":
            logger.info("CORS_ORIGINS not set, using default: localhost:3000")
            return ["http://localhost:3000"]

        # If it's already a list, clean and return it
        if isinstance(v, list):
            return [origin.strip() for origin in v if origin and origin.strip()]

        # If it's a string, parse it
        if isinstance(v, str):
            v = v.strip()

            if not v:
                return ["http://localhost:3000"]

            # Handle comma-separated values
            if "," in v:
                origins = [origin.strip() for origin in v.split(",") if origin.strip()]
                logger.info(f"Parsed CORS_ORIGINS from CSV: {origins}")
                return origins

            # Single value
            logger.info(f"Using single CORS origin: {v}")
            return [v]

        logger.warning(f"Unexpected CORS_ORIGINS type: {type(v)}, defaulting to localhost")
        return ["http://localhost:3000"]

    @field_validator("JWT_SECRET_KEY")
    @classmethod
    def validate_jwt_secret(cls, v: Optional[str]) -> Optional[str]:
        """Validate JWT_SECRET_KEY if set."""
        if not v:
            logger.warning("JWT_SECRET_KEY not set - authentication will fail")
            return None
        if len(v) < 32:
            logger.error("JWT_SECRET_KEY must be at least 32 characters")
            return None
        return v

    @field_validator("FRONTEND_URL")
    @classmethod
    def validate_frontend_url(cls, v: str) -> str:
        """Clean up FRONTEND_URL."""
        if not v:
            return "http://localhost:3000"
        return v.rstrip("/")

    # ============================================
    # OAuth Configuration (Optional)
    # ============================================

    # Google OAuth
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GOOGLE_REDIRECT_URI: Optional[str] = None

    # GitHub OAuth
    GITHUB_CLIENT_ID: Optional[str] = None
    GITHUB_CLIENT_SECRET: Optional[str] = None
    GITHUB_REDIRECT_URI: Optional[str] = None

    class Config:
        env_file = ".env"
        extra = "ignore"  # Allow extra fields

    def get_google_redirect_uri(self) -> str:
        """Get Google OAuth redirect URI."""
        return self.GOOGLE_REDIRECT_URI or f"{self.FRONTEND_URL}/auth/google/callback"

    def get_github_redirect_uri(self) -> str:
        """Get GitHub OAuth redirect URI."""
        return self.GITHUB_REDIRECT_URI or f"{self.FRONTEND_URL}/auth/github/callback"

    def get_cors_origins(self) -> List[str]:
        """
        Get CORS origins list, including FRONTEND_URL if not already present.
        """
        origins = list(self.CORS_ORIGINS)
        if self.FRONTEND_URL and self.FRONTEND_URL not in origins:
            origins.append(self.FRONTEND_URL)
        return origins


# Instantiate settings - app will start even with missing env vars
try:
    settings = Settings()
    logger.info(f"Settings loaded: APP_ENV={settings.APP_ENV}")
    logger.info(f"CORS origins configured: {settings.get_cors_origins()}")

    # Verify critical settings for Phase 2
    if not settings.DATABASE_URL:
        logger.warning("DATABASE_URL not configured - database features disabled")
    if not settings.JWT_SECRET_KEY:
        logger.warning("JWT_SECRET_KEY not configured - authentication disabled")

except Exception as e:
    logger.error(f"Failed to load settings: {e}")
    # Create minimal settings to allow app to start for healthcheck
    settings = Settings(
        DATABASE_URL=None,
        JWT_SECRET_KEY=None,
        FRONTEND_URL="http://localhost:3000",
        CORS_ORIGINS=["http://localhost:3000"]
    )
