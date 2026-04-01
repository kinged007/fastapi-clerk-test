"""
Authentication routes for the FastAPI + Clerk demo.

This module contains all authentication-related endpoints:
- Login URL generation
- User data retrieval
- Token debugging
- Health checks
"""

import logging
from datetime import datetime
from typing import Dict, Any
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse

from app.auth.clerk_auth import get_current_user, get_clerk_client, decode_token_without_verification
from app.core.config import settings
from app.schemas.auth import (
    LoginResponse, 
    UserResponse, 
    TokenDebugRequest, 
    TokenDebugResponse,
    HealthResponse
)

logger = logging.getLogger(__name__)

# Create router
router = APIRouter()


@router.get("/auth/login", response_model=LoginResponse)
async def get_login_url():
    """
    Generate Clerk sign-in URL for authentication.
    
    This endpoint creates a redirect URL to Clerk's hosted sign-in page.
    After successful authentication, Clerk will redirect back to the application.
    
    Returns:
        LoginResponse: Contains the redirect URL and message
        
    Raises:
        HTTPException: If Clerk configuration is missing
    """
    logger.info("[INFO] Login URL requested")

    if not settings.clerk_configured:
        logger.error("[ERROR] Clerk not configured")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service not configured"
        )
    
    try:
        # Build Clerk sign-in URL with return URL
        base_url = settings.CLERK_SIGN_IN_URL
        params = {
            "redirect_url": f"http://{settings.HOST}:{settings.PORT}/"
        }
        
        redirect_url = f"{base_url}?{urlencode(params)}"
        
        logger.info(f"[OK] Login URL generated: {redirect_url}")
        
        return LoginResponse(
            redirect_url=redirect_url,
            message="Redirect to Clerk for authentication"
        )
        
    except Exception as e:
        logger.error(f"[ERROR] Failed to generate login URL: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate login URL: {str(e)}"
        )


@router.get("/users/me", response_model=UserResponse)
async def get_current_user_data(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> UserResponse:
    """
    Get current user's data from Clerk.
    
    This endpoint demonstrates the complete JWT verification flow:
    1. Frontend sends JWT token
    2. Backend verifies token with Clerk
    3. Backend fetches user data from Clerk
    4. Backend returns user data
    
    Args:
        current_user: Authenticated user data from dependency
        
    Returns:
        UserResponse: Complete user profile data
        
    Raises:
        HTTPException: If user data cannot be retrieved
    """
    logger.info(f"[INFO] User data requested for: {current_user.get('user_id')}")
    
    try:
        clerk_client = get_clerk_client()
        user_id = current_user.get("user_id")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User ID not found in token"
            )
        
        # Fetch user data from Clerk
        logger.debug(f"[DEBUG] Fetching user data from Clerk for user: {user_id}")
        user = clerk_client.users.get(user_id=user_id)

        logger.info("[OK] User data retrieved from Clerk")
                
        # Build response
        user_response = UserResponse(
            id=user.id,
            first_name=getattr(user, 'first_name', None),
            last_name=getattr(user, 'last_name', None),
            username=getattr(user, 'username', None),
            image_url=getattr(user, 'image_url', None),
            has_image=getattr(user, 'has_image', False),
            created_at=getattr(user, 'created_at', None),
            updated_at=getattr(user, 'updated_at', None),
            last_sign_in_at=getattr(user, 'last_sign_in_at', None),
            full_profile=user.model_dump(mode='json') if hasattr(user, 'model_dump') else None
        )
        
        logger.info(f"[OK] User data prepared for response: {user_response.first_name}")
        return user_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[ERROR] Failed to get user data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve user data: {str(e)}"
        )


@router.post("/debug/token")
async def debug_jwt_token(request: TokenDebugRequest):
    """
    Debug JWT token by decoding without verification.

    This endpoint shows what the backend sees when processing a JWT token:
    - Complete token structure (header, payload, signature)
    - All claims and their meanings
    - Timing analysis (expiration, issued at, etc.)
    - Clerk-specific claims explanation
    - Backend verification process details

    Args:
        request: Token debug request containing the JWT

    Returns:
        Complete JWT analysis from backend perspective

    Raises:
        HTTPException: If token cannot be decoded
    """
    logger.info("[INFO] === BACKEND JWT ANALYSIS ===")
    logger.info("[INFO] Analyzing JWT token from backend perspective...")

    try:
        debug_data = decode_token_without_verification(request.token)

        logger.info("[OK] JWT token analysis completed")
        logger.info(f"[INFO] User ID from token: {debug_data.get('clerk_specific_claims', {}).get('user_id', 'Not found')}")
        logger.info(f"[INFO] Token expires at: {debug_data.get('timing_analysis', {}).get('expires_at', 'Unknown')}")

        return {
            "message": "JWT Token Analysis from Backend Perspective",
            "explanation": {
                "what_happened": [
                    "1. Frontend sent JWT token to backend",
                    "2. Backend extracted token from request",
                    "3. Backend decoded token structure (header.payload.signature)",
                    "4. Backend analyzed all claims and metadata",
                    "5. Backend checked timing and expiration"
                ],
                "verification_note": "This is unverified decode for educational purposes. In production, backend would verify signature with Clerk."
            },
            **debug_data
        }

    except Exception as e:
        logger.error(f"[ERROR] JWT token analysis failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"JWT analysis failed: {str(e)}"
        )


@router.get("/debug/jwt-process")
async def show_jwt_verification_process(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Show the complete JWT verification process from backend perspective.

    This endpoint demonstrates what happens when the backend receives and verifies a JWT:
    1. Token extraction from request
    2. Token structure analysis
    3. Signature verification with Clerk
    4. Claims validation
    5. User data retrieval

    This is a protected endpoint that requires valid JWT authentication.

    Returns:
        Complete breakdown of JWT verification process
    """
    logger.info("[INFO] === JWT VERIFICATION PROCESS DEMO ===")
    logger.info("[INFO] Showing complete JWT verification from backend perspective...")

    try:
        return {
            "message": "JWT Verification Process - Backend Perspective",
            "process_steps": {
                "step_1": {
                    "action": "Token Extraction",
                    "description": "Backend extracts JWT from Authorization: Bearer header or cookies",
                    "implementation": "extract_token_from_request() function",
                    "result": "JWT token string obtained"
                },
                "step_2": {
                    "action": "Token Structure Analysis",
                    "description": "Backend decodes token to examine header, payload, and signature",
                    "implementation": "jwt.decode() with verify_signature=False for analysis",
                    "result": "Token structure and claims visible"
                },
                "step_3": {
                    "action": "Signature Verification",
                    "description": "Backend verifies token signature with Clerk's public keys",
                    "implementation": "verify_jwt_token() function with Clerk API",
                    "result": "Token authenticity confirmed"
                },
                "step_4": {
                    "action": "Claims Validation",
                    "description": "Backend validates expiration, issuer, audience, etc.",
                    "implementation": "Check exp, iss, azp, nbf claims",
                    "result": "Token validity confirmed"
                },
                "step_5": {
                    "action": "User Data Extraction",
                    "description": "Backend extracts user ID and session info from verified token",
                    "implementation": "Extract 'sub' (user_id) and 'sid' (session_id) claims",
                    "result": "User identity established"
                }
            },
            "current_verification_result": {
                "user_id": current_user.get("user_id"),
                "token_data": current_user.get("token_data", {}),
                "authenticated": current_user.get("authenticated", False),
                "verification_method": "Clerk JWT verification"
            },
            "backend_security_notes": {
                "signature_verification": "Backend MUST verify JWT signature with Clerk's public keys",
                "expiration_check": "Backend MUST check token expiration (exp claim)",
                "issuer_validation": "Backend MUST validate issuer matches Clerk instance",
                "audience_check": "Backend SHOULD validate audience matches application",
                "replay_protection": "Backend SHOULD implement additional replay protection if needed"
            }
        }

    except Exception as e:
        logger.error(f"[ERROR] JWT process demo failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"JWT process demo failed: {str(e)}"
        )


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Health check endpoint.
    
    Returns application status and configuration information.
    Useful for monitoring and debugging.
    
    Returns:
        HealthResponse: Application health status
    """
    logger.debug("[DEBUG] Health check requested")
    
    return HealthResponse(
        status="healthy",
        message=f"{settings.APP_NAME} is running",
        clerk_configured=settings.clerk_configured,
        timestamp=datetime.utcnow()
    )
