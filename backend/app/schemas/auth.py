"""
Pydantic schemas for authentication endpoints.

These schemas define the request and response structures for:
- User registration
- User login
- Token responses
- OAuth authentication (Google, GitHub)
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Literal, Optional


class RegisterRequest(BaseModel):
    """
    Request payload for user registration.

    Validates:
        - Email format (valid email address)
        - Password length (minimum 8 characters)
    """

    email: EmailStr = Field(
        ...,
        description="User's email address (must be valid and unique)",
        examples=["user@example.com"]
    )

    password: str = Field(
        ...,
        min_length=8,
        description="Password (minimum 8 characters)",
        examples=["SecurePassword123"]
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "email": "newuser@example.com",
                    "password": "SecurePassword123"
                }
            ]
        }
    }


class LoginRequest(BaseModel):
    """
    Request payload for user login.

    Validates:
        - Email format (valid email address)
        - Password present (no length validation on login)
    """

    email: EmailStr = Field(
        ...,
        description="User's email address",
        examples=["user@example.com"]
    )

    password: str = Field(
        ...,
        description="User's password",
        examples=["SecurePassword123"]
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "email": "user@example.com",
                    "password": "SecurePassword123"
                }
            ]
        }
    }


class UserResponse(BaseModel):
    """
    User information included in responses.

    Note: Does NOT include password or hashed_password (security).
    """

    id: str = Field(
        ...,
        description="User's unique identifier (UUID as string)",
        examples=["123e4567-e89b-12d3-a456-426614174000"]
    )

    email: str = Field(
        ...,
        description="User's email address",
        examples=["user@example.com"]
    )

    name: Optional[str] = Field(
        default=None,
        description="User's display name",
        examples=["John Doe"]
    )

    avatar_url: Optional[str] = Field(
        default=None,
        description="URL to user's profile picture",
        examples=["https://lh3.googleusercontent.com/a/..."]
    )

    oauth_provider: Optional[str] = Field(
        default=None,
        description="OAuth provider if user signed up via OAuth",
        examples=["google", "github"]
    )

    model_config = {
        "from_attributes": True,  # Enable ORM mode for SQLModel compatibility
        "json_schema_extra": {
            "examples": [
                {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "email": "user@example.com",
                    "name": "John Doe",
                    "avatar_url": None,
                    "oauth_provider": None
                }
            ]
        }
    }


class TokenResponse(BaseModel):
    """
    Response payload for successful authentication (login/register).

    Contains:
        - JWT access token
        - Token type (always "bearer")
        - User information
    """

    access_token: str = Field(
        ...,
        description="JWT access token (15-minute expiration)",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."]
    )

    token_type: Literal["bearer"] = Field(
        default="bearer",
        description="Token type (always 'bearer' for JWT)"
    )

    user: UserResponse = Field(
        ...,
        description="Authenticated user's information"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjNlNDU2Ny1lODliLTEyZDMtYTQ1Ni00MjY2MTQxNzQwMDAiLCJleHAiOjE3MDk1NjQ0MDB9.signature",
                    "token_type": "bearer",
                    "user": {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "email": "user@example.com"
                    }
                }
            ]
        }
    }


# ============================================
# OAuth Schemas
# ============================================

class OAuthURLResponse(BaseModel):
    """
    Response containing the OAuth authorization URL.

    The frontend should redirect the user to this URL
    to begin the OAuth authentication flow.
    """

    auth_url: str = Field(
        ...,
        description="The OAuth provider's authorization URL",
        examples=["https://accounts.google.com/o/oauth2/v2/auth?client_id=..."]
    )

    provider: str = Field(
        ...,
        description="OAuth provider name",
        examples=["google", "github"]
    )


class OAuthCallbackRequest(BaseModel):
    """
    Request payload for OAuth callback.

    After the user authorizes with the OAuth provider,
    they are redirected back with an authorization code.
    """

    code: str = Field(
        ...,
        description="Authorization code from OAuth provider",
        examples=["4/0AX4XfWj..."]
    )

    state: Optional[str] = Field(
        default=None,
        description="State parameter for CSRF protection",
        examples=["random_state_string"]
    )


class OAuthErrorResponse(BaseModel):
    """
    Error response for OAuth operations.
    """

    error: str = Field(
        ...,
        description="Error type",
        examples=["oauth_not_configured", "invalid_code", "provider_error"]
    )

    detail: str = Field(
        ...,
        description="Human-readable error message",
        examples=["Google OAuth is not configured. Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET."]
    )
