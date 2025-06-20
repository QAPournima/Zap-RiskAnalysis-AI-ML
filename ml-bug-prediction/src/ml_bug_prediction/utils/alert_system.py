"""
Risk Threshold Alert System
Monitors component risk levels and sends notifications when thresholds are exceeded
"""

import smtplib
import json
import requests
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from .jira_utils import connect_to_jira, fetch_project_data
from ..config import JIRA_CONFIG, PROJECT_MAPPINGS

class AlertConfig:
    """Alert configuration settings"""
    
    # Risk thresholds
    HIGH_RISK_THRESHOLD = 5      # bugs
    CRITICAL_RISK_THRESHOLD = 10  # bugs
    URGENT_RISK_THRESHOLD = 15   # bugs
    
    # Alert settings
    CHECK_INTERVAL_HOURS = 6     # Check every 6 hours
    ALERT_COOLDOWN_HOURS = 24    # Don't spam same alert within 24 hours
    
    # Email settings (configure these)
    EMAIL_ENABLED = False        # Set to True to enable email alerts
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    EMAIL_USERNAME = ""          # Your email
    EMAIL_PASSWORD = ""          # Your app password
    EMAIL_RECIPIENTS = []        # List of email addresses
    
    # Slack settings (configure these)
    SLACK_ENABLED = False        # Set to True to enable Slack alerts
    SLACK_WEBHOOK_URL = ""       # Your Slack webhook URL
    SLACK_CHANNEL = "#qa-alerts" # Slack channel for notifications

class RiskAlertSystem:
    """Main alert system for monitoring component risks"""
    
    def __init__(self):
        self.jira = connect_to_jira()
        self.alert_history = {}  # Track sent alerts to avoid spam
        
    def check_all_projects(self):
        """Check risk levels across all configured projects"""
        print("🚨 Starting risk threshold monitoring...")
        
        all_alerts = []
        
        for project_code, project_info in PROJECT_MAPPINGS.items():
            try:
                project_key = project_info['jira_key']
                project_name = project_info['name']
                
                print(f"  🔍 Checking {project_name} ({project_key})...")
                
                # Fetch current risk data
                alerts = self._check_project_risks(project_key, project_name)
                all_alerts.extend(alerts)
                
            except Exception as e:
                print(f"  ❌ Error checking {project_code}: {e}")
        
        # Send notifications if any alerts found
        if all_alerts:
            self._send_notifications(all_alerts)
            print(f"✅ Monitoring complete - {len(all_alerts)} alerts sent")
        else:
            print("✅ Monitoring complete - no threshold violations found")
        
        return all_alerts
    
    def check_project_alerts(self, project_key, project_name):
        """Check risk levels for a specific project (public method)"""
        print(f"🔍 Checking alerts for {project_name} ({project_key})...")
        
        try:
            alerts = self._check_project_risks(project_key, project_name)
            
            if alerts:
                print(f"  ⚠️  Found {len(alerts)} alerts for {project_name}")
            else:
                print(f"  ✅ No alerts for {project_name}")
            
            return alerts
            
        except Exception as e:
            print(f"  ❌ Error checking alerts for {project_name}: {e}")
            return []
    
    def _check_project_risks(self, project_key, project_name):
        """Check risk levels for a specific project"""
        try:
            # Fetch recent bug data
            data = fetch_project_data(project_key)
            
            if data.empty:
                return []
            
            # Analyze component risks
            component_counts = data['Components'].value_counts()
            alerts = []
            
            for component, bug_count in component_counts.items():
                alert = self._evaluate_component_risk(
                    project_key, project_name, component, bug_count
                )
                if alert:
                    alerts.append(alert)
            
            return alerts
            
        except Exception as e:
            print(f"    ❌ Error analyzing {project_name}: {e}")
            return []
    
    def _evaluate_component_risk(self, project_key, project_name, component, bug_count):
        """Evaluate if a component exceeds risk thresholds"""
        alert_key = f"{project_key}_{component}"
        
        # Check if we've already alerted for this component recently
        if self._is_alert_on_cooldown(alert_key):
            return None
        
        alert_level = None
        risk_color = None
        
        if bug_count >= AlertConfig.URGENT_RISK_THRESHOLD:
            alert_level = "🚨 URGENT"
            risk_color = "#FF0000"  # Red
        elif bug_count >= AlertConfig.CRITICAL_RISK_THRESHOLD:
            alert_level = "⚠️ CRITICAL"
            risk_color = "#FF6600"  # Orange-Red
        elif bug_count >= AlertConfig.HIGH_RISK_THRESHOLD:
            alert_level = "⚡ HIGH RISK"
            risk_color = "#FFAA00"  # Orange
        
        if alert_level:
            alert = {
                'project_key': project_key,
                'project_name': project_name,
                'component': component,
                'bug_count': bug_count,
                'alert_level': alert_level,
                'risk_color': risk_color,
                'timestamp': datetime.now(),
                'recommendations': self._get_recommendations(bug_count)
            }
            
            # Record this alert to prevent spam
            self.alert_history[alert_key] = datetime.now()
            
            return alert
        
        return None
    
    def _is_alert_on_cooldown(self, alert_key):
        """Check if we've sent an alert for this component recently"""
        if alert_key not in self.alert_history:
            return False
        
        last_alert_time = self.alert_history[alert_key]
        cooldown_threshold = datetime.now() - timedelta(hours=AlertConfig.ALERT_COOLDOWN_HOURS)
        
        return last_alert_time > cooldown_threshold
    
    def _get_recommendations(self, bug_count):
        """Get recommendations based on bug count"""
        if bug_count >= AlertConfig.URGENT_RISK_THRESHOLD:
            return [
                "🚨 IMMEDIATE ACTION REQUIRED",
                "Consider emergency code review and testing",
                "Assign dedicated resources to this component",
                "Investigate root causes and implement fixes",
                "Consider rolling back recent changes if possible"
            ]
        elif bug_count >= AlertConfig.CRITICAL_RISK_THRESHOLD:
            return [
                "⚠️ Prioritize this component for immediate attention",
                "Increase testing coverage and code review",
                "Assign senior developers to investigate",
                "Consider refactoring if pattern persists"
            ]
        else:
            return [
                "⚡ Monitor closely and increase testing",
                "Review recent code changes",
                "Consider additional automated tests"
            ]
    
    def _send_notifications(self, alerts):
        """Send notifications via configured channels"""
        if AlertConfig.EMAIL_ENABLED and AlertConfig.EMAIL_RECIPIENTS:
            self._send_email_alerts(alerts)
        
        if AlertConfig.SLACK_ENABLED and AlertConfig.SLACK_WEBHOOK_URL:
            self._send_slack_alerts(alerts)
    
    def _send_email_alerts(self, alerts):
        """Send email notifications"""
        try:
            # Group alerts by project for cleaner emails
            projects_with_alerts = {}
            for alert in alerts:
                project = alert['project_name']
                if project not in projects_with_alerts:
                    projects_with_alerts[project] = []
                projects_with_alerts[project].append(alert)
            
            for project_name, project_alerts in projects_with_alerts.items():
                self._send_project_email(project_name, project_alerts)
                
        except Exception as e:
            print(f"❌ Error sending email alerts: {e}")
    
    def _send_project_email(self, project_name, alerts):
        """Send email for a specific project's alerts"""
        try:
            # Create email content
            subject = f"🚨 Risk Alert: {project_name} - {len(alerts)} Component(s) Exceed Thresholds"
            
            html_content = self._generate_email_html(project_name, alerts)
            
            # Create email message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = AlertConfig.EMAIL_USERNAME
            msg['To'] = ', '.join(AlertConfig.EMAIL_RECIPIENTS)
            
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(AlertConfig.SMTP_SERVER, AlertConfig.SMTP_PORT) as server:
                server.starttls()
                server.login(AlertConfig.EMAIL_USERNAME, AlertConfig.EMAIL_PASSWORD)
                server.send_message(msg)
            
            print(f"  📧 Email alert sent for {project_name}")
            
        except Exception as e:
            print(f"  ❌ Error sending email for {project_name}: {e}")
    
    def _generate_email_html(self, project_name, alerts):
        """Generate HTML content for email alerts"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Sort alerts by severity
        alerts.sort(key=lambda x: x['bug_count'], reverse=True)
        
        alert_rows = []
        for alert in alerts:
            recommendations_html = "<ul>" + "".join([
                f"<li>{rec}</li>" for rec in alert['recommendations']
            ]) + "</ul>"
            
            alert_rows.append(f"""
            <tr style="border-bottom: 1px solid #ddd;">
                <td style="padding: 12px; font-weight: bold; color: {alert['risk_color']}">
                    {alert['alert_level']}
                </td>
                <td style="padding: 12px;">{alert['component']}</td>
                <td style="padding: 12px; text-align: center; font-size: 18px; font-weight: bold; color: {alert['risk_color']}">
                    {alert['bug_count']}
                </td>
                <td style="padding: 12px; font-size: 12px;">
                    {recommendations_html}
                </td>
            </tr>
            """)
        
        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
                .container {{ max-width: 800px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                .header {{ background-color: #e74c3c; color: white; padding: 20px; border-radius: 8px 8px 0 0; margin: -20px -20px 20px -20px; }}
                .alert-table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                .alert-table th {{ background-color: #34495e; color: white; padding: 12px; text-align: left; }}
                .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚨 Bug Risk Alert: {project_name}</h1>
                    <p>Risk threshold violations detected at {timestamp}</p>
                </div>
                
                <p><strong>Summary:</strong> {len(alerts)} component(s) in {project_name} have exceeded risk thresholds and require immediate attention.</p>
                
                <table class="alert-table">
                    <thead>
                        <tr>
                            <th>Alert Level</th>
                            <th>Component</th>
                            <th>Bug Count</th>
                            <th>Recommendations</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join(alert_rows)}
                    </tbody>
                </table>
                
                <div class="footer">
                    <p><strong>Risk Thresholds:</strong></p>
                    <ul>
                        <li>🚨 URGENT: {AlertConfig.URGENT_RISK_THRESHOLD}+ bugs</li>
                        <li>⚠️ CRITICAL: {AlertConfig.CRITICAL_RISK_THRESHOLD}+ bugs</li>
                        <li>⚡ HIGH RISK: {AlertConfig.HIGH_RISK_THRESHOLD}+ bugs</li>
                    </ul>
                    <p>This alert was generated automatically by the JIRA Bug Risk Analysis System.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_content
    
    def _send_slack_alerts(self, alerts):
        """Send Slack notifications"""
        try:
            # Group alerts by project
            projects_with_alerts = {}
            for alert in alerts:
                project = alert['project_name']
                if project not in projects_with_alerts:
                    projects_with_alerts[project] = []
                projects_with_alerts[project].append(alert)
            
            for project_name, project_alerts in projects_with_alerts.items():
                self._send_slack_message(project_name, project_alerts)
                
        except Exception as e:
            print(f"❌ Error sending Slack alerts: {e}")
    
    def _send_slack_message(self, project_name, alerts):
        """Send Slack message for project alerts"""
        try:
            # Sort alerts by severity
            alerts.sort(key=lambda x: x['bug_count'], reverse=True)
            
            # Create Slack message
            alert_text = f"🚨 *Risk Alert: {project_name}*\n"
            alert_text += f"_{len(alerts)} component(s) exceed risk thresholds_\n\n"
            
            for alert in alerts:
                alert_text += f"{alert['alert_level']} *{alert['component']}*: {alert['bug_count']} bugs\n"
            
            alert_text += f"\n📊 <http://localhost:5001|View Dashboard> for detailed analysis"
            
            payload = {
                "channel": AlertConfig.SLACK_CHANNEL,
                "username": "Bug Risk Monitor",
                "icon_emoji": ":warning:",
                "text": alert_text
            }
            
            response = requests.post(AlertConfig.SLACK_WEBHOOK_URL, json=payload)
            
            if response.status_code == 200:
                print(f"  💬 Slack alert sent for {project_name}")
            else:
                print(f"  ❌ Slack alert failed for {project_name}: {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ Error sending Slack message for {project_name}: {e}")

def setup_monitoring():
    """Setup monitoring with configuration instructions"""
    print("🔧 Risk Threshold Monitoring Setup")
    print("=" * 50)
    
    print("\n📋 Current Configuration:")
    print(f"  • High Risk Threshold: {AlertConfig.HIGH_RISK_THRESHOLD} bugs")
    print(f"  • Critical Risk Threshold: {AlertConfig.CRITICAL_RISK_THRESHOLD} bugs")
    print(f"  • Urgent Risk Threshold: {AlertConfig.URGENT_RISK_THRESHOLD} bugs")
    print(f"  • Check Interval: {AlertConfig.CHECK_INTERVAL_HOURS} hours")
    print(f"  • Alert Cooldown: {AlertConfig.ALERT_COOLDOWN_HOURS} hours")
    
    print(f"\n📧 Email Notifications: {'✅ Enabled' if AlertConfig.EMAIL_ENABLED else '❌ Disabled'}")
    if AlertConfig.EMAIL_ENABLED:
        print(f"  • Recipients: {len(AlertConfig.EMAIL_RECIPIENTS)} configured")
    
    print(f"\n💬 Slack Notifications: {'✅ Enabled' if AlertConfig.SLACK_ENABLED else '❌ Disabled'}")
    if AlertConfig.SLACK_ENABLED:
        print(f"  • Channel: {AlertConfig.SLACK_CHANNEL}")
    
    if not AlertConfig.EMAIL_ENABLED and not AlertConfig.SLACK_ENABLED:
        print("\n⚠️  No notification channels configured!")
        print("Edit alert_system.py to configure email or Slack notifications")

def run_monitoring():
    """Run the monitoring system once"""
    alert_system = RiskAlertSystem()
    return alert_system.check_all_projects()

def test_notifications():
    """Test notification system with sample data"""
    print("🧪 Testing notification system...")
    
    # Create sample alerts for testing
    test_alerts = [
        {
            'project_key': 'TEST',
            'project_name': 'Test Project',
            'component': 'Test Component',
            'bug_count': 12,
            'alert_level': '🚨 URGENT',
            'risk_color': '#FF0000',
            'timestamp': datetime.now(),
            'recommendations': [
                "🚨 IMMEDIATE ACTION REQUIRED",
                "Consider emergency code review and testing"
            ]
        }
    ]
    
    alert_system = RiskAlertSystem()
    alert_system._send_notifications(test_alerts)
    print("✅ Test complete - check your configured notification channels")

if __name__ == "__main__":
    print("🚨 JIRA Bug Risk Alert System")
    print("=" * 40)
    print("1. setup_monitoring() - View current configuration")
    print("2. run_monitoring() - Run monitoring once")
    print("3. test_notifications() - Test notification channels")
    print("\nTo configure alerts, edit the AlertConfig class in this file.") 