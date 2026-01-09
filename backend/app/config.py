from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import Optional
import logging
import os

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    The app will start even with missing env vars to allow healthcheck to work.
    Database/auth operations will fail gracefully if required vars are missing.
    """

    # Core
    APP_NAME: str = "Todo Web API"
    APP_ENV: str = "production"
    LOG_LEVEL: str = "info"

    # Database - Optional at startup, required for DB operations
    DATABASE_URL: Optional[str] = None

    # CORS
    CORS_ORIGINS: str = "http://localhost:3000"

    # Auth - JWT - Optional at startup, required for auth operations
    JWT_SECRET_KEY: Optional[str] = None
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 15

    # Frontend URL - defaults to allow app to start
    FRONTEND_URL: str = "http://localhost:3000"

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, v: Optional[str]) -> Optional[str]:
        """Convert DATABASE_URL to use psycopg2 driver if set."""
        if not v:
            logger.warning("DATABASE_URL not set - database operations will fail")
            return None

        if not v.startswith(("postgresql://", "postgresql+psycopg2://", "postgresql+psycopg://", "postgres://")):
            logger.error("DATABASE_URL must be a PostgreSQL connection string")
            return None

        # Normalize all PostgreSQL URLs to use psycopg2 driver explicitly
        if v.startswith("postgres://"):
            v = v.replace("postgres://", "postgresql+psycopg2://", 1)
        elif v.startswith("postgresql+psycopg://"):
            v = v.replace("postgresql+psycopg://", "postgresql+psycopg2://", 1)
        elif v.startswith("postgresql://"):
            v = v.replace("postgresql://", "postgresql+psycopg2://", 1)
        return v

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
    # OAuth Configuration
    # ============================================
    #
    # To enable OAuth, set these environment variables in your .env file:
    #
    # GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
    # GOOGLE_CLIENT_SECRET=your-google-client-secret
    #
    # GITHUB_CLIENT_ID=your-github-client-id
    # GITHUB_CLIENT_SECRET=your-github-client-secret
    #
    # ============================================
    # Google OAuth Setup Instructions:
    # ============================================
    # 1. Go to https://console.cloud.google.com/
    # 2. Create a new project or select existing
    # 3. Go to "APIs & Services" > "Credentials"
    # 4. Click "Create Credentials" > "OAuth client ID"
    # 5. Select "Web application"
    # 6. Add authorized redirect URIs:
    #    - http://localhost:3000/auth/google/callback (development)
    #    - https://your-domain.com/auth/google/callback (production)
    # 7. Copy the Client ID and Client Secret
    #
    # ============================================
    # GitHub OAuth Setup Instructions:
    # ============================================
    # 1. Go to https://github.com/settings/developers
    # 2. Click "New OAuth App"
    # 3. Set Application name: "TaskFlow" (or your app name)
    # 4. Set Homepage URL: http://localhost:3000 (or your domain)
    # 5. Set Authorization callback URL:
    #    - http://localhost:3000/auth/github/callback (development)
    #    - https://your-domain.com/auth/github/callback (production)
    # 6. Click "Register application"
    # 7. Copy the Client ID and generate a Client Secret
    # ============================================

    # Google OAuth
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GOOGLE_REDIRECT_URI: Optional[str] = None  # Will default to FRONTEND_URL + /auth/google/callback

    # GitHub OAuth
    GITHUB_CLIENT_ID: Optional[str] = None
    GITHUB_CLIENT_SECRET: Optional[str] = None
    GITHUB_REDIRECT_URI: Optional[str] = None  # Will default to FRONTEND_URL + /auth/github/callback

    class Config:
        env_file = ".env"
        extra = "ignore"  # Allow extra fields (Railway may set additional vars)

    def get_google_redirect_uri(self) -> str:
        """Get Google OAuth redirect URI, defaulting to FRONTEND_URL + callback path."""
        return self.GOOGLE_REDIRECT_URI or f"{self.FRONTEND_URL}/auth/google/callback"

    def get_github_redirect_uri(self) -> str:
        """Get GitHub OAuth redirect URI, defaulting to FRONTEND_URL + callback path."""
        return self.GITHUB_REDIRECT_URI or f"{self.FRONTEND_URL}/auth/github/callback"


# Instantiate settings - app will start even with missing env vars
# Database/auth operations will fail gracefully if required vars are missing
try:
    settings = Settings()
    logger.info(f"Settings loaded: APP_ENV={settings.APP_ENV}")
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
        FRONTEND_URL="http://localhost:3000"
    )
