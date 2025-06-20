#!/usr/bin/env python3
"""
Settings Management System for ML Risk Analysis Dashboard
Handles JIRA configuration and project management
"""

import json
import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from jira import JIRA
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SettingsManager:
    """Manages dashboard configuration settings"""
    
    def __init__(self, config_dir: str = "config"):
        """Initialize settings manager
        
        Args:
            config_dir: Directory to store configuration files
        """
        # Always use absolute path relative to the project root
        if not os.path.isabs(config_dir):
            # Get the directory where this file is located (services directory)
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # Go up three levels: services -> ml_bug_prediction -> src -> project_root 
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
            self.config_dir = os.path.join(project_root, config_dir)
        else:
            self.config_dir = config_dir
            
        self.jira_config_file = os.path.join(self.config_dir, "jira_config.json")
        self.projects_config_file = os.path.join(self.config_dir, "projects_config.json")
        
        # Create config directory if it doesn't exist
        os.makedirs(self.config_dir, exist_ok=True)
        
        # Initialize default configs if files don't exist
        self._initialize_default_configs()
    
    def _initialize_default_configs(self):
        """Initialize default configuration files if they don't exist"""
        
        # Default JIRA config
        if not os.path.exists(self.jira_config_file):
            default_jira_config = {
                "company_name": "",
                "jira_url": "",
                "username": "",
                "api_token": "",
                "environment": "Production",
                "max_results": 1000,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            self._save_json(self.jira_config_file, default_jira_config)
        
        # Default projects config
        if not os.path.exists(self.projects_config_file):
            default_projects_config = {
                "projects": [],
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            self._save_json(self.projects_config_file, default_projects_config)
    
    def _load_json(self, file_path: str) -> Dict[str, Any]:
        """Load JSON configuration file
        
        Args:
            file_path: Path to JSON file
            
        Returns:
            Configuration dictionary
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Error loading {file_path}: {e}")
            return {}
    
    def _save_json(self, file_path: str, data: Dict[str, Any]) -> bool:
        """Save configuration to JSON file
        
        Args:
            file_path: Path to JSON file
            data: Configuration data
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Add updated timestamp
            data["updated_at"] = datetime.now().isoformat()
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"Error saving {file_path}: {e}")
            return False
    
    # JIRA Configuration Methods
    def get_jira_config(self) -> Dict[str, Any]:
        """Get current JIRA configuration
        
        Returns:
            JIRA configuration dictionary
        """
        return self._load_json(self.jira_config_file)
    
    def get_company_name(self) -> str:
        """Get configured company name
        
        Returns:
            Company name or default fallback
        """
        config = self.get_jira_config()
        return config.get("company_name", "Your Company").strip() or "Your Company"
    
    def save_jira_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Save JIRA configuration
        
        Args:
            config: JIRA configuration data
            
        Returns:
            Dictionary with success status and message
        """
        try:
            current_config = self.get_jira_config()
            
            # Update with new values (preserve existing API token if not provided or masked)
            updates = {
                "company_name": config.get("company_name", "").strip(),
                "jira_url": config.get("jira_url", "").strip(),
                "username": config.get("username", "").strip(),
                "environment": config.get("environment", "Production"),
                "max_results": int(config.get("max_results", 1000))
            }
            
            # Only update API token if provided and not masked
            if "api_token" in config and config["api_token"].strip() and config["api_token"].strip() != "***":
                updates["api_token"] = config["api_token"].strip()
            
            current_config.update(updates)
            
            if self._save_json(self.jira_config_file, current_config):
                return {
                    "success": True,
                    "message": "JIRA configuration saved successfully"
                }
            else:
                return {
                    "success": False,
                    "message": "Failed to save JIRA configuration"
                }
        except Exception as e:
            logger.error(f"Error saving JIRA config: {e}")
            return {
                "success": False,
                "message": f"Error saving configuration: {str(e)}"
            }
    
    def test_jira_connection(self, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Test JIRA connection with given or current configuration
        
        Args:
            config: Optional JIRA configuration to test
            
        Returns:
            Dictionary with test results
        """
        if config is None:
            config = self.get_jira_config()
        
        try:
            # Validate required fields
            required_fields = ['jira_url', 'username', 'api_token']
            for field in required_fields:
                if not config.get(field):
                    return {
                        "success": False,
                        "message": f"Missing required field: {field}"
                    }
            
            # Test JIRA connection
            jira = JIRA(
                server=config['jira_url'],
                basic_auth=(config['username'], config['api_token'])
            )
            
            # Try to get user info to verify connection
            user = jira.myself()
            
            # Try to get projects to verify permissions
            projects = jira.projects()
            
            # Safely extract user information (handle different JIRA API versions)
            user_email = "Unknown"
            user_name = "Unknown"
            
            try:
                # Try different ways to access user email
                if hasattr(user, 'emailAddress'):
                    user_email = user.emailAddress
                elif hasattr(user, 'email'):
                    user_email = user.email
                elif isinstance(user, dict):
                    user_email = user.get('emailAddress', user.get('email', 'Unknown'))
                
                # Try different ways to access user name
                if hasattr(user, 'displayName'):
                    user_name = user.displayName
                elif hasattr(user, 'name'):
                    user_name = user.name
                elif isinstance(user, dict):
                    user_name = user.get('displayName', user.get('name', 'Unknown'))
                    
            except Exception as e:
                logger.warning(f"Could not extract user details: {e}")
            
            # Safely extract server info
            server_title = "Unknown"
            server_version = "Unknown"
            
            try:
                server_info = jira.server_info()
                if isinstance(server_info, dict):
                    server_title = server_info.get('serverTitle', 'Unknown')
                    server_version = server_info.get('version', 'Unknown')
            except Exception as e:
                logger.warning(f"Could not get server info: {e}")
            
            # Get current projects to see which ones are new
            current_projects = self.get_projects()
            current_keys = {p.get("jira_key", "").upper() for p in current_projects}
            
            # Find new projects that could be added
            new_projects = []
            for project in projects[:10]:  # Show first 10 new projects
                project_key = project.key.upper()
                if project_key not in current_keys:
                    new_projects.append({
                        "key": project_key,
                        "name": project.name,
                        "description": getattr(project, 'description', f"JIRA project: {project.name}")
                    })
            
            return {
                "success": True,
                "message": "Connection successful",
                "user_email": user_email,
                "user_name": user_name,
                "projects_count": len(projects),
                "new_projects_count": len([p for p in projects if p.key.upper() not in current_keys]),
                "new_projects_sample": new_projects,
                "can_auto_discover": len([p for p in projects if p.key.upper() not in current_keys]) > 0,
                "server_info": {
                    "server_title": server_title,
                    "version": server_version
                }
            }
            
        except Exception as e:
            logger.error(f"JIRA connection test failed: {e}")
            return {
                "success": False,
                "message": f"Connection failed: {str(e)}"
            }
    
    # Projects Configuration Methods
    def get_projects_config(self) -> Dict[str, Any]:
        """Get current projects configuration
        
        Returns:
            Projects configuration dictionary
        """
        return self._load_json(self.projects_config_file)
    
    def get_projects(self) -> List[Dict[str, Any]]:
        """Get list of configured projects
        
        Returns:
            List of project dictionaries
        """
        config = self.get_projects_config()
        return config.get("projects", [])
    
    def add_project(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add a new project
        
        Args:
            project_data: Project configuration data
            
        Returns:
            Result dictionary with success status and message
        """
        try:
            # Validate required fields
            if not project_data.get("project_name") or not project_data.get("project_key"):
                return {
                    "success": False,
                    "message": "Project name and key are required"
                }
            
            # Load current projects
            config = self.get_projects_config()
            projects = config.get("projects", [])
            
            # Check for duplicate project key
            project_key = project_data["project_key"].upper().strip()
            if any(p.get("jira_key", "").upper() == project_key for p in projects):
                return {
                    "success": False,
                    "message": f"Project with key '{project_key}' already exists"
                }
            
            # Create new project
            new_project = {
                "id": str(uuid.uuid4()),
                "name": project_data["project_name"].strip(),
                "jira_key": project_key,
                "description": project_data.get("description", "").strip(),
                "enabled_for_analysis": project_data.get("enabled_for_analysis", False),  # Default enabled when manually added
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            # Add to projects list
            projects.append(new_project)
            config["projects"] = projects
            
            # Save configuration
            if self._save_json(self.projects_config_file, config):
                return {
                    "success": True,
                    "message": "Project added successfully",
                    "project": new_project
                }
            else:
                return {
                    "success": False,
                    "message": "Failed to save project configuration"
                }
                
        except Exception as e:
            logger.error(f"Error adding project: {e}")
            return {
                "success": False,
                "message": f"Error adding project: {str(e)}"
            }
    
    def update_project(self, project_id: str, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing project
        
        Args:
            project_id: Project ID to update
            project_data: Updated project data
            
        Returns:
            Result dictionary with success status and message
        """
        try:
            config = self.get_projects_config()
            projects = config.get("projects", [])
            
            # Find project to update
            project_index = None
            for i, project in enumerate(projects):
                if project.get("id") == project_id:
                    project_index = i
                    break
            
            if project_index is None:
                return {
                    "success": False,
                    "message": "Project not found"
                }
            
            # Update project
            project = projects[project_index]
            project.update({
                "name": project_data.get("project_name", project.get("name", "")).strip(),
                "jira_key": project_data.get("project_key", project.get("jira_key", "")).upper().strip(),
                "description": project_data.get("description", project.get("description", "")).strip(),
                "enabled_for_analysis": project_data.get("enabled_for_analysis", project.get("enabled_for_analysis", True)),
                "updated_at": datetime.now().isoformat()
            })
            
            projects[project_index] = project
            config["projects"] = projects
            
            # Save configuration
            if self._save_json(self.projects_config_file, config):
                return {
                    "success": True,
                    "message": "Project updated successfully",
                    "project": project
                }
            else:
                return {
                    "success": False,
                    "message": "Failed to save project configuration"
                }
                
        except Exception as e:
            logger.error(f"Error updating project: {e}")
            return {
                "success": False,
                "message": f"Error updating project: {str(e)}"
            }
    
    def delete_project(self, project_id: str) -> Dict[str, Any]:
        """Delete a project
        
        Args:
            project_id: Project ID to delete
            
        Returns:
            Result dictionary with success status and message
        """
        try:
            config = self.get_projects_config()
            projects = config.get("projects", [])
            
            # Find and remove project
            original_count = len(projects)
            projects = [p for p in projects if p.get("id") != project_id]
            
            if len(projects) == original_count:
                return {
                    "success": False,
                    "message": "Project not found"
                }
            
            config["projects"] = projects
            
            # Save configuration
            if self._save_json(self.projects_config_file, config):
                return {
                    "success": True,
                    "message": "Project deleted successfully"
                }
            else:
                return {
                    "success": False,
                    "message": "Failed to save project configuration"
                }
                
        except Exception as e:
            logger.error(f"Error deleting project: {e}")
            return {
                "success": False,
                "message": f"Error deleting project: {str(e)}"
            }
    
    def discover_projects_from_jira(self) -> Dict[str, Any]:
        """Discover projects from JIRA without automatically adding them
        
        Returns:
            Result dictionary with discovered projects list
        """
        try:
            # Get JIRA configuration
            jira_config = self.get_jira_config()
            
            # Check if using test/placeholder credentials
            jira_url = jira_config.get('jira_url', '').lower()
            username = jira_config.get('username', '').lower()
            api_token = jira_config.get('api_token', '')
            
            is_test_credentials = (
                'test' in jira_url or 
                'example' in jira_url or 
                'finaltest' in jira_url or
                'placeholder' in jira_url or
                'demo' in jira_url or
                'test' in username or
                'example' in username or
                'final' in username or
                'demo' in username or
                api_token in ['test_token', 'final_test_token', 'demo_token', 'placeholder_token']
            )
            
            if is_test_credentials:
                # Provide demo projects for testing
                demo_projects = [
                    {
                        "key": "AND",
                        "name": "Android Mobile App",
                        "description": "Main Android application for mobile users",
                        "is_new": True,
                        "already_configured": False,
                        "demo": True
                    },
                    {
                        "key": "IOS", 
                        "name": "iOS Application",
                        "description": "Native iOS app for iPhone and iPad users",
                        "is_new": True,
                        "already_configured": False,
                        "demo": True
                    },
                    {
                        "key": "WEB",
                        "name": "Web Platform",
                        "description": "Main web application and dashboard",
                        "is_new": True,
                        "already_configured": False,
                        "demo": True
                    },
                    {
                        "key": "API",
                        "name": "Core API Services",
                        "description": "Backend API and microservices",
                        "is_new": True,
                        "already_configured": False,
                        "demo": True
                    },
                    {
                        "key": "INT",
                        "name": "Integration Platform",
                        "description": "Third-party integrations and connectors",
                        "is_new": True,
                        "already_configured": False,
                        "demo": True
                    }
                ]
                
                return {
                    "success": True,
                    "message": f"📋 Demo Mode: Showing {len(demo_projects)} sample projects (test credentials detected)",
                    "projects": demo_projects,
                    "total_projects": len(demo_projects),
                    "new_projects": len(demo_projects),
                    "demo_mode": True,
                    "guidance": {
                        "title": "🔗 Connect to Real JIRA",
                        "message": "To discover actual JIRA projects, please configure real JIRA credentials:",
                        "steps": [
                            "1. Go to your JIRA instance (e.g., https://yourcompany.atlassian.net)",
                            "2. Generate an API token: Profile → Account Settings → Security → API Tokens",
                            "3. Use your email address as username",
                            "4. Enter the real JIRA URL, email, and API token above",
                            "5. Click 'Test Connection' to verify, then try Auto-Discover again"
                        ]
                    }
                }
            
            # Test connection first for real credentials
            connection_test = self.test_jira_connection(jira_config)
            if not connection_test["success"]:
                # Enhanced error handling for authentication issues
                error_message = connection_test['message'].lower()
                
                if '401' in error_message or 'authenticated' in error_message:
                    return {
                        "success": False,
                        "message": "🔐 Authentication Failed",
                        "error_type": "authentication",
                        "detailed_message": "JIRA rejected the provided credentials. Please check:",
                        "troubleshooting": [
                            "✅ JIRA URL is correct (e.g., https://yourcompany.atlassian.net)",
                            "✅ Email address is correct",
                            "✅ API token is valid and not expired",
                            "✅ Account has permission to access JIRA projects"
                        ],
                        "help": {
                            "title": "How to fix authentication:",
                            "steps": [
                                "1. Verify your JIRA URL is accessible in a browser",
                                "2. Generate a new API token from JIRA Account Settings",
                                "3. Use your full email address as the username",
                                "4. Test the connection before trying Auto-Discover"
                            ]
                        }
                    }
                elif '404' in error_message or 'not found' in error_message:
                    return {
                        "success": False,
                        "message": "🌐 JIRA URL Not Found",
                        "error_type": "url_not_found",
                        "detailed_message": "The JIRA URL appears to be incorrect or unreachable.",
                        "troubleshooting": [
                            "✅ Check if the JIRA URL works in your browser",
                            "✅ Ensure the URL format: https://yourcompany.atlassian.net",
                            "✅ Verify your company's JIRA instance is accessible"
                        ]
                    }
                else:
                    return {
                        "success": False,
                        "message": f"🔌 JIRA Connection Failed: {connection_test['message']}",
                        "error_type": "connection",
                        "help": "Please check your JIRA configuration and try the 'Test Connection' button first."
                    }
            
            # Connect to JIRA with real credentials
            jira = JIRA(
                server=jira_config['jira_url'],
                basic_auth=(jira_config['username'], jira_config['api_token'])
            )
            
            # Get all projects
            jira_projects = jira.projects()
            
            # Get current projects to identify new ones
            current_projects = self.get_projects()
            current_keys = {p.get("jira_key", "").upper() for p in current_projects}
            
            # Build list of discovered projects
            discovered_projects = []
            for jira_project in jira_projects:
                project_key = jira_project.key.upper()
                
                discovered_projects.append({
                    "key": project_key,
                    "name": jira_project.name,
                    "description": getattr(jira_project, 'description', f"JIRA project: {jira_project.name}"),
                    "is_new": project_key not in current_keys,
                    "already_configured": project_key in current_keys,
                    "demo": False
                })
            
            return {
                "success": True,
                "message": f"✅ Discovered {len(discovered_projects)} projects from JIRA",
                "projects": discovered_projects,
                "total_projects": len(discovered_projects),
                "new_projects": len([p for p in discovered_projects if p["is_new"]]),
                "demo_mode": False
            }
            
        except Exception as e:
            logger.error(f"Error discovering projects: {e}")
            
            # Enhanced error handling for common issues
            error_str = str(e).lower()
            if '401' in error_str or 'unauthorized' in error_str:
                return {
                    "success": False,
                    "message": "🔐 JIRA Authentication Error",
                    "error_type": "authentication",
                    "detailed_message": "Your JIRA credentials are not valid or have expired.",
                    "solution": "Please update your JIRA credentials and try again."
                }
            elif '404' in error_str or 'not found' in error_str:
                return {
                    "success": False,
                    "message": "🌐 JIRA Server Not Found",
                    "error_type": "server_not_found", 
                    "detailed_message": "Cannot connect to the specified JIRA server.",
                    "solution": "Please check your JIRA URL and try again."
                }
            else:
                return {
                    "success": False,
                    "message": f"❌ Discovery Error: {str(e)}",
                    "error_type": "unknown",
                    "solution": "Please check your JIRA configuration and connection."
                }

    def auto_add_discovered_projects(self) -> Dict[str, Any]:
        """Auto-add all discovered projects (legacy functionality)
        
        Returns:
            Result dictionary with added projects count
        """
        try:
            # Discover projects first
            discovery_result = self.discover_projects_from_jira()
            if not discovery_result["success"]:
                return discovery_result
            
            # Add new projects that aren't already configured
            added_count = 0
            for project in discovery_result["projects"]:
                if project["is_new"]:
                    project_data = {
                        "project_name": project["name"],
                        "project_key": project["key"],
                        "description": project["description"],
                        "enabled_for_analysis": False  # Don't enable by default
                    }
                    
                    result = self.add_project(project_data)
                    if result["success"]:
                        added_count += 1
                        logger.info(f"Added project: {project['key']} - {project['name']}")
            
            return {
                "success": True,
                "message": f"Discovery completed. Added {added_count} new projects (not enabled for analysis).",
                "added_count": added_count,
                "total_jira_projects": discovery_result["total_projects"]
            }
            
        except Exception as e:
            logger.error(f"Error auto-adding projects: {e}")
            return {
                "success": False,
                "message": f"Error auto-adding projects: {str(e)}"
            }

    def enable_project_for_analysis(self, project_id: str) -> Dict[str, Any]:
        """Enable a project for dashboard analysis
        
        Args:
            project_id: Project ID to enable
            
        Returns:
            Result dictionary with success status
        """
        try:
            config = self.get_projects_config()
            projects = config.get("projects", [])
            
            # Find project
            for project in projects:
                if project.get("id") == project_id:
                    project["enabled_for_analysis"] = True
                    project["updated_at"] = datetime.now().isoformat()
                    
                    config["projects"] = projects
                    
                    if self._save_json(self.projects_config_file, config):
                        return {
                            "success": True,
                            "message": "Project enabled for analysis successfully"
                        }
                    else:
                        return {
                            "success": False,
                            "message": "Failed to save configuration"
                        }
            
            return {
                "success": False,
                "message": "Project not found"
            }
            
        except Exception as e:
            logger.error(f"Error enabling project: {e}")
            return {
                "success": False,
                "message": f"Error enabling project: {str(e)}"
            }

    def disable_project_for_analysis(self, project_id: str) -> Dict[str, Any]:
        """Disable a project for dashboard analysis
        
        Args:
            project_id: Project ID to disable
            
        Returns:
            Result dictionary with success status
        """
        try:
            config = self.get_projects_config()
            projects = config.get("projects", [])
            
            # Find project
            for project in projects:
                if project.get("id") == project_id:
                    project["enabled_for_analysis"] = False
                    project["updated_at"] = datetime.now().isoformat()
                    
                    config["projects"] = projects
                    
                    if self._save_json(self.projects_config_file, config):
                        return {
                            "success": True,
                            "message": "Project disabled for analysis successfully"
                        }
                    else:
                        return {
                            "success": False,
                            "message": "Failed to save configuration"
                        }
            
            return {
                "success": False,
                "message": "Project not found"
            }
            
        except Exception as e:
            logger.error(f"Error disabling project: {e}")
            return {
                "success": False,
                "message": f"Error disabling project: {str(e)}"
            }
    
    # Configuration Management Methods
    def export_configuration(self) -> Dict[str, Any]:
        """Export complete configuration
        
        Returns:
            Complete configuration dictionary
        """
        jira_config = self.get_jira_config()
        projects_config = self.get_projects_config()
        
        # Remove sensitive information from export
        export_jira_config = jira_config.copy()
        export_jira_config.pop("api_token", None)  # Don't export API token
        
        return {
            "export_info": {
                "exported_at": datetime.now().isoformat(),
                "version": "1.0",
                "tool": "ML Risk Analysis Dashboard"
            },
            "jira_config": export_jira_config,
            "projects_config": projects_config
        }
    
    def import_configuration(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Import configuration from exported data
        
        Args:
            config_data: Configuration data to import
            
        Returns:
            Result dictionary with success status and message
        """
        try:
            imported_count = 0
            
            # Import JIRA config (but preserve existing API token if not provided)
            if "jira_config" in config_data:
                current_jira_config = self.get_jira_config()
                import_jira_config = config_data["jira_config"]
                
                # Preserve existing API token if not in import
                if "api_token" not in import_jira_config and "api_token" in current_jira_config:
                    import_jira_config["api_token"] = current_jira_config["api_token"]
                
                jira_result = self.save_jira_config(import_jira_config)
                if jira_result.get('success'):
                    imported_count += 1
            
            # Import projects config
            if "projects_config" in config_data:
                projects_data = config_data["projects_config"]
                if self._save_json(self.projects_config_file, projects_data):
                    imported_count += 1
            
            return {
                "success": True,
                "message": f"Successfully imported {imported_count} configuration sections",
                "imported_count": imported_count
            }
            
        except Exception as e:
            logger.error(f"Error importing configuration: {e}")
            return {
                "success": False,
                "message": f"Error importing configuration: {str(e)}"
            }
    
    def get_configuration_summary(self) -> Dict[str, Any]:
        """Get summary of current configuration
        
        Returns:
            Configuration summary dictionary
        """
        jira_config = self.get_jira_config()
        projects = self.get_projects()
        
        # JIRA connection status
        jira_configured = bool(jira_config.get("jira_url") and 
                             jira_config.get("username") and 
                             jira_config.get("api_token"))
        
        return {
            "jira_config": {
                "configured": jira_configured,
                "jira_url": jira_config.get("jira_url", ""),
                "username": jira_config.get("username", ""),
                "environment": jira_config.get("environment", "Production"),
                "max_results": jira_config.get("max_results", 1000),
                "last_updated": jira_config.get("updated_at", "Never")
            },
            "projects": {
                "count": len(projects),
                "projects": projects,
                "last_updated": self.get_projects_config().get("updated_at", "Never")
            },
            "system_status": {
                "config_directory": self.config_dir,
                "jira_config_exists": os.path.exists(self.jira_config_file),
                "projects_config_exists": os.path.exists(self.projects_config_file)
            }
        }
    
    # Compatibility Methods for Existing Code
    def get_project_mappings(self) -> Dict[str, Dict[str, str]]:
        """Get project mappings in the format expected by existing code
        Only returns projects that are enabled for analysis
        
        Returns:
            Dictionary mapping project IDs to project info
        """
        projects = self.get_projects()
        mappings = {}
        
        for project in projects:
            # Only include projects enabled for analysis
            if project.get("enabled_for_analysis", True):  # Default True for backward compatibility
                project_id = project.get("jira_key", "").replace("-", "").upper()
                if project_id:
                    mappings[project_id] = {
                        "name": project.get("name", ""),
                        "jira_key": project.get("jira_key", "")
                    }
        
        return mappings
    
    def get_jira_connection_config(self) -> Dict[str, Any]:
        """Get JIRA connection configuration in the format expected by existing code
        
        Returns:
            JIRA connection configuration
        """
        config = self.get_jira_config()
        
        return {
            "JIRA_URL": config.get("jira_url", ""),
            "USERNAME": config.get("username", ""),
            "API_TOKEN": config.get("api_token", ""),
            "ENVIRONMENT": config.get("environment", "Production"),
            "MAX_RESULTS": config.get("max_results", 1000)
        }

    # Reset Methods
    def reset_jira_configuration(self) -> Dict[str, Any]:
        """Reset JIRA configuration to default values
        
        Returns:
            Result dictionary with success status
        """
        try:
            # Create default JIRA configuration
            default_config = {
                "jira_url": "",
                "username": "",
                "api_token": "",
                "environment": "Production",
                "max_results": 1000,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            # Save the reset configuration
            if self._save_json(self.jira_config_file, default_config):
                logger.info("JIRA configuration reset successfully")
                return {
                    "success": True,
                    "message": "JIRA configuration reset successfully"
                }
            else:
                return {
                    "success": False,
                    "message": "Failed to save reset JIRA configuration"
                }
                
        except Exception as e:
            logger.error(f"Error resetting JIRA configuration: {e}")
            return {
                "success": False,
                "message": f"Error resetting JIRA configuration: {str(e)}"
            }

    def reset_projects_configuration(self) -> Dict[str, Any]:
        """Reset all projects configuration
        
        Returns:
            Result dictionary with success status
        """
        try:
            # Create empty projects configuration
            default_config = {
                "projects": [],
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            # Save the reset configuration
            if self._save_json(self.projects_config_file, default_config):
                logger.info("Projects configuration reset successfully")
                return {
                    "success": True,
                    "message": "All projects configuration reset successfully"
                }
            else:
                return {
                    "success": False,
                    "message": "Failed to save reset projects configuration"
                }
                
        except Exception as e:
            logger.error(f"Error resetting projects configuration: {e}")
            return {
                "success": False,
                "message": f"Error resetting projects configuration: {str(e)}"
            }

    def reset_all_configuration(self) -> Dict[str, Any]:
        """Reset both JIRA and projects configuration
        
        Returns:
            Result dictionary with success status
        """
        try:
            jira_result = self.reset_jira_configuration()
            projects_result = self.reset_projects_configuration()
            
            if jira_result["success"] and projects_result["success"]:
                logger.info("All configuration reset successfully")
                return {
                    "success": True,
                    "message": "All configuration reset successfully"
                }
            else:
                errors = []
                if not jira_result["success"]:
                    errors.append(f"JIRA: {jira_result['message']}")
                if not projects_result["success"]:
                    errors.append(f"Projects: {projects_result['message']}")
                
                return {
                    "success": False,
                    "message": f"Partial reset failed: {'; '.join(errors)}"
                }
                
        except Exception as e:
            logger.error(f"Error resetting all configuration: {e}")
            return {
                "success": False,
                "message": f"Error resetting all configuration: {str(e)}"
            }


# Global settings manager instance
settings_manager = SettingsManager() 