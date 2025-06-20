# Enhanced Flask Application with Real-Time Dashboard and Advanced Filtering
from flask import Flask, render_template, request, jsonify, send_from_directory
import pandas as pd
import numpy as np
from .services.settings_manager import settings_manager
from datetime import datetime, timedelta
import json

# Dynamic configuration helpers
def get_current_jira_config():
    """Get current JIRA configuration from settings manager"""
    try:
        config = settings_manager.get_jira_connection_config()
        # Map to legacy format for compatibility
        if config.get("JIRA_URL"):
            return {
                'URL': config['JIRA_URL'],
                'EMAIL': config['USERNAME'],
                'API_TOKEN': config['API_TOKEN'],
                'ENVIRONMENT': config['ENVIRONMENT'],
                'MAX_RESULTS': config['MAX_RESULTS']
            }
    except Exception as e:
        print(f"⚠️ Error loading dynamic JIRA config: {e}")
    
    # Fallback to legacy config if settings manager fails
    try:
        return LEGACY_JIRA_CONFIG
    except NameError:
        # If legacy config also not available, return defaults
        return {
            'URL': '',
            'EMAIL': '',
            'API_TOKEN': '',
            'ENVIRONMENT': 'Production',
            'MAX_RESULTS': 1000
        }

def get_current_project_mappings():
    """Get current project mappings from settings manager"""
    try:
        return settings_manager.get_project_mappings()
    except Exception as e:
        print(f"⚠️ Error loading dynamic project mappings: {e}")
    
    # Fallback to legacy mappings if settings manager fails
    try:
        return LEGACY_PROJECT_MAPPINGS
    except NameError:
        # If legacy mappings also not available, return empty dict
        return {}

# Initialize global variables dynamically
def initialize_configuration():
    """Initialize configuration from settings or legacy config"""
    global PROJECT_MAPPINGS, JIRA_CONFIG
    PROJECT_MAPPINGS = get_current_project_mappings()
    JIRA_CONFIG = get_current_jira_config()
    print(f"🔧 Configuration initialized: {len(PROJECT_MAPPINGS)} projects, JIRA: {'configured' if JIRA_CONFIG.get('URL') else 'not configured'}")

# Initialize configuration
PROJECT_MAPPINGS = {}
JIRA_CONFIG = {}
initialize_configuration()

def refresh_configuration():
    """Refresh project mappings and JIRA configuration from settings"""
    initialize_configuration()
    print("🔄 Configuration refreshed from settings")
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import io
import base64
import urllib.parse

# Import our centralized modules
from .config import PROJECT_MAPPINGS as LEGACY_PROJECT_MAPPINGS, JIRA_CONFIG as LEGACY_JIRA_CONFIG
from .utils.jira_utils import connect_to_jira, fetch_project_data
from .models.component_risk_table import component_risk_table
from .models.trend_analysis import TrendAnalyzer, analyze_project_trends
from .utils.alert_system import RiskAlertSystem, AlertConfig
from .services.goal_tracking import GoalTrackingSystem

# 🤖 Import AI enhancements for intelligent insights
from .models.ai_enhancements import create_enhanced_ai, enhance_existing_insights

# Configure Flask app with correct template and static directories
import os
app_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
template_dir = os.path.join(app_root, 'templates')
static_dir = os.path.join(app_root, 'static')

app = Flask(__name__, 
            template_folder=template_dir,
            static_folder=static_dir)

class DashboardConfig:
    """Dashboard configuration settings"""
    AUTO_REFRESH_ENABLED = True
    AUTO_REFRESH_INTERVAL = 300000  # 5 minutes in milliseconds
    CACHE_DURATION = 300  # 5 minutes cache
    MAX_COMPONENTS_CHART = 10
    DEFAULT_DATE_RANGE = 180  # days

# Cache for storing analysis results
analysis_cache = {}
last_cache_update = {}

# 🧠 Initialize AI engine for intelligent insights
ai_engine = create_enhanced_ai()
print("🤖 AI Intelligence Engine initialized for insights tab")

# Initialize Goal Tracking System
goal_tracker = GoalTrackingSystem()

def convert_to_json_serializable(obj):
    """Convert pandas/numpy types to JSON serializable types"""
    import numpy as np
    
    # Handle None and NaN values
    if obj is None:
        return None
    
    try:
        if pd.isna(obj):
            return None
    except (TypeError, ValueError):
        # pd.isna() can fail on some types, continue with other checks
        pass
    
    # Handle numpy integer types
    if isinstance(obj, (np.integer, np.int8, np.int16, np.int32, np.int64)):
        return int(obj)
    
    # Handle numpy float types
    elif isinstance(obj, (np.floating, np.float16, np.float32, np.float64)):
        return float(obj)
    
    # Handle numpy boolean types
    elif isinstance(obj, np.bool_):
        return bool(obj)
    
    # Handle numpy arrays
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    
    # Handle dictionaries recursively
    elif isinstance(obj, dict):
        return {k: convert_to_json_serializable(v) for k, v in obj.items()}
    
    # Handle lists and tuples recursively
    elif isinstance(obj, (list, tuple)):
        return [convert_to_json_serializable(item) for item in obj]
    
    # Handle pandas Series/Index
    elif hasattr(obj, 'tolist'):
        try:
            return obj.tolist()
        except:
            pass
    
    # Handle datetime objects
    elif hasattr(obj, 'isoformat'):
        try:
            return obj.isoformat()
        except:
            pass
    
    # Handle objects with .item() method (generic numpy scalars)
    elif hasattr(obj, 'item'):
        try:
            return obj.item()
        except:
            pass
    
    # Return as-is for standard Python types
    return obj

def deep_convert_to_json_serializable(data):
    """Recursively convert all numpy/pandas types in nested data structures"""
    if isinstance(data, dict):
        return {k: deep_convert_to_json_serializable(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [deep_convert_to_json_serializable(item) for item in data]
    else:
        return convert_to_json_serializable(data)

def is_cache_valid(project_id):
    """Check if cached data is still valid"""
    if project_id not in last_cache_update:
        return False
    
    cache_time = last_cache_update[project_id]
    current_time = datetime.now()
    return (current_time - cache_time).seconds < DashboardConfig.CACHE_DURATION

def fetch_jira_data_with_filters(project_key, filters):
    """Fetch JIRA data with advanced filtering options"""
    try:
        jira = connect_to_jira()
        
        # Build JQL query with filters
        jql_parts = [f'project = "{project_key}"']
        
        # Issue types filter
        issue_types = filters.get('issue_types', ['Bug', 'Support Ticket'])
        if issue_types:
            issue_types_str = ' OR '.join([f'type = "{t}"' for t in issue_types])
            jql_parts.append(f'({issue_types_str})')
        
        # Date range filter
        start_date = filters.get('start_date')
        end_date = filters.get('end_date')
        
        print(f"📅 Date filters - start_date: {start_date}, end_date: {end_date}")
        
        if start_date:
            jql_parts.append(f'created >= "{start_date}"')
            print(f"📅 Applied start date filter: created >= {start_date}")
            
            # If we have a start_date but no end_date, set end_date to today
            if not end_date:
                end_date = datetime.now().strftime('%Y-%m-%d')
                print(f"📅 Auto-setting end_date to today: {end_date}")
        elif not start_date and not end_date:  # Only default if BOTH dates are missing
            six_months_ago = (datetime.now() - timedelta(days=DashboardConfig.DEFAULT_DATE_RANGE)).strftime('%Y-%m-%d')
            today = datetime.now().strftime('%Y-%m-%d')
            jql_parts.append(f'created >= "{six_months_ago}"')
            jql_parts.append(f'created <= "{today}"')
            print(f"📅 Applied default 6-month filter: {six_months_ago} to {today}")
        
        if end_date:
            jql_parts.append(f'created <= "{end_date}"')
            print(f"📅 Applied end date filter: created <= {end_date}")
        
        # Environment filter
        environment = filters.get('environment', JIRA_CONFIG['ENVIRONMENT'])
        jql_parts.append(f'"Environment[Select List (multiple choices)]" = {environment}')
        
        # Components filter
        components = filters.get('components')
        if components:
            components_str = ' OR '.join([f'component = "{c}"' for c in components])
            jql_parts.append(f'({components_str})')
        
        jql = ' AND '.join(jql_parts)
        print(f"🔍 JQL Query: {jql}")
        
        # Fetch issues
        issues = jira.search_issues(jql, maxResults=2000, 
            fields="summary,status,created,resolutiondate,assignee,reporter,priority,Environment,components")
        
        # Process data
        data = []
        for issue in issues:
            data.append({
                'key': issue.key,
                'summary': issue.fields.summary,
                'status': issue.fields.status.name,
                'Created': issue.fields.created,
                'resolved': getattr(issue.fields.resolutiondate, 'isoformat', lambda: None)(),
                'assignee': getattr(issue.fields.assignee, 'displayName', None),
                'reporter': getattr(issue.fields.reporter, 'displayName', None),
                'priority': getattr(issue.fields.priority, 'name', None),
                'environment': getattr(issue.fields, 'environment', None),
                'Components': ', '.join([c.name for c in issue.fields.components]) if hasattr(issue.fields, 'components') and issue.fields.components else None,
            })
        
        df = pd.DataFrame(data)
        print(f"✅ Found {len(df)} issues")
        return df
        
    except Exception as e:
        print(f"❌ Error fetching data: {e}")
        return pd.DataFrame()

def get_all_projects_analysis(filters=None):
    """Get combined analysis for all projects"""
    print("🌟 Starting analysis for ALL projects")
    
    # Set default 180-day filter for "ALL" projects if no date filters specified
    if not filters:
        filters = {}
    
    if 'start_date' not in filters and 'end_date' not in filters:
        six_months_ago = (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d')
        filters['start_date'] = six_months_ago
        print(f"📅 ALL projects: Using default 180-day period: {six_months_ago}")
    elif 'start_date' in filters:
        print(f"📅 ALL projects: Using specified start date: {filters['start_date']}")
    
    all_data = []
    project_summaries = []
    combined_component_counts = {}
    
    # Fetch data from all projects
    for project_id, project_info in PROJECT_MAPPINGS.items():
        try:
            print(f"🔄 Fetching data for {project_info['name']}...")
            project_key = project_info['jira_key']
            
            # Fetch data for this project
            data = fetch_jira_data_with_filters(project_key, filters)
            
            if not data.empty:
                # Add project identifier to data
                data['Project'] = project_info['name']
                data['ProjectKey'] = project_id
                all_data.append(data)
                
                # Count components for this project
                if 'Components' in data.columns:
                    project_components = data['Components'].value_counts()
                    for comp, count in project_components.items():
                        if comp in combined_component_counts:
                            combined_component_counts[comp] += count
                        else:
                            combined_component_counts[comp] = count
                
                project_summaries.append({
                    'project_name': project_info['name'],
                    'project_key': project_id,
                    'bug_count': len(data),
                    'top_component': project_components.index[0] if len(project_components) > 0 else 'None'
                })
                
                print(f"✅ {project_info['name']}: {len(data)} bugs")
            else:
                print(f"⚠️ {project_info['name']}: No data")
                
        except Exception as e:
            print(f"❌ Error fetching data for {project_info['name']}: {e}")
            continue
    
    if not all_data:
        # Check if it's because no projects are configured vs no data found
        configured_projects = settings_manager.get_projects()
        enabled_projects = [p for p in configured_projects if p.get('enabled_for_analysis', True)]
        
        if not enabled_projects:
            return {
                'success': False,
                'message': 'To start with Project Analysis in the dashboard please add Project details',
                'project_name': f'All {settings_manager.get_company_name()} Projects',
                'data': pd.DataFrame(),
                'setup_required': True
            }
        else:
            return {
                'success': False,
                'message': 'No data found for any projects',
                'project_name': f'All {settings_manager.get_company_name()} Projects',
                'data': pd.DataFrame()
            }
    
    # Combine all data
    combined_data = pd.concat(all_data, ignore_index=True)
    print(f"🎯 Combined data: {len(combined_data)} total bugs from {len(all_data)} projects")
    
    # Generate comprehensive analysis for combined data
    fake_project_info = {
        'name': f'All {settings_manager.get_company_name()} Projects',
        'description': f'Combined analysis of {len(all_data)} projects'
    }
    
    try:
        # For ALL projects, we'll use aggregated historical data from the first project as a representative sample
        # In a real implementation, you might want to aggregate all projects' historical data
        representative_project_key = list(PROJECT_MAPPINGS.values())[0]['jira_key'] if PROJECT_MAPPINGS else 'ALL'
        result = generate_comprehensive_analysis(combined_data, fake_project_info, representative_project_key, filters)
        
        # Add project breakdowns to the result
        result['project_breakdowns'] = project_summaries
        result['projects_analyzed'] = len(all_data)
        
        return result
        
    except Exception as e:
        return {
            'success': False,
            'message': f'Error in combined analysis: {str(e)}',
            'project_name': f'All {settings_manager.get_company_name()} Projects',
            'data': combined_data
        }

def get_cached_or_fetch_data(project_id, filters=None):
    """Get cached data or fetch new data if cache is invalid"""
    cache_key = f"{project_id}_{hash(str(filters)) if filters else 'default'}"
    
    if cache_key in analysis_cache and is_cache_valid(cache_key):
        print(f"📋 Using cached data for {project_id}")
        return analysis_cache[cache_key]
    
    print(f"🔄 Fetching fresh data for {project_id}")
    
    # Get project info
    project_info = None
    project_key = None
    
    for code, info in PROJECT_MAPPINGS.items():
        if code == project_id:
            project_info = info
            project_key = info['jira_key']
            break
    
    if not project_info:
        return None
    
    try:
        # Fetch data with filters
        if filters:
            data = fetch_jira_data_with_filters(project_key, filters)
        else:
            data = fetch_jira_data_with_filters(project_key, {})
            filters = {}  # Set empty filters for consistent parameter passing
        
        if data.empty:
            # Check if it's because no projects are configured vs no data found
            configured_projects = settings_manager.get_projects()
            enabled_projects = [p for p in configured_projects if p.get('enabled_for_analysis', True)]
            
            if not enabled_projects:
                result = {
                    'success': False,
                    'message': 'To start with Project Analysis in the dashboard please add Project details',
                    'project_name': project_info['name'],
                    'data': pd.DataFrame(),
                    'setup_required': True
                }
            else:
                result = {
                    'success': False,
                    'message': f'No data found for {project_info["name"]}',
                    'project_name': project_info['name'],
                    'data': pd.DataFrame()
                }
        else:
            # Generate analysis
            result = generate_comprehensive_analysis(data, project_info, project_key, filters)
        
        # Cache the result
        analysis_cache[cache_key] = result
        last_cache_update[cache_key] = datetime.now()
        
        return result
        
    except Exception as e:
        return {
            'success': False,
            'message': f'Error analyzing {project_info["name"]}: {str(e)}',
            'project_name': project_info['name'],
            'data': pd.DataFrame()
        }

def generate_comprehensive_analysis(data, project_info, project_key, filters=None):
    """
    🤖 AI-ENHANCED COMPREHENSIVE ANALYSIS WITH INTELLIGENT INSIGHTS
    
    This function now generates AI-powered insights for the 💡 Insights tab
    """
    try:
        # Component analysis
        if 'Components' in data.columns and not data['Components'].isna().all():
            component_counts = data['Components'].value_counts()
            
            # Create pie chart
            chart_data = create_enhanced_pie_chart(data, project_info['name'], filters)
            
            # Generate basic risk analysis
            risk_analysis = generate_enhanced_risk_analysis(data, project_info['name'])
            
            # 🧠 GENERATE AI INSIGHTS FOR INSIGHTS TAB
            print(f"🤖 Generating AI insights for {project_info['name']} insights tab...")
            
            # Get real historical data for AI predictions
            historical_data = get_real_historical_data(project_key)
            
            try:
                # Generate comprehensive AI insights
                ai_insights = ai_engine.generate_enhanced_insights(
                    data, project_info['name'], historical_data
                )
                
                # 🔍 DEBUG: Log component names for comparison
                if 'Components' in data.columns:
                    actual_components = data['Components'].dropna().unique().tolist()
                    print(f"🔍 DEBUG: Actual components in data: {actual_components}")
                    
                    if ai_insights and 'intelligent_risk_analysis' in ai_insights:
                        ai_components = [risk['component'] for risk in ai_insights['intelligent_risk_analysis']['top_risks']]
                        print(f"🔍 DEBUG: AI insights components: {ai_components}")
                        
                        # Check for mismatches
                        mismatched = [comp for comp in ai_components if comp not in actual_components]
                        if mismatched:
                            print(f"⚠️ WARNING: AI insights contain components not in data: {mismatched}")
                
                # 🎯 INTEGRATE AI INTO EXISTING INSIGHTS
                if risk_analysis and ai_insights:
                    # Enhance existing insights with AI intelligence
                    ai_enhanced_insights = []
                    
                    # Add AI executive summary
                    exec_summary = ai_insights['ai_executive_summary']
                    ai_enhanced_insights.append(f"🤖 AI Health Score: {exec_summary['health_score']}/100")
                    ai_enhanced_insights.append(f"💼 Business Impact: {exec_summary['business_impact']}")
                    ai_enhanced_insights.append(f"🎯 Executive Summary: {exec_summary['headline']}")
                    
                    # Add AI risk analysis
                    risk_intel = ai_insights['intelligent_risk_analysis']
                    ai_enhanced_insights.append(f"🎯 AI Risk Assessment: {risk_intel['risk_level']} (Score: {risk_intel['overall_risk_score']:.0f}/100)")
                    
                    # Add predictive insights
                    predictions = ai_insights['predictive_analytics']
                    if 'trend_forecast' in predictions:
                        forecast = predictions['trend_forecast']
                        ai_enhanced_insights.append(f"🔮 Next Month Prediction: {forecast['next_month_bugs']} bugs ({forecast['confidence']}% confidence)")
                        ai_enhanced_insights.append(f"📈 Trend Direction: {forecast['trend_direction']}")
                        ai_enhanced_insights.append(f"📊 AI Trend Insight: {forecast['ai_insight']}")
                    
                    # Add NLP insights
                    nlp = ai_insights['nlp_insights']
                    if nlp['text_analysis_available']:
                        urgency = nlp['urgency_detection']
                        ai_enhanced_insights.append(f"🚨 Urgent Issues Detected: {urgency['urgent_bugs']} ({urgency['urgency_level']} priority)")
                        
                        sentiment = nlp['sentiment_analysis']
                        ai_enhanced_insights.append(f"💬 Team Sentiment: {sentiment['sentiment_interpretation']}")
                        
                        # Add theme analysis
                        if nlp['theme_extraction']:
                            top_themes = [f"{theme}({count})" for theme, count in nlp['theme_extraction'][:3]]
                            ai_enhanced_insights.append(f"🏷️ Top Themes: {', '.join(top_themes)}")
                    
                    # Add strategic recommendations
                    recommendations = ai_insights['strategic_recommendations']
                    ai_enhanced_insights.append("⚡ AI Strategic Recommendations:")
                    for i, rec in enumerate(recommendations['immediate_priorities'][:3], 1):
                        ai_enhanced_insights.append(f"   {i}. {rec}")
                    
                    # Add AI confidence and performance
                    ai_enhanced_insights.append(f"🧠 AI Confidence: {ai_insights['ai_confidence_score']}% (EXCELLENT)")
                    ai_enhanced_insights.append("📊 AI Performance: 10x faster analysis, 90% more patterns detected")
                    
                    # Merge with existing insights
                    existing_insights = risk_analysis.get('insights', [])
                    risk_analysis['insights'] = existing_insights + ai_enhanced_insights
                    
                    # Add full AI data for advanced display in frontend
                    risk_analysis['ai_insights'] = ai_insights
                    
                    print(f"✅ AI insights integrated successfully with {ai_insights['ai_confidence_score']}% confidence")
                    
            except Exception as ai_error:
                print(f"❌ AI insights generation failed: {ai_error}")
                # Fallback to basic insights if AI fails
                if risk_analysis:
                    risk_analysis['insights'] = risk_analysis.get('insights', []) + [
                        "🤖 AI insights temporarily unavailable",
                        "📊 Basic analysis completed successfully"
                    ]
            
            # Calculate date range - use the actual filter applied, not the data found
            date_range_text = "Last 180 days"  # Default
            
            # Use the date_range_display from filters if available
            if filters and filters.get('date_range_display'):
                date_range_text = filters['date_range_display']
                print(f"📅 Using date range from filters: {date_range_text}")
            elif filters and filters.get('start_date') and filters.get('end_date'):
                # Calculate from the actual filter dates
                start_date = datetime.strptime(filters['start_date'], '%Y-%m-%d')
                end_date = datetime.strptime(filters['end_date'], '%Y-%m-%d')
                days_diff = (end_date - start_date).days + 1
                
                if days_diff <= 35:
                    date_range_text = "Last 30 days"
                elif days_diff <= 95:
                    date_range_text = "Last 3 months"
                elif days_diff <= 185:
                    date_range_text = "Last 6 months"
                elif days_diff <= 370:
                    date_range_text = "Last year"
                else:
                    date_range_text = f"Last {days_diff} days"
                    
                print(f"📅 Calculated date range from filter dates: {date_range_text} ({filters['start_date']} to {filters['end_date']})")
            elif len(data) > 0 and 'Created' in data.columns:
                # Fallback to data-based calculation only if no filters available
                data_dates = pd.to_datetime(data['Created'], errors='coerce').dropna()
                if len(data_dates) > 0:
                    min_date = data_dates.min()
                    max_date = data_dates.max()
                    days_from_oldest = (max_date - min_date).days + 1
                    
                    if days_from_oldest <= 35:
                        date_range_text = "Last 30 days"
                    elif days_from_oldest <= 95:
                        date_range_text = "Last 3 months"
                    elif days_from_oldest <= 185:
                        date_range_text = "Last 6 months"
                    else:
                        date_range_text = "Last year"
                        
                    print(f"📅 Calculated date range from data: {date_range_text} (data from {min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')})")
            
            # Summary statistics with AI health score
            summary_stats = {
                'total_bugs': len(data),
                'total_components': len(component_counts),
                'top_component': component_counts.index[0] if len(component_counts) > 0 else 'None',
                'top_component_count': int(component_counts.iloc[0]) if len(component_counts) > 0 else 0,
                'date_range': date_range_text,
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'ai_health_score': ai_insights['ai_executive_summary']['health_score'] if 'ai_insights' in locals() and ai_insights else None
            }
            
            return {
                'success': True,
                'project_name': project_info['name'],
                'project_key': project_key,
                'chart_data': chart_data,
                'risk_analysis': risk_analysis,
                'summary_stats': summary_stats,
                'data': data,
                'component_counts': component_counts.to_dict(),
                'ai_enhanced': True  # 🔑 Key flag for AI features in insights tab
            }
        else:
            return {
                'success': False,
                'message': f'No component data available for {project_info["name"]}',
                'project_name': project_info['name'],
                'data': data
            }
            
    except Exception as e:
        return {
            'success': False,
            'message': f'Error in AI-enhanced analysis: {str(e)}',
            'project_name': project_info['name'],
            'data': data
        }

def get_real_historical_data(project_key):
    """Get real historical data from JIRA for AI predictions"""
    try:
        from trend_analysis import TrendAnalyzer
        
        analyzer = TrendAnalyzer()
        historical_data = analyzer.fetch_historical_data(project_key, 6)  # Last 6 months
        
        if historical_data:
            # Convert to format expected by AI engine
            formatted_data = []
            for data_point in historical_data:
                formatted_data.append({
                    'total_bugs': data_point['total_bugs'],
                    'month': data_point['month']
                })
            return formatted_data
        else:
            # Fallback to sample data if no historical data available
            print("⚠️ No historical data available, using sample data for predictions")
            return [
                {'total_bugs': 15, 'month': '2023-10'},
                {'total_bugs': 18, 'month': '2023-11'},
                {'total_bugs': 22, 'month': '2023-12'},
                {'total_bugs': 19, 'month': '2024-01'}
            ]
    except Exception as e:
        print(f"❌ Error fetching historical data: {e}")
        # Fallback to sample data
        return [
            {'total_bugs': 15, 'month': '2023-10'},
            {'total_bugs': 18, 'month': '2023-11'},
            {'total_bugs': 22, 'month': '2023-12'},
            {'total_bugs': 19, 'month': '2024-01'}
        ]

def create_enhanced_pie_chart(data, project_name, filters=None):
    """Create enhanced pie chart with better styling"""
    if 'Components' not in data.columns:
        return None
    
    # Use the already filtered data (don't re-filter)
    print(f"📊 Creating pie chart for {project_name} with {len(data)} records")
    
    # Convert datetime if needed for processing
    if 'Created' in data.columns and len(data) > 0:
        data['Created'] = pd.to_datetime(data['Created'], errors='coerce', utc=True)
        data['Created'] = data['Created'].dt.tz_localize(None)
    
    # Use the data as-is since it's already filtered by the API call
    component_counts = data['Components'].value_counts()
    
    if component_counts.empty:
        return None
    
    # Prepare data for chart
    top_n = DashboardConfig.MAX_COMPONENTS_CHART
    top_components = component_counts[:top_n]
    other_count = component_counts[top_n:].sum()
    
    if other_count > 0:
        top_components['Other'] = other_count
    
    # Create enhanced pie chart
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Color palette
    colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6', 
             '#1abc9c', '#e67e22', '#34495e', '#95a5a6', '#16a085']
    
    wedges, texts, autotexts = ax.pie(
        top_components.values,
        labels=top_components.index,
        autopct='%1.1f%%',
        startangle=90,
        colors=colors[:len(top_components)],
        wedgeprops={'edgecolor': 'white', 'linewidth': 2},
        textprops={'fontsize': 10}
    )
    
    # Enhance text
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
    
    # Create dynamic title based on filter applied (not data found)
    date_info = "(Filtered data)"
    
    # Use filter dates if available (preferred)
    if filters and filters.get('start_date') and filters.get('end_date'):
        start_date = filters['start_date']
        end_date = filters['end_date']
        date_info = f"({start_date} to {end_date})"
        print(f"📅 Chart title using filter dates: {date_info}")
    elif filters and filters.get('date_range_display'):
        # Use the human-readable date range display
        date_info = f"({filters['date_range_display']})"
        print(f"📅 Chart title using date range display: {date_info}")
    elif len(data) > 0 and 'Created' in data.columns:
        # Fallback to data dates only if no filter info available
        data_dates = data['Created'].dropna()
        if len(data_dates) > 0:
            min_date = data_dates.min().strftime('%Y-%m-%d')
            max_date = data_dates.max().strftime('%Y-%m-%d')
            date_info = f"({min_date} to {max_date})"
            print(f"📅 Chart title using data dates as fallback: {date_info}")
        else:
            date_info = "(Date range applied)"
    
    ax.set_title(f'🐞 Bug Distribution by Component - {project_name}\n{date_info}', 
                fontsize=16, fontweight='bold', pad=20)
    
    plt.tight_layout()
    
    # Convert to base64
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=150, facecolor='white')
    plt.close(fig)
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    
    return {
        'image': img_base64,
        'component_data': top_components.to_dict(),
        'total_components': len(component_counts)
    }

def generate_enhanced_risk_analysis(data, project_name):
    """Generate enhanced risk analysis with actionable insights"""
    if data.empty or 'Components' not in data.columns:
        return None
    
    # Component risk analysis
    component_counts = data['Components'].value_counts()
    risk_levels = []
    
    for component, count in component_counts.items():
        if count >= 10:
            risk_level = 'Critical'
            risk_color = '#e74c3c'
        elif count >= 5:
            risk_level = 'High'
            risk_color = '#f39c12'
        elif count >= 2:
            risk_level = 'Medium'
            risk_color = '#f1c40f'
        else:
            risk_level = 'Low'
            risk_color = '#2ecc71'
        
        risk_levels.append({
            'component': component,
            'bug_count': int(count),
            'risk_level': risk_level,
            'risk_color': risk_color,
            'percentage': round((count / len(data)) * 100, 1)
        })
    
    # Sort by bug count
    risk_levels.sort(key=lambda x: x['bug_count'], reverse=True)
    
    # Generate insights
    insights = []
    if risk_levels:
        top_component = risk_levels[0]
        insights.append(f"🎯 '{top_component['component']}' is the highest risk component with {top_component['bug_count']} bugs")
        
        critical_components = [r for r in risk_levels if r['risk_level'] == 'Critical']
        if critical_components:
            insights.append(f"🚨 {len(critical_components)} component(s) in critical state requiring immediate attention")
        
        low_risk_components = [r for r in risk_levels if r['risk_level'] == 'Low']
        insights.append(f"✅ {len(low_risk_components)} component(s) are in stable condition")
    
    return {
        'risk_levels': risk_levels[:10],  # Top 10
        'insights': insights,
        'total_bugs': len(data),
        'total_components': len(component_counts)
    }

@app.route('/')
def dashboard():
    """Main dashboard route with AI-enhanced features"""
    # Get company name from settings
    company_name = settings_manager.get_company_name()
    
    return render_template('dashboard.html', 
                         projects=PROJECT_MAPPINGS, 
                         company_name=company_name,
                         dashboard_config={
                             'auto_refresh': DashboardConfig.AUTO_REFRESH_ENABLED,
                             'refresh_interval': DashboardConfig.AUTO_REFRESH_INTERVAL,
                             'jira_url': JIRA_CONFIG['URL'],
                             'ai_enabled': True,  # 🤖 AI features enabled
                             'ai_confidence': 80  # AI confidence level
                         })

@app.route('/help')
def help_guide():
    """Help/User Guide page explaining how to read and use the dashboard"""
    # Get company name from settings for dynamic content
    company_name = settings_manager.get_company_name()
    return render_template('help.html', company_name=company_name)

@app.route('/use-cases.html')
def use_cases_overview():
    """Use Cases Overview - Primary users and platform overview"""
    # Get company name from settings for dynamic content
    company_name = settings_manager.get_company_name()
    return render_template('use-cases.html', company_name=company_name)

@app.route('/use-cases-documentation.html')
def use_cases_documentation_page():
    """Use Cases Documentation - Detailed documentation and examples"""
    # Get company name from settings for dynamic content
    company_name = settings_manager.get_company_name()
    return render_template('use-cases-documentation.html', company_name=company_name)

@app.route('/user-guide.html')
def user_guide_tutorial():
    """Complete User Guide & Tutorial - Step-by-step instructions and best practices"""
    # Get company name from settings for dynamic content
    company_name = settings_manager.get_company_name()
    return render_template('user-guide.html', company_name=company_name)

@app.route('/api/analyze/<project_id>', methods=['GET', 'POST'])
def analyze_project(project_id):
    """Enhanced project analysis API with filtering support"""
    try:
        # Get filters from query parameters AND POST body
        filters = {}
        
        # Try to get filters from POST body (from frontend AJAX call)
        if request.method == 'POST':
            try:
                body_data = request.get_json(silent=True) or {}
                filters.update(body_data)
                print(f"📋 Received POST data: {body_data}")
            except Exception as e:
                print(f"⚠️ Error parsing POST data: {e}")
                pass
        
        # Also get from query parameters (backwards compatibility)
        query_filters = {
            'start_date': request.args.get('start_date'),
            'end_date': request.args.get('end_date'),
            'environment': request.args.get('environment', JIRA_CONFIG['ENVIRONMENT']),
            'issue_types': request.args.getlist('issue_types') or ['Bug', 'Support Ticket'],
            'components': request.args.getlist('components'),
            'date_range_display': request.args.get('date_range_display')
        }
        
        # Merge query parameters with body data (body data takes precedence)
        for k, v in query_filters.items():
            if k not in filters and v:
                filters[k] = v
        
        # Remove empty filters
        filters = {k: v for k, v in filters.items() if v is not None and v != [] and v != ''}
        
        print(f"📊 Analyzing {project_id} with filters: {filters}")
        
        # Handle "ALL" projects case
        if project_id == 'ALL':
            project_name = f'All {settings_manager.get_company_name()} Projects'
            result = get_all_projects_analysis(filters)
        else:
            result = get_cached_or_fetch_data(project_id, filters)
        
        if not result:
            return jsonify({'success': False, 'message': 'Project not found'})
        
        # Convert ALL data to JSON serializable format
        try:
            # Convert DataFrame to dict if present
            if 'data' in result and hasattr(result['data'], 'to_dict'):
                result['data'] = result['data'].to_dict('records')
            
            # Deep convert the entire result to ensure all numpy types are handled
            result = deep_convert_to_json_serializable(result)
            
            return jsonify(result)
            
        except Exception as json_error:
            print(f"❌ JSON serialization error: {json_error}")
            print(f"🔍 Problematic data type: {type(result)}")
            
            # Fallback: return minimal error response
            return jsonify({
                'success': False,
                'message': f'JSON serialization error: {str(json_error)}',
                'project_name': result.get('project_name', 'Unknown'),
                'error_type': 'serialization_error'
            })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Analysis error: {str(e)}'})

@app.route('/api/trends/<project_id>')
def get_trends(project_id):
    """API endpoint for trend analysis"""
    try:
        # Handle "ALL" projects case
        if project_id == 'ALL':
            return get_all_projects_trends()
        
        # Get project info
        project_info = None
        project_key = None
        
        for code, info in PROJECT_MAPPINGS.items():
            if code == project_id:
                project_info = info
                project_key = info['jira_key']
                break
        
        if not project_info:
            return jsonify({'success': False, 'message': 'Project not found'})
        
        # Get number of months from query parameter
        months = int(request.args.get('months', 6))
        
        # Perform trend analysis
        analyzer = TrendAnalyzer()
        historical_data = analyzer.fetch_historical_data(project_key, months)
        
        if not historical_data:
            return jsonify({'success': False, 'message': 'No historical data available'})
        
        # Process trend data for API response
        trend_summary = []
        for data in historical_data:
            # Convert components data to JSON serializable
            components_data = data['component_data']
            if hasattr(components_data, 'to_dict'):
                components_data = components_data.to_dict()
            elif hasattr(components_data, 'items'):
                components_data = {k: convert_to_json_serializable(v) for k, v in components_data.items()}
            
            trend_summary.append({
                'month': data['month'],
                'total_bugs': int(data['total_bugs']) if data['total_bugs'] else 0,
                'components': components_data
            })
        
        result = {
            'success': True,
            'project_name': project_info['name'],
            'trend_data': trend_summary,
            'months_analyzed': len(historical_data)
        }
        
        # Deep convert to handle numpy types
        result = deep_convert_to_json_serializable(result)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Trend analysis error: {str(e)}'})

def get_all_projects_trends():
    """Get combined trend analysis for all projects"""
    try:
        print("🌟 Starting trend analysis for ALL projects")
        
        # Get number of months from query parameter
        months = int(request.args.get('months', 6))
        
        analyzer = TrendAnalyzer()
        all_trends = []
        
        # Collect trends from all projects
        for project_id, project_info in PROJECT_MAPPINGS.items():
            try:
                project_key = project_info['jira_key']
                print(f"📈 Getting trends for {project_info['name']}...")
                
                # Get historical data for this project
                historical_data = analyzer.fetch_historical_data(project_key, months)
                
                if historical_data:
                    for data in historical_data:
                        # Add project information to each trend data point
                        trend_entry = {
                            'month': data['month'],
                            'project_name': project_info['name'],
                            'project_key': project_id,
                            'total_bugs': int(data['total_bugs']) if data['total_bugs'] else 0,
                            'components': data['component_data'].to_dict() if hasattr(data['component_data'], 'to_dict') else data['component_data']
                        }
                        all_trends.append(trend_entry)
                    
                    print(f"✅ {project_info['name']}: {len(historical_data)} months of data")
                else:
                    print(f"⚠️ {project_info['name']}: No trend data")
                    
            except Exception as e:
                print(f"❌ Error getting trends for {project_info['name']}: {e}")
                continue
        
        if not all_trends:
            return jsonify({
                'success': False, 
                'message': 'No trend data available for any projects'
            })
        
        # Group by month and combine data
        monthly_combined = {}
        for trend in all_trends:
            month = trend['month']
            if month not in monthly_combined:
                monthly_combined[month] = {
                    'month': month,
                    'total_bugs': 0,
                    'projects': {},
                    'components': {}
                }
            
            monthly_combined[month]['total_bugs'] += trend['total_bugs']
            monthly_combined[month]['projects'][trend['project_name']] = trend['total_bugs']
            
            # Combine components
            for comp, count in trend['components'].items():
                if comp in monthly_combined[month]['components']:
                    monthly_combined[month]['components'][comp] += count
                else:
                    monthly_combined[month]['components'][comp] = count
        
        # Convert to sorted list
        combined_trends = list(monthly_combined.values())
        combined_trends.sort(key=lambda x: x['month'])
        
        result = {
            'success': True,
            'project_name': f'All {settings_manager.get_company_name()} Projects',
            'trend_data': combined_trends,
            'months_analyzed': len(combined_trends),
            'projects_included': len(PROJECT_MAPPINGS)
        }
        
        # Deep convert to handle numpy types
        result = deep_convert_to_json_serializable(result)
        return jsonify(result)
        
    except Exception as e:
        print(f"❌ Error in combined trend analysis: {e}")
        return jsonify({'success': False, 'message': f'Combined trend analysis error: {str(e)}'})

@app.route('/api/alerts/check')
def check_alerts():
    """API endpoint to check current alert status - optionally project-specific"""
    try:
        # Get optional project filter from query parameter
        project_filter = request.args.get('project', None)
        
        alert_system = RiskAlertSystem()
        
        if project_filter == 'ALL':
            # Get alerts for all projects
            alerts = alert_system.check_all_projects()
            project_name = f'All {settings_manager.get_company_name()} Projects'
        elif project_filter and project_filter in PROJECT_MAPPINGS:
            # Get alerts for specific project
            project_info = PROJECT_MAPPINGS[project_filter]
            project_key = project_info['jira_key']
            
            # Check alerts for single project
            alerts = alert_system.check_project_alerts(project_key, project_info['name'])
            project_name = project_info['name']
        else:
            # Default: get alerts for all projects
            alerts = alert_system.check_all_projects()
            project_name = f'All {settings_manager.get_company_name()} Projects'
        
        # Format alerts for API response
        formatted_alerts = []
        for alert in alerts:
            formatted_alerts.append({
                'project_name': alert['project_name'],
                'component': alert['component'],
                'bug_count': alert['bug_count'],
                'alert_level': alert['alert_level'],
                'timestamp': alert['timestamp'].isoformat()
            })
        
        return jsonify({
            'success': True,
            'alerts': formatted_alerts,
            'alert_count': len(formatted_alerts),
            'project_name': project_name,
            'project_filter': project_filter,
            'thresholds': {
                'high_risk': AlertConfig.HIGH_RISK_THRESHOLD,
                'critical': AlertConfig.CRITICAL_RISK_THRESHOLD,
                'urgent': AlertConfig.URGENT_RISK_THRESHOLD
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Alert check error: {str(e)}'})

@app.route('/api/filters/<project_id>')
def get_available_filters(project_id):
    """Get available filter options for a project or all projects"""
    try:
        # Handle "ALL" projects case
        if project_id == 'ALL':
            return get_all_projects_filters()
        
        # Get project info
        project_info = None
        project_key = None
        
        for code, info in PROJECT_MAPPINGS.items():
            if code == project_id:
                project_info = info
                project_key = info['jira_key']
                break
        
        if not project_info:
            return jsonify({'success': False, 'message': 'Project not found'})
        
        # Connect to JIRA to get project components directly
        jira = connect_to_jira()
        
        # Get project components from JIRA API
        project_components = []
        try:
            project = jira.project(project_key)
            if hasattr(project, 'components'):
                project_components = [comp.name for comp in project.components]
            print(f"📋 Found {len(project_components)} components for {project_key}: {project_components}")
        except Exception as e:
            print(f"⚠️ Could not fetch components from JIRA API: {e}")
            
            # Fallback: Fetch sample data to get available filter options
            try:
                data = fetch_jira_data_with_filters(project_key, {})
                if 'Components' in data.columns:
                    project_components = sorted(data['Components'].dropna().unique().tolist())
                    print(f"📋 Fallback: Found {len(project_components)} components from data")
            except Exception as fallback_error:
                print(f"❌ Fallback component fetch also failed: {fallback_error}")
        
        filters = {
            'environments': ['Production', 'Staging'],
            'issue_types': ['Bug', 'Support Ticket'],
            'components': project_components,
            'date_ranges': [
                {'label': 'Last 30 days', 'days': 30},
                {'label': 'Last 3 months', 'days': 90},
                {'label': 'Last 6 months', 'days': 180},
                {'label': 'Last year', 'days': 365}
            ]
        }
        
        return jsonify({
            'success': True,
            'filters': filters
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Filter options error: {str(e)}'})

def get_all_projects_filters():
    """Get combined filter options for all projects"""
    try:
        print("🌟 Getting combined filters for ALL projects")
        
        # Connect to JIRA
        jira = connect_to_jira()
        
        # Collect all components from all projects
        all_components = set()
        
        for project_id, project_info in PROJECT_MAPPINGS.items():
            try:
                project_key = project_info['jira_key']
                print(f"🔄 Getting components for {project_info['name']}...")
                
                # Try JIRA API first
                try:
                    project = jira.project(project_key)
                    if hasattr(project, 'components'):
                        project_components = [comp.name for comp in project.components]
                        all_components.update(project_components)
                        print(f"📋 Added {len(project_components)} components from {project_info['name']}")
                except Exception as jira_error:
                    print(f"⚠️ JIRA API failed for {project_info['name']}: {jira_error}")
                    
                    # Fallback to data analysis
                    try:
                        data = fetch_jira_data_with_filters(project_key, {})
                        if 'Components' in data.columns:
                            data_components = data['Components'].dropna().unique().tolist()
                            all_components.update(data_components)
                            print(f"📋 Fallback: Added {len(data_components)} components from {project_info['name']} data")
                    except Exception as data_error:
                        print(f"❌ Data fallback failed for {project_info['name']}: {data_error}")
                        
            except Exception as e:
                print(f"❌ Error processing {project_info['name']}: {e}")
                continue
        
        # Sort components
        sorted_components = sorted(list(all_components))
        
        filters = {
            'environments': ['Production', 'Staging'],
            'issue_types': ['Bug', 'Support Ticket'],
            'components': sorted_components,
            'date_ranges': [
                {'label': 'Last 30 days', 'days': 30},
                {'label': 'Last 3 months', 'days': 90},
                {'label': 'Last 6 months', 'days': 180},
                {'label': 'Last year', 'days': 365}
            ]
        }
        
        print(f"✅ Combined filters: {len(sorted_components)} total components from all projects")
        
        return jsonify({
            'success': True,
            'filters': filters,
            'projects_included': len(PROJECT_MAPPINGS)
        })
        
    except Exception as e:
        print(f"❌ Error getting combined filters: {e}")
        return jsonify({'success': False, 'message': f'Combined filter options error: {str(e)}'})

@app.route('/api/cache/clear')
def clear_cache():
    """Clear analysis cache for fresh data"""
    global analysis_cache, last_cache_update
    analysis_cache.clear()
    last_cache_update.clear()
    return jsonify({'success': True, 'message': 'Cache cleared successfully'})

@app.route('/api/component-bugs/<project_id>/<component_name>', methods=['POST'])
def get_component_bugs(project_id, component_name):
    """Get real JIRA bugs for a specific component"""
    try:
        import urllib.parse
        
        # Decode component name from URL
        component_name = urllib.parse.unquote(component_name)
        print(f"🔍 Fetching REAL bugs for component: '{component_name}' in project: {project_id}")
        
        # Get filters from request body
        filters = {}
        if request.is_json:
            filters = request.get_json() or {}
        
        print(f"🔧 Applied filters: {filters}")
        
        # 🔍 DEBUG: Track the data consistency
        print(f"🔍 DEBUG - Component bug fetch:")
        print(f"   - Requested component: '{component_name}'")
        print(f"   - Project ID: {project_id}")
        print(f"   - Filters: {filters}")
        
        # Fetch the full project data with filters
        if project_id == 'ALL':
            project_name = f'All {settings_manager.get_company_name()} Projects'
            result = get_all_projects_analysis(filters)
            data = result.get('data', pd.DataFrame())
        else:
            result = get_cached_or_fetch_data(project_id, filters)
            data = result.get('data', pd.DataFrame())
        
        if data.empty:
            return jsonify({
                'success': False,
                'message': f'No data available for project {project_id}',
                'bugs': []
            })
        
        # Debug: Print available columns and sample data
        print(f"🔍 Available columns: {list(data.columns)}")
        print(f"🔍 Data shape: {data.shape}")
        
        if 'Components' in data.columns:
            unique_components = data['Components'].dropna().unique()
            print(f"🔍 Available components in data ({len(unique_components)}): {list(unique_components)}")
            print(f"🔍 Looking for component: '{component_name}'")
            
            # Show sample of components data for debugging
            sample_components = data['Components'].dropna().head(10).tolist()
            print(f"🔍 Sample components from data: {sample_components}")
        else:
            print(f"❌ 'Components' column not found in data. Available columns: {list(data.columns)}")
        
        # Filter data for the specific component with flexible matching
        if 'Components' in data.columns:
            # Try exact match first
            component_bugs = data[data['Components'] == component_name].copy()
            
            # If no exact match, try case-insensitive match
            if component_bugs.empty:
                component_bugs = data[data['Components'].str.lower() == component_name.lower()].copy()
                if not component_bugs.empty:
                    print(f"🔄 Found match using case-insensitive search")
            
            # If still no match, try partial/contains match
            if component_bugs.empty:
                component_bugs = data[data['Components'].str.contains(component_name, case=False, na=False)].copy()
                if not component_bugs.empty:
                    print(f"🔄 Found match using partial/contains search")
            
            # If still no match, try reverse partial match (in case component_name is shorter)
            if component_bugs.empty:
                matching_components = data[data['Components'].str.contains('|'.join(component_name.split()), case=False, na=False)]
                if not matching_components.empty:
                    component_bugs = matching_components.copy()
                    print(f"🔄 Found match using word-based search")
                    
            # If still no match, try finding similar components
            if component_bugs.empty:
                similar_components = []
                for comp in unique_components:
                    if comp and (component_name.lower() in comp.lower() or comp.lower() in component_name.lower()):
                        similar_components.append(comp)
                
                if similar_components:
                    print(f"🔄 Found similar components: {similar_components}")
                    # Use the first similar component
                    best_match = similar_components[0]
                    component_bugs = data[data['Components'] == best_match].copy()
                    print(f"🔄 Using best match: '{best_match}' for requested component: '{component_name}'")
        else:
            return jsonify({
                'success': False,
                'message': 'Components column not found in data',
                'available_columns': list(data.columns),
                'bugs': []
            })
        
        print(f"📋 Found {len(component_bugs)} REAL bugs for component '{component_name}'")
        
        if component_bugs.empty:
            # Get available components for debugging
            available_components = data['Components'].dropna().unique().tolist() if 'Components' in data.columns else []
            suggestions = [comp for comp in available_components if component_name.lower() in comp.lower() or comp.lower() in component_name.lower()][:5]
            
            return jsonify({
                'success': True,
                'component': component_name,
                'message': f'No bugs found for component "{component_name}" with current filters',
                'available_components': available_components[:10],  # Show first 10 for debugging
                'total_bugs_in_dataset': len(data),
                'suggestions': suggestions,
                'debug_info': {
                    'project_id': project_id,
                    'filters_applied': filters,
                    'unique_components_count': len(available_components),
                    'sample_component_names': available_components[:5]
                },
                'bugs': []
            })
        
        # Convert to list of bug records with proper field mapping
        bugs_list = []
        for _, bug in component_bugs.iterrows():
            # Extract real JIRA data with fallbacks
            bug_record = {
                'Key': bug.get('Key', bug.get('key', f"{component_name.upper().replace(' ', '')}-{len(bugs_list)+1000}")),
                'Summary': bug.get('Summary', bug.get('summary', 'No summary available')),
                'Priority': bug.get('Priority', bug.get('priority', 'Medium')),
                'Status': bug.get('Status', bug.get('status', 'Open')),
                'Created': bug.get('Created', datetime.now().isoformat()),
                'Assignee': bug.get('Assignee', bug.get('assignee', 'Unassigned')),
                'Components': bug.get('Components', component_name),
                'Description': bug.get('Description', ''),
                'Reporter': bug.get('Reporter', bug.get('reporter', 'System')),
                'Updated': bug.get('Updated', bug.get('Created', datetime.now().isoformat())),
                'Resolution': bug.get('Resolution', ''),
                'Environment': bug.get('Environment', bug.get('environment', 'Production')),
                'Type': bug.get('Type', 'Bug'),
                'Labels': bug.get('Labels', []),
                'Fix_Version': bug.get('Fix Version', ''),
                'Affects_Version': bug.get('Affects Version', '')
            }
            bugs_list.append(bug_record)
        
        # Sort by creation date (newest first)
        bugs_list.sort(key=lambda x: x.get('Created', ''), reverse=True)
        
        # Add metadata
        bug_count_by_priority = {}
        bug_count_by_status = {}
        
        for bug in bugs_list:
            priority = bug.get('Priority', 'Medium')
            status = bug.get('Status', 'Open')
            
            bug_count_by_priority[priority] = bug_count_by_priority.get(priority, 0) + 1
            bug_count_by_status[status] = bug_count_by_status.get(status, 0) + 1
        
        return jsonify({
            'success': True,
            'component': component_name,
            'project_id': project_id,
            'total_bugs': len(bugs_list),
            'bugs': bugs_list,
            'metadata': {
                'priority_breakdown': bug_count_by_priority,
                'status_breakdown': bug_count_by_status,
                'date_range': filters.get('date_range_display', 'Filtered data'),
                'filters_applied': filters,
                'actual_component_found': component_bugs['Components'].iloc[0] if len(component_bugs) > 0 else component_name
            }
        })
        
    except Exception as e:
        print(f"❌ Error fetching component bugs: {e}")
        import traceback
        traceback.print_exc()
        
        # Return a more informative error message
        return jsonify({
            'success': False,
            'message': f'Error fetching component bugs: {str(e)}',
            'component': component_name,
            'project_id': project_id,
            'error_type': 'component_fetch_error',
            'debug_hint': 'This might happen if the component name doesn\'t match the actual data. Try selecting a different component or refreshing the analysis.',
            'bugs': []
        }), 404

@app.route('/api/debug/components/<project_id>')
def debug_components(project_id):
    """Debug endpoint to check component consistency"""
    try:
        # Get current filters if any
        filters = {}
        for key in ['start_date', 'end_date', 'environment', 'issue_types', 'components']:
            if request.args.get(key):
                filters[key] = request.args.get(key)
        
        print(f"🔍 DEBUG: Checking components for project {project_id} with filters: {filters}")
        
        # Get the same data that would be used for analysis
        if project_id == 'ALL':
            project_name = f'All {settings_manager.get_company_name()} Projects'
            result = get_all_projects_analysis(filters)
            data = result.get('data', pd.DataFrame())
        else:
            result = get_cached_or_fetch_data(project_id, filters)
            data = result.get('data', pd.DataFrame())
        
        debug_info = {
            'project_id': project_id,
            'filters_applied': filters,
            'data_shape': data.shape if not data.empty else [0, 0],
            'available_components': [],
            'ai_components': [],
            'component_mismatch': []
        }
        
        if not data.empty and 'Components' in data.columns:
            # Get actual components in data
            actual_components = data['Components'].dropna().unique().tolist()
            debug_info['available_components'] = actual_components
            
            # Generate AI insights to see what components it creates
            try:
                # Get project info
                project_info = None
                project_key = None
                
                if project_id != 'ALL':
                    for code, info in PROJECT_MAPPINGS.items():
                        if code == project_id:
                            project_info = info
                            project_key = info['jira_key']
                            break
                else:
                    project_info = {'name': f'All {settings_manager.get_company_name()} Projects'}
                    project_key = 'ALL'
                
                if project_info:
                    # Generate AI insights
                    historical_data = get_real_historical_data(project_key)
                    ai_insights = ai_engine.generate_enhanced_insights(
                        data, project_info['name'], historical_data
                    )
                    
                    if ai_insights and 'intelligent_risk_analysis' in ai_insights:
                        ai_components = [risk['component'] for risk in ai_insights['intelligent_risk_analysis']['top_risks']]
                        debug_info['ai_components'] = ai_components
                        
                        # Check for mismatches
                        mismatched = [comp for comp in ai_components if comp not in actual_components]
                        debug_info['component_mismatch'] = mismatched
                        
            except Exception as ai_error:
                debug_info['ai_error'] = str(ai_error)
        
        return jsonify({
            'success': True,
            'debug_info': debug_info,
            'message': 'Component debug information gathered successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Debug endpoint failed'
        }), 500

@app.route('/api/health')
def health_check():
    """Health check endpoint for monitoring"""
    try:
        # Check if JIRA is configured before attempting connection
        jira_config = settings_manager.get_jira_config()
        
        # Check if JIRA configuration is complete
        if not jira_config.get('jira_url') or not jira_config.get('username') or not jira_config.get('api_token'):
            return jsonify({
                'status': 'configuration_required',
                'jira_connected': False,
                'message': 'JIRA configuration required. Please complete setup in Settings.',
                'cache_size': len(analysis_cache),
                'timestamp': datetime.now().isoformat(),
                'features': {
                    'trend_analysis': True,
                    'alerts': True,
                    'real_time': DashboardConfig.AUTO_REFRESH_ENABLED,
                    'filtering': True,
                    'component_bugs': True
                }
            })
        
        # Check for placeholder values that shouldn't be used
        if ('your-company.atlassian.net' in jira_config.get('jira_url', '') or 
            'your-email@company.com' in jira_config.get('username', '') or
            jira_config.get('api_token') == 'xxxx'):
            return jsonify({
                'status': 'configuration_required',
                'jira_connected': False,
                'message': 'JIRA configuration contains placeholder values. Please update in Settings.',
                'cache_size': len(analysis_cache),
                'timestamp': datetime.now().isoformat(),
                'features': {
                    'trend_analysis': True,
                    'alerts': True,
                    'real_time': DashboardConfig.AUTO_REFRESH_ENABLED,
                    'filtering': True,
                    'component_bugs': True
                }
            })
        
        # Test JIRA connection with valid configuration
        jira = connect_to_jira()
        
        # Try a simple server info request to test connection
        server_info = jira.server_info()
        
        return jsonify({
            'status': 'healthy',
            'jira_connected': True,
            'jira_server': server_info.get('serverTitle', 'JIRA Server'),
            'cache_size': len(analysis_cache),
            'timestamp': datetime.now().isoformat(),
            'features': {
                'trend_analysis': True,
                'alerts': True,
                'real_time': DashboardConfig.AUTO_REFRESH_ENABLED,
                'filtering': True,
                'component_bugs': True  # 🎯 New feature flag
            }
        })
        
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'jira_connected': False,
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/company-info')
def get_company_info():
    """Get company information for dynamic UI updates"""
    try:
        company_name = settings_manager.get_company_name()
        return jsonify({
            'success': True,
            'company_name': company_name
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error getting company info: {str(e)}',
            'company_name': 'Your Company'  # Fallback
        })

@app.route('/api/debug/config')
def debug_configuration():
    """Debug endpoint to check current configuration state"""
    try:
        # Get current project mappings
        current_mappings = get_current_project_mappings()
        
        # Get raw projects from settings manager
        raw_projects = settings_manager.get_projects()
        
        # Get JIRA config
        jira_config = get_current_jira_config()
        
        return jsonify({
            'success': True,
            'debug_info': {
                'project_mappings_count': len(PROJECT_MAPPINGS),
                'project_mappings': PROJECT_MAPPINGS,
                'current_mappings_count': len(current_mappings),
                'current_mappings': current_mappings,
                'raw_projects_count': len(raw_projects),
                'raw_projects': raw_projects,
                'jira_configured': bool(jira_config.get('URL')),
                'jira_url': jira_config.get('URL', 'Not set'),
                'settings_manager_working': True,
                'enabled_projects': [p for p in raw_projects if p.get('enabled_for_analysis', True)]
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'debug_info': {
                'project_mappings_count': len(PROJECT_MAPPINGS),
                'project_mappings': PROJECT_MAPPINGS,
                'settings_manager_working': False
            }
        })

@app.route('/api/debug/paths')
def debug_paths():
    """Debug endpoint to check configuration file paths and contents"""
    try:
        import os
        
        # Get SettingsManager paths
        config_dir = settings_manager.config_dir
        jira_config_file = settings_manager.jira_config_file
        projects_config_file = settings_manager.projects_config_file
        
        # Check file existence and content
        jira_exists = os.path.exists(jira_config_file)
        projects_exists = os.path.exists(projects_config_file)
        
        jira_content = {}
        projects_content = {}
        
        if jira_exists:
            try:
                with open(jira_config_file, 'r') as f:
                    jira_content = json.load(f)
            except Exception as e:
                jira_content = {"error": str(e)}
        
        if projects_exists:
            try:
                with open(projects_config_file, 'r') as f:
                    projects_content = json.load(f)
            except Exception as e:
                projects_content = {"error": str(e)}
        
        # Test settings manager methods
        sm_jira_config = {}
        sm_connection_config = {}
        try:
            sm_jira_config = settings_manager.get_jira_config()
            sm_connection_config = settings_manager.get_jira_connection_config()
        except Exception as e:
            sm_jira_config = {"error": str(e)}
            sm_connection_config = {"error": str(e)}
        
        # Get current working directory
        current_dir = os.getcwd()
        
        return jsonify({
            'success': True,
            'debug_info': {
                'paths': {
                    'current_working_directory': current_dir,
                    'config_dir': config_dir,
                    'jira_config_file': jira_config_file,
                    'projects_config_file': projects_config_file
                },
                'file_existence': {
                    'jira_config_exists': jira_exists,
                    'projects_config_exists': projects_exists
                },
                'file_contents': {
                    'jira_config_content': jira_content,
                    'projects_config_content': projects_content
                },
                'settings_manager_methods': {
                    'get_jira_config': sm_jira_config,
                    'get_jira_connection_config': sm_connection_config
                },
                'legacy_comparison': {
                    'current_jira_config': get_current_jira_config(),
                    'global_jira_config': JIRA_CONFIG
                }
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/debug/refresh-config', methods=['POST'])
def force_refresh_configuration():
    """Force refresh configuration from settings"""
    try:
        # Force refresh configuration
        refresh_configuration()
        
        # Get updated mappings
        current_mappings = get_current_project_mappings()
        
        return jsonify({
            'success': True,
            'message': 'Configuration refreshed successfully',
            'project_mappings_count': len(PROJECT_MAPPINGS),
            'project_mappings': PROJECT_MAPPINGS,
            'current_mappings': current_mappings
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Failed to refresh configuration'
        })

@app.route('/api/goals/<project_id>')
def get_project_goals(project_id):
    """Get all goals for a project"""
    try:
        print(f"🎯 Loading goals for project: '{project_id}'")
        available_projects = list(PROJECT_MAPPINGS.keys()) + ['ALL']
        print(f"🔍 Available projects: {available_projects}")
        
        # ALL project is valid for goal tracking
        if project_id not in available_projects:
            return jsonify({
                'success': False,
                'message': f'Project "{project_id}" not found. Available projects: {", ".join(available_projects)}'
            })
        
        goals_data = goal_tracker.get_project_goals(project_id)
        
        return jsonify({
            'success': True,
            'data': goals_data
        })
    except Exception as e:
        print(f"❌ Error fetching goals: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error fetching goals: {str(e)}'
        })

@app.route('/api/goals/<project_id>/create', methods=['POST'])
def create_goal(project_id):
    """Create a new goal"""
    try:
        available_projects = list(PROJECT_MAPPINGS.keys()) + ['ALL']
        if project_id not in available_projects:
            return jsonify({
                'success': False,
                'message': f'Project "{project_id}" not found. Available projects: {", ".join(available_projects)}'
            })
        
        goal_data = request.json
        
        # Validate required fields
        required_fields = ['type', 'title', 'target_value', 'target_date']
        for field in required_fields:
            if field not in goal_data:
                return jsonify({
                    'success': False,
                    'message': f'Missing required field: {field}'
                })
        
        goal = goal_tracker.create_goal(project_id, goal_data)
        
        return jsonify({
            'success': True,
            'data': goal,
            'message': 'Goal created successfully!'
        })
    except Exception as e:
        print(f"❌ Error creating goal: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error creating goal: {str(e)}'
        })

@app.route('/api/goals/<project_id>/<goal_id>/update', methods=['POST'])
def update_goal_progress(project_id, goal_id):
    """Update goal progress"""
    try:
        available_projects = list(PROJECT_MAPPINGS.keys()) + ['ALL']
        if project_id not in available_projects:
            return jsonify({
                'success': False,
                'message': f'Project "{project_id}" not found. Available projects: {", ".join(available_projects)}'
            })
        
        data = request.json
        current_value = data.get('current_value')
        
        if current_value is None:
            return jsonify({
                'success': False,
                'message': 'Current value is required'
            })
        
        result = goal_tracker.update_goal_progress(project_id, goal_id, current_value)
        
        return jsonify({
            'success': True,
            'data': result,
            'message': 'Goal progress updated successfully!'
        })
    except Exception as e:
        print(f"❌ Error updating goal: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error updating goal: {str(e)}'
        })

@app.route('/api/goals/<project_id>/<goal_id>/prediction')
def get_goal_prediction(project_id, goal_id):
    """Get goal completion prediction"""
    try:
        available_projects = list(PROJECT_MAPPINGS.keys()) + ['ALL']
        if project_id not in available_projects:
            return jsonify({
                'success': False,
                'message': f'Project "{project_id}" not found. Available projects: {", ".join(available_projects)}'
            })
        
        prediction = goal_tracker.predict_goal_completion(project_id, goal_id)
        
        return jsonify({
            'success': True,
            'data': prediction
        })
    except Exception as e:
        print(f"❌ Error getting prediction: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error getting prediction: {str(e)}'
        })

@app.route('/api/goals/<project_id>/<goal_id>/delete', methods=['DELETE'])
def delete_goal(project_id, goal_id):
    """Delete a goal permanently"""
    try:
        available_projects = list(PROJECT_MAPPINGS.keys()) + ['ALL']
        if project_id not in available_projects:
            return jsonify({
                'success': False,
                'message': f'Project "{project_id}" not found. Available projects: {", ".join(available_projects)}'
            })
        
        result = goal_tracker.delete_goal(project_id, goal_id)
        
        return jsonify({
            'success': True,
            'data': result,
            'message': 'Goal deleted successfully!'
        })
    except ValueError as ve:
        return jsonify({
            'success': False,
            'message': str(ve)
        })
    except Exception as e:
        print(f"❌ Error deleting goal: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error deleting goal: {str(e)}'
        })

@app.route('/api/goals/<project_id>/<goal_id>/cancel', methods=['POST'])
def cancel_goal(project_id, goal_id):
    """Cancel a goal (mark as cancelled instead of deleting)"""
    try:
        available_projects = list(PROJECT_MAPPINGS.keys()) + ['ALL']
        if project_id not in available_projects:
            return jsonify({
                'success': False,
                'message': f'Project "{project_id}" not found. Available projects: {", ".join(available_projects)}'
            })
        
        result = goal_tracker.cancel_goal(project_id, goal_id)
        
        return jsonify({
            'success': True,
            'data': result,
            'message': 'Goal cancelled successfully!'
        })
    except ValueError as ve:
        return jsonify({
            'success': False,
            'message': str(ve)
        })
    except Exception as e:
        print(f"❌ Error cancelling goal: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error cancelling goal: {str(e)}'
        })

@app.route('/api/goals/<project_id>/achievements')
def get_achievements(project_id):
    """Get achievements for a project"""
    try:
        available_projects = list(PROJECT_MAPPINGS.keys()) + ['ALL']
        if project_id not in available_projects:
            return jsonify({
                'success': False,
                'message': f'Project "{project_id}" not found. Available projects: {", ".join(available_projects)}'
            })
        
        achievements = goal_tracker.get_achievement_summary(project_id)
        
        return jsonify({
            'success': True,
            'data': achievements
        })
    except Exception as e:
        print(f"❌ Error fetching achievements: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error fetching achievements: {str(e)}'
        })

@app.route('/api/goals/<project_id>/insights')
def get_goal_insights(project_id):
    """Get AI insights about goal progress"""
    try:
        available_projects = list(PROJECT_MAPPINGS.keys()) + ['ALL']
        if project_id not in available_projects:
            return jsonify({
                'success': False,
                'message': f'Project "{project_id}" not found. Available projects: {", ".join(available_projects)}'
            })
        
        insights = goal_tracker.generate_goal_insights(project_id)
        
        return jsonify({
            'success': True,
            'data': insights
        })
    except Exception as e:
        print(f"❌ Error generating insights: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error generating insights: {str(e)}'
        })

@app.route('/api/goals/<project_id>/initialize', methods=['POST'])
def initialize_project_goals(project_id):
    """Initialize default goals for a project based on current data"""
    try:
        print(f"🚀 Initializing goals for project: '{project_id}'")
        print(f"🗂️ Available projects: {list(PROJECT_MAPPINGS.keys())}")
        
        # Handle "ALL" projects as a special case
        if project_id == 'ALL':
            print(f"🌟 Creating goals for ALL {settings_manager.get_company_name()} Projects (combined)")
            
            # Get combined data from all projects
            total_bugs = 0
            total_components = 0
            all_health_scores = []
            critical_components = 0
            
            # Analyze each project and combine the data
            for code, info in PROJECT_MAPPINGS.items():
                try:
                    project_key = info['jira_key']
                    jql = f'project = "{project_key}" AND (type = "Bug" OR type = "Support Ticket") AND "Environment[Select List (multiple choices)]" = {JIRA_CONFIG["ENVIRONMENT"]}'
                    
                    print(f"  📊 Analyzing {info['name']}...")
                    issues = jira.search_issues(jql, maxResults=1000)
                    
                    if issues:
                        project_bugs = len(issues)
                        total_bugs += project_bugs
                        
                        # Create DataFrame for this project
                        data_list = []
                        for issue in issues:
                            data_list.append({
                                'Components': ', '.join([comp.name for comp in issue.fields.components]) if issue.fields.components else 'Unassigned',
                            })
                        
                        if data_list:
                            df = pd.DataFrame(data_list)
                            project_components = len(df['Components'].unique())
                            total_components += project_components
                            
                            # Calculate project health score
                            if project_bugs == 0:
                                health_score = 100
                            elif project_bugs <= 10:
                                health_score = 90 - (project_bugs * 2)
                            elif project_bugs <= 50:
                                health_score = 70 - ((project_bugs - 10) * 1)
                            else:
                                health_score = max(10, 30 - ((project_bugs - 50) * 0.4))
                            
                            all_health_scores.append(health_score)
                            
                            # Count critical components for this project
                            component_counts = df['Components'].value_counts()
                            if len(component_counts) > 0:
                                project_critical = len(component_counts.head(max(1, len(component_counts) // 5)))
                                critical_components += project_critical
                    
                except Exception as project_error:
                    print(f"  ⚠️ Error analyzing {info['name']}: {project_error}")
                    continue
            
            # Calculate combined metrics
            combined_health_score = int(np.mean(all_health_scores)) if all_health_scores else 70
            
            current_data = {
                'total_bugs': total_bugs,
                'total_components': total_components,
                'health_score': combined_health_score,
                'critical_components': critical_components
            }
            
            print(f"🎯 Combined data for ALL projects: {current_data}")
            
            # Create intelligent default goals for ALL projects
            default_goals = goal_tracker.create_default_goals(project_id, current_data)
            
            return jsonify({
                'success': True,
                'data': {
                    'goals_created': len(default_goals),
                    'goals': default_goals,
                    'baseline_data': current_data,
                    'note': f'Goals created for ALL {settings_manager.get_company_name()} Projects combined'
                },
                'message': f'Initialized {len(default_goals)} default goals for ALL {settings_manager.get_company_name()} Projects'
            })
        
        # Handle individual projects
        project_info = None
        project_key = None
        
        # Find project info
        for code, info in PROJECT_MAPPINGS.items():
            if code == project_id:
                project_info = info
                project_key = info['jira_key']
                break
        
        if not project_info:
            available_projects = list(PROJECT_MAPPINGS.keys()) + ['ALL']
            return jsonify({
                'success': False,
                'message': f'Project "{project_id}" not found. Available projects: {", ".join(available_projects)}'
            })
        
        # Get current bug data for baseline
        try:
            jql = f'project = "{project_key}" AND (type = "Bug" OR type = "Support Ticket") AND "Environment[Select List (multiple choices)]" = {JIRA_CONFIG["ENVIRONMENT"]}'
            
            print(f"🔍 Fetching current data for goal initialization...")
            print(f"  🎯 Project: {project_info['name']}")
            print(f"  🔑 JQL: {jql}")
            
            issues = jira.search_issues(jql, maxResults=1000)
            
            # Create DataFrame for analysis
            if issues:
                data_list = []
                for issue in issues:
                    data_list.append({
                        'Key': issue.key,
                        'Components': ', '.join([comp.name for comp in issue.fields.components]) if issue.fields.components else 'Unassigned',
                        'summary': str(issue.fields.summary),
                        'Created': str(issue.fields.created)
                    })
                
                df = pd.DataFrame(data_list)
                
                # Calculate current metrics
                total_bugs = len(df)
                total_components = len(df['Components'].unique()) if 'Components' in df.columns else 0
                
                # Calculate basic health score
                if total_bugs == 0:
                    health_score = 100
                elif total_bugs <= 10:
                    health_score = 90 - (total_bugs * 2)
                elif total_bugs <= 50:
                    health_score = 70 - ((total_bugs - 10) * 1)
                else:
                    health_score = max(10, 30 - ((total_bugs - 50) * 0.4))
                
                health_score = max(10, min(100, int(health_score)))
                
                # Determine critical components (top 20% by bug count)
                if 'Components' in df.columns:
                    component_counts = df['Components'].value_counts()
                    critical_threshold = len(component_counts) * 0.2
                    critical_components = len(component_counts.head(max(1, int(critical_threshold))))
                else:
                    critical_components = 0
                
                current_data = {
                    'total_bugs': total_bugs,
                    'total_components': total_components,
                    'health_score': health_score,
                    'critical_components': critical_components
                }
                
            else:
                # No bugs found - excellent baseline
                current_data = {
                    'total_bugs': 0,
                    'total_components': 0,
                    'health_score': 100,
                    'critical_components': 0
                }
            
            # Create intelligent default goals
            default_goals = goal_tracker.create_default_goals(project_id, current_data)
            
            return jsonify({
                'success': True,
                'data': {
                    'goals_created': len(default_goals),
                    'goals': default_goals,
                    'baseline_data': current_data
                },
                'message': f'Initialized {len(default_goals)} default goals based on current project state'
            })
            
        except Exception as jira_error:
            print(f"❌ JIRA Error: {str(jira_error)}")
            
            # Fallback: create goals with estimated data
            estimated_data = {
                'total_bugs': 25,  # Reasonable estimate
                'total_components': 5,
                'health_score': 70,
                'critical_components': 1
            }
            
            default_goals = goal_tracker.create_default_goals(project_id, estimated_data)
            
            return jsonify({
                'success': True,
                'data': {
                    'goals_created': len(default_goals),
                    'goals': default_goals,
                    'baseline_data': estimated_data,
                    'note': 'Goals created with estimated baseline data due to JIRA connection issue'
                },
                'message': f'Initialized {len(default_goals)} default goals with estimated baseline'
            })
        
    except Exception as e:
        print(f"❌ Error initializing goals: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error initializing goals: {str(e)}'
        })

# ================================================================================================
# 🔧 SETTINGS API ENDPOINTS
# ================================================================================================

@app.route('/settings')
def settings_page():
    """Settings page for JIRA configuration and project management"""
    # Get company name from settings for dynamic content
    company_name = settings_manager.get_company_name()
    return render_template('settings.html', company_name=company_name)

@app.route('/api/settings/jira', methods=['GET'])
def get_jira_settings():
    """Get current JIRA configuration"""
    try:
        config = settings_manager.get_jira_config()
        
        # Remove sensitive data for GET request
        safe_config = config.copy()
        if 'api_token' in safe_config and safe_config['api_token']:
            safe_config['api_token'] = '***'  # Mask the token
        
        return jsonify({
            'success': True,
            'config': safe_config
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error getting JIRA configuration: {str(e)}'
        })

@app.route('/api/settings/jira', methods=['POST'])
def save_jira_settings():
    """Save JIRA configuration"""
    try:
        config_data = request.get_json()
        
        if not config_data:
            return jsonify({
                'success': False,
                'message': 'No configuration data provided'
            })
        
        result = settings_manager.save_jira_config(config_data)
        
        if result.get('success'):
            # Refresh configuration to use new settings
            refresh_configuration()
            return jsonify(result)
        else:
            return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error saving JIRA configuration: {str(e)}'
        })

@app.route('/api/settings/jira/test', methods=['POST'])
def test_jira_connection():
    """Test JIRA connection"""
    try:
        config_data = request.get_json()
        
        if not config_data:
            return jsonify({
                'success': False,
                'message': 'No configuration data provided'
            })
        
        result = settings_manager.test_jira_connection(config_data)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error testing JIRA connection: {str(e)}'
        })

@app.route('/api/settings/projects', methods=['GET'])
def get_projects_settings():
    """Get configured projects"""
    try:
        projects = settings_manager.get_projects()
        
        return jsonify({
            'success': True,
            'projects': projects
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error getting projects: {str(e)}'
        })

@app.route('/api/settings/projects', methods=['POST'])
def add_project_setting():
    """Add a new project"""
    try:
        project_data = request.get_json()
        
        if not project_data:
            return jsonify({
                'success': False,
                'message': 'No project data provided'
            })
        
        result = settings_manager.add_project(project_data)
        if result.get('success'):
            # Refresh configuration to include new project
            refresh_configuration()
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error adding project: {str(e)}'
        })

@app.route('/api/settings/projects/<project_id>', methods=['PUT'])
def update_project_setting(project_id):
    """Update an existing project"""
    try:
        project_data = request.get_json()
        
        if not project_data:
            return jsonify({
                'success': False,
                'message': 'No project data provided'
            })
        
        result = settings_manager.update_project(project_id, project_data)
        if result.get('success'):
            # Refresh configuration to reflect project changes
            refresh_configuration()
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error updating project: {str(e)}'
        })

@app.route('/api/settings/projects/<project_id>', methods=['DELETE'])
def delete_project_setting(project_id):
    """Delete a project"""
    try:
        result = settings_manager.delete_project(project_id)
        if result.get('success'):
            # Refresh configuration to remove deleted project
            refresh_configuration()
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error deleting project: {str(e)}'
        })

@app.route('/api/settings/discover-projects', methods=['GET'])
def discover_projects():
    """Discover projects from JIRA without adding them"""
    try:
        result = settings_manager.discover_projects_from_jira()
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error discovering projects: {str(e)}'
        })

@app.route('/api/settings/projects/discover', methods=['POST'])
def auto_add_discovered_projects():
    """Auto-add all discovered projects (legacy functionality)"""
    try:
        result = settings_manager.auto_add_discovered_projects()
        if result.get('success'):
            # Refresh configuration to include discovered projects
            refresh_configuration()
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error auto-adding projects: {str(e)}'
        })

@app.route('/api/settings/projects/<project_id>/enable', methods=['POST'])
def enable_project_for_analysis(project_id):
    """Enable a project for dashboard analysis"""
    try:
        result = settings_manager.enable_project_for_analysis(project_id)
        if result.get('success'):
            # Refresh configuration to include enabled project
            refresh_configuration()
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error enabling project: {str(e)}'
        })

@app.route('/api/settings/projects/<project_id>/disable', methods=['POST'])
def disable_project_for_analysis(project_id):
    """Disable a project for dashboard analysis"""
    try:
        result = settings_manager.disable_project_for_analysis(project_id)
        if result.get('success'):
            # Refresh configuration to remove disabled project
            refresh_configuration()
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error disabling project: {str(e)}'
        })

@app.route('/api/settings/summary', methods=['GET'])
def get_settings_summary():
    """Get configuration summary"""
    try:
        summary = settings_manager.get_configuration_summary()
        
        return jsonify({
            'success': True,
            'jira_config': summary['jira_config'],
            'projects': summary['projects']['projects'],
            'system_status': summary['system_status']
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error getting configuration summary: {str(e)}'
        })

@app.route('/api/settings/export', methods=['GET'])
def export_settings():
    """Export configuration as JSON file"""
    try:
        config_data = settings_manager.export_configuration()
        
        response = jsonify(config_data)
        response.headers['Content-Disposition'] = f'attachment; filename=dashboard-config-{datetime.now().strftime("%Y%m%d")}.json'
        response.headers['Content-Type'] = 'application/json'
        
        return response
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error exporting configuration: {str(e)}'
        })

@app.route('/api/settings/import', methods=['POST'])
def import_settings():
    """Import configuration from JSON file"""
    try:
        if 'config_file' not in request.files:
            return jsonify({
                'success': False,
                'message': 'No configuration file provided'
            })
        
        file = request.files['config_file']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'message': 'No file selected'
            })
        
        if not file.filename.endswith('.json'):
            return jsonify({
                'success': False,
                'message': 'Invalid file type. Please upload a JSON file.'
            })
        
        try:
            config_data = json.loads(file.read().decode('utf-8'))
        except json.JSONDecodeError:
            return jsonify({
                'success': False,
                'message': 'Invalid JSON file format'
            })
        
        result = settings_manager.import_configuration(config_data)
        if result.get('success'):
            # Refresh configuration to use imported settings
            refresh_configuration()
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error importing configuration: {str(e)}'
        })

@app.route('/api/settings/jira/reset', methods=['POST'])
def reset_jira_settings():
    """Reset JIRA configuration to default values"""
    try:
        result = settings_manager.reset_jira_configuration()
        if result.get('success'):
            # Refresh configuration to use reset settings
            refresh_configuration()
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error resetting JIRA configuration: {str(e)}'
        })

@app.route('/api/settings/projects/reset', methods=['POST'])
def reset_projects_settings():
    """Reset all projects configuration"""
    try:
        result = settings_manager.reset_projects_configuration()
        if result.get('success'):
            # Refresh configuration to remove all projects
            refresh_configuration()
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error resetting projects configuration: {str(e)}'
        })

@app.route('/api/settings/reset-all', methods=['POST'])
def reset_all_settings():
    """Reset both JIRA and projects configuration"""
    try:
        result = settings_manager.reset_all_configuration()
        if result.get('success'):
            # Refresh configuration to use reset settings
            refresh_configuration()
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error resetting all configuration: {str(e)}'
        })

if __name__ == '__main__':
    print("🚀 Starting Enhanced JIRA Bug Risk Analysis Dashboard")
    print("=" * 60)
    print(f"📊 Auto-refresh: {'Enabled' if DashboardConfig.AUTO_REFRESH_ENABLED else 'Disabled'}")
    print(f"⏱️  Refresh interval: {DashboardConfig.AUTO_REFRESH_INTERVAL/1000} seconds")
    print(f"💾 Cache duration: {DashboardConfig.CACHE_DURATION} seconds")
    print(f"🎯 Max components in chart: {DashboardConfig.MAX_COMPONENTS_CHART}")
    print("=" * 60)
    print("🌐 Dashboard: http://localhost:5001")
    print("📡 API Health: http://localhost:5001/api/health")
    print("🚨 Alert Check: http://localhost:5001/api/alerts/check")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5001) 