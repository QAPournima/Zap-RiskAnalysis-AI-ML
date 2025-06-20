#!/usr/bin/env python3
"""
Centralized configuration for JIRA Bug Risk Analysis
"""
import os

# Try to load environment variables from .env file (optional)
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Environment variables loaded from .env file")
except ImportError:
    print("ℹ️  python-dotenv not installed - using fallback configuration")
except Exception as e:
    print(f"ℹ️  Could not load .env file: {e} - using fallback configuration")

# JIRA Configuration
JIRA_CONFIG = {
    'URL': os.getenv('JIRA_URL', 'https://your-company.atlassian.net/'),
    'EMAIL': os.getenv('JIRA_EMAIL', 'your-email@company.com'),
    'API_TOKEN': os.getenv('JIRA_API_TOKEN', 'xxxx')
}

# Project configurations
PROJECTS = {
    'AND': {
        'name': 'Android (AND)',
        'notebook': 'notebooks/AND_Bugs_Predict_Report.ipynb',
        'key': 'AND',
        'description': 'Android mobile application bug analysis'
    },
    'iOS': {
        'name': 'iOS Application',
        'notebook': 'notebooks/iOS_Bugs_Predict_Report.ipynb', 
        'key': 'iOS',
        'description': 'iOS mobile application bug analysis'
    },
    'WS': {
        'name': 'WORKSPACE (PH)',
        'notebook': 'notebooks/WS_Bugs_Predict_Report.ipynb',
        'key': 'PH', 
        'description': 'Workspace bug analysis'
    },
    'MSG': {
        'name': 'MESSAGING (MES)',
        'notebook': 'notebooks/MSG_Bugs_Predict_Report.ipynb',
        'key': 'MES',
        'description': 'Messaging bug analysis'
    },
    'AWC': {
        'name': 'Workspace Core (AW)',
        'notebook': 'notebooks/AWC_Bugs_Predict_Report.ipynb',
        'key': 'AW',
        'description': 'Workspace Core bug analysis'
    }
}

# Analysis Configuration
ANALYSIS_CONFIG = {
    'MONTHS_BACK': 6,
    'MAX_RESULTS': 2000,
    'ENVIRONMENT': 'Production',
    'ISSUE_TYPES': ['Bug', 'Support Ticket']
}

# Add ENVIRONMENT to JIRA_CONFIG for consistency
JIRA_CONFIG['ENVIRONMENT'] = ANALYSIS_CONFIG['ENVIRONMENT']

# Add PROJECT_MAPPINGS that matches the structure expected by new modules
PROJECT_MAPPINGS = {
    'AND': {
        'name': 'Android (AND)',
        'jira_key': 'AND',
        'description': 'Android mobile application bug analysis'
    },
    'iOS': {
        'name': 'iOS Application', 
        'jira_key': 'IOS',
        'description': 'iOS mobile application bug analysis'
    },
    'MSG': {
        'name': 'MESSAGING (MES)',
        'jira_key': 'MES',
        'description': 'Messaging bug analysis'
    },
    'AWC': {
        'name': 'Workspace Core (AW)',
        'jira_key': 'AW',
        'description': 'Workspace Core bug analysis'
    },
    'WS': {
        'name': 'WORKSPACE (PH)',
        'jira_key': 'PH',
        'description': 'Workspace bug analysis'
    }
}

def get_jira_credentials():
    """Return JIRA credentials as tuple"""
    return (JIRA_CONFIG['EMAIL'], JIRA_CONFIG['API_TOKEN'])

def get_jql_query(project_key, months_back=6, environment='Production'):
    """Generate JQL query for project analysis"""
    from datetime import datetime, timedelta
    
    date_ago = datetime.now() - timedelta(days=months_back * 30) # 30 days
    date_filter = date_ago.strftime('%Y-%m-%d')
    
    issue_types = ' OR '.join([f'type = "{t}"' for t in ANALYSIS_CONFIG['ISSUE_TYPES']])
    
    jql = (
        f'project = "{project_key}" AND '
        f'({issue_types}) AND '
        f'created >= "{date_filter}" AND '
        f'"Environment[Select List (multiple choices)]" = {environment}'
    )
    
    return jql

def print_config_summary():
    """Print configuration summary for debugging"""
    print("🔧 JIRA Configuration:")
    print(f"   URL: {JIRA_CONFIG['URL']}")
    print(f"   Email: {JIRA_CONFIG['EMAIL']}")
    print(f"   Token: {'*' * 20}...{JIRA_CONFIG['API_TOKEN'][-10:]}")
    print(f"   Projects: {list(PROJECTS.keys())}")
    print(f"   Environment: {ANALYSIS_CONFIG['ENVIRONMENT']}")
    print(f"   Months back: {ANALYSIS_CONFIG['MONTHS_BACK']}") 