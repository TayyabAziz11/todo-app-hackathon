"""
Custom exceptions for authentication and authorization.
"""


class InvalidTokenError(Exception):
    """
    Raised when a JWT token is malformed, has invalid signature, or is otherwise invalid.

    Examples:
        - Tampered token (signature mismatch)
        - Malformed JWT structure
        - Missing required claims (sub, exp)
    """
    pass


class ExpiredTokenError(Exception):
    """
    Raised when a JWT token has expired.

    The token was valid at creation but the expiration time (exp) has passed.
    User must re-authenticate to obtain a fresh token.
    """
    pass
