"""
FastAPI + Clerk Authentication Demo - Main Application

This is the main application file that:
1. Initializes the FastAPI app
2. Configures middleware
3. Registers routes
4. Sets up logging and monitoring

Educational Flow:
User clicks login -> Redirected to Clerk -> Returns with JWT -> Backend verifies JWT -> User data fetched
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.core.config import settings, logger
from app.routes import auth, frontend


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    
    Handles startup and shutdown events for the application.
    """
    # Startup
    logger.info("Starting FastAPI + Clerk Authentication Demo")
    logger.info(f"Configuration: Debug={settings.DEBUG}, Clerk={settings.clerk_configured}")
    
    if not settings.clerk_configured:
        logger.warning("Clerk is not properly configured!")
        logger.warning("Please check your environment variables:")
        logger.warning("   - CLERK_PUBLISHABLE_KEY")
        logger.warning("   - CLERK_SECRET_KEY") 
        logger.warning("   - CLERK_FRONTEND_API")
    
    yield
    
    # Shutdown
    logger.info("Shutting down FastAPI + Clerk Authentication Demo")


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Returns:
        FastAPI: Configured application instance
    """
    # Initialize FastAPI app
    app = FastAPI(
        title=settings.APP_NAME,
        description="Educational demo showing Clerk JWT authentication flow with FastAPI",
        version=settings.APP_VERSION,
        debug=settings.DEBUG,
        lifespan=lifespan
    )
    
    # Add middleware
    setup_middleware(app)
    
    # Register routes
    register_routes(app)
    
    return app


def setup_middleware(app: FastAPI) -> None:
    """
    Configure application middleware.
    
    Args:
        app: FastAPI application instance
    """
    # CORS middleware for frontend-backend communication
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )
    
    # Trusted host middleware for security
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["localhost", "127.0.0.1", settings.HOST]
    )
    
    # Request logging middleware
    @app.middleware("http")
    async def log_requests(request, call_next):
        """Log all HTTP requests for educational purposes."""
        logger.info(f"Request: {request.method} {request.url.path}")
        
        response = await call_next(request)
        
        logger.info(f"Response: {request.method} {request.url.path} -> {response.status_code}")
        return response


def register_routes(app: FastAPI) -> None:
    """
    Register all application routes.
    
    Args:
        app: FastAPI application instance
    """
    # Include authentication routes
    app.include_router(
        auth.router,
        tags=["Authentication"],
        responses={
            401: {"description": "Unauthorized"},
            500: {"description": "Internal Server Error"}
        }
    )
    
    # Include frontend routes
    app.include_router(
        frontend.router,
        tags=["Frontend"]
    )
    
    logger.info("Routes registered successfully")


# Create the application instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting server on {settings.HOST}:{settings.PORT}")
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
