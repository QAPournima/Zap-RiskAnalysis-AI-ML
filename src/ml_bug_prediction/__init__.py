"""
ML Risk Analysis System

An enterprise-grade intelligent bug risk analysis system that provides 
comprehensive component-level risk assessment across multiple software projects.
"""

__version__ = "2.0.0"
__author__ = "Pournima Tele"
__description__ = "AI-powered JIRA bug risk analysis and prediction system by Pournima Tele"

# Main package imports for easy access
try:
    from .app import app
    from .config import *
except ImportError:
    # Handle import errors gracefully during setup
    pass

__all__ = [
    "__version__",
    "__author__", 
    "__description__",
] 