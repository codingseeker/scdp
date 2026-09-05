"""
core — Cross-cutting concerns: configuration, security, errors, middleware, logging.
"""
from core.config import Settings, get_settings

__all__ = ["Settings", "get_settings"]