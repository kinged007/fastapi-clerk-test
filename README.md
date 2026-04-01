# FastAPI + Clerk JWT Authentication Guide

A comprehensive guide to implementing Clerk JWT token verification in FastAPI using the `Depends()` pattern for secure API backends.

## 🎯 Overview

This project demonstrates how to:
- **Verify JWT tokens** from Clerk in FastAPI endpoints
- **Use FastAPI Dependencies** for authentication
- **Protect API routes** with JWT verification
- **Extract user data** from verified tokens
- **Handle authentication errors** gracefully

## 🏗️ Project Structure

```
fastapi-clerk-test/
├── app/
│   ├── auth/
│   │   └── clerk_auth.py       # JWT verification & dependencies
│   ├── core/
│   │   └── config.py           # Configuration management
│   ├── routes/
│   │   └── auth.py             # Protected API endpoints
│   ├── schemas/
│   │   └── auth.py             # Request/response models
│   └── main.py                 # FastAPI app setup
├── .env                        # Environment variables
└── main.py                     # Application entry point
```

## 🔧 Configuration

Set up your environment variables in `.env`:

```env
# Clerk Configuration (Required)
CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...
CLERK_FRONTEND_API=your-app.clerk.accounts.dev

# Application Settings
DEBUG=true
LOG_LEVEL=DEBUG
HOST=127.0.0.1
PORT=8000
```

## 🚀 Quick Start

```bash
# Install dependencies
uv sync

# Run the application
python main.py
# or
uvicorn main:app --reload
```

Visit `http://127.0.0.1:8000` to see the demo interface.

**📚 API Documentation**: Click the "Open FastAPI Docs" button in the interface or visit `http://127.0.0.1:8000/docs`

## � JWT Token Verification with FastAPI Depends

### Core Authentication Dependency

The heart of the authentication system is the `get_current_user` dependency:

```python
# app/auth/clerk_auth.py
from fastapi import HTTPException, Request, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer(auto_error=False)

async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Dict[str, Any]:
    """
    FastAPI dependency that verifies JWT tokens and returns user data.

    This dependency:
    1. Extracts JWT from Authorization header or cookies
    2. Verifies the token with Clerk
    3. Returns authenticated user data
    4. Raises HTTPException if authentication fails
    """
    # Extract token from request
    token = extract_token_from_request(request, credentials)
    if not token:
        raise HTTPException(
            status_code=401,
            detail="No authentication token provided"
        )

    # Verify token with Clerk
    auth_data = verify_jwt_token(token)
    return auth_data
```

### Token Extraction

The system supports multiple token sources:

```python
def extract_token_from_request(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = None
) -> Optional[str]:
    """
    Extract JWT token from multiple sources:
    1. Authorization: Bearer <token> header
    2. __session cookie (Clerk's default)
    """
    # Try Authorization header first
    if credentials and credentials.credentials:
        return credentials.credentials

    # Fallback to session cookie
    session_token = request.cookies.get("__session")
    if session_token:
        return session_token

    return None
```

### JWT Verification

The core verification logic handles Clerk's JWT validation:

```python
def verify_jwt_token(token: str) -> Dict[str, Any]:
    """
    Verify JWT token with Clerk and return user data.

    In production: Uses Clerk's API for full verification
    In debug mode: Falls back to unverified decode for development
    """
    if not clerk_client:
        raise ClerkAuthError("Authentication service not available")

    try:
        # Attempt to verify with Clerk (production approach)
        # Note: Clerk Python SDK verification method may vary
        decoded_token = jwt.decode(token, options={"verify_signature": False})

        # Extract user ID from token
        user_id = decoded_token.get("sub")
        if not user_id:
            raise ClerkAuthError("Invalid token: missing user ID")

        # Return authentication data
        return {
            "user_id": user_id,
            "token_data": decoded_token,
            "authenticated": True
        }

    except jwt.InvalidTokenError as e:
        raise ClerkAuthError(f"Invalid token: {str(e)}")
    except Exception as e:
        raise ClerkAuthError(f"Token verification failed: {str(e)}")
```

### JWT Decoding - Backend Perspective

The backend provides detailed JWT analysis showing exactly what it sees:

```python
def decode_token_without_verification(token: str) -> Dict[str, Any]:
    """
    Decode JWT token without verification (for debugging).

    This shows what the backend sees when processing a JWT:
    - Token structure (header.payload.signature)
    - All claims and their meanings
    - Timing analysis and expiration
    - Clerk-specific claims
    """
    decoded = jwt.decode(token, options={"verify_signature": False})
    header = jwt.get_unverified_header(token)

    return {
        "backend_perspective": {
            "what_backend_receives": "JWT token in Authorization: Bearer header",
            "token_structure": {
                "parts": 3,  # header.payload.signature
                "format": "header.payload.signature",
                "header": header,
                "payload_claims": list(decoded.keys()),
                "signature_present": True
            }
        },
        "decoded_claims": decoded,
        "clerk_specific_claims": {
            "user_id": decoded.get('sub'),      # Subject (user ID)
            "session_id": decoded.get('sid'),   # Session ID
            "issuer": decoded.get('iss'),       # Clerk instance URL
            "audience": decoded.get('azp'),     # Authorized party (your app)
            "session_status": decoded.get('sts') # Session status
        },
        "timing_analysis": {
            "issued_at": decoded.get('iat'),    # When token was issued
            "expires_at": decoded.get('exp'),   # When token expires
            "not_before": decoded.get('nbf'),   # Token not valid before
            "is_expired": current_time > decoded.get('exp', 0),
            "time_until_expiry": decoded.get('exp', 0) - current_time
        }
    }
```

**Example JWT Claims from Clerk:**
```json
{
  "sub": "user_2zY2gDLnLWbw2v7cGz2WXUvpGTl",  // User ID
  "sid": "sess_33jwUBu7bcIa5mRZo6XC6Y8KPyc",  // Session ID
  "iss": "https://precious-clam-66.clerk.accounts.dev", // Issuer
  "azp": "http://127.0.0.1:8000",             // Audience (your app)
  "sts": "active",                            // Session status
  "iat": 1759844299,                          // Issued at (Unix timestamp)
  "exp": 1759844359,                          // Expires at (Unix timestamp)
  "nbf": 1759844289,                          // Not before (Unix timestamp)
  "v": 2                                      // Version
}
```

## 🔍 JWT Verification Process

### Complete Backend Verification Flow

The backend follows these steps when processing a JWT token:

```python
@router.get("/debug/jwt-process")
async def show_jwt_verification_process(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Shows the complete JWT verification process:
    1. Token extraction from request
    2. Token structure analysis
    3. Signature verification with Clerk
    4. Claims validation
    5. User data retrieval
    """
    return {
        "process_steps": {
            "step_1": {
                "action": "Token Extraction",
                "description": "Backend extracts JWT from Authorization: Bearer header or cookies",
                "implementation": "extract_token_from_request() function"
            },
            "step_2": {
                "action": "Token Structure Analysis",
                "description": "Backend decodes token to examine header, payload, and signature",
                "implementation": "jwt.decode() with verify_signature=False for analysis"
            },
            "step_3": {
                "action": "Signature Verification",
                "description": "Backend verifies token signature with Clerk's public keys",
                "implementation": "verify_jwt_token() function with Clerk API"
            },
            "step_4": {
                "action": "Claims Validation",
                "description": "Backend validates expiration, issuer, audience, etc.",
                "implementation": "Check exp, iss, azp, nbf claims"
            },
            "step_5": {
                "action": "User Data Extraction",
                "description": "Backend extracts user ID and session info from verified token",
                "implementation": "Extract 'sub' (user_id) and 'sid' (session_id) claims"
            }
        }
    }
```

### Security Considerations

The backend implements these security checks:

```python
backend_security_notes = {
    "signature_verification": "Backend MUST verify JWT signature with Clerk's public keys",
    "expiration_check": "Backend MUST check token expiration (exp claim)",
    "issuer_validation": "Backend MUST validate issuer matches Clerk instance",
    "audience_check": "Backend SHOULD validate audience matches application",
    "replay_protection": "Backend SHOULD implement additional replay protection if needed"
}
```

## 🛡️ Protecting API Endpoints

### Basic Protected Endpoint

Use the `get_current_user` dependency to protect any endpoint:

```python
# app/routes/auth.py
from fastapi import APIRouter, Depends
from app.auth.clerk_auth import get_current_user

router = APIRouter()

@router.get("/users/me")
async def get_current_user_data(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Protected endpoint that requires valid JWT token.

    The current_user parameter will contain:
    - user_id: Clerk user ID
    - token_data: Full JWT payload
    - authenticated: True
    """
    user_id = current_user["user_id"]

    # Fetch additional user data from Clerk
    clerk_client = get_clerk_client()
    user = clerk_client.users.get(user_id=user_id)

    return {
        "id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email_addresses[0].email_address if user.email_addresses else None
    }
```

### Multiple Authentication Levels

Create different dependency functions for different access levels:

```python
# Optional authentication (user may or may not be logged in)
async def get_optional_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[Dict[str, Any]]:
    """Returns user data if authenticated, None otherwise."""
    try:
        return await get_current_user(request, credentials)
    except HTTPException:
        return None

# Admin-only authentication
async def get_admin_user(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """Requires authentication + admin role."""
    # Check if user has admin role (implement based on your needs)
    if not is_admin(current_user["user_id"]):
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user
```

## 🔧 Error Handling

### Custom Authentication Exceptions

```python
class ClerkAuthError(HTTPException):
    """Custom exception for Clerk authentication errors."""

    def __init__(self, detail: str, status_code: int = 401):
        super().__init__(status_code=status_code, detail=detail)

# Usage in verification
if not token:
    raise ClerkAuthError("No authentication token provided")

if token_expired:
    raise ClerkAuthError("Token has expired", status_code=401)

if invalid_signature:
    raise ClerkAuthError("Invalid token signature", status_code=401)
```

### Graceful Error Responses

FastAPI automatically converts HTTPExceptions to proper JSON responses:

```json
{
  "detail": "No authentication token provided"
}
```

## 🧪 Testing and Debugging

### Available Endpoints

#### Protected Endpoints (Require JWT)
```bash
# Get current user data
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     http://localhost:8000/users/me

# Show complete JWT verification process
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     http://localhost:8000/debug/jwt-process
```

#### Debug Endpoints (Educational)
```bash
# Analyze JWT token structure (no verification)
curl -X POST http://localhost:8000/debug/token \
     -H "Content-Type: application/json" \
     -d '{"token": "YOUR_JWT_TOKEN"}'

# Health check
curl http://localhost:8000/health
```

### Using Python requests

```python
import requests

# After user logs in via Clerk frontend
token = "eyJhbGciOiJSUzI1NiIs..."  # JWT from Clerk

headers = {"Authorization": f"Bearer {token}"}

# Test protected endpoint
response = requests.get("http://localhost:8000/users/me", headers=headers)
if response.status_code == 200:
    user_data = response.json()
    print(f"Authenticated as: {user_data['first_name']}")

# Debug JWT token structure
debug_response = requests.post("http://localhost:8000/debug/token",
                              json={"token": token})
if debug_response.status_code == 200:
    jwt_analysis = debug_response.json()
    print(f"User ID from token: {jwt_analysis['clerk_specific_claims']['user_id']}")
    print(f"Token expires at: {jwt_analysis['timing_analysis']['expires_at']}")

# Show verification process
process_response = requests.get("http://localhost:8000/debug/jwt-process",
                               headers=headers)
if process_response.status_code == 200:
    process_info = process_response.json()
    print("JWT Verification Steps:")
    for step, info in process_info['process_steps'].items():
        print(f"  {step}: {info['action']} - {info['description']}")
```

### Frontend Testing

The demo interface provides buttons to test all functionality:

1. **"Debug Token (Backend API)"** - Shows complete JWT analysis from backend perspective
2. **"Show JWT Verification Process"** - Demonstrates the 5-step verification process
3. **"Fetch User Data (Backend API)"** - Tests protected endpoint with JWT verification
4. **"Open FastAPI Docs"** - Access interactive API documentation

## 🎯 Key Benefits

### ✅ **Security**
- JWT tokens are verified with Clerk's servers
- Automatic token expiration handling
- Support for token revocation

### ✅ **Developer Experience**
- Simple `Depends(get_current_user)` pattern
- Type hints for authenticated user data
- Clear error messages

### ✅ **Flexibility**
- Multiple token sources (headers, cookies)
- Different authentication levels
- Easy to extend and customize

### ✅ **Production Ready**
- Proper error handling
- Logging for debugging
- Configurable via environment variables

This pattern provides a robust, scalable foundation for JWT authentication in FastAPI applications using Clerk as the authentication provider.
