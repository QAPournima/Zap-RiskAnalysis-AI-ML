#!/usr/bin/env python3
"""
Setup script for JIRA Bug Risk Analysis Environment
"""

import os
import sys
from pathlib import Path

def create_env_file_template():
    """Create a template .env file"""
    
    env_path = Path('.env')
    
    if env_path.exists():
        print("📁 .env file already exists!")
        return False
    
    env_template = """# JIRA Configuration for Bug Risk Analysis
# Copy this template and fill in your actual values

# JIRA Server Configuration
JIRA_URL=https://your-company.atlassian.net/
JIRA_EMAIL=your-email@company.com
JIRA_API_TOKEN=your-jira-api-token-here

# Analysis Configuration
ANALYSIS_MONTHS_BACK=6
ANALYSIS_ENVIRONMENT=Production
ANALYSIS_MAX_RESULTS=2000

# Security Note:
# - Never comproprietary commercial this file to version control
# - Add .env to your .gitignore file
# - Keep your API token secure
"""
    
    try:
        with open(env_path, 'w') as f:
            f.write(env_template)
        
        print("✅ Created .env template file")
        print("📝 Please edit .env with your actual JIRA credentials")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def check_dependencies():
    """Check if all required dependencies are installed"""
    
    print("🔍 Checking dependencies...")
    
    required_packages = [
        'flask',
        'jira',
        'pandas',
        'matplotlib',
        'seaborn',
        'python-dotenv'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} - MISSING")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n📦 Missing packages: {', '.join(missing_packages)}")
        print("💡 Install with: pip install " + ' '.join(missing_packages))
        return False
    else:
        print("✅ All dependencies are installed!")
        return True

def test_configuration():
    """Test the centralized configuration system"""
    
    print("\n🧪 Testing centralized configuration...")
    
    try:
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
        from ml_bug_prediction.config import JIRA_CONFIG, PROJECTS, ANALYSIS_CONFIG, print_config_summary
        
        print("✅ Configuration files imported successfully")
        print(f"✅ Found {len(PROJECTS)} projects configured")
        print(f"✅ JIRA URL: {JIRA_CONFIG['URL']}")
        print(f"✅ Analysis environment: {ANALYSIS_CONFIG['ENVIRONMENT']}")
        
        print("\n📊 Configuration Summary:")
        print_config_summary()
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_jira_connection():
    """Test JIRA connection"""
    
    print("\n🔗 Testing JIRA connection...")
    
    try:
        from jira_utils import connect_to_jira
        
        jira = connect_to_jira()
        
        # Test with a simple query
        projects = jira.projects()
        print(f"✅ JIRA connection successful!")
        print(f"✅ Found {len(projects)} projects in JIRA")
        
        return True
        
    except Exception as e:
        print(f"❌ JIRA connection failed: {e}")
        print("💡 Check your JIRA credentials in .env file")
        return False

def test_notebook_helpers():
    """Test notebook helper functions"""
    
    print("\n📓 Testing notebook helpers...")
    
    try:
        from notebook_helper import setup_notebook, show_example_usage
        from component_risk_table import component_risk_table
        
        print("✅ Notebook helper functions imported successfully")
        
        # Test setup with Android project
        setup_info = setup_notebook('AND', display_config=False)
        print(f"✅ Notebook setup test successful for {setup_info['project_info']['name']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Notebook helper test failed: {e}")
        return False

def show_next_steps():
    """Show what to do next"""
    
    print("\n" + "=" * 60)
    print("🎯 NEXT STEPS")
    print("=" * 60)
    
    print("\n1. 📝 Update .env file with your actual JIRA credentials")
    print("   - Edit the .env file that was created")
    print("   - Replace 'your-email@company.com' with your email")
    print("   - Replace 'your-jira-api-token-here' with your actual token")
    
    print("\n2. 📚 Migrate your notebooks")
    print("   - Follow the NOTEBOOK_MIGRATION_GUIDE.md")
    print("   - Use the templates provided for each project")
    print("   - Test each notebook after migration")
    
    print("\n3. 🚀 Start using centralized configuration")
    print("   - All notebooks will use the same config")
    print("   - Flask dashboard will use the same config")
    print("   - Update config in one place affects everything")
    
    print("\n4. 🧪 Test your setup")
    print("   - Run notebooks to verify they work")
    print("   - Check Flask dashboard functionality")
    print("   - Verify JIRA data fetching")
    
    print("\n📚 Resources:")
    print("   - NOTEBOOK_MIGRATION_GUIDE.md - Complete migration guide")
    print("   - config.py - Central configuration")
    print("   - notebook_helper.py - Helper functions for notebooks")
    print("   - component_risk_table.py - Risk analysis functions")

def main():
    """Main setup function"""
    
    print("🔧 JIRA Bug Risk Analysis Environment Setup")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not Path('config.py').exists():
        print("❌ Error: config.py not found!")
        print("💡 Please run this script from the ml-bug-prediction directory")
        sys.exit(1)
    
    print("📍 Current directory: " + str(Path.cwd()))
    
    # Step 1: Check dependencies
    deps_ok = check_dependencies()
    if not deps_ok:
        print("\n❌ Please install missing dependencies before continuing")
        return
    
    # Step 2: Create .env template
    print("\n" + "-" * 40)
    create_env_file_template()
    
    # Step 3: Test configuration
    print("\n" + "-" * 40)
    config_ok = test_configuration()
    
    # Step 4: Test notebook helpers
    print("\n" + "-" * 40)
    helpers_ok = test_notebook_helpers()
    
    # Step 5: Test JIRA connection (optional, might fail if .env not configured)
    print("\n" + "-" * 40)
    jira_ok = test_jira_connection()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SETUP SUMMARY")
    print("=" * 60)
    
    print(f"Dependencies: {'✅ OK' if deps_ok else '❌ FAILED'}")
    print(f"Configuration: {'✅ OK' if config_ok else '❌ FAILED'}")
    print(f"Notebook Helpers: {'✅ OK' if helpers_ok else '❌ FAILED'}")
    print(f"JIRA Connection: {'✅ OK' if jira_ok else '❌ NEEDS SETUP'}")
    
    if deps_ok and config_ok and helpers_ok:
        print("\n🎉 Setup completed successfully!")
        if not jira_ok:
            print("💡 Configure .env file to enable JIRA connection")
    else:
        print("\n❌ Setup incomplete. Please fix the issues above.")
    
    show_next_steps()

if __name__ == "__main__":
    main() 