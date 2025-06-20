# 🔧 Settings Management System Guide

## Overview

Your ML Risk Analysis Dashboard now includes a comprehensive settings management system that allows you to:

- **Configure JIRA connection details** dynamically without code changes
- **Manage project mappings** through a user-friendly interface  
- **Auto-discover projects** from your JIRA instance
- **Export/Import configurations** for backup and sharing
- **Test connections** before saving settings

## 📖 How to Access Settings

### Via Dashboard
1. **Click the "⚙️ Settings" button** in the top-right corner of the dashboard
2. Or navigate directly to: `http://localhost:5001/settings`

### Settings Page Features
The settings page has **3 main tabs**:

1. **🔗 JIRA Configuration** - Connection settings
2. **📂 Project Management** - Add/manage projects  
3. **📋 Configuration Summary** - Overview and export/import

---

## 🔗 JIRA Configuration

### Required Fields
- **JIRA Server URL**: Your JIRA instance URL (e.g., `https://your-company.atlassian.net`)
- **Username/Email**: Your JIRA login email
- **API Token**: Generate from JIRA → Account Settings → Security → API tokens

### Optional Fields
- **Environment**: Production/Staging/Development (default: Production)
- **Max Results**: Number of issues per query (default: 1000)

### Test Connection
- Click **"🔍 Test Connection"** to verify your settings before saving
- Shows connection status, user info, and available projects count

---

## 📂 Project Management

### Adding Projects Manually
1. **Project Name**: Display name (e.g., "Android App")
2. **JIRA Project Key**: The key from JIRA (e.g., "AND")
3. **Description**: Optional project description

### Auto-Discovery
- Click **"🔍 Auto-Discover Projects"** to automatically find all JIRA projects
- Only adds new projects (won't duplicate existing ones)
- Uses current JIRA connection settings

### Managing Projects
- **Edit**: Modify project details
- **Delete**: Remove projects permanently
- Projects appear immediately in the dashboard dropdown

---

## 📋 Configuration Summary

### Export Configuration
- **📤 Export Configuration**: Download settings as JSON file
- **Excludes sensitive data** (API tokens) for security
- Useful for backup and sharing team configurations

### Import Configuration  
- **📥 Import Configuration**: Upload previously exported settings
- **Preserves existing API tokens** if not included in import
- Validates JSON format before importing

---

## 🚀 Getting Started

### First-Time Setup

1. **Start the Dashboard**:
   ```bash
   python3 app.py
   ```

2. **Access Settings**:
   - Go to `http://localhost:5001/settings`

3. **Configure JIRA**:
   - Enter your JIRA URL, email, and API token
   - Click "Test Connection" to verify
   - Save configuration

4. **Add Projects**:
   - Use "Auto-Discover Projects" for automatic setup
   - Or manually add projects you want to analyze

5. **Return to Dashboard**:
   - Click "← Back to Dashboard"
   - Your projects will now appear in the dropdown

### Migration from Hardcoded Config

If you previously used hardcoded configuration:

1. **Your existing settings will work** as fallback
2. **Configure via settings page** to override hardcoded values
3. **Settings take precedence** over hardcoded configuration
4. **No code changes required** - completely backward compatible

---

## 🔧 Technical Details

### File Structure
```
ml-bug-prediction/
├── config/                    # Settings directory
│   ├── jira_config.json      # JIRA connection settings
│   └── projects_config.json  # Project mappings
├── settings_manager.py       # Settings management logic
├── settings.html            # Settings page interface
└── app.py                   # Updated with settings integration
```

### API Endpoints
- `GET /settings` - Settings page
- `GET/POST /api/settings/jira` - JIRA configuration
- `POST /api/settings/jira/test` - Test connection
- `GET/POST /api/settings/projects` - Project management
- `POST /api/settings/projects/discover` - Auto-discovery
- `GET /api/settings/summary` - Configuration overview
- `GET /api/settings/export` - Export settings
- `POST /api/settings/import` - Import settings

### Dynamic Configuration
- **Settings auto-refresh** when changed via web interface
- **Fallback to legacy config** if settings files don't exist
- **Thread-safe** configuration updates
- **Validation** for all inputs

---

## 🛡️ Security Features

### API Token Protection
- **Masked in UI** (shows `***` instead of actual token)
- **Not included in exports** for security
- **Preserved during imports** if not provided

### Input Validation
- **URL validation** for JIRA server
- **Duplicate project key prevention**
- **Required field validation**
- **JSON format validation** for imports

### Error Handling
- **Graceful fallbacks** to legacy configuration
- **Clear error messages** for troubleshooting
- **Connection testing** before saving

---

## 📊 Benefits

### For Users
- **No code editing** required for configuration changes
- **Visual interface** for managing projects
- **Instant validation** with connection testing
- **Easy backup/restore** with export/import

### For Teams
- **Share configurations** easily via export/import
- **Team-specific settings** without code changes
- **Environment management** (Production/Staging/Dev)
- **Centralized project management**

### For Administrators
- **Dynamic updates** without restarting application
- **Configuration audit trail** with timestamps
- **Bulk project management** via auto-discovery
- **Settings validation** before deployment

---

## 🔍 Troubleshooting

### Common Issues

**Connection Test Fails**
- Verify JIRA URL is correct and accessible
- Check username/email is valid
- Ensure API token has proper permissions
- Confirm JIRA instance is online

**Projects Not Appearing**
- Check if projects were saved successfully
- Refresh browser page
- Verify JIRA project keys are correct
- Ensure you have access to the projects in JIRA

**Settings Not Saving**
- Check browser console for errors
- Verify disk space for config files
- Ensure proper file permissions
- Check server logs for detailed errors

### Support
- Check server logs in terminal
- Use browser developer tools (F12) for frontend issues
- Test JIRA connection separately using connection test
- Verify file system permissions for config directory

---

## 🎯 Next Steps

1. **Configure your JIRA connection** through the settings page
2. **Auto-discover your projects** for instant setup
3. **Test the dashboard** with your real JIRA data
4. **Export your configuration** for backup
5. **Share settings** with team members if needed

Your dashboard is now **fully configurable** without any code changes! 🚀 