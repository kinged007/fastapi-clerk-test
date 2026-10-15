"""
Core module containing configuration and utilities.

This module provides centralized configuration management
and core utilities used throughout the application.
"""

from .config import logger, settings, setup_logging

__all__ = ["settings", "logger", "setup_logging"]
