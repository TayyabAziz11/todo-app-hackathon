"""
User model for authentication and ownership.

Supports both email/password and OAuth authentication methods.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    """
    User model representing authenticated users in the system.

    Supports two authentication methods:
    1. Email/Password: Traditional registration with hashed password
    2. OAuth: Google or GitHub sign-in (no password required)

    Each user has a unique email address and can own multiple todos.
    Passwords are stored as bcrypt hashes, never in plaintext.
    """

    __tablename__ = "users"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        nullable=False,
        description="Unique identifier for the user"
    )

    email: str = Field(
        max_length=255,
        nullable=False,
        unique=True,
        index=True,
        description="User's email address (unique, used for login)"
    )

    hashed_password: Optional[str] = Field(
        default=None,
        max_length=255,
        nullable=True,
        description="Bcrypt hashed password (NULL for OAuth users)"
    )

    # OAuth fields
    oauth_provider: Optional[str] = Field(
        default=None,
        max_length=50,
        nullable=True,
        description="OAuth provider name (google, github) - NULL for email/password users"
    )

    oauth_id: Optional[str] = Field(
        default=None,
        max_length=255,
        nullable=True,
        description="Unique identifier from OAuth provider"
    )

    # User profile info (can be populated from OAuth)
    name: Optional[str] = Field(
        default=None,
        max_length=255,
        nullable=True,
        description="User's display name (from OAuth profile or set manually)"
    )

    avatar_url: Optional[str] = Field(
        default=None,
        max_length=500,
        nullable=True,
        description="URL to user's profile picture (from OAuth)"
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
        description="Timestamp when user account was created"
    )

    def __repr__(self) -> str:
        provider = self.oauth_provider or "email"
        return f"<User(id={self.id}, email={self.email}, provider={provider})>"

    @property
    def is_oauth_user(self) -> bool:
        """Check if user signed up via OAuth"""
        return self.oauth_provider is not None

    @property
    def display_name(self) -> str:
        """Return the best available display name"""
        if self.name:
            return self.name
        # Extract name from email
        return self.email.split("@")[0]
