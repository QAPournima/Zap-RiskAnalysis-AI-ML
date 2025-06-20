# 📊 Risk Analysis Dashboard

An **enterprise-grade** intelligent bug risk analysis system with **AI-powered insights**, **dynamic configuration**, and **real-time monitoring**.

## 🚀 **Quick Start**

### **1. Setup Environment**
```bash
# Clone the repository
git clone https://github.com/QAPournima/RiskAnalysis-AI-ML.git
cd RiskAnalysis-AI-ML

# Set up virtual environment
python3 -m venv venv_local
source venv_local/bin/activate  # On Windows: venv_local\Scripts\activate

# Install dependencies
pip install -r requirements/requirements_webapp.txt
```

### **2. Start Dashboard**
```bash
# Run the application
python run.py

# Open browser
open http://localhost:5001
```

### **3. Configure JIRA**
1. Click **Settings** (⚙️) in the dashboard
2. Enter your **JIRA URL**, **email**, and **API token**
3. Click **Test Connection** to verify
4. Use **Discover Projects** to auto-add your projects
5. Start analyzing your bug data! 🎯

## 📁 **Project Structure**

This project follows **Python best practices** with a clean, modular architecture:

```
ml-bug-prediction/
├── 🐍 src/ml_bug_prediction/      # Main package
│   ├── 🧠 models/                 # AI/ML models & analysis
│   ├── 🔧 services/               # Business logic services  
│   ├── 🛠️ utils/                  # Utility modules
│   └── 🌐 web/                    # Web components
├── 📚 docs/                       # Documentation
├── 🚀 scripts/                    # Utility scripts
├── 📦 requirements/               # Dependencies
├── 🎨 templates/                  # HTML templates
├── 🎨 static/                     # CSS, JS, images
├── ⚙️ config/                     # Configuration files
├── 💾 data/                       # Data storage
├── 📓 notebooks/                  # Jupyter analysis
└── 🚀 deployments/               # Deployment files
```

## ✨ **Key Features**

- **🤖 AI-Powered Insights**: Executive-level intelligent analysis
- **⚙️ Dynamic Configuration**: Web-based JIRA setup with auto-discovery
- **📊 Real-Time Dashboard**: Live monitoring with auto-refresh
- **📈 Trend Analysis**: Historical patterns and predictive analytics
- **🚨 Smart Alerts**: Automated risk threshold monitoring
- **🔗 JIRA Integration**: Seamless connection with comprehensive testing
- **🎯 Multi-Project**: Unified analysis across all your projects

## 📖 **Documentation**

- **[Complete Documentation](docs/README.md)**: Full project documentation
- **[Project Structure](docs/PROJECT_STRUCTURE.md)**: Detailed architecture guide
- **[Settings Guide](docs/SETTINGS_GUIDE.md)**: Configuration instructions
- **[User Guide](docs/)**: In-depth usage documentation

## 🛠️ **Development**

### **Environment Setup**
```bash
# Development dependencies
pip install -e ".[dev]"

# Run tests
python -m pytest src/tests/

# Format code
black src/ scripts/

# Check code quality  
flake8 src/ scripts/
```

### **Alternative Entry Points**
```bash
# Using scripts
python scripts/start_dashboard.py

# Test JIRA connection
python scripts/test_jira_connection.py

# Environment validation
python scripts/setup_environment.py
```

## 📊 **What's New in v2.0**

### **🏗️ Reorganized Architecture**
- **Modular Package Structure**: Clean separation of concerns
- **Best Practice Organization**: Follows Python packaging standards
- **Professional Development**: Proper testing, linting, documentation

### **🚀 Enhanced Features**
- **Improved Import Structure**: Organized modules for better maintainability
- **Development Tools**: Comprehensive development workflow
- **Distribution Ready**: Can be packaged and distributed properly

## 🔧 **Migration from v1.x**

The application functionality remains **exactly the same** - only the internal organization has improved:

- **✅ Same Web Interface**: Dashboard, settings, all features work identically
- **✅ Same Configuration**: JIRA settings and project configs unchanged
- **✅ Same Data**: All your existing data and configurations preserved
- **✅ Same Performance**: No changes to functionality or speed

**Just use `python run.py` instead of `python app.py`** 🎯

## 🆘 **Support**

- **🐛 Issues**: [GitHub Issues](https://github.com/QAPournima/RiskAnalysis-AI-ML/issues)
- **📖 Documentation**: [docs/README.md](docs/README.md)
- **💬 Help**: Built-in help system in the dashboard

---

**🎉 Transform your bug analysis workflow with enterprise-grade, AI-powered component risk assessment!**

*Now with professional project structure and best-practice architecture for scalable development.* 🚀 