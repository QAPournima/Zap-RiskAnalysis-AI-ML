"""
Business Logic Services
=======================

This package contains business logic services for user management,
analytics, goal tracking, and configuration management.

Modules:
- settings_manager: Configuration and settings management
- auth: Authentication and authorization
- analytics: Business analytics and reporting
- goal_tracking: Goal setting and progress tracking
"""

from .settings_manager import SettingsManager
from .goal_tracking import GoalTrackingSystem

# Optional imports that require additional dependencies
try:
    from .analytics import AnalyticsEngine
    analytics_available = True
except ImportError:
    analytics_available = False

try:
    from .auth import UserAuth, ActivityTracker
    auth_available = True
except ImportError:
    auth_available = False

__all__ = ['SettingsManager', 'GoalTrackingSystem']

if analytics_available:
    __all__.append('AnalyticsEngine')

if auth_available:
    __all__.extend(['UserAuth', 'ActivityTracker']) 