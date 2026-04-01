"""
Core module containing configuration and utilities.

This module provides centralized configuration management
and core utilities used throughout the application.
"""

from .config import settings, logger, setup_logging

__all__ = ["settings", "logger", "setup_logging"]
