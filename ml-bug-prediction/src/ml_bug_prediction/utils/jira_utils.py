#!/usr/bin/env python3
"""
JIRA utility functions for notebooks and Flask app
"""
import pandas as pd
from jira import JIRA
from ..config import JIRA_CONFIG, ANALYSIS_CONFIG, get_jira_credentials, get_jql_query
from datetime import datetime, timedelta

# Try to import settings manager for dynamic configuration
try:
    from ..services.settings_manager import settings_manager
    SETTINGS_MANAGER_AVAILABLE = True
except ImportError:
    SETTINGS_MANAGER_AVAILABLE = False

def connect_to_jira():
    """Create JIRA connection using dynamic or centralized configuration"""
    print("🔧 DEBUG: Starting JIRA connection...")
    
    try:
        # Try to use settings manager first
        if SETTINGS_MANAGER_AVAILABLE:
            print("🔧 DEBUG: Settings manager available, getting config...")
            config = settings_manager.get_jira_connection_config()
            print(f"🔧 DEBUG: Config loaded - URL: {config.get('JIRA_URL', 'NOT SET')}")
            print(f"🔧 DEBUG: Config loaded - USERNAME: {config.get('USERNAME', 'NOT SET')}")
            print(f"🔧 DEBUG: Config loaded - API_TOKEN: {'SET' if config.get('API_TOKEN') else 'NOT SET'}")
            
            if config.get('JIRA_URL') and config.get('USERNAME') and config.get('API_TOKEN'):
                print("🔧 DEBUG: Using settings manager config for JIRA connection")
                return JIRA(
                    server=config['JIRA_URL'], 
                    basic_auth=(config['USERNAME'], config['API_TOKEN'])
                )
            else:
                print("🔧 DEBUG: Settings manager config incomplete, falling back to legacy")
        else:
            print("🔧 DEBUG: Settings manager not available")
    except Exception as e:
        print(f"⚠️ Error using dynamic JIRA config, falling back to legacy: {e}")
    
    # Fallback to legacy configuration
    print("🔧 DEBUG: Using legacy configuration")
    email, api_token = get_jira_credentials()
    print(f"🔧 DEBUG: Legacy URL: {JIRA_CONFIG['URL']}")
    print(f"🔧 DEBUG: Legacy EMAIL: {email}")
    return JIRA(server=JIRA_CONFIG['URL'], basic_auth=(email, api_token))

def fetch_project_data(project_key, months_back=None, environment=None):
    """
    Fetch JIRA data for a specific project
    
    Args:
        project_key (str): JIRA project key (e.g., 'AND', 'IOS')
        months_back (int): Number of months to look back (default from config)
        environment (str): Environment filter (default from config)
    
    Returns:
        pd.DataFrame: Processed JIRA data
    """
    try:
        # Use defaults from config if not specified
        if months_back is None:
            months_back = ANALYSIS_CONFIG['MONTHS_BACK']
        if environment is None:
            environment = ANALYSIS_CONFIG['ENVIRONMENT']
        
        # Connect to JIRA
        jira = connect_to_jira()
        
        # Generate JQL query
        jql = get_jql_query(project_key, months_back, environment)
        print(f"🔍 JQL Query: {jql}")
        
        # Fetch issues
        issues = jira.search_issues(jql, maxResults=ANALYSIS_CONFIG['MAX_RESULTS'], 
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
                'Components': ', '.join([c.name for c in issue.fields.components]) if hasattr(issue.fields, 'components') else None,
            })
        
        df = pd.DataFrame(data)
        
        if not df.empty:
            print(f"✅ Total issues retrieved with Environment = '{environment}': {len(df)}")
        else:
            print(f"⚠️  No issues found for project '{project_key}' with Environment = '{environment}'")
        
        return df
        
    except Exception as e:
        print(f"❌ Error fetching JIRA data for {project_key}: {e}")
        return pd.DataFrame()

def save_project_data(data, project_key, output_dir='../data/processed'):
    """
    Save project data to CSV file
    
    Args:
        data (pd.DataFrame): JIRA data
        project_key (str): Project key for filename
        output_dir (str): Output directory
    """
    import os
    
    if data.empty:
        print(f"⚠️  No data to save for project {project_key}")
        return None
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate filename
    filename = f"jira-{project_key.lower()}-bugs.csv"
    filepath = os.path.join(output_dir, filename)
    
    # Save data
    data.to_csv(filepath, index=False)
    print(f"💾 Data saved to: {filepath}")
    
    return filepath

def get_project_info(project_code):
    """
    Get project information from centralized configuration
    
    Args:
        project_code (str): Project code (e.g., 'AND', 'iOS')
    
    Returns:
        dict: Project information
    """
    from ..config import PROJECTS
    return PROJECTS.get(project_code, None)

def print_available_projects():
    """Print all available projects"""
    from ..config import PROJECTS
    
    print("📊 Available Projects:")
    print("=" * 50)
    for code, info in PROJECTS.items():
        print(f"🔹 {code}: {info['name']} (Key: {info['key']})")
    print("=" * 50)

# Notebook helper functions
def setup_notebook_environment(project_key):
    """
    Setup notebook environment with centralized configuration
    
    Args:
        project_key (str): JIRA project key
    
    Returns:
        tuple: (jira_connection, project_config)
    """
    from ..config import PROJECTS, print_config_summary
    
    # Print configuration summary
    print_config_summary()
    print()
    
    # Find project info
    project_info = None
    for code, info in PROJECTS.items():
        if info['key'] == project_key:
            project_info = info
            break
    
    if not project_info:
        print(f"❌ Project with key '{project_key}' not found in configuration")
        return None, None
    
    print(f"📊 Setting up analysis for: {project_info['name']}")
    
    # Connect to JIRA
    jira = connect_to_jira()
    
    return jira, project_info

# Example usage function
def example_usage():
    """Example of how to use this utility"""
    print("🔧 JIRA Utility Example Usage:")
    print()
    
    # Show available projects
    print_available_projects()
    
    # Fetch data for Android project
    print("\n📱 Fetching Android project data:")
    android_data = fetch_project_data('AND')
    
    if not android_data.empty:
        print(f"📊 Android data shape: {android_data.shape}")
        print(f"📋 Columns: {list(android_data.columns)}")
        
        # Save data
        save_project_data(android_data, 'AND')

if __name__ == "__main__":
    example_usage() 