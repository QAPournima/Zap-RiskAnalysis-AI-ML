#!/usr/bin/env python3
"""
Bug Risk Analysis Dashboard Startup Script
===========================================

This script starts the Flask web application that provides a dynamic
HTML dashboard for bug risk analysis across multiple projects.

Usage:
    python3 start_dashboard.py

The dashboard will be available at: http://localhost:5001
"""

import os
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """Check if all required dependencies are installed"""
    try:
        import flask
        import pandas
        import jira
        import matplotlib
        import seaborn
        print("✅ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("\n💡 To install dependencies, run:")
        print("pip install -r requirements_webapp.txt")
        return False

def start_dashboard():
    """Start the Flask dashboard application"""
    if not check_dependencies():
        sys.exit(1)
    
    print("🚀 Starting Bug Risk Analysis Dashboard...")
    print("📊 Dashboard will be available at: http://localhost:5001")
    print("🔍 Available projects:")
    print("   • Android (AND) - Android mobile application")
    print("   • iOS Application - iOS mobile application") 
    print("   • WORKSPACE (WS) - Workspace backend analysis")
    print("   • Messaging (MSG) - Messaging system")
    print("\n⏳ Starting server...")
    print("📝 Press Ctrl+C to stop the server")
    print("-" * 50)
    
    # Change to the correct directory
    os.chdir(Path(__file__).parent)
    
    # Start the Flask app
    try:
        from app import app
        app.run(debug=True, host='0.0.0.0', port=5001)
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped by user")
    except Exception as e:
        print(f"❌ Error starting dashboard: {e}")
        sys.exit(1)

if __name__ == "__main__":
    start_dashboard() 