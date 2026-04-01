"""
Pydantic schemas for authentication-related data structures.

This module defines all the data models used for:
- User authentication responses
- JWT token handling
- API request/response models
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class TokenDebugRequest(BaseModel):
    """Request model for token debugging endpoint."""
    token: str = Field(..., description="JWT token to debug")


class TokenDebugResponse(BaseModel):
    """Response model for token debugging endpoint."""
    token_preview: str = Field(..., description="First 50 characters of the token")
    decoded_claims: Dict[str, Any] = Field(..., description="Decoded JWT claims")
    token_length: int = Field(..., description="Length of the token")
    verification_status: str = Field(..., description="Token verification status")


class UserResponse(BaseModel):
    """User data response model."""
    id: str = Field(..., description="Unique user identifier")
    first_name: Optional[str] = Field(None, description="User's first name")
    last_name: Optional[str] = Field(None, description="User's last name")
    username: Optional[str] = Field(None, description="Username")
    image_url: Optional[str] = Field(None, description="Profile image URL")
    has_image: bool = Field(False, description="Whether user has a profile image")
    created_at: Optional[datetime] = Field(None, description="Account creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    last_sign_in_at: Optional[datetime] = Field(None, description="Last sign-in timestamp")
    full_profile: Optional[Dict[str, Any]] = Field(None, description="Complete user profile data")


class LoginResponse(BaseModel):
    """Response model for login endpoint."""
    redirect_url: str = Field(..., description="URL to redirect user for authentication")
    message: str = Field(..., description="Human-readable message")


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""
    status: str = Field(..., description="Application status")
    message: str = Field(..., description="Status message")
    clerk_configured: bool = Field(..., description="Whether Clerk is properly configured")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")


class ErrorResponse(BaseModel):
    """Standard error response model."""
    detail: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Application-specific error code")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")


class AuthenticationError(BaseModel):
    """Authentication-specific error response."""
    detail: str = Field(..., description="Authentication error message")
    error_type: str = Field("authentication_error", description="Type of authentication error")
    suggestions: List[str] = Field(default_factory=list, description="Suggestions to resolve the error")
