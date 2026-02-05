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

    Security Note:
        Bcrypt has a 72-byte password limit. Passwords are automatically
        truncated to 72 bytes to comply with this limitation.

    Example:
        >>> hashed = hash_password("MySecurePassword123")
        >>> hashed.startswith("$2b$")
        True
        >>> len(hashed)
        60
    """
    if not plain_password or not plain_password.strip():
        raise ValueError("Password cannot be empty")

    # Bcrypt has a 72-byte limit - truncate password to comply
    # Using UTF-8 encoding to count bytes, not characters
    password_bytes = plain_password.encode('utf-8')[:72]
    truncated_password = password_bytes.decode('utf-8', errors='ignore')

    return pwd_context.hash(truncated_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain-text password against a bcrypt hash.

    Uses constant-time comparison to prevent timing attacks.

    Args:
        plain_password: The password to verify
        hashed_password: The bcrypt hash to compare against

    Returns:
        True if password matches hash, False otherwise

    Security Note:
        Bcrypt has a 72-byte password limit. Passwords are automatically
        truncated to 72 bytes before verification to match hashing behavior.

    Example:
        >>> hashed = hash_password("MySecurePassword123")
        >>> verify_password("MySecurePassword123", hashed)
        True
        >>> verify_password("WrongPassword", hashed)
        False
    """
    if not plain_password or not hashed_password:
        return False

    # Bcrypt has a 72-byte limit - truncate password to comply
    # This must match the truncation in hash_password()
    password_bytes = plain_password.encode('utf-8')[:72]
    truncated_password = password_bytes.decode('utf-8', errors='ignore')

    return pwd_context.verify(truncated_password, hashed_password)
