"""
Frontend routes for serving the demo application.

This module handles:
- Serving the main HTML page
- Template rendering with Clerk configuration
- Static file serving (if needed)
"""

import logging
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.core.config import settings

logger = logging.getLogger(__name__)

# Initialize templates
templates = Jinja2Templates(directory="app/templates")

# Create router
router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def serve_frontend(request: Request):
    """
    Serve the main frontend application.
    
    This endpoint renders the HTML template with embedded Clerk configuration
    and serves the complete authentication demo interface.
    
    Args:
        request: FastAPI request object
        
    Returns:
        HTMLResponse: Rendered HTML page with Clerk integration
    """
    logger.info("🌐 Frontend page requested")
    
    # Prepare template context
    context = {
        "request": request,
        "app_name": settings.APP_NAME,
        "clerk_publishable_key": settings.CLERK_PUBLISHABLE_KEY or "NOT_CONFIGURED",
        "clerk_frontend_api": settings.CLERK_FRONTEND_API or "NOT_CONFIGURED",
        "debug_mode": settings.DEBUG,
        "clerk_configured": settings.clerk_configured
    }
    
    logger.debug(f"📄 Rendering template with context: clerk_configured={settings.clerk_configured}")
    
    return templates.TemplateResponse("index.html", context)
