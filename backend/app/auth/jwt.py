"""
JWT token creation and verification.

Security Design:
- HS256 algorithm (HMAC with SHA-256)
- 15-minute token expiration (configurable via settings)
- Minimal payload (only user_id, reduces token size and attack surface)
- Secret key loaded from environment (never hardcoded)
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import jwt, JWTError, ExpiredSignatureError
from app.config import settings
from app.auth.exceptions import InvalidTokenError, ExpiredTokenError


def create_access_token(user_id: str) -> str:
    """
    Create a JWT access token for the given user.

    Token Payload:
        - sub (subject): user_id as string
        - exp (expiration): current time + JWT_EXPIRE_MINUTES

    Args:
        user_id: UUID of the user (as string)

    Returns:
        Encoded JWT token string

    Example:
        >>> token = create_access_token("123e4567-e89b-12d3-a456-426614174000")
        >>> len(token) > 100
        True
        >>> '.' in token  # JWT format: header.payload.signature
        True
    """
    # Calculate expiration time
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)

    # Create token payload
    payload = {
        "sub": user_id,  # Subject: user identifier
        "exp": expire    # Expiration: Unix timestamp
    }

    # Encode and sign the token
    encoded_jwt = jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )

    return encoded_jwt


def verify_token(token: str) -> str:
    """
    Verify a JWT token and extract the user_id.

    Validates:
        - Token signature (using JWT_SECRET_KEY)
        - Token expiration (exp claim)
        - Token structure (valid JWT format)

    Args:
        token: JWT token string to verify

    Returns:
        user_id (string) extracted from the 'sub' claim

    Raises:
        ExpiredTokenError: If token has expired
        InvalidTokenError: If token is malformed, has invalid signature, or missing claims

    Example:
        >>> token = create_access_token("123e4567-e89b-12d3-a456-426614174000")
        >>> user_id = verify_token(token)
        >>> user_id
        '123e4567-e89b-12d3-a456-426614174000'
    """
    try:
        # Decode and verify the token
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )

        # Extract user_id from 'sub' claim
        user_id: str = payload.get("sub")
        if not user_id:
            raise InvalidTokenError("Token payload missing 'sub' claim")

        return user_id

    except ExpiredSignatureError:
        # Token has expired
        raise ExpiredTokenError("Token has expired")

    except JWTError as e:
        # Invalid token (malformed, bad signature, etc.)
        raise InvalidTokenError(f"Invalid token: {str(e)}")
