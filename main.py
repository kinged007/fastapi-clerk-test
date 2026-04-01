"""
FastAPI + Clerk Authentication Demo - Application Entry Point

This is the main entry point for the application.
Run this file to start the server.

Usage:
    python main.py

Or with uvicorn:
    uvicorn main:app --reload
"""

from app.main import app

if __name__ == "__main__":
    import uvicorn
    from app.core.config import settings, logger

    logger.info(f"Starting server on {settings.HOST}:{settings.PORT}")

    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
