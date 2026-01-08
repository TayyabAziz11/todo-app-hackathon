"""
FastAPI dependency functions for authentication and authorization.

Usage in route handlers:
    @app.get("/api/todos")
    async def get_todos(user_id: str = Depends(get_current_user_id)):
        # user_id is automatically extracted and verified from JWT
        ...
"""

from fastapi import Header, HTTPException, status
from app.auth.jwt import verify_token
from app.auth.exceptions import InvalidTokenError, ExpiredTokenError


def get_current_user_id(authorization: str = Header(...)) -> str:
    """
    FastAPI dependency that extracts and verifies JWT from Authorization header.

    Expected Header Format:
        Authorization: Bearer <jwt_token>

    Security Checks:
        1. Header must be present
        2. Header must start with "Bearer "
        3. Token must have valid signature
        4. Token must not be expired
        5. Token must contain 'sub' claim (user_id)

    Args:
        authorization: Authorization header value (injected by FastAPI)

    Returns:
        user_id (string) extracted from verified JWT

    Raises:
        HTTPException(401): If authorization fails for any reason
            - Missing header
            - Invalid header format
            - Invalid token signature
            - Expired token
            - Missing claims

    Example:
        ```python
        @router.get("/api/todos")
        async def get_todos(user_id: str = Depends(get_current_user_id)):
            # user_id is guaranteed to be valid here
            todos = get_user_todos(user_id)
            return todos
        ```
    """
    # Check if authorization header is provided
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Validate header format: "Bearer <token>"
    parts = authorization.split(" ")
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format. Expected: 'Bearer <token>'",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract token
    token = parts[1]

    # Verify token and extract user_id
    try:
        user_id = verify_token(token)
        return user_id

    except ExpiredTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
