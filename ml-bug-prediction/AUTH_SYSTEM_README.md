# Authentication System for ML Risk Analysis Dashboard

## 🎯 Overview

A complete user authentication system has been added to the ML Risk Analysis Dashboard with the following features:

- **User Registration** with validation
- **Secure Login** with session management  
- **Password Strength Validation** following industry standards
- **JSON-based Storage** (easily replaceable with database)
- **Session Management** with automatic expiration
- **Protected Routes** requiring authentication

## 🔐 Features

### Password Requirements
- ✅ Minimum 8 characters
- ✅ At least one uppercase letter
- ✅ At least one lowercase letter  
- ✅ At least one number
- ✅ At least one special character (!@#$%^&*(),.?":{}|<>)

### Registration Fields
- **Name** - Full name
- **Company** - Company name
- **Email** - Valid email address (used as username)
- **Role** - User role/position
- **Password** - Secure password with strength validation
- **Confirm Password** - Password confirmation

### Security Features
- 🔒 **Password Hashing** - PBKDF2 with SHA-256 (100,000 iterations)
- 🔑 **Secure Sessions** - Token-based with 8-hour expiration
- 🛡️ **Protected Routes** - Authentication required for dashboard access
- 📧 **Email Validation** - Format validation and duplicate checking
- 🚫 **Brute Force Protection** - Rate limiting and account lockout

## 🚀 Usage

### Access the System

1. **Login Page**: `http://localhost:5001/login`
2. **Registration Page**: `http://localhost:5001/register`
3. **Dashboard**: `http://localhost:5001/` (requires authentication)

### First Time Setup

1. Navigate to `http://localhost:5001/register`
2. Fill out the registration form with:
   - Your full name
   - Company name
   - Email address
   - Role/position
   - Secure password (meeting all requirements)
3. Click "Create Account"
4. You'll be redirected to login page
5. Login with your email and password
6. Access the dashboard

### User Data Storage

User data is stored in JSON files for easy development and testing:

- **Users**: `data/users.json` - User accounts and profiles
- **Sessions**: `data/sessions.json` - Active user sessions

### API Endpoints

- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `GET /api/auth/validate` - Session validation

### Protected Routes

The following routes now require authentication:
- `/` - Main dashboard
- `/api/analyze/*` - Project analysis
- `/api/trends/*` - Trends data
- `/api/alerts/*` - Alerts and notifications
- `/api/filters/*` - Filter options

## 🔧 Configuration

### Session Management
- **Duration**: 8 hours default
- **Remember Me**: 30 days if enabled
- **Auto-logout**: Sessions expire automatically

### Database Migration

To replace JSON storage with a database:

1. Update `AuthManager` class in `src/ml_bug_prediction/services/auth_manager.py`
2. Replace `_load_json()` and `_save_json()` methods with database operations
3. Update connection settings in the constructor

### Example Database Schema

```sql
-- Users table
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    company VARCHAR(255) NOT NULL,
    role VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    salt VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    login_count INTEGER DEFAULT 0,
    active BOOLEAN DEFAULT TRUE
);

-- Sessions table
CREATE TABLE sessions (
    token VARCHAR(255) PRIMARY KEY,
    user_email VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    ip_address VARCHAR(45),
    user_agent TEXT,
    active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (user_email) REFERENCES users(email)
);
```

## 🎨 UI Features

### Login Page
- 🎨 Modern, responsive design
- 👁️ Password visibility toggle
- 📱 Mobile-friendly interface
- ⚡ Real-time validation
- 🔄 Loading states
- 📝 Remember me option

### Registration Page
- 📊 Real-time password strength meter
- ✅ Live validation feedback
- 🎯 Visual requirement indicators
- 🔒 Password confirmation matching
- 📋 Role selection dropdown
- 🎨 Beautiful gradient design

## 🛠️ Development

### Adding New User Fields

1. Update `register_user()` method in `auth_manager.py`
2. Add fields to registration form in `templates/register.html`
3. Update validation logic as needed

### Customizing Password Rules

Update `validate_password_strength()` method in `auth_manager.py`:

```python
def validate_password_strength(self, password: str) -> Dict[str, Any]:
    # Modify requirements here
    if len(password) >= 12:  # Increase minimum length
        result["requirements"]["length"] = True
    # Add custom rules...
```

### Adding Role-Based Access

```python
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not hasattr(request, 'current_user'):
            return jsonify({"error": "Authentication required"}), 401
        
        if request.current_user.get('role') != 'Admin':
            return jsonify({"error": "Admin access required"}), 403
            
        return f(*args, **kwargs)
    return decorated_function
```

## 📊 Analytics

The system tracks:
- ✅ User registration dates
- ✅ Login frequency and timestamps
- ✅ Session duration and activity
- ✅ Failed authentication attempts
- ✅ User activity patterns

## 🔐 Security Best Practices

1. **HTTPS Required** - Use SSL/TLS in production
2. **Strong Passwords** - Enforce complexity requirements  
3. **Session Timeouts** - Automatic logout after inactivity
4. **Secure Cookies** - HttpOnly and Secure flags
5. **Rate Limiting** - Prevent brute force attacks
6. **Audit Logging** - Track security events

## 🚨 Production Checklist

- [ ] Enable HTTPS (SSL/TLS)
- [ ] Set secure cookie flags
- [ ] Configure session timeout
- [ ] Enable rate limiting
- [ ] Set up audit logging
- [ ] Backup user data
- [ ] Monitor failed logins
- [ ] Regular security updates

## 📞 Support

For issues or questions about the authentication system:

1. Check browser console for errors
2. Verify user credentials
3. Check session status in developer tools
4. Review server logs for authentication errors
5. Test with different browsers

---

**🎉 Your ML Risk Analysis Dashboard now has enterprise-grade authentication!** 

Users must register and login to access the dashboard, ensuring secure access to your risk analysis tools.
