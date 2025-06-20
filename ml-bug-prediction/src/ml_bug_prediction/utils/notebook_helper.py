#!/usr/bin/env python3
"""
Notebook Helper for JIRA Bug Risk Analysis
Simplifies using centralized configuration in Jupyter notebooks
"""

import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
from IPython.display import display, HTML
from .jira_utils import fetch_project_data, save_project_data
from ..config import JIRA_CONFIG, PROJECTS, ANALYSIS_CONFIG, print_config_summary
from ..models.trend_analysis import TrendAnalyzer, analyze_project_trends

def setup_notebook(project_key, display_config=True):
    """
    Set up notebook environment with centralized JIRA configuration
    
    Args:
        project_key (str): JIRA project key (e.g., 'AND', 'IOS', 'MES', 'AW', 'PH')
        display_config (bool): Whether to display configuration summary
    
    Returns:
        dict: Project information and configuration
    """
    
    if display_config:
        print("🔧 JIRA Bug Risk Analysis - Notebook Setup")
        print("=" * 50)
        print_config_summary()
        print()
    
    # Find project info by key
    project_info = None
    project_code = None
    
    for code, info in PROJECTS.items():
        if info['key'] == project_key:
            project_info = info
            project_code = code
            break
    
    if not project_info:
        available_keys = [info['key'] for info in PROJECTS.values()]
        raise ValueError(f"Project key '{project_key}' not found. Available keys: {available_keys}")
    
    print(f"📊 Setting up analysis for: {project_info['name']}")
    print(f"🔑 Project Key: {project_key}")
    print(f"📅 Analysis Period: Last {ANALYSIS_CONFIG['MONTHS_BACK']} months")
    print(f"🌍 Environment: {ANALYSIS_CONFIG['ENVIRONMENT']}")
    print()
    
    return {
        'project_info': project_info,
        'project_code': project_code,
        'project_key': project_key,
        'config': ANALYSIS_CONFIG
    }

def fetch_and_display_jira_data(project_key, save_to_csv=True):
    """
    Fetch JIRA data for project and optionally save to CSV
    
    Args:
        project_key (str): JIRA project key
        save_to_csv (bool): Whether to save data to CSV file
    
    Returns:
        pd.DataFrame: JIRA data
    """
    
    print(f"📡 Fetching JIRA data for project: {project_key}")
    print("-" * 40)
    
    # Fetch data using centralized configuration
    data = fetch_project_data(project_key)
    
    if data.empty:
        print(f"⚠️  No data found for project {project_key}")
        return data
    
    print(f"✅ Successfully fetched {len(data)} issues")
    print(f"📊 Data columns: {list(data.columns)}")
    
    if save_to_csv:
        # Save to CSV with consistent naming
        csv_path = save_project_data(data, project_key.lower())
        if csv_path:
            print(f"💾 Data saved to: {csv_path}")
    
    # Display basic info
    if 'Components' in data.columns:
        component_counts = data['Components'].value_counts()
        print(f"🧩 Components found: {len(component_counts)}")
        print(f"🔝 Top component: {component_counts.index[0]} ({component_counts.iloc[0]} issues)")
    
    print()
    return data

def create_pie_chart(data, project_name, title_override=None):
    """
    Create pie chart for component distribution
    
    Args:
        data (pd.DataFrame): JIRA data
        project_name (str): Project name for title
        title_override (str): Custom title (optional)
    
    Returns:
        str: Base64 encoded image for display
    """
    
    if data.empty or 'Components' not in data.columns:
        print("⚠️  Cannot create pie chart: No component data available")
        return None
    
    # Filter and process data for last 6 months
    data_filtered = data[data['Components'].notna()].copy()
    
    if data_filtered.empty:
        print("⚠️  Cannot create pie chart: No components after filtering")
        return None
    
    # Process dates
    data_filtered['Created'] = pd.to_datetime(data_filtered['Created'], errors='coerce', utc=True)
    data_filtered['Created'] = data_filtered['Created'].dt.tz_localize(None)
    
    # Filter last 6 months
    last_month = data_filtered['Created'].max().to_period('M')
    last_6_months = pd.period_range(end=last_month, periods=6, freq='M').astype(str)
    data_filtered['Created_Month'] = data_filtered['Created'].dt.to_period('M').astype(str)
    data_last6 = data_filtered[data_filtered['Created_Month'].isin(last_6_months)]
    
    if data_last6.empty:
        print("⚠️  No data available for the last 6 months")
        return None
    
    # Create component distribution
    component_counts = data_last6['Components'].value_counts()
    top_n = 10
    top_components = component_counts[:top_n]
    other_count = component_counts[top_n:].sum()
    if other_count > 0:
        top_components['Other'] = other_count
    
    # Create pie chart
    fig, ax = plt.subplots(figsize=(12, 12))
    ax.pie(
        top_components,
        labels=top_components.index,
        autopct='%1.1f%%',
        startangle=140,
        counterclock=False,
        wedgeprops={'edgecolor': 'white'}
    )
    
    chart_title = title_override or f'{project_name} Bugs Distribution by Component (Last 6 Months)'
    ax.set_title(chart_title, fontsize=18, fontweight='bold')
    plt.tight_layout()
    
    # Convert to base64 for display
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    
    # Display the chart
    display(HTML(f"""
    <div style="display: flex; flex-direction: column; align-items: center;">
        <img src="data:image/png;base64,{img_base64}" style="max-width:600px; height:auto; margin: 0 auto 32px auto;" />
    </div>
    """))
    
    return img_base64

def get_notebook_template_code(project_key):
    """
    Generate template code for notebook cell
    
    Args:
        project_key (str): JIRA project key
    
    Returns:
        str: Template code to use in notebook
    """
    
    template = f'''# JIRA Bug Risk Analysis - {project_key} Project
# Using Centralized Configuration

# Import the notebook helper
from notebook_helper import setup_notebook, fetch_and_display_jira_data, create_pie_chart
from component_risk_table import component_risk_table

# Setup notebook with centralized configuration
setup_info = setup_notebook('{project_key}')
project_name = setup_info['project_info']['name']

# Fetch JIRA data using centralized configuration
data = fetch_and_display_jira_data('{project_key}', save_to_csv=True)

# Create pie chart if data exists
if not data.empty:
    create_pie_chart(data, project_name)
    
    # Generate component risk analysis
    component_risk_table(data, project_name)
else:
    print("⚠️  No data available for analysis")
'''
    
    return template

# Example usage function
def show_example_usage():
    """Show example of how to use notebook helper"""
    
    print("📚 Notebook Helper Usage Examples:")
    print("=" * 50)
    
    print("\n1. 🔧 Basic Setup:")
    print("   from notebook_helper import setup_notebook")
    print("   setup_info = setup_notebook('AND')  # For Android project")
    
    print("\n2. 📊 Fetch Data:")
    print("   from notebook_helper import fetch_and_display_jira_data")
    print("   data = fetch_and_display_jira_data('AND')")
    
    print("\n3. 📈 Create Charts:")
    print("   from notebook_helper import create_pie_chart")
    print("   create_pie_chart(data, 'Android Project')")
    
    print("\n4. 📋 Full Template:")
    print("   from notebook_helper import get_notebook_template_code")
    print("   code = get_notebook_template_code('AND')")
    print("   print(code)")
    
    print("\n5. 🔑 Available Project Keys:")
    for code, info in PROJECTS.items():
        print(f"   • {info['key']} - {info['name']}")

def fetch_and_display_trend_analysis(project_key, project_name, months=6):
    """
    Fetch and display historical trend analysis for a project
    """
    print(f"📈 Starting trend analysis for {project_name}...")
    
    try:
        # Use the comprehensive trend analysis function
        result = analyze_project_trends(project_key, project_name, months)
        
        if result:
            print(f"✅ Trend analysis completed!")
            print(f"📊 Analyzed {months} months of data")
            return result
        else:
            print("❌ No trend data available")
            return None
            
    except Exception as e:
        print(f"❌ Error in trend analysis: {e}")
        return None

def create_trend_charts(project_key, project_name, months=6):
    """
    Create trend charts for display in notebooks
    """
    try:
        analyzer = TrendAnalyzer()
        historical_data = analyzer.fetch_historical_data(project_key, months)
        
        if historical_data:
            analyzer.generate_trend_charts(project_key, historical_data, project_name)
            print("✅ Trend charts generated successfully!")
        else:
            print("❌ No historical data available for trend charts")
            
    except Exception as e:
        print(f"❌ Error creating trend charts: {e}")

def get_trend_insights(project_key, months=6):
    """
    Get trend insights for a project
    """
    try:
        analyzer = TrendAnalyzer()
        historical_data = analyzer.fetch_historical_data(project_key, months)
        
        if historical_data:
            insights = analyzer.identify_risk_patterns(historical_data)
            return insights
        else:
            return None
            
    except Exception as e:
        print(f"❌ Error getting trend insights: {e}")
        return None

if __name__ == "__main__":
    show_example_usage() 