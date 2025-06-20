#!/usr/bin/env python3
"""
Authentication Manager for ML Risk Analysis Dashboard
"""

import json
import os
import hashlib
import secrets
import re
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)

class AuthManager:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.users_file = os.path.join(data_dir, "users.json")
        self.sessions_file = os.path.join(data_dir, "sessions.json")
        
        # Ensure data directory exists
        os.makedirs(data_dir, exist_ok=True)
        
        # Initialize files if they don't exist
        self._initialize_files()
    
    def _initialize_files(self):
        """Initialize user and session files if they don't exist"""
        
        # Initialize users file
        if not os.path.exists(self.users_file):
            default_users = {
                "users": {},
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            self._save_json(self.users_file, default_users)
        
        # Initialize sessions file
        if not os.path.exists(self.sessions_file):
            default_sessions = {
                "sessions": {},
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            self._save_json(self.sessions_file, default_sessions)
    
    def _load_json(self, file_path: str) -> Dict[str, Any]:
        """Load JSON file safely"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Error loading {file_path}: {e}")
            return {}
    
    def _save_json(self, file_path: str, data: Dict[str, Any]) -> bool:
        """Save data to JSON file safely"""
        try:
            data["updated_at"] = datetime.now().isoformat()
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"Error saving {file_path}: {e}")
            return False
    
    def _hash_password(self, password: str, salt: str = None) -> tuple:
        """Hash password with salt"""
        if salt is None:
            salt = secrets.token_hex(32)
        
        # Use PBKDF2 with SHA-256
        hashed = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # 100,000 iterations
        )
        
        return hashed.hex(), salt
    
    def validate_password_strength(self, password: str) -> Dict[str, Any]:
        """Validate password strength according to standard rules"""
        result = {
            "valid": True,
            "score": 0,
            "feedback": [],
            "requirements": {
                "length": False,
                "uppercase": False,
                "lowercase": False,
                "digit": False,
                "special": False
            }
        }
        
        # Check length (minimum 8 characters)
        if len(password) >= 8:
            result["requirements"]["length"] = True
            result["score"] += 20
        else:
            result["feedback"].append("Password must be at least 8 characters long")
            result["valid"] = False
        
        # Check for uppercase letter
        if re.search(r'[A-Z]', password):
            result["requirements"]["uppercase"] = True
            result["score"] += 20
        else:
            result["feedback"].append("Password must contain at least one uppercase letter")
            result["valid"] = False
        
        # Check for lowercase letter
        if re.search(r'[a-z]', password):
            result["requirements"]["lowercase"] = True
            result["score"] += 20
        else:
            result["feedback"].append("Password must contain at least one lowercase letter")
            result["valid"] = False
        
        # Check for digit
        if re.search(r'\d', password):
            result["requirements"]["digit"] = True
            result["score"] += 20
        else:
            result["feedback"].append("Password must contain at least one number")
            result["valid"] = False
        
        # Check for special character
        if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            result["requirements"]["special"] = True
            result["score"] += 20
        else:
            result["feedback"].append("Password must contain at least one special character")
            result["valid"] = False
        
        return result
    
    def validate_email(self, email: str) -> bool:
        """Validate email format"""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_pattern, email) is not None
    
    def user_exists(self, email: str) -> bool:
        """Check if user with given email exists"""
        users_data = self._load_json(self.users_file)
        return email.lower() in users_data.get("users", {})
    
    def register_user(self, user_data: Dict[str, str]) -> Dict[str, Any]:
        """Register a new user"""
        email = user_data.get("email", "").lower().strip()
        password = user_data.get("password", "")
        name = user_data.get("name", "").strip()
        company = user_data.get("company", "").strip()
        role = user_data.get("role", "").strip()
        
        # Validate required fields
        if not all([email, password, name, company, role]):
            return {
                "success": False,
                "message": "All fields are required"
            }
        
        # Validate email format
        if not self.validate_email(email):
            return {
                "success": False,
                "message": "Invalid email format"
            }
        
        # Check if user already exists
        if self.user_exists(email):
            return {
                "success": False,
                "message": "User with this email already exists"
            }
        
        # Validate password strength
        password_validation = self.validate_password_strength(password)
        if not password_validation["valid"]:
            return {
                "success": False,
                "message": "Password does not meet security requirements",
                "feedback": password_validation["feedback"]
            }
        
        # Hash password
        hashed_password, salt = self._hash_password(password)
        
        # Load users data
        users_data = self._load_json(self.users_file)
        
        # Create user record
        user_record = {
            "name": name,
            "email": email,
            "company": company,
            "role": role,
            "password_hash": hashed_password,
            "salt": salt,
            "created_at": datetime.now().isoformat(),
            "last_login": None,
            "login_count": 0,
            "active": True
        }
        
        # Add user to data
        users_data["users"][email] = user_record
        
        # Save users data
        if self._save_json(self.users_file, users_data):
            return {
                "success": True,
                "message": "User registered successfully"
            }
        else:
            return {
                "success": False,
                "message": "Failed to save user data"
            }
    
    def authenticate_user(self, email: str, password: str) -> Dict[str, Any]:
        """Authenticate user with email and password"""
        email = email.lower().strip()
        
        # Load users data
        users_data = self._load_json(self.users_file)
        user_record = users_data.get("users", {}).get(email)
        
        if not user_record:
            return {
                "success": False,
                "message": "Invalid email or password"
            }
        
        # Check if user is active
        if not user_record.get("active", True):
            return {
                "success": False,
                "message": "Account is deactivated"
            }
        
        # Verify password
        stored_hash = user_record.get("password_hash")
        salt = user_record.get("salt")
        
        # Hash provided password with stored salt
        hashed_password, _ = self._hash_password(password, salt)
        
        if hashed_password == stored_hash:
            # Update login statistics
            user_record["last_login"] = datetime.now().isoformat()
            user_record["login_count"] = user_record.get("login_count", 0) + 1
            users_data["users"][email] = user_record
            self._save_json(self.users_file, users_data)
            
            return {
                "success": True,
                "message": "Authentication successful",
                "user": {
                    "email": user_record["email"],
                    "name": user_record["name"],
                    "company": user_record["company"],
                    "role": user_record["role"]
                }
            }
        else:
            return {
                "success": False,
                "message": "Invalid email or password"
            }
    
    def create_session(self, email: str) -> str:
        """Create a new session for authenticated user"""
        session_token = secrets.token_urlsafe(32)
        
        # Load sessions data
        sessions_data = self._load_json(self.sessions_file)
        
        # Create session record
        session_record = {
            "email": email.lower(),
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(hours=8)).isoformat(),
            "active": True
        }
        
        # Add session to data
        sessions_data["sessions"][session_token] = session_record
        
        # Save sessions data
        self._save_json(self.sessions_file, sessions_data)
        
        return session_token
    
    def validate_session(self, session_token: str) -> Dict[str, Any]:
        """Validate session token"""
        if not session_token:
            return {"valid": False, "message": "No session token provided"}
        
        # Load sessions data
        sessions_data = self._load_json(self.sessions_file)
        session_record = sessions_data.get("sessions", {}).get(session_token)
        
        if not session_record:
            return {"valid": False, "message": "Invalid session token"}
        
        # Check if session is active
        if not session_record.get("active", True):
            return {"valid": False, "message": "Session is inactive"}
        
        # Check if session has expired
        expires_at = datetime.fromisoformat(session_record["expires_at"])
        if datetime.now() > expires_at:
            return {"valid": False, "message": "Session has expired"}
        
        # Get user information
        email = session_record["email"]
        users_data = self._load_json(self.users_file)
        user_record = users_data.get("users", {}).get(email)
        
        if not user_record or not user_record.get("active", True):
            return {"valid": False, "message": "User account is inactive"}
        
        return {
            "valid": True,
            "user": {
                "email": user_record["email"],
                "name": user_record["name"],
                "company_name": user_record["company"],
                "role": user_record["role"],
                "created_at": user_record.get("created_at")
            }
        }
    
    def logout_session(self, session_token: str) -> bool:
        """Logout user by invalidating session"""
        sessions_data = self._load_json(self.sessions_file)
        
        if session_token in sessions_data.get("sessions", {}):
            sessions_data["sessions"][session_token]["active"] = False
            return self._save_json(self.sessions_file, sessions_data)
        
        return True  # Already logged out or session doesn't exist
    
    def update_user_profile(self, email: str, update_fields: Dict[str, str]) -> bool:
        """Update user profile information"""
        email = email.lower().strip()
        
        # Load users data
        users_data = self._load_json(self.users_file)
        
        if email not in users_data.get("users", {}):
            return False
        
        # Update fields
        user_record = users_data["users"][email]
        
        for field, value in update_fields.items():
            if field in ['name', 'company_name', 'role']:
                # Map company_name to company for consistency
                if field == 'company_name':
                    user_record['company'] = value
                else:
                    user_record[field] = value
        
        users_data["users"][email] = user_record
        
        return self._save_json(self.users_file, users_data)
    
    def change_password(self, email: str, new_password: str) -> bool:
        """Change user password"""
        email = email.lower().strip()
        
        # Validate password strength
        password_validation = self.validate_password_strength(new_password)
        if not password_validation["valid"]:
            return False
        
        # Load users data
        users_data = self._load_json(self.users_file)
        
        if email not in users_data.get("users", {}):
            return False
        
        # Hash new password
        hashed_password, salt = self._hash_password(new_password)
        
        # Update user record
        user_record = users_data["users"][email]
        user_record["password_hash"] = hashed_password
        user_record["salt"] = salt
        
        users_data["users"][email] = user_record
        
        return self._save_json(self.users_file, users_data)
    
    def validate_password(self, password: str) -> Dict[str, Any]:
        """Alias for validate_password_strength for consistency"""
        validation = self.validate_password_strength(password)
        return {
            "valid": validation["valid"],
            "error": "; ".join(validation["feedback"]) if validation["feedback"] else ""
        }

# Global instance
auth_manager = AuthManager()
