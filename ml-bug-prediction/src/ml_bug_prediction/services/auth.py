# Multi-User Authentication System for Bug Risk Analysis Platform
# Supports company email-based login with session management

import os
import hashlib
import secrets
import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, session, redirect, url_for, g
import psycopg2
from psycopg2.extras import RealDictCursor
import bcrypt
import re

class UserAuth:
    def __init__(self, db_config=None):
        pass

class ActivityTracker:
    def __init__(self, db_config=None):
        pass

def get_db_config():
    return {}

# Flask decorators for authentication
def login_required(f):
    """Decorator to require user login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        session_token = request.headers.get('X-Session-Token') or session.get('session_token')
        
        if not session_token:
            return jsonify({'error': 'Authentication required', 'code': 'AUTH_REQUIRED'}), 401
        
        auth = UserAuth(get_db_config())
        user_session = auth.validate_session(session_token)
        
        if not user_session:
            return jsonify({'error': 'Invalid or expired session', 'code': 'SESSION_INVALID'}), 401
        
        if not user_session['is_active']:
            return jsonify({'error': 'User account is disabled', 'code': 'ACCOUNT_DISABLED'}), 403
        
        # Store user info in request context
        g.current_user = user_session
        g.session_token = session_token
        
        return f(*args, **kwargs)
    
    return decorated_function

def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not hasattr(g, 'current_user') or g.current_user['role'] not in ['admin', 'super_admin']:
            return jsonify({'error': 'Admin access required', 'code': 'ADMIN_REQUIRED'}), 403
        
        return f(*args, **kwargs)
    
    return decorated_function

def track_activity(action_type, **activity_kwargs):
    """Decorator to automatically track user activity"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            start_time = datetime.now()
            
            try:
                # Execute the function
                result = f(*args, **kwargs)
                
                # Track successful activity
                if hasattr(g, 'current_user'):
                    duration = (datetime.now() - start_time).total_seconds()
                    
                    tracker = ActivityTracker(get_db_config())
                    tracker.log_activity(
                        user_id=g.current_user['user_id'],
                        session_id=g.current_user['id'],
                        action_type=action_type,
                        duration_seconds=int(duration),
                        ip_address=request.remote_addr,
                        **activity_kwargs
                    )
                
                return result
                
            except Exception as e:
                # Track failed activity
                if hasattr(g, 'current_user'):
                    tracker = ActivityTracker(get_db_config())
                    tracker.log_activity(
                        user_id=g.current_user['user_id'],
                        session_id=g.current_user['id'],
                        action_type=f"{action_type}_failed",
                        ip_address=request.remote_addr,
                        metadata={'error': str(e)}
                    )
                
                raise e
        
        return decorated_function
    return decorator

# Rate limiting for authentication attempts
class RateLimiter:
    def __init__(self):
        self.attempts = {}  # In production, use Redis for distributed rate limiting
    
    def is_allowed(self, identifier, max_attempts=5, window_minutes=15):
        """Check if request is allowed based on rate limiting"""
        now = datetime.now()
        window_start = now - timedelta(minutes=window_minutes)
        
        if identifier not in self.attempts:
            self.attempts[identifier] = []
        
        # Clean old attempts
        self.attempts[identifier] = [
            attempt for attempt in self.attempts[identifier] 
            if attempt > window_start
        ]
        
        # Check if under limit
        if len(self.attempts[identifier]) >= max_attempts:
            return False
        
        # Record this attempt
        self.attempts[identifier].append(now)
        return True

# Security utilities
def hash_token(token):
    """Hash token for secure storage"""
    return hashlib.sha256(token.encode()).hexdigest()

def generate_csrf_token():
    """Generate CSRF token"""
    return secrets.token_hex(16)

def validate_csrf_token(token, session_token):
    """Validate CSRF token"""
    expected = hashlib.sha256(f"{session_token}{token}".encode()).hexdigest()
    provided = hashlib.sha256(f"{session_token}{token}".encode()).hexdigest()
    return expected == provided 