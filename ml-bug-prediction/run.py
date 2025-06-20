#!/usr/bin/env python3
"""
Main entry point for ML Risk Analysis Dashboard
"""
import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

if __name__ == "__main__":
    try:
        from ml_bug_prediction.app import app
        print("🚀 Starting ML Risk Analysis Dashboard at http://localhost:5001")
        app.run(host='0.0.0.0', port=5001, debug=False)
    except ImportError as e:
        print(f"❌ Error: {e}")
        print("💡 Install requirements: pip install -r requirements/requirements_webapp.txt")
    except Exception as e:
        print(f"❌ Error: {e}") 