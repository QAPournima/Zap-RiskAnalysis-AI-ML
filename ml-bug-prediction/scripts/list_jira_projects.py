#!/usr/bin/env python3

from jira import JIRA
import json

# JIRA Configuration
JIRA_URL = 'https://your-company.atlassian.net/'
EMAIL = 'your-email@company.com'
API_TOKEN = 'ATATT3xFfGF0_73HkQ20uaZKr-Xjn0oRC7-OS7Ve9o99yYWfVxM_6gYSy4YYRGKsr6JMTLAJkelmVElAcsopcfMoUevazYAPabm9x3ShJIS-k9hOYXe1KUJ7isOiahl89vsXpVEQ4qRr8yPldGVyugzzgXHntje4auOnCFD0I1_zP2241rz17hA=28FA7C69'

def list_jira_projects():
    """List all JIRA projects to find correct project keys"""
    try:
        jira = JIRA(server=JIRA_URL, basic_auth=(EMAIL, API_TOKEN))
        
        # Get all projects
        projects = jira.projects()
        
        print("Available JIRA Projects:")
        print("=" * 50)
        print(f"{'Key':<10} {'Name':<30} {'Type':<15}")
        print("-" * 50)
        
        messaging_projects = []
        
        for project in projects:
            print(f"{project.key:<10} {project.name:<30} {getattr(project, 'projectTypeKey', 'N/A'):<15}")
            
            # Look for messaging-related projects
            if any(keyword in project.name.lower() for keyword in ['message', 'msg', 'messaging', 'communication', 'chat']):
                messaging_projects.append((project.key, project.name))
        
        print("\n" + "=" * 50)
        
        if messaging_projects:
            print("\nPossible Messaging-related projects found:")
            for key, name in messaging_projects:
                print(f"  {key} - {name}")
        else:
            print("\nNo obvious messaging-related projects found.")
            print("Please check the full list above for the correct project key.")
        
        return projects
        
    except Exception as e:
        print(f"Error connecting to JIRA: {e}")
        return None

if __name__ == "__main__":
    list_jira_projects() 