-- Multi-User Bug Risk Analysis Platform Database Schema
-- Supports 100+ concurrent company users with activity tracking

-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255),
    department VARCHAR(100),
    role VARCHAR(50) DEFAULT 'user', -- 'user', 'admin', 'super_admin'
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User sessions for tracking active users
CREATE TABLE user_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    session_token VARCHAR(255) UNIQUE NOT NULL,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    is_active BOOLEAN DEFAULT TRUE
);

-- User activity tracking
CREATE TABLE user_activities (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    session_id INTEGER REFERENCES user_sessions(id) ON DELETE CASCADE,
    action_type VARCHAR(100) NOT NULL, -- 'login', 'analyze_project', 'view_trends', 'export_data', etc.
    project_analyzed VARCHAR(100),
    filters_used JSONB,
    page_visited VARCHAR(100),
    duration_seconds INTEGER,
    ip_address INET,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB -- Additional context data
);

-- Usage analytics aggregated data
CREATE TABLE usage_analytics (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    total_users INTEGER DEFAULT 0,
    active_users INTEGER DEFAULT 0,
    new_users INTEGER DEFAULT 0,
    total_sessions INTEGER DEFAULT 0,
    total_analyses INTEGER DEFAULT 0,
    avg_session_duration INTERVAL,
    most_analyzed_project VARCHAR(100),
    peak_concurrent_users INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Project usage statistics
CREATE TABLE project_analytics (
    id SERIAL PRIMARY KEY,
    project_key VARCHAR(100) NOT NULL,
    date DATE NOT NULL,
    analysis_count INTEGER DEFAULT 0,
    unique_users INTEGER DEFAULT 0,
    avg_bugs_found FLOAT,
    critical_components_found INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(project_key, date)
);

-- Feature usage tracking
CREATE TABLE feature_usage (
    id SERIAL PRIMARY KEY,
    feature_name VARCHAR(100) NOT NULL,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    usage_count INTEGER DEFAULT 1,
    last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date DATE DEFAULT CURRENT_DATE,
    UNIQUE(feature_name, user_id, date)
);

-- System configuration for shared JIRA settings
CREATE TABLE system_config (
    id SERIAL PRIMARY KEY,
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value TEXT NOT NULL,
    is_encrypted BOOLEAN DEFAULT FALSE,
    description TEXT,
    updated_by INTEGER REFERENCES users(id),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Audit log for admin actions
CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    admin_user_id INTEGER REFERENCES users(id),
    action VARCHAR(200) NOT NULL,
    target_user_id INTEGER REFERENCES users(id),
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_active ON users(is_active);
CREATE INDEX idx_sessions_token ON user_sessions(session_token);
CREATE INDEX idx_sessions_user_active ON user_sessions(user_id, is_active);
CREATE INDEX idx_activities_user_timestamp ON user_activities(user_id, timestamp);
CREATE INDEX idx_activities_action_timestamp ON user_activities(action_type, timestamp);
CREATE INDEX idx_analytics_date ON usage_analytics(date);
CREATE INDEX idx_project_analytics_date ON project_analytics(date);
CREATE INDEX idx_feature_usage_date ON feature_usage(date);

-- Insert default system configuration
INSERT INTO system_config (config_key, config_value, description) VALUES
('jira_url', 'https://your-company.atlassian.net', 'Shared JIRA instance URL'),
('jira_email', 'your-service-account@company.com', 'Shared JIRA service account'),
('jira_api_token', 'your-encrypted-token-here', 'Shared JIRA API token (encrypted)'),
('session_timeout_hours', '8', 'User session timeout in hours'),
('max_concurrent_users', '150', 'Maximum concurrent users allowed'),
('analytics_retention_days', '365', 'How long to keep analytics data');

-- Create views for common queries
CREATE VIEW active_users_today AS
SELECT 
    u.id, u.email, u.full_name, u.department,
    s.session_token, s.created_at as login_time,
    COUNT(a.id) as activities_today
FROM users u
JOIN user_sessions s ON u.id = s.user_id
LEFT JOIN user_activities a ON u.id = a.user_id AND DATE(a.timestamp) = CURRENT_DATE
WHERE s.is_active = TRUE AND s.expires_at > NOW()
GROUP BY u.id, u.email, u.full_name, u.department, s.session_token, s.created_at;

CREATE VIEW daily_usage_summary AS
SELECT 
    DATE(timestamp) as date,
    COUNT(DISTINCT user_id) as unique_users,
    COUNT(*) as total_activities,
    COUNT(CASE WHEN action_type = 'analyze_project' THEN 1 END) as analyses,
    COUNT(CASE WHEN action_type = 'view_trends' THEN 1 END) as trend_views,
    COUNT(CASE WHEN action_type = 'view_insights' THEN 1 END) as insight_views
FROM user_activities
WHERE timestamp >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE(timestamp)
ORDER BY date DESC; 