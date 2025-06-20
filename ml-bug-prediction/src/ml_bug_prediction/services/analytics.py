# Analytics and Usage Tracking System for Multi-User Platform
# Provides detailed insights into user behavior and platform usage

import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta
import json
from collections import defaultdict
from auth import get_db_config

class PlatformAnalytics:
    def __init__(self, db_config=None):
        self.db_config = db_config or get_db_config()
    
    def get_db_connection(self):
        """Get database connection"""
        return psycopg2.connect(**self.db_config, cursor_factory=RealDictCursor)
    
    def get_usage_overview(self, days=30):
        """Get platform usage overview for specified days"""
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Basic usage stats
            cursor.execute("""
                SELECT 
                    COUNT(DISTINCT u.id) as total_registered_users,
                    COUNT(DISTINCT CASE WHEN u.last_login >= NOW() - INTERVAL '%s days' THEN u.id END) as active_users,
                    COUNT(DISTINCT CASE WHEN u.created_at >= NOW() - INTERVAL '%s days' THEN u.id END) as new_users,
                    COUNT(DISTINCT CASE WHEN s.expires_at > NOW() AND s.is_active THEN s.user_id END) as current_online_users
                FROM users u
                LEFT JOIN user_sessions s ON u.id = s.user_id
            """, (days, days))
            
            user_stats = cursor.fetchone()
            
            # Activity stats
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_activities,
                    COUNT(DISTINCT user_id) as active_users_with_activity,
                    COUNT(CASE WHEN action_type = 'analyze_project' THEN 1 END) as total_analyses,
                    COUNT(CASE WHEN action_type = 'view_trends' THEN 1 END) as trend_views,
                    COUNT(CASE WHEN action_type = 'view_insights' THEN 1 END) as insight_views,
                    AVG(duration_seconds) as avg_action_duration
                FROM user_activities 
                WHERE timestamp >= NOW() - INTERVAL '%s days'
            """, (days,))
            
            activity_stats = cursor.fetchone()
            
            # Session stats
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_sessions,
                    AVG(EXTRACT(EPOCH FROM (expires_at - created_at))/3600) as avg_session_hours,
                    MAX(created_at) as last_session_time
                FROM user_sessions 
                WHERE created_at >= NOW() - INTERVAL '%s days'
            """, (days,))
            
            session_stats = cursor.fetchone()
            
            return {
                'user_stats': dict(user_stats),
                'activity_stats': dict(activity_stats),
                'session_stats': dict(session_stats),
                'period_days': days,
                'generated_at': datetime.now().isoformat()
            }
    
    def get_daily_usage_trends(self, days=30):
        """Get daily usage trends"""
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    DATE(a.timestamp) as date,
                    COUNT(DISTINCT a.user_id) as unique_users,
                    COUNT(*) as total_activities,
                    COUNT(CASE WHEN a.action_type = 'analyze_project' THEN 1 END) as analyses,
                    COUNT(CASE WHEN a.action_type = 'view_trends' THEN 1 END) as trend_views,
                    COUNT(CASE WHEN a.action_type = 'view_insights' THEN 1 END) as insight_views,
                    AVG(a.duration_seconds) as avg_duration,
                    COUNT(DISTINCT s.id) as sessions_started
                FROM user_activities a
                LEFT JOIN user_sessions s ON DATE(s.created_at) = DATE(a.timestamp)
                WHERE a.timestamp >= NOW() - INTERVAL '%s days'
                GROUP BY DATE(a.timestamp)
                ORDER BY date DESC
            """, (days,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_project_usage_stats(self, days=30):
        """Get project-specific usage statistics"""
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    project_analyzed,
                    COUNT(*) as analysis_count,
                    COUNT(DISTINCT user_id) as unique_users,
                    AVG(duration_seconds) as avg_analysis_time,
                    MAX(timestamp) as last_analyzed
                FROM user_activities 
                WHERE action_type = 'analyze_project' 
                    AND project_analyzed IS NOT NULL
                    AND timestamp >= NOW() - INTERVAL '%s days'
                GROUP BY project_analyzed
                ORDER BY analysis_count DESC
            """, (days,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_feature_usage_stats(self, days=30):
        """Get feature usage statistics"""
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    f.feature_name,
                    SUM(f.usage_count) as total_usage,
                    COUNT(DISTINCT f.user_id) as unique_users,
                    AVG(f.usage_count) as avg_usage_per_user,
                    MAX(f.last_used) as last_used
                FROM feature_usage f
                WHERE f.date >= CURRENT_DATE - INTERVAL '%s days'
                GROUP BY f.feature_name
                ORDER BY total_usage DESC
            """, (days,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_user_activity_details(self, user_id=None, days=7):
        """Get detailed user activity (for specific user or all users)"""
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            
            where_clause = "WHERE a.timestamp >= NOW() - INTERVAL '%s days'"
            params = [days]
            
            if user_id:
                where_clause += " AND a.user_id = %s"
                params.append(user_id)
            
            cursor.execute(f"""
                SELECT 
                    u.email, u.full_name, u.department,
                    a.action_type, a.project_analyzed, a.filters_used,
                    a.duration_seconds, a.timestamp, a.ip_address
                FROM user_activities a
                JOIN users u ON a.user_id = u.id
                {where_clause}
                ORDER BY a.timestamp DESC
                LIMIT 1000
            """, params)
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_peak_usage_analysis(self, days=30):
        """Analyze peak usage patterns"""
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Hourly distribution
            cursor.execute("""
                SELECT 
                    EXTRACT(HOUR FROM timestamp) as hour,
                    COUNT(*) as activity_count,
                    COUNT(DISTINCT user_id) as unique_users
                FROM user_activities 
                WHERE timestamp >= NOW() - INTERVAL '%s days'
                GROUP BY EXTRACT(HOUR FROM timestamp)
                ORDER BY hour
            """, (days,))
            
            hourly_stats = [dict(row) for row in cursor.fetchall()]
            
            # Day of week distribution
            cursor.execute("""
                SELECT 
                    EXTRACT(DOW FROM timestamp) as day_of_week,
                    COUNT(*) as activity_count,
                    COUNT(DISTINCT user_id) as unique_users
                FROM user_activities 
                WHERE timestamp >= NOW() - INTERVAL '%s days'
                GROUP BY EXTRACT(DOW FROM timestamp)
                ORDER BY day_of_week
            """, (days,))
            
            daily_stats = [dict(row) for row in cursor.fetchall()]
            
            # Peak concurrent users
            cursor.execute("""
                SELECT 
                    DATE(created_at) as date,
                    MAX(concurrent_count) as peak_concurrent
                FROM (
                    SELECT 
                        created_at,
                        COUNT(*) OVER (
                            ORDER BY created_at 
                            RANGE BETWEEN INTERVAL '1 hour' PRECEDING AND CURRENT ROW
                        ) as concurrent_count
                    FROM user_sessions
                    WHERE created_at >= NOW() - INTERVAL '%s days'
                ) sub
                GROUP BY DATE(created_at)
                ORDER BY date DESC
            """, (days,))
            
            concurrent_stats = [dict(row) for row in cursor.fetchall()]
            
            return {
                'hourly_distribution': hourly_stats,
                'daily_distribution': daily_stats,
                'peak_concurrent_users': concurrent_stats
            }
    
    def get_user_retention_metrics(self):
        """Calculate user retention metrics"""
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Daily retention for last 30 days
            cursor.execute("""
                WITH daily_users AS (
                    SELECT 
                        DATE(timestamp) as activity_date,
                        user_id
                    FROM user_activities
                    WHERE timestamp >= CURRENT_DATE - INTERVAL '30 days'
                    GROUP BY DATE(timestamp), user_id
                ),
                retention_cohorts AS (
                    SELECT 
                        d1.activity_date as cohort_date,
                        d1.user_id,
                        d2.activity_date as return_date,
                        d2.activity_date - d1.activity_date as days_diff
                    FROM daily_users d1
                    LEFT JOIN daily_users d2 ON d1.user_id = d2.user_id 
                        AND d2.activity_date > d1.activity_date
                        AND d2.activity_date <= d1.activity_date + INTERVAL '7 days'
                )
                SELECT 
                    cohort_date,
                    COUNT(DISTINCT user_id) as cohort_size,
                    COUNT(DISTINCT CASE WHEN days_diff = 1 THEN user_id END) as day_1_retention,
                    COUNT(DISTINCT CASE WHEN days_diff = 7 THEN user_id END) as day_7_retention
                FROM retention_cohorts
                GROUP BY cohort_date
                ORDER BY cohort_date DESC
                LIMIT 30
            """)
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_department_usage_breakdown(self, days=30):
        """Get usage breakdown by department"""
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    COALESCE(u.department, 'Unknown') as department,
                    COUNT(DISTINCT u.id) as total_users,
                    COUNT(DISTINCT CASE WHEN a.timestamp >= NOW() - INTERVAL '%s days' THEN u.id END) as active_users,
                    COUNT(CASE WHEN a.timestamp >= NOW() - INTERVAL '%s days' THEN 1 END) as total_activities,
                    COUNT(CASE WHEN a.action_type = 'analyze_project' AND a.timestamp >= NOW() - INTERVAL '%s days' THEN 1 END) as analyses_performed
                FROM users u
                LEFT JOIN user_activities a ON u.id = a.user_id
                GROUP BY u.department
                ORDER BY active_users DESC
            """, (days, days, days))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def generate_usage_report(self, days=30):
        """Generate comprehensive usage report"""
        return {
            'report_period': f"Last {days} days",
            'generated_at': datetime.now().isoformat(),
            'overview': self.get_usage_overview(days),
            'daily_trends': self.get_daily_usage_trends(days),
            'project_usage': self.get_project_usage_stats(days),
            'feature_usage': self.get_feature_usage_stats(days),
            'peak_usage': self.get_peak_usage_analysis(days),
            'retention_metrics': self.get_user_retention_metrics(),
            'department_breakdown': self.get_department_usage_breakdown(days)
        }
    
    def update_daily_analytics(self, date=None):
        """Update daily analytics aggregation (run this daily via cron)"""
        if not date:
            date = datetime.now().date() - timedelta(days=1)  # Previous day
        
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Calculate daily metrics
            cursor.execute("""
                WITH daily_metrics AS (
                    SELECT 
                        COUNT(DISTINCT u.id) as total_users,
                        COUNT(DISTINCT CASE WHEN DATE(a.timestamp) = %s THEN a.user_id END) as active_users,
                        COUNT(DISTINCT CASE WHEN DATE(u.created_at) = %s THEN u.id END) as new_users,
                        COUNT(DISTINCT CASE WHEN DATE(s.created_at) = %s THEN s.id END) as total_sessions,
                        COUNT(CASE WHEN DATE(a.timestamp) = %s AND a.action_type = 'analyze_project' THEN 1 END) as total_analyses,
                        AVG(CASE WHEN DATE(a.timestamp) = %s THEN a.duration_seconds END) as avg_session_duration
                    FROM users u
                    LEFT JOIN user_activities a ON u.id = a.user_id
                    LEFT JOIN user_sessions s ON u.id = s.user_id
                ),
                most_analyzed AS (
                    SELECT project_analyzed
                    FROM user_activities
                    WHERE DATE(timestamp) = %s AND action_type = 'analyze_project'
                    GROUP BY project_analyzed
                    ORDER BY COUNT(*) DESC
                    LIMIT 1
                )
                INSERT INTO usage_analytics (
                    date, total_users, active_users, new_users, 
                    total_sessions, total_analyses, avg_session_duration, most_analyzed_project
                )
                SELECT 
                    %s, dm.total_users, dm.active_users, dm.new_users,
                    dm.total_sessions, dm.total_analyses, 
                    INTERVAL '1 second' * COALESCE(dm.avg_session_duration, 0),
                    ma.project_analyzed
                FROM daily_metrics dm
                CROSS JOIN (SELECT project_analyzed FROM most_analyzed UNION SELECT NULL LIMIT 1) ma
                ON CONFLICT (date) DO UPDATE SET
                    total_users = EXCLUDED.total_users,
                    active_users = EXCLUDED.active_users,
                    new_users = EXCLUDED.new_users,
                    total_sessions = EXCLUDED.total_sessions,
                    total_analyses = EXCLUDED.total_analyses,
                    avg_session_duration = EXCLUDED.avg_session_duration,
                    most_analyzed_project = EXCLUDED.most_analyzed_project
            """, (date, date, date, date, date, date, date))
            
            conn.commit()
    
    def get_real_time_metrics(self):
        """Get real-time platform metrics"""
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Current active users
            cursor.execute("""
                SELECT COUNT(DISTINCT user_id) as current_active_users
                FROM user_sessions 
                WHERE is_active = TRUE AND expires_at > NOW()
            """)
            active_users = cursor.fetchone()['current_active_users']
            
            # Activities in last hour
            cursor.execute("""
                SELECT COUNT(*) as activities_last_hour
                FROM user_activities 
                WHERE timestamp >= NOW() - INTERVAL '1 hour'
            """)
            recent_activities = cursor.fetchone()['activities_last_hour']
            
            # Peak today
            cursor.execute("""
                SELECT MAX(hourly_count) as peak_today
                FROM (
                    SELECT 
                        EXTRACT(HOUR FROM created_at) as hour,
                        COUNT(DISTINCT user_id) as hourly_count
                    FROM user_sessions
                    WHERE DATE(created_at) = CURRENT_DATE
                    GROUP BY EXTRACT(HOUR FROM created_at)
                ) hourly_stats
            """)
            peak_today = cursor.fetchone()['peak_today'] or 0
            
            return {
                'current_active_users': active_users,
                'activities_last_hour': recent_activities,
                'peak_users_today': peak_today,
                'timestamp': datetime.now().isoformat()
            }

class UserAnalytics:
    """Analytics focused on individual user behavior"""
    
    def __init__(self, db_config=None):
        self.db_config = db_config or get_db_config()
    
    def get_db_connection(self):
        return psycopg2.connect(**self.db_config, cursor_factory=RealDictCursor)
    
    def get_user_profile(self, user_id):
        """Get comprehensive user profile with usage stats"""
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Basic user info
            cursor.execute("""
                SELECT 
                    u.*,
                    COUNT(DISTINCT s.id) as total_sessions,
                    COUNT(DISTINCT a.id) as total_activities,
                    COUNT(CASE WHEN a.action_type = 'analyze_project' THEN 1 END) as total_analyses,
                    MAX(s.created_at) as last_session,
                    AVG(a.duration_seconds) as avg_activity_duration
                FROM users u
                LEFT JOIN user_sessions s ON u.id = s.user_id
                LEFT JOIN user_activities a ON u.id = a.user_id
                WHERE u.id = %s
                GROUP BY u.id
            """, (user_id,))
            
            user_info = cursor.fetchone()
            
            # Recent activities
            cursor.execute("""
                SELECT action_type, project_analyzed, timestamp, duration_seconds
                FROM user_activities
                WHERE user_id = %s
                ORDER BY timestamp DESC
                LIMIT 10
            """, (user_id,))
            
            recent_activities = cursor.fetchall()
            
            # Feature usage
            cursor.execute("""
                SELECT feature_name, SUM(usage_count) as total_usage, MAX(last_used) as last_used
                FROM feature_usage
                WHERE user_id = %s
                GROUP BY feature_name
                ORDER BY total_usage DESC
            """, (user_id,))
            
            feature_usage = cursor.fetchall()
            
            return {
                'user_info': dict(user_info) if user_info else None,
                'recent_activities': [dict(a) for a in recent_activities],
                'feature_usage': [dict(f) for f in feature_usage]
            } 