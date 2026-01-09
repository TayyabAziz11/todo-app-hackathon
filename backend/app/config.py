from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import Optional
import sys


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Required environment variables (app will fail to start without these):
    - DATABASE_URL: PostgreSQL connection string
    - JWT_SECRET_KEY: Secret key for JWT token signing (min 32 chars)
    - FRONTEND_URL: URL of the frontend for CORS configuration

    Optional environment variables:
    - APP_NAME: Application name (default: "Todo Web API")
    - APP_ENV: Environment (development/staging/production)
    - LOG_LEVEL: Logging level (default: info)
    - JWT_ALGORITHM: JWT algorithm (default: HS256)
    - JWT_EXPIRE_MINUTES: Token expiration in minutes (default: 15)
    """

    # Core
    APP_NAME: str = "Todo Web API"
    APP_ENV: str = "production"
    LOG_LEVEL: str = "info"

    # Database - REQUIRED (no default, must be set via env)
    DATABASE_URL: str

    # CORS
    CORS_ORIGINS: str = "http://localhost:3000"

    # Auth - JWT
    JWT_SECRET_KEY: str  # REQUIRED - no default for security
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 15

    # Frontend URL - REQUIRED for CORS
    FRONTEND_URL: str

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """Validate DATABASE_URL is set and convert to use psycopg2 driver."""
        if not v:
            print("FATAL: DATABASE_URL environment variable is required", file=sys.stderr)
            sys.exit(1)
        if not v.startswith(("postgresql://", "postgresql+psycopg2://", "postgresql+psycopg://", "postgres://")):
            print("FATAL: DATABASE_URL must be a PostgreSQL connection string", file=sys.stderr)
            sys.exit(1)
        # Normalize all PostgreSQL URLs to use psycopg2 driver explicitly
        # Railway uses postgres://, others may use postgresql:// or postgresql+psycopg://
        if v.startswith("postgres://"):
            v = v.replace("postgres://", "postgresql+psycopg2://", 1)
        elif v.startswith("postgresql+psycopg://"):
            v = v.replace("postgresql+psycopg://", "postgresql+psycopg2://", 1)
        elif v.startswith("postgresql://"):
            v = v.replace("postgresql://", "postgresql+psycopg2://", 1)
        return v

    @field_validator("JWT_SECRET_KEY")
    @classmethod
    def validate_jwt_secret(cls, v: str) -> str:
        """Validate JWT_SECRET_KEY is set and sufficiently long."""
        if not v:
            print("FATAL: JWT_SECRET_KEY environment variable is required", file=sys.stderr)
            sys.exit(1)
        if len(v) < 32:
            print("FATAL: JWT_SECRET_KEY must be at least 32 characters for security", file=sys.stderr)
            sys.exit(1)
        return v

    @field_validator("FRONTEND_URL")
    @classmethod
    def validate_frontend_url(cls, v: str) -> str:
        """Validate FRONTEND_URL is set."""
        if not v:
            print("FATAL: FRONTEND_URL environment variable is required", file=sys.stderr)
            sys.exit(1)
        # Remove trailing slash for consistency
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


# Instantiate settings - this will fail fast if required env vars are missing
try:
    settings = Settings()
except Exception as e:
    print(f"FATAL: Failed to load settings: {e}", file=sys.stderr)
    print("Please ensure all required environment variables are set:", file=sys.stderr)
    print("  - DATABASE_URL", file=sys.stderr)
    print("  - JWT_SECRET_KEY (min 32 characters)", file=sys.stderr)
    print("  - FRONTEND_URL", file=sys.stderr)
    sys.exit(1)
