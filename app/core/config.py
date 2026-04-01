"""
Core configuration settings for the FastAPI + Clerk Authentication Demo.

This module centralizes all configuration management including:
- Environment variables
- Clerk settings
- Application settings
- Logging configuration
"""

import logging
import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv(".env", override=True)


class Settings:
    """Application settings loaded from environment variables."""
    
    # Application settings
    APP_NAME: str = "FastAPI + Clerk Authentication Demo"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()
    
    # Clerk configuration
    CLERK_PUBLISHABLE_KEY: Optional[str] = os.getenv("CLERK_PUBLISHABLE_KEY")
    CLERK_SECRET_KEY: Optional[str] = os.getenv("CLERK_SECRET_KEY")
    CLERK_FRONTEND_API: Optional[str] = os.getenv("CLERK_FRONTEND_API")
    CLERK_SIGN_IN_URL: Optional[str] = os.getenv("CLERK_SIGN_IN_URL")
    
    # Server settings
    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # CORS settings
    ALLOWED_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://127.0.0.1:3000"
    ]
    
    def validate_clerk_config(self) -> bool:
        """Validate that required Clerk configuration is present."""
        required_vars = [
            self.CLERK_PUBLISHABLE_KEY,
            self.CLERK_SECRET_KEY,
            self.CLERK_FRONTEND_API
        ]
        return all(var is not None for var in required_vars)
    
    @property
    def clerk_configured(self) -> bool:
        """Check if Clerk is properly configured."""
        return self.validate_clerk_config()


# Global settings instance
settings = Settings()
print(settings.__dict__)

def setup_logging() -> logging.Logger:
    """Configure logging for the application."""
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("clerk_auth.log")
        ]
    )

    logger = logging.getLogger(__name__)

    if settings.DEBUG:
        logger.info("[DEBUG] Debug mode enabled")

    if settings.clerk_configured:
        logger.info("[OK] Clerk configuration validated")
    else:
        logger.warning("[WARNING] Clerk configuration incomplete")
        logger.warning("Required: CLERK_PUBLISHABLE_KEY, CLERK_SECRET_KEY, CLERK_FRONTEND_API")

    return logger


# Initialize logger
logger = setup_logging()
