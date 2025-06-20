# Multi-User Bug Risk Analysis Platform Deployment Guide

## 🏗️ Complete Setup for 100+ Concurrent Company Users

This guide will help you deploy the multi-user Bug Risk Analysis Platform that supports concurrent access for all company employees.

## 📋 Prerequisites

### 1. System Requirements
- **Python 3.9+**
- **PostgreSQL 12+** (for user management and analytics)
- **Redis** (for session caching and rate liproprietary commercialing)
- **NGINX** (for load balancing and SSL)
- **Docker** (recommended for production)

### 2. Hardware Requirements
- **CPU**: 4+ cores for 100+ users
- **RAM**: 8GB+ (16GB recommended)
- **Storage**: 100GB+ (for analytics data)
- **Network**: High-bandwidth internet connection

## 🚀 Step-by-Step Installation

### Step 1: Database Setup

```bash
# Install PostgreSQL
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql
CREATE DATABASE bugdash_multiuser;
CREATE USER bugdash WITH PASSWORD 'your-secure-password';
GRANT ALL PRIVILEGES ON DATABASE bugdash_multiuser TO bugdash;
\q

# Run database schema
psql -U bugdash -d bugdash_multiuser -f database_schema.sql
```

### Step 2: Redis Setup (for session caching)

```bash
# Install Redis
sudo apt-get install redis-server

# Configure Redis for sessions
sudo nano /etc/redis/redis.conf
# Set: maxmemory 1gb
# Set: maxmemory-policy allkeys-lru

sudo systemctl restart redis-server
```

### Step 3: Application Setup

```bash
# Clone repository
git clone <your-repo-url>
cd ml-bug-prediction

# Create virtual environment
python3 -m venv multiuser_env
source multiuser_env/bin/activate

# Install dependencies
pip install -r requirements_multiuser.txt
```

### Step 4: Environment Configuration

Create `.env` file:

```bash
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=bugdash_multiuser
DB_USER=bugdash
DB_PASSWORD=your-secure-password

# Flask Configuration
FLASK_SECRET_KEY=your-super-secret-flask-key-generate-randomly
JWT_SECRET_KEY=your-jwt-secret-key-generate-randomly

# JIRA Configuration (Shared across all users)
JIRA_URL=https://your-company.atlassian.net
JIRA_EMAIL=service-account@company.com
JIRA_API_TOKEN=your-jira-api-token
JIRA_ENVIRONMENT=Production

# Platform Configuration
MAX_CONCURRENT_USERS=150
SESSION_TIMEOUT_HOURS=8
ANALYTICS_RETENTION_DAYS=365

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Email Configuration (for notifications)
SMTP_HOST=smtp.company.com
SMTP_PORT=587
SMTP_USER=noreply@company.com
SMTP_PASSWORD=your-smtp-password

# Monitoring
SENTRY_DSN=your-sentry-dsn-for-error-tracking
```

### Step 5: Required Dependencies

Create `requirements_multiuser.txt`:

```txt
# Core Flask dependencies
Flask==2.3.3
Flask-Session==0.5.0
Flask-CORS==4.0.0

# Database
psycopg2-binary==2.9.7
SQLAlchemy==2.0.21
alembic==1.12.0

# Authentication & Security
PyJWT==2.8.0
bcrypt==4.0.1
cryptography==41.0.4

# Data Processing
pandas==2.1.1
numpy==1.24.3
matplotlib==3.7.2
scipy==1.11.3

# JIRA Integration
jira==3.5.0
requests==2.31.0

# Caching & Sessions
redis==4.6.0
Flask-Redis==0.4.0

# Background Tasks
celery==5.3.2
flower==2.0.1

# Monitoring & Analytics
psutil==5.9.5
prometheus-client==0.17.1

# Email
Flask-Mail==0.9.1

# Environment
python-dotenv==1.0.0
```

## 🔧 Configuration Files

### 1. Gunicorn Configuration (`gunicorn.conf.py`)

```python
# Gunicorn configuration for production
bind = "0.0.0.0:5001"
workers = 4  # 2x CPU cores
worker_class = "gevent"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 120
keepalive = 5

# Logging
accesslog = "/var/log/bugdash/access.log"
errorlog = "/var/log/bugdash/error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "bugdash-multiuser"

# Security
liproprietary commercial_request_line = 4094
liproprietary commercial_request_fields = 100
liproprietary commercial_request_field_size = 8190
```

### 2. NGINX Configuration (`/etc/nginx/sites-available/bugdash`)

```nginx
server {
    listen 80;
    server_name bugdash.company.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name bugdash.company.com;

    # SSL Configuration
    ssl_certificate /path/to/ssl/cert.pem;
    ssl_certificate_key /path/to/ssl/private.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers EECDH+AESGCM:EDH+AESGCM;

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Rate liproprietary commercialing
    liproprietary commercial_req_zone $binary_remote_addr zone=auth:10m rate=5r/m;
    liproprietary commercial_req_zone $binary_remote_addr zone=api:10m rate=100r/m;

    # Static files
    location /static/ {
        alias /path/to/bugdash/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Authentication endpoints (rate liproprietary commercialed)
    location /auth/ {
        liproprietary commercial_req zone=auth burst=3 nodelay;
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # API endpoints (rate liproprietary commercialed)
    location /api/ {
        liproprietary commercial_req zone=api burst=20 nodelay;
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Main application
    location / {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### 3. Systemd Service (`/etc/systemd/system/bugdash.service`)

```ini
[Unit]
Description=BugDash Multi-User Platform
After=network.target postgresql.service redis.service

[Service]
Type=notify
User=bugdash
Group=bugdash
WorkingDirectory=/opt/bugdash
Environment=PATH=/opt/bugdash/multiuser_env/bin
ExecStart=/opt/bugdash/multiuser_env/bin/gunicorn --config gunicorn.conf.py app_multiuser:app
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

## 📊 Monitoring & Analytics Setup

### 1. Background Tasks with Celery

Create `celery_tasks.py`:

```python
from celery import Celery
from analytics import PlatformAnalytics
from auth import UserAuth
import os

# Configure Celery
celery = Celery('bugdash_tasks')
celery.conf.update(
    broker_url=f"redis://{os.getenv('REDIS_HOST', 'localhost')}:6379/1",
    result_backend=f"redis://{os.getenv('REDIS_HOST', 'localhost')}:6379/1",
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

@celery.task
def cleanup_expired_sessions():
    """Clean up expired user sessions"""
    auth = UserAuth()
    return auth.cleanup_expired_sessions()

@celery.task
def update_daily_analytics():
    """Update daily analytics aggregation"""
    analytics = PlatformAnalytics()
    analytics.update_daily_analytics()
    return "Daily analytics updated"

@celery.task
def generate_usage_report(days=30):
    """Generate comprehensive usage report"""
    analytics = PlatformAnalytics()
    return analytics.generate_usage_report(days)

# Schedule tasks
celery.conf.beat_schedule = {
    'cleanup-sessions': {
        'task': 'celery_tasks.cleanup_expired_sessions',
        'schedule': 3600.0,  # Every hour
    },
    'daily-analytics': {
        'task': 'celery_tasks.update_daily_analytics',
        'schedule': 86400.0,  # Every day at midnight
    },
}
```

### 2. Prometheus Metrics

Create `metrics.py`:

```python
from prometheus_client import Counter, Histogram, Gauge, generate_latest
import time
from functools import wraps

# Define metrics
REQUEST_COUNT = Counter('bugdash_requests_total', 'Total requests', ['method', 'endpoint', 'status'])
REQUEST_LATENCY = Histogram('bugdash_request_duration_seconds', 'Request latency')
ACTIVE_USERS = Gauge('bugdash_active_users', 'Number of active users')
JIRA_API_CALLS = Counter('bugdash_jira_api_calls_total', 'Total JIRA API calls', ['status'])

def track_metrics(f):
    """Decorator to track request metrics"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        
        try:
            result = f(*args, **kwargs)
            REQUEST_COUNT.labels(
                method=request.method,
                endpoint=request.endpoint,
                status='success'
            ).inc()
            return result
        except Exception as e:
            REQUEST_COUNT.labels(
                method=request.method,
                endpoint=request.endpoint,
                status='error'
            ).inc()
            raise
        finally:
            REQUEST_LATENCY.observe(time.time() - start_time)
    
    return decorated_function

@app.route('/metrics')
def metrics():
    """Prometheus metrics endpoint"""
    return generate_latest(), 200, {'Content-Type': 'text/plain; charset=utf-8'}
```

## 🚀 Deployment Commands

### Production Deployment

```bash
# 1. Update application code
git pull origin main

# 2. Install/update dependencies
source multiuser_env/bin/activate
pip install -r requirements_multiuser.txt

# 3. Run database migrations
alembic upgrade head

# 4. Restart services
sudo systemctl restart bugdash
sudo systemctl restart nginx
sudo systemctl restart redis

# 5. Start background workers
celery -A celery_tasks worker --loglevel=info --detach
celery -A celery_tasks beat --loglevel=info --detach
```

### Health Checks

```bash
# Check application status
curl https://bugdash.company.com/api/system/status

# Check database connection
psql -U bugdash -d bugdash_multiuser -c "SELECT COUNT(*) FROM users;"

# Check Redis
redis-cli ping

# Check logs
tail -f /var/log/bugdash/error.log
```

## 🔐 Security Configuration

### 1. Firewall Rules

```bash
# Allow only necessary ports
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP (redirects to HTTPS)
sudo ufw allow 443   # HTTPS
sudo ufw enable
```

### 2. SSL Certificate (Let's Encrypt)

```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d bugdash.company.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### 3. Database Security

```bash
# Secure PostgreSQL
sudo nano /etc/postgresql/12/main/postgresql.conf
# Set: listen_addresses = 'localhost'

sudo nano /etc/postgresql/12/main/pg_hba.conf
# Ensure: host bugdash_multiuser bugdash 127.0.0.1/32 md5

sudo systemctl restart postgresql
```

## 📈 Scaling for 100+ Users

### 1. Load Balancing Setup

```nginx
upstream bugdash_backend {
    server 127.0.0.1:5001 weight=3;
    server 127.0.0.1:5002 weight=3;
    server 127.0.0.1:5003 weight=2;
    keepalive 32;
}

server {
    location / {
        proxy_pass http://bugdash_backend;
        # ... other proxy settings
    }
}
```

### 2. Database Optimization

```sql
-- Index optimization for better performance
CREATE INDEX CONCURRENTLY idx_user_activities_user_timestamp 
ON user_activities(user_id, timestamp DESC);

CREATE INDEX CONCURRENTLY idx_user_sessions_active 
ON user_sessions(is_active, expires_at) WHERE is_active = true;

-- Connection pooling
ALTER SYSTEM SET max_connections = 200;
ALTER SYSTEM SET shared_buffers = '2GB';
ALTER SYSTEM SET effective_cache_size = '6GB';
SELECT pg_reload_conf();
```

### 3. Caching Strategy

```python
# Redis caching configuration
CACHES = {
    'default': {
        'BACKEND': 'redis_cache.RedisCache',
        'LOCATION': 'redis://localhost:6379/0',
        'OPTIONS': {
            'CLIENT_CLASS': 'redis_cache.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {'max_connections': 50},
        },
        'KEY_PREFIX': 'bugdash',
        'VERSION': 1,
    }
}
```

## 📊 Usage Analytics Dashboard

The platform provides comprehensive analytics:

### Admin Analytics Available:
- **Real-time metrics**: Active users, current sessions
- **Usage trends**: Daily/weekly/monthly activity patterns
- **Project analytics**: Most analyzed projects, user engagement
- **Feature usage**: Which features are used most
- **User activity**: Individual user behavior tracking
- **Performance metrics**: API response times, error rates
- **Department breakdown**: Usage by team/department

### Key Metrics Tracked:
- User login/logout events
- Project analysis requests
- Feature usage (trends, insights, filters)
- Session duration and frequency
- Error rates and performance issues
- JIRA API call statistics

## 🚨 Troubleshooting

### Common Issues:

1. **High CPU Usage**
   ```bash
   # Check processes
   htop
   # Scale horizontally with more app instances
   ```

2. **Database Connection Issues**
   ```bash
   # Check connections
   sudo -u postgres psql -c "SELECT count(*) FROM pg_stat_activity;"
   # Tune connection pool
   ```

3. **Memory Issues**
   ```bash
   # Monitor memory
   free -h
   # Adjust Redis maxmemory
   redis-cli CONFIG SET maxmemory 2gb
   ```

## 🎯 Go-Live Checklist

- [ ] Database schema created and migrated
- [ ] Environment variables configured
- [ ] SSL certificate installed
- [ ] NGINX configured and tested
- [ ] Firewall rules applied
- [ ] Background tasks running
- [ ] Monitoring configured
- [ ] Backup strategy implemented
- [ ] Load testing completed
- [ ] Admin users created
- [ ] Documentation updated

## 📞 Support & Maintenance

### Daily Tasks:
- Monitor system status and user activity
- Check error logs and system performance
- Verify background tasks are running

### Weekly Tasks:
- Review usage analytics and user feedback
- Update dependencies and security patches
- Database maintenance and optimization

### Monthly Tasks:
- Generate comprehensive usage reports
- Review and optimize system performance
- Plan capacity scaling if needed

---

**Ready for Production!** 🚀

This multi-user platform is designed to scale efficiently and provide comprehensive analytics for tracking company team usage of the Bug Risk Analysis tool. 