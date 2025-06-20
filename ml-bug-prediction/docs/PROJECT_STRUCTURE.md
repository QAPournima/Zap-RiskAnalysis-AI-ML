# Project Structure Documentation

## Overview

The ML Risk Analysis Dashboard follows Python best practices for package organization, with a clear separation of concerns across different modules and directories.

## Directory Structure

```
ml-risk-analysis/
├── src/ml_bug_prediction/           # Main application package
│   ├── __init__.py                  # Package initialization
│   ├── app.py                       # Flask application (main entry point)
│   ├── config.py                    # Configuration constants
│   ├── models/                      # AI/ML models and analysis
│   │   ├── __init__.py
│   │   ├── ai_intelligence.py       # Core AI engine
│   │   ├── ai_enhancements.py       # AI feature enhancements
│   │   ├── advanced_ai_engine.py    # Advanced AI capabilities
│   │   ├── trend_analysis.py        # Trend analysis and prediction
│   │   ├── component_risk_table.py  # Component risk assessment
│   │   ├── data_preprocessing.py    # Data cleaning and preprocessing
│   │   ├── feature_engineering.py   # Feature extraction
│   │   ├── model_training.py        # ML model training
│   │   ├── model_evaluation.py      # Model evaluation metrics
│   │   └── predict.py               # Prediction utilities
│   ├── services/                    # Business logic services
│   │   ├── __init__.py
│   │   ├── settings_manager.py      # Configuration management
│   │   ├── auth.py                  # Authentication services
│   │   ├── analytics.py             # Business analytics
│   │   └── goal_tracking.py         # Goal management system
│   ├── utils/                       # Utility functions
│   │   ├── __init__.py
│   │   ├── jira_utils.py            # JIRA API integration
│   │   ├── alert_system.py          # Alert and notification system
│   │   └── notebook_helper.py       # Jupyter notebook utilities
│   └── web/                         # Web components (future expansion)
│       └── __init__.py
├── docs/                            # Documentation
│   ├── PROJECT_STRUCTURE.md         # This file
│   ├── README.md                    # Main documentation
│   ├── INTEGRATION_GUIDE.md         # Integration instructions
│   ├── SETTINGS_GUIDE.md            # Settings configuration
│   ├── PWA_FEATURES.md              # Progressive Web App features
│   └── ai_roadmap.md                # AI development roadmap
├── scripts/                         # Utility scripts
│   ├── setup_environment.py         # Environment setup
│   ├── start_dashboard.py           # Dashboard startup script
│   ├── list_jira_projects.py        # JIRA project discovery
│   └── test_jira_connection.py      # JIRA connection testing
├── requirements/                    # Dependencies
│   ├── requirements.txt             # Core dependencies
│   └── requirements_webapp.txt      # Web application dependencies
├── templates/                       # HTML templates
│   ├── dashboard.html               # Main dashboard template
│   ├── settings.html                # Settings page template
│   ├── help.html                    # Help documentation
│   ├── user-guide.html              # User guide
│   ├── use-cases.html               # Use cases examples
│   └── use-cases-documentation.html # Detailed use cases
├── static/                          # Static web assets
│   ├── *.gif                        # Animation assets  
│   ├── manifest.json                # PWA manifest
│   ├── sw.js                        # Service worker
│   ├── offline.html                 # Offline page
│   ├── push-notifications.js        # Push notification handler
│   └── icons/                       # Application icons
├── notebooks/                       # Jupyter notebooks
│   ├── *_Bugs_Predict_Report.ipynb # Analysis notebooks
│   ├── notebook_helper.py           # Notebook utilities
│   └── config/                      # Notebook configurations
├── data/                            # Data storage
│   ├── raw/                         # Raw data files
│   ├── processed/                   # Processed data
│   ├── achievements.json            # Achievement data
│   └── goals.json                   # Goals data
├── deployments/                     # Deployment configurations
│   └── database_schema.sql          # Database schema
├── config/                          # Configuration files
│   ├── jira_config.json             # JIRA settings
│   └── projects_config.json         # Project configurations
├── run.py                           # Main application entry point
├── setup.py                         # Package setup (legacy)
├── pyproject.toml                   # Modern Python packaging
├── Makefile                         # Development commands
├── MANIFEST.in                      # Package distribution files
├── README.md                        # Project documentation
└── .gitignore                       # Git ignore rules
```

## Package Architecture

### Core Application (`src/ml_bug_prediction/`)

The main application package follows a modular architecture:

#### `app.py`
- **Purpose**: Main Flask application with all route handlers
- **Key Features**:
  - Dynamic configuration management
  - RESTful API endpoints
  - Template rendering with proper paths
  - AI-enhanced analysis integration
  - Real-time data caching

#### `config.py`
- **Purpose**: Configuration constants and fallback settings
- **Contains**: Legacy project mappings, JIRA configuration defaults

### AI/ML Models (`models/`)

Contains all machine learning and AI-related components:

#### `ai_intelligence.py`
- **Purpose**: Core AI engine for intelligent insights
- **Features**: Advanced pattern recognition, predictive analytics

#### `trend_analysis.py`
- **Purpose**: Time series analysis and trend prediction
- **Features**: Historical analysis, future trend forecasting

#### `component_risk_table.py`
- **Purpose**: Component-level risk assessment
- **Features**: Risk scoring, component ranking

### Business Services (`services/`)

Business logic and service layer components:

#### `settings_manager.py`
- **Purpose**: Centralized configuration management
- **Features**: 
  - JIRA configuration handling
  - Project settings management
  - Dynamic configuration updates
  - Configuration validation

#### `goal_tracking.py`
- **Purpose**: Goal management and progress tracking
- **Features**: Goal creation, progress monitoring, achievement tracking

### Utility Functions (`utils/`)

Common utilities and helper functions:

#### `jira_utils.py`
- **Purpose**: JIRA API integration and utilities
- **Features**: Connection management, data fetching, error handling

#### `alert_system.py`
- **Purpose**: Risk alerting and notification system
- **Features**: Alert configuration, notification delivery

#### `notebook_helper.py`
- **Purpose**: Jupyter notebook integration
- **Features**: Configuration loading, project data access

## Key Design Decisions

### 1. Package Structure
- **Rationale**: Follows Python packaging best practices
- **Benefits**: Clear separation of concerns, easy testing, better maintainability

### 2. Flask Template Configuration
- **Issue**: Templates not found after reorganization
- **Solution**: Dynamic template and static folder path configuration
- **Implementation**: 
  ```python
  app_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
  template_dir = os.path.join(app_root, 'templates')
  static_dir = os.path.join(app_root, 'static')
  
  app = Flask(__name__, 
              template_folder=template_dir,
              static_folder=static_dir)
  ```

### 3. Import Strategy
- **Problem**: Circular imports and path issues
- **Solution**: Relative imports within package, absolute imports from outside
- **Pattern**: 
  - Within package: `from .services.settings_manager import SettingsManager`
  - From scripts: `from ml_bug_prediction.services.settings_manager import SettingsManager`

### 4. Configuration Management
- **Architecture**: Centralized settings manager with fallback support
- **Benefits**: 
  - Dynamic configuration updates
  - Legacy compatibility
  - Environment-specific settings

## Entry Points

### 1. Main Application (`run.py`)
```python
#!/usr/bin/env python3
import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

if __name__ == "__main__":
    from ml_bug_prediction.app import app
    app.run(host='0.0.0.0', port=5001, debug=False)
```

### 2. Package Entry Point (`setup.py`)
```python
entry_points={
    "console_scripts": [
        "ml-risk-analysis=ml_bug_prediction.app:main",
    ],
}
```

### 3. Development Commands (`Makefile`)
- `make run`: Start the application
- `make install`: Install dependencies
- `make test`: Run tests
- `make clean`: Clean build artifacts

## Testing Strategy

### Test Organization
```
src/tests/
├── test_models/          # Model testing
├── test_services/        # Service layer tests
├── test_utils/           # Utility function tests
└── test_integration/     # Integration tests
```

### Test Execution
```bash
# Run all tests
make test

# Run specific test module
python -m pytest src/tests/test_services/ -v
```

## Deployment Considerations

### 1. Production Deployment
- Use `gunicorn` for WSGI server
- Configure proper logging
- Set environment variables
- Use reverse proxy (nginx)

### 2. Development Setup
```bash
# Quick setup
make dev-setup

# Manual setup
python -m venv venv_local
source venv_local/bin/activate
pip install -r requirements/requirements_webapp.txt
python run.py
```

### 3. Package Installation
```bash
# Development installation
pip install -e .

# Production installation
pip install ml-risk-prediction
```

## Future Enhancements

### 1. Web Package (`web/`)
- API endpoint organization
- Template filters
- Web-specific utilities

### 2. Testing Infrastructure
- Comprehensive test suite
- CI/CD integration
- Code coverage reporting

### 3. Documentation
- API documentation
- User guides
- Development tutorials

## Migration Notes

### From Flat Structure
The reorganization from a flat file structure to a proper package structure involved:

1. **File Movement**: Moving files to appropriate packages
2. **Import Updates**: Updating all import statements
3. **Path Configuration**: Fixing Flask template/static paths
4. **Entry Point Creation**: Creating proper entry points
5. **Package Metadata**: Adding `__init__.py` files and metadata

### Compatibility Considerations
- Legacy configurations still supported
- Gradual migration approach
- Fallback mechanisms for missing configurations
- Backward compatibility for existing integrations

This structure provides a solid foundation for future development while maintaining the existing functionality and user experience. 