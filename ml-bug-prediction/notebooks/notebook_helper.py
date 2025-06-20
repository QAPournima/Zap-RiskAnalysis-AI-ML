"""
Notebook Helper for ML Risk Analysis
===================================

This module provides common functionality for Jupyter notebooks to load
JIRA configuration from the settings system instead of hardcoded credentials.

Usage in notebooks:
    from notebook_helper import load_jira_config, get_project_list
    
    jira_config = load_jira_config()
    projects = get_project_list()
"""

import sys
import os
from typing import Dict, List, Any

# Add parent directory to path to import settings_manager
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from ml_bug_prediction.services.settings_manager import SettingsManager
except ImportError:
    print("❌ Error: Could not import SettingsManager...")

def load_jira_config() -> Dict[str, Any]:
    """
    Load JIRA configuration from the settings system.
    
    Returns:
        Dictionary containing JIRA configuration with keys:
        - jira_url: JIRA server URL
        - username: JIRA email/username  
        - api_token: JIRA API token
        - company_name: Company name from settings
    """
    try:
        settings_manager = SettingsManager()
    except NameError:
        print("❌ SettingsManager not available. Please configure dashboard settings first.")
        return {}
    
    try:
        jira_config = settings_manager.get_jira_config()
        
        # Validate that required fields are present
        required_fields = ['jira_url', 'username', 'api_token']
        missing_fields = [field for field in required_fields if not jira_config.get(field)]
        
        if missing_fields:
            print(f"⚠️  Warning: Missing JIRA configuration fields: {', '.join(missing_fields)}")
            print("📝 Please configure JIRA settings in the main dashboard settings page.")
        else:
            print("✅ JIRA configuration loaded successfully from settings!")
            print(f"📊 JIRA URL: {jira_config.get('jira_url', 'Not configured')}")
            print(f"👤 Email: {jira_config.get('username', 'Not configured')}")
            print(f"🔑 API Token: {'*' * 20}...{jira_config.get('api_token', '')[-10:] if jira_config.get('api_token') else 'Not configured'}")
            print(f"🏢 Company: {jira_config.get('company_name', 'Not configured')}")
        
        return jira_config
        
    except Exception as e:
        print(f"❌ Error loading JIRA configuration: {str(e)}")
        print("📝 Please ensure JIRA settings are configured in the main dashboard.")
        return {}

def get_project_list() -> List[Dict[str, Any]]:
    """
    Get the list of configured projects from settings.
    
    Returns:
        List of project dictionaries with keys:
        - id: Project ID
        - name: Project display name
        - jira_key: JIRA project key
        - enabled_for_analysis: Whether project is enabled
    """
    settings_manager = SettingsManager()
    
    try:
        projects = settings_manager.get_projects()
        
        if projects:
            print(f"📂 Found {len(projects)} configured projects:")
            for project in projects:
                status = "✅ Enabled" if project.get('enabled_for_analysis') else "⏸️  Disabled"
                print(f"   • {project.get('name', 'Unknown')} ({project.get('jira_key', 'Unknown')}) - {status}")
        else:
            print("📂 No projects configured. Please add projects in the dashboard settings.")
        
        return projects
        
    except Exception as e:
        print(f"❌ Error loading projects: {str(e)}")
        return []

def get_project_keys(enabled_only: bool = True) -> List[str]:
    """
    Get a list of JIRA project keys.
    
    Args:
        enabled_only: If True, only return enabled projects. If False, return all projects.
        
    Returns:
        List of JIRA project key strings
    """
    projects = get_project_list()
    
    if enabled_only:
        return [proj.get('jira_key') for proj in projects if proj.get('enabled_for_analysis') and proj.get('jira_key')]
    else:
        return [proj.get('jira_key') for proj in projects if proj.get('jira_key')]

def validate_setup() -> bool:
    """
    Validate that both JIRA configuration and projects are properly set up.
    
    Returns:
        True if setup is valid, False otherwise
    """
    print("🔍 Validating notebook setup...")
    
    # Check JIRA config
    jira_config = load_jira_config()
    jira_valid = bool(jira_config.get('jira_url') and jira_config.get('username') and jira_config.get('api_token'))
    
    # Check projects
    projects = get_project_list()
    projects_valid = len(projects) > 0
    
    if jira_valid and projects_valid:
        print("✅ Setup validation successful! Ready to run analysis.")
        return True
    else:
        print("❌ Setup validation failed:")
        if not jira_valid:
            print("   • JIRA configuration incomplete")
        if not projects_valid:
            print("   • No projects configured")
        print("📝 Please complete setup in the main dashboard settings page.")
        return False

# Example usage and testing
if __name__ == "__main__":
    print("🧪 Testing notebook helper...")
    validate_setup() 