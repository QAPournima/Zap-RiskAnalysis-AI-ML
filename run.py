#!/usr/bin/env python3
"""
Main entry point for ML Risk Analysis Dashboard

This script provides a convenient way to start the dashboard
from the reorganized project structure.
"""

import sys
import os

# Add src directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """Main entry point for the dashboard application."""
    try:
        from ml_bug_prediction.app import app
        
        print("🚀 Starting ML Risk Analysis Dashboard...")
        print("📊 Dashboard will be available at: http://localhost:5001")
        print("⚙️ Use Ctrl+C to stop the server")
        print("=" * 60)
        
        # Run the Flask app
        app.run(
            host='0.0.0.0',
            port=5001,
            debug=False
        )
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("💡 Make sure you've installed the requirements:")
        print("   pip install -r requirements/requirements_webapp.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting dashboard: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 