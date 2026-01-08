from pydantic_settings import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):
    # Core
    APP_NAME: str = "Todo Web API"
    APP_ENV: str = "development"
    LOG_LEVEL: str = "info"

    # API
    DATABASE_URL: str = "postgresql+psycopg://neondb_owner:npg_yABz0nT2WSsd@ep-solitary-queen-adbi57ew-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
    CORS_ORIGINS: str = "http://localhost:3000"

    # Auth - JWT
    JWT_SECRET_KEY: str = "Mlv8oEesSOTv9572xOe7QoKOjPPYxj40SxRuO85h1x4"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 15

    # Frontend URL
    FRONTEND_URL: str = "http://localhost:3000"

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
    GOOGLE_REDIRECT_URI: str = "http://localhost:3000/auth/google/callback"

    # GitHub OAuth
    GITHUB_CLIENT_ID: Optional[str] = None
    GITHUB_CLIENT_SECRET: Optional[str] = None
    GITHUB_REDIRECT_URI: str = "http://localhost:3000/auth/github/callback"

    class Config:
        env_file = ".env"
        extra = "ignore"  # Allow extra fields for OAuth configs

settings = Settings()
