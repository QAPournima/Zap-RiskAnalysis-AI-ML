"""
Historical Trend Analysis Module
Analyzes component risk trends over time and generates insights
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import numpy as np
import io
import base64
from IPython.display import display, HTML
from ..utils.jira_utils import connect_to_jira
from ..config import JIRA_CONFIG

class TrendAnalyzer:
    """Analyze component risk trends over time"""
    
    def __init__(self):
        self.jira = connect_to_jira()
        
    def fetch_historical_data(self, project_key, months=6):
        """Fetch bug data for multiple time periods"""
        print(f"📊 Fetching {months} months of historical data for {project_key}...")
        
        historical_data = []
        current_date = datetime.now()
        
        for month_offset in range(months):
            # Calculate proper calendar month boundaries
            if month_offset == 0:
                # Current month: from start of month to today
                end_date = current_date
                start_date = datetime(current_date.year, current_date.month, 1)
                month_label = current_date.strftime('%Y-%m')
            else:
                # Previous months: full calendar months
                # Go back month_offset months from current month
                year = current_date.year
                month = current_date.month - month_offset
                
                # Handle year rollover
                while month <= 0:
                    month += 12
                    year -= 1
                
                # Start of target month
                start_date = datetime(year, month, 1)
                
                # End of target month (start of next month - 1 day)
                next_month = month + 1
                next_year = year
                if next_month > 12:
                    next_month = 1
                    next_year += 1
                
                end_date = datetime(next_year, next_month, 1) - timedelta(days=1)
                month_label = start_date.strftime('%Y-%m')
            
            print(f"  📅 Fetching data for {month_label}...")
            
            # Construct JQL query for specific month
            jql = (
                f'project = "{project_key}" AND '
                f'(type = "Bug" OR type = "Support Ticket") AND '
                f'created >= "{start_date.strftime("%Y-%m-%d")}" AND '
                f'created <= "{end_date.strftime("%Y-%m-%d")}" AND '
                f'"Environment[Select List (multiple choices)]" = {JIRA_CONFIG["ENVIRONMENT"]}'
            )
            
            try:
                issues = self.jira.search_issues(jql, maxResults=1000, 
                    fields="summary,status,created,components")
                
                monthly_data = {
                    'month': month_label,
                    'start_date': start_date,
                    'end_date': end_date,
                    'total_bugs': len(issues),
                    'component_data': self._process_components(issues),
                    'issues': issues
                }
                
                historical_data.append(monthly_data)
                print(f"    ✅ Found {len(issues)} bugs")
                
            except Exception as e:
                print(f"    ❌ Error fetching data for {month_label}: {e}")
                
        print(f"✅ Historical data collection complete!")
        return historical_data
    
    def _process_components(self, issues):
        """Process component data for a set of issues"""
        component_counts = {}
        
        for issue in issues:
            if hasattr(issue.fields, 'components') and issue.fields.components:
                for component in issue.fields.components:
                    component_name = component.name
                    component_counts[component_name] = component_counts.get(component_name, 0) + 1
        
        return component_counts
    
    def generate_trend_charts(self, project_key, historical_data, project_name):
        """Generate comprehensive trend visualizations"""
        if not historical_data:
            print("❌ No historical data available for trend analysis")
            return
        
        # Sort data by date
        historical_data.sort(key=lambda x: x['start_date'])
        
        # Generate multiple chart types
        self._create_overall_trend_chart(historical_data, project_name)
        self._create_component_trend_chart(historical_data, project_name)
        self._create_trend_summary_table(historical_data, project_name)
        
    def _create_overall_trend_chart(self, historical_data, project_name):
        """Create overall bug count trend chart"""
        months = [data['month'] for data in historical_data]
        bug_counts = [data['total_bugs'] for data in historical_data]
        
        plt.figure(figsize=(12, 6))
        plt.plot(months, bug_counts, marker='o', linewidth=2, markersize=8, color='#e74c3c')
        plt.title(f'📈 Overall Bug Trend - {project_name}', fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('Month', fontsize=12)
        plt.ylabel('Total Bugs', fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        
        # Add trend line
        x_numeric = range(len(months))
        z = np.polyfit(x_numeric, bug_counts, 1)
        p = np.poly1d(z)
        plt.plot(months, p(x_numeric), linestyle='--', alpha=0.8, color='#3498db', 
                label=f'Trend: {"↗️ Increasing" if z[0] > 0 else "↘️ Decreasing"}')
        
        plt.legend()
        plt.tight_layout()
        
        # Convert to base64 for display
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', dpi=150)
        plt.close()
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        buf.close()
        
        display(HTML(f"""
        <div style="text-align: center; margin: 20px 0;">
            <img src="data:image/png;base64,{img_base64}" style="max-width:100%; height:auto;" />
        </div>
        """))
    
    def _create_component_trend_chart(self, historical_data, project_name, top_n=5):
        """Create component-specific trend charts"""
        # Get top components across all months
        all_components = {}
        for data in historical_data:
            for component, count in data['component_data'].items():
                all_components[component] = all_components.get(component, 0) + count
        
        # Select top N components
        top_components = sorted(all_components.items(), key=lambda x: x[1], reverse=True)[:top_n]
        
        if not top_components:
            print("❌ No component data available for trend analysis")
            return
        
        plt.figure(figsize=(14, 8))
        
        months = [data['month'] for data in historical_data]
        colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c', '#e67e22']
        
        for i, (component, _) in enumerate(top_components):
            component_trends = []
            for data in historical_data:
                count = data['component_data'].get(component, 0)
                component_trends.append(count)
            
            plt.plot(months, component_trends, marker='o', linewidth=2, 
                    markersize=6, label=component, color=colors[i % len(colors)])
        
        plt.title(f'📊 Component Risk Trends - {project_name}', fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('Month', fontsize=12)
        plt.ylabel('Bug Count', fontsize=12)
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Convert to base64 for display
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', dpi=150)
        plt.close()
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        buf.close()
        
        display(HTML(f"""
        <div style="text-align: center; margin: 20px 0;">
            <img src="data:image/png;base64,{img_base64}" style="max-width:100%; height:auto;" />
        </div>
        """))
    
    def _create_trend_summary_table(self, historical_data, project_name):
        """Create trend analysis summary table"""
        # Calculate trends for each component
        all_components = set()
        for data in historical_data:
            all_components.update(data['component_data'].keys())
        
        trend_summary = []
        
        for component in all_components:
            counts = []
            for data in historical_data:
                counts.append(data['component_data'].get(component, 0))
            
            if len(counts) >= 2:
                # Calculate trend
                x = range(len(counts))
                z = np.polyfit(x, counts, 1) if len(counts) > 1 else [0, 0]
                trend_slope = z[0]
                
                total_bugs = sum(counts)
                avg_bugs = total_bugs / len(counts)
                
                if trend_slope > 0.5:
                    trend_direction = "📈 Increasing"
                    trend_color = "#e74c3c"  # Red
                elif trend_slope < -0.5:
                    trend_direction = "📉 Decreasing"
                    trend_color = "#2ecc71"  # Green
                else:
                    trend_direction = "➡️ Stable"
                    trend_color = "#f39c12"  # Orange
                
                trend_summary.append({
                    'component': component,
                    'total_bugs': total_bugs,
                    'avg_bugs': round(avg_bugs, 1),
                    'trend_direction': trend_direction,
                    'trend_slope': round(trend_slope, 2),
                    'trend_color': trend_color
                })
        
        # Sort by total bugs
        trend_summary.sort(key=lambda x: x['total_bugs'], reverse=True)
        
        # Create HTML table
        table_rows = []
        for i, trend in enumerate(trend_summary[:10]):  # Top 10 components
            table_rows.append(f"""
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">{i+1}</td>
                <td style="padding: 8px; border: 1px solid #ddd;">{trend['component']}</td>
                <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">{trend['total_bugs']}</td>
                <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">{trend['avg_bugs']}</td>
                <td style="padding: 8px; border: 1px solid #ddd; text-align: center; color: {trend['trend_color']}; font-weight: bold;">
                    {trend['trend_direction']}
                </td>
                <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">{trend['trend_slope']}</td>
            </tr>
            """)
        
        trend_table_html = f"""
        <div style="background: #111; border-radius: 12px; padding: 18px 28px; margin: 24px 0; box-shadow: 0 2px 8px #222;">
            <h2 style="margin-top:0; color:#ffe066;">📈 <b>Component Trend Analysis - {project_name}</b></h2>
            <p style="color: #fff; margin-bottom: 20px;">
                Trend analysis over the last 6 months showing which components are improving (📉) or deteriorating (📈).
            </p>
        </div>
        
        <div style="display: flex; flex-direction: column; align-items: center;">
            <table style="border-collapse: collapse; width: 100%; max-width: 900px; margin: 0 auto;">
                <thead>
                    <tr style="background-color: #1a1368; color: white; font-size: 1.1em;">
                        <th style="padding: 12px; border: 1px solid #ddd;">Rank</th>
                        <th style="padding: 12px; border: 1px solid #ddd;">Component</th>
                        <th style="padding: 12px; border: 1px solid #ddd;">Total Bugs</th>
                        <th style="padding: 12px; border: 1px solid #ddd;">Avg/Month</th>
                        <th style="padding: 12px; border: 1px solid #ddd;">Trend</th>
                        <th style="padding: 12px; border: 1px solid #ddd;">Slope</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join(table_rows)}
                </tbody>
            </table>
            <p style="color:#888; font-size:0.95em; margin-top:18px;">
                📈 Increasing = Getting worse | 📉 Decreasing = Getting better | ➡️ Stable = No significant change
            </p>
        </div>
        """
        
        display(HTML(trend_table_html))
    
    def identify_risk_patterns(self, historical_data):
        """Identify patterns and insights from historical data"""
        insights = {
            'improving_components': [],
            'deteriorating_components': [],
            'stable_components': [],
            'overall_trend': None,
            'seasonal_patterns': [],
            'recommendations': []
        }
        
        # Analyze overall trend
        total_bugs_per_month = [data['total_bugs'] for data in historical_data]
        if len(total_bugs_per_month) >= 2:
            x = range(len(total_bugs_per_month))
            z = np.polyfit(x, total_bugs_per_month, 1)
            
            if z[0] > 1:
                insights['overall_trend'] = "📈 Bug count is increasing over time"
                insights['recommendations'].append("Consider increasing testing resources and code review processes")
            elif z[0] < -1:
                insights['overall_trend'] = "📉 Bug count is decreasing over time" 
                insights['recommendations'].append("Good progress! Continue current quality practices")
            else:
                insights['overall_trend'] = "➡️ Bug count is stable"
                insights['recommendations'].append("Maintain current quality processes")
        
        return insights

def analyze_project_trends(project_key, project_name, months=6):
    """Main function to analyze trends for a project"""
    print(f"🔍 Starting trend analysis for {project_name}...")
    
    try:
        analyzer = TrendAnalyzer()
        
        # Fetch historical data
        historical_data = analyzer.fetch_historical_data(project_key, months)
        
        if not historical_data:
            print("❌ No historical data available")
            return None
        
        # Generate trend charts
        analyzer.generate_trend_charts(project_key, historical_data, project_name)
        
        # Identify patterns and insights
        insights = analyzer.identify_risk_patterns(historical_data)
        
        print("✅ Trend analysis complete!")
        return {
            'historical_data': historical_data,
            'insights': insights
        }
        
    except Exception as e:
        print(f"❌ Error in trend analysis: {e}")
        return None

# Helper function for notebooks
def setup_trend_analysis(project_key, display_config=False):
    """Setup trend analysis for notebook usage"""
    from ..config import PROJECT_MAPPINGS
    
    if project_key not in PROJECT_MAPPINGS:
        raise ValueError(f"Project key '{project_key}' not found in configuration")
    
    project_info = PROJECT_MAPPINGS[project_key]
    
    if display_config:
        config_html = f"""
        <div style="background: #f8f9fa; border-left: 4px solid #007bff; padding: 15px; margin: 15px 0;">
            <h4 style="color: #007bff; margin-top: 0;">📊 Trend Analysis Configuration</h4>
            <p><strong>Project:</strong> {project_info['name']}</p>
            <p><strong>JIRA Key:</strong> {project_key}</p>
            <p><strong>Analysis Period:</strong> Last 6 months</p>
            <p><strong>Environment:</strong> {JIRA_CONFIG['ENVIRONMENT']}</p>
        </div>
        """
        display(HTML(config_html))
    
    return {
        'project_key': project_key,
        'project_info': project_info
    } 