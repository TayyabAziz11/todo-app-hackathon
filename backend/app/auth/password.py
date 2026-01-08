"""
Password hashing and verification using bcrypt.

Security Design:
- Uses bcrypt algorithm via passlib (industry standard)
- Automatic salt generation for each password
- Configurable rounds (default: 12, provides good security/performance balance)
- Protection against timing attacks via constant-time comparison
"""

from passlib.context import CryptContext

# Configure password hashing context
# - schemes: bcrypt only (strong, well-tested algorithm)
# - deprecated: none (only bcrypt is allowed)
# - bcrypt rounds: 12 (2^12 = 4096 iterations, good security/performance tradeoff)
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12
)


def hash_password(plain_password: str) -> str:
    """
    Hash a plain-text password using bcrypt.

    Args:
        plain_password: The password to hash (must not be empty)

    Returns:
        Bcrypt hash string (format: $2b$rounds$salt+hash)

    Raises:
        ValueError: If password is empty or None

    Example:
        >>> hashed = hash_password("MySecurePassword123")
        >>> hashed.startswith("$2b$")
        True
        >>> len(hashed)
        60
    """
    if not plain_password or not plain_password.strip():
        raise ValueError("Password cannot be empty")

    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain-text password against a bcrypt hash.

    Uses constant-time comparison to prevent timing attacks.

    Args:
        plain_password: The password to verify
        hashed_password: The bcrypt hash to compare against

    Returns:
        True if password matches hash, False otherwise

    Example:
        >>> hashed = hash_password("MySecurePassword123")
        >>> verify_password("MySecurePassword123", hashed)
        True
        >>> verify_password("WrongPassword", hashed)
        False
    """
    if not plain_password or not hashed_password:
        return False

    return pwd_context.verify(plain_password, hashed_password)
