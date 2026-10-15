"""
Authentication module for Clerk integration.

This module provides authentication utilities and dependencies
for JWT token verification and user management.
"""

from .clerk_auth import (
    ClerkAuthError,
    decode_token_without_verification,
    get_clerk_client,
    get_current_user,
    verify_jwt_token,
)

__all__ = [
    "get_current_user",
    "get_clerk_client",
    "verify_jwt_token",
    "decode_token_without_verification",
    "ClerkAuthError",
]
