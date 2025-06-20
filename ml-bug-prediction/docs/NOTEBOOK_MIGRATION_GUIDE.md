# 📚 Notebook Migration Guide: Using Centralized JIRA Configuration

## 🎯 Overview

This guide shows you how to update all your notebook files (`.ipynb`) to use centralized JIRA configuration from `config.py` instead of hardcoded credentials and settings.

## ✅ Benefits of Settings System Integration

- 🔒 **Enhanced Security**: 
  - No hardcoded API tokens in notebook files
  - Credentials managed through secure settings system
  - No risk of accidental credential exposure in version control

- 🎯 **Dashboard Integration**: 
  - Configure once in the dashboard settings page
  - Automatic validation and connection testing
  - Company-agnostic configuration with dynamic naming

- 🔄 **Consistency**: 
  - Same JIRA configuration across all notebooks and main application
  - Centralized project management and enablement
  - Unified settings system for the entire platform

- 🛠️ **Superior Maintainability**: 
  - Update credentials in one place (settings UI)
  - Easy project enable/disable without touching code
  - Visual configuration management

- 📝 **Cleaner Code**: 
  - 2-3 lines of code vs 50+ lines of connection logic
  - Helper functions handle all complexity
  - Notebooks focus purely on analysis

- ♻️ **Advanced Reusability**: 
  - Notebook helper provides consistent API
  - Automatic setup validation and error handling
  - Shared configuration across development and production

## 🔧 Setup Instructions

### 1. Configure Dashboard Settings (Recommended Approach)

**The easiest way is to use the dashboard settings page:**

1. Start the dashboard: `python app.py`
2. Go to `/settings` in your browser  
3. Configure:
   - Company Name (required)
   - JIRA URL, username, and API token
   - Add and enable projects for analysis
4. Test the connection to ensure everything works

### 2. Environment Variables (Legacy Approach - Optional)

Create a `.env` file in the `ml-bug-prediction/` directory:

```bash
# JIRA Configuration
JIRA_URL=https://your-company.atlassian.net/
JIRA_EMAIL=your-email@company.com
JIRA_API_TOKEN=your-api-token-here

# Analysis Configuration
ANALYSIS_MONTHS_BACK=6
ANALYSIS_ENVIRONMENT=Production
```

**Note**: The system works with or without environment variables (uses fallback values).

### 2. Verify Setup

Run this in a notebook cell to test the configuration:

```python
# Test centralized configuration
import sys
sys.path.append('..')

from config import print_config_summary
print_config_summary()
```

## 📊 Notebook Update Templates

### ✅ NEW Recommended Approach (Settings System)

Replace your existing JIRA connection code with this modern approach:

```python
# Load JIRA configuration from dashboard settings
from notebook_helper import load_jira_config, validate_setup, get_project_list

# Validate that everything is set up correctly
if not validate_setup():
    raise ValueError("❌ Please configure JIRA settings in the dashboard settings page")

# Load configuration from settings system
jira_config = load_jira_config()
JIRA_URL = jira_config.get('jira_url')
EMAIL = jira_config.get('username') 
API_TOKEN = jira_config.get('api_token')

# Project configuration
PROJECT_KEY = 'YOUR_PROJECT'  # e.g., 'AND', 'iOS', 'WS'
Environment = 'Production'    # or 'Staging'

# The rest of your analysis code stays the same...
```

### Legacy Template (Environment Variables)

If you prefer environment variables, you can still use this template:

```python
# JIRA Bug Risk Analysis - [PROJECT_NAME] Project
# Using Centralized Configuration System

# Import required libraries
import jinja2
print(f"Jinja2 version: {jinja2.__version__}")

# Import centralized configuration system
import sys
sys.path.append('..')  # Add parent directory to path

from notebook_helper import setup_notebook, fetch_and_display_jira_data, create_pie_chart
from component_risk_table import component_risk_table
from IPython.display import display, HTML

print("🔧 JIRA Bug Risk Analysis - [PROJECT_NAME] Project")
print("=" * 60)

# Setup notebook with centralized configuration
setup_info = setup_notebook('[PROJECT_KEY]', display_config=True)
project_name = setup_info['project_info']['name']
project_key = setup_info['project_key']

# Fetch JIRA data using centralized configuration
data = fetch_and_display_jira_data(project_key, save_to_csv=True)

# Display title and create visualizations
report_title_html = f"""
<div style="background: #111; border-radius: 12px; padding: 18px 28px; margin-bottom: 24px; box-shadow: 0 2px 8px #222; text-align:center;">
    <h2 style="margin-top:0; color:#ffe066;">🔎 <b>Bug Risk Analysis: {project_name}</b></h2>
    <p style="font-size: 1.5em; color: #fff; margin: 0 auto; display: inline-block; text-align: center;">
        Analyzing bug distribution and risk scores to spotlight the most vulnerable components.<br>
        <b>Data window:</b> Last 6 months<br>
        <b>Use:</b> Guide testing, triage, and resource allocation.
    </p>
</div>
"""
display(HTML(report_title_html))

# Create pie chart if data exists
if not data.empty:
    create_pie_chart(data, project_name)
    
    # Generate component risk analysis
    component_risk_table(data, project_name)
else:
    print("⚠️  No data available for analysis")
```

## 🗂️ Project-Specific Templates

### 1. Android Project (`AND_Bugs_Predict_Report.ipynb`)
```python
# Replace [PROJECT_NAME] with: Android
# Replace [PROJECT_KEY] with: AND
```

### 2. iOS Project (`iOS_Bugs_Predict_Report.ipynb`)
```python
# Replace [PROJECT_NAME] with: iOS
# Replace [PROJECT_KEY] with: IOS
```

### 3. Messaging Project (`MSG_Bugs_Predict_Report.ipynb`)
```python
# Replace [PROJECT_NAME] with: Messaging
# Replace [PROJECT_KEY] with: MES
```

### 4. Workspace Core Project (`AWC_Bugs_Predict_Report.ipynb`)
```python
# Replace [PROJECT_NAME] with: Workspace Core
# Replace [PROJECT_KEY] with: AW
```

### 5. Workspace Project (`WS_Bugs_Predict_Report.ipynb`)
```python
# Replace [PROJECT_NAME] with: Workspace
# Replace [PROJECT_KEY] with: PH
```

## 🔄 Migration Steps

### For Each Notebook:

1. **Open the notebook** in Jupyter/VSCode
2. **Identify the main cell** with JIRA connection code
3. **Replace entire cell content** with the appropriate template above
4. **Update the project name and key** as shown in project-specific templates
5. **Save and test** the notebook

### Before (Old Way):
```python
# ❌ OLD hardcoded approach - NOT RECOMMENDED
# JIRA_URL = 'https://your-company.atlassian.net/'
# EMAIL = 'your-email@company.com'
# API_TOKEN = 'long-token-here...'
# PROJECT_KEY = 'AND'

# ✅ NEW approach - Use settings system
from notebook_helper import load_jira_config, validate_setup

# Validate setup and load configuration
if not validate_setup():
    raise ValueError("Please configure JIRA settings in the main dashboard")

jira_config = load_jira_config()
JIRA_URL = jira_config.get('jira_url')
EMAIL = jira_config.get('username')
API_TOKEN = jira_config.get('api_token')
PROJECT_KEY = 'AND'  # Or get from settings
# ... lots of JIRA connection code
# ... data fetching logic
# ... chart generation code
# ... component analysis function
```

### After (New Way):
```python
# New centralized approach - 10 lines of code
from notebook_helper import setup_notebook, fetch_and_display_jira_data, create_pie_chart
from component_risk_table import component_risk_table

setup_info = setup_notebook('AND')
data = fetch_and_display_jira_data('AND')
create_pie_chart(data, setup_info['project_info']['name'])
component_risk_table(data, setup_info['project_info']['name'])
```

## 🛡️ Security Best Practices

### Option 1: Environment Variables (Recommended)
1. Create `.env` file with credentials
2. Never comproprietary commercial `.env` to version control
3. Add `.env` to `.gitignore`

### Option 2: Fallback Configuration
- Uses hardcoded values in `config.py` as fallback
- Still more secure than having credentials in every notebook

## 🔍 Available Helper Functions

### From `notebook_helper.py`:
- `setup_notebook(project_key)` - Initialize notebook with project config
- `fetch_and_display_jira_data(project_key)` - Fetch and display JIRA data
- `create_pie_chart(data, project_name)` - Generate component distribution chart

### From `component_risk_table.py`:
- `component_risk_table(data, project_name)` - Generate risk analysis table

### From `config.py`:
- `print_config_summary()` - Display current configuration
- `get_jira_credentials()` - Get JIRA credentials
- `get_jql_query(project_key)` - Generate JQL query

## 🎯 Project Key Reference

| Notebook File | Project Name | Project Key |
|---------------|--------------|-------------|
| `AND_Bugs_Predict_Report.ipynb` | Android | `AND` |
| `iOS_Bugs_Predict_Report.ipynb` | iOS | `IOS` |
| `MSG_Bugs_Predict_Report.ipynb` | Messaging | `MES` |
| `AWC_Bugs_Predict_Report.ipynb` | Workspace Core | `AW` |
| `WS_Bugs_Predict_Report.ipynb` | Workspace | `PH` |

## 🧪 Testing Your Migration

After updating each notebook, test with:

```python
# Test cell - run this in any notebook
from notebook_helper import show_example_usage
show_example_usage()
```

## ❓ Troubleshooting

### Import Errors
```python
# If you get import errors, add this at the top:
import sys
sys.path.append('..')
```

### JIRA Connection Issues
```python
# Test JIRA connection manually:
from config import print_config_summary
print_config_summary()
```

### Environment Variable Issues
- Check if `.env` file exists in correct directory
- Verify environment variable names match exactly
- Use fallback configuration if needed

## 🎉 Benefits After Migration

- **📝 Cleaner notebooks**: 90% less configuration code
- **🔄 Consistent results**: All notebooks use same JIRA settings
- **🛠️ Easy maintenance**: Update config in one place
- **🔒 Better security**: Credentials centralized
- **⚡ Faster development**: Focus on analysis, not setup

## 📞 Need Help?

If you encounter issues during migration:
1. Check the `NOTEBOOK_MIGRATION_GUIDE.md` file
2. Run the test functions provided
3. Verify your environment setup
4. Check that all helper files are in the correct location

---

**Happy Analyzing! 🎯📊** 