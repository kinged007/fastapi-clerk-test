"""
Clerk authentication and JWT verification utilities.

This module handles:
- Clerk client initialization
- JWT token verification
- User authentication dependency
- Security utilities
"""

import logging
from typing import Dict, Optional, Any

import jwt
from clerk_backend_api import Clerk
from fastapi import HTTPException, Request, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.config import settings

logger = logging.getLogger(__name__)

# Initialize Clerk client
clerk_client = None
if settings.clerk_configured:
    try:
        clerk_client = Clerk(bearer_auth=settings.CLERK_SECRET_KEY)
        logger.info("[OK] Clerk client initialized successfully")
    except Exception as e:
        logger.error(f"[ERROR] Failed to initialize Clerk client: {e}")
        clerk_client = None
else:
    logger.warning("[WARNING] Clerk client not initialized - missing configuration")

# HTTP Bearer security scheme
security = HTTPBearer(auto_error=False)


class ClerkAuthError(HTTPException):
    """Custom exception for Clerk authentication errors."""
    
    def __init__(self, detail: str, status_code: int = status.HTTP_401_UNAUTHORIZED):
        super().__init__(status_code=status_code, detail=detail)


def extract_token_from_request(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = None
) -> Optional[str]:
    """
    Extract JWT token from request.
    
    Tries multiple sources:
    1. Authorization header (Bearer token)
    2. __session cookie (Clerk's default cookie name)
    
    Args:
        request: FastAPI request object
        credentials: HTTP authorization credentials
        
    Returns:
        JWT token string or None if not found
    """
    # Try Authorization header first
    if credentials and credentials.credentials:
        logger.debug("🎫 Token found in Authorization header")
        return credentials.credentials
    
    # Try __session cookie (Clerk's default)
    session_cookie = request.cookies.get("__session")
    if session_cookie:
        logger.debug("🎫 Token found in __session cookie")
        return session_cookie
    
    logger.debug("[DEBUG] No token found in request")
    return None


def verify_jwt_token(token: str) -> Dict[str, Any]:
    """
    Verify JWT token with Clerk.
    
    Args:
        token: JWT token string
        
    Returns:
        Dictionary containing user_id, token, and claims
        
    Raises:
        ClerkAuthError: If token verification fails
    """
    if not clerk_client:
        raise ClerkAuthError("Clerk client not initialized")
    
    try:
        # Attempt to verify token with Clerk
        logger.debug("[DEBUG] Verifying JWT token with Clerk...")

        verified_token = clerk_client.jwt_templates.verify_token(
            token=token,
            options={"verify": True}
        )

        logger.info("[OK] JWT token verified successfully with Clerk")
        
        return {
            "user_id": verified_token.get("sub"),
            "token": token,
            "claims": verified_token
        }
        
    except Exception as clerk_error:
        logger.warning(f"[WARNING] Clerk verification failed: {clerk_error}")

        # Fallback: decode without verification for educational purposes
        if settings.DEBUG:
            try:
                logger.debug("[DEBUG] Attempting unverified token decode for debugging...")
                decoded = jwt.decode(token, options={"verify_signature": False})

                logger.warning("[WARNING] Using unverified token decode (DEBUG mode)")
                
                return {
                    "user_id": decoded.get("sub"),
                    "token": token,
                    "claims": decoded,
                    "verification_status": "unverified_debug_mode"
                }
                
            except Exception as decode_error:
                logger.error(f"[ERROR] Token decode failed: {decode_error}")
                raise ClerkAuthError(f"Invalid token format: {decode_error}")
        
        raise ClerkAuthError(f"Token verification failed: {clerk_error}")


def decode_token_without_verification(token: str) -> Dict[str, Any]:
    """
    Decode JWT token without verification (for debugging).

    This function shows what the backend sees when it receives a JWT token:
    - Token structure (header, payload, signature)
    - Claims and their meanings
    - Expiration and timing information
    - User identification data

    Args:
        token: JWT token string

    Returns:
        Dictionary containing decoded claims and metadata

    Raises:
        ClerkAuthError: If token cannot be decoded
    """
    try:
        logger.debug("🔍 Decoding JWT token without verification...")

        # Decode without verification to see the structure
        decoded = jwt.decode(token, options={"verify_signature": False})

        # Extract header information
        header = jwt.get_unverified_header(token)

        # Analyze token structure
        token_parts = token.split('.')

        # Calculate time information
        import time
        current_time = int(time.time())
        issued_at = decoded.get('iat', 0)
        expires_at = decoded.get('exp', 0)
        not_before = decoded.get('nbf', 0)

        logger.info("✅ JWT token decoded successfully (unverified)")

        return {
            "backend_perspective": {
                "what_backend_receives": "JWT token in Authorization: Bearer header",
                "token_structure": {
                    "parts": len(token_parts),
                    "format": "header.payload.signature",
                    "header": header,
                    "payload_claims": list(decoded.keys()),
                    "signature_present": len(token_parts) == 3
                }
            },
            "decoded_claims": decoded,
            "clerk_specific_claims": {
                "user_id": decoded.get('sub', 'Not found'),
                "session_id": decoded.get('sid', 'Not found'),
                "issuer": decoded.get('iss', 'Not found'),
                "audience": decoded.get('azp', 'Not found'),
                "session_status": decoded.get('sts', 'Not found')
            },
            "timing_analysis": {
                "issued_at": issued_at,
                "expires_at": expires_at,
                "not_before": not_before,
                "current_time": current_time,
                "is_expired": current_time > expires_at if expires_at else False,
                "is_active": current_time >= not_before if not_before else True,
                "time_until_expiry": expires_at - current_time if expires_at else None
            },
            "token_metadata": {
                "token_preview": token[:50] + "..." if len(token) > 50 else token,
                "token_length": len(token),
                "algorithm": header.get('alg', 'Unknown'),
                "key_id": header.get('kid', 'Not specified'),
                "verification_status": "unverified (for debugging only)"
            }
        }

    except Exception as e:
        logger.error(f"[ERROR] Token decode failed: {e}")
        raise ClerkAuthError(f"Invalid token format: {e}")


async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Dict[str, Any]:
    """
    FastAPI dependency to get current authenticated user.
    
    This function:
    1. Extracts JWT token from request
    2. Verifies token with Clerk
    3. Returns user information
    
    Args:
        request: FastAPI request object
        credentials: HTTP authorization credentials
        
    Returns:
        Dictionary containing user information and token data
        
    Raises:
        HTTPException: If authentication fails
    """
    logger.debug("🔐 Authenticating user request...")
    
    # Extract token from request
    token = extract_token_from_request(request, credentials)
    
    if not token:
        logger.warning("❌ No authentication token provided")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No authentication token provided",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Verify token and get user info
    try:
        auth_data = verify_jwt_token(token)
        logger.info(f"✅ User authenticated: {auth_data.get('user_id')}")
        return auth_data
        
    except ClerkAuthError as e:
        logger.error(f"❌ Authentication failed: {e.detail}")
        raise HTTPException(
            status_code=e.status_code,
            detail=e.detail,
            headers={"WWW-Authenticate": "Bearer"}
        )


def get_clerk_client() -> Clerk:
    """
    Get the Clerk client instance.
    
    Returns:
        Clerk client instance
        
    Raises:
        HTTPException: If Clerk client is not initialized
    """
    if not clerk_client:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Clerk client not initialized"
        )
    return clerk_client
