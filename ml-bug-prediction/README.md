# ML Risk Analysis Dashboard 🔧📊🤖

A Product by Zap ⚡️ Team, an intelligent project management tool with an integrated dashboard for predicting and analyzing risks across software projects using machine learning and AI insights.

## ✨ Features

- 🔍 **Real-time Risk Analysis** - Live analysis of JIRA projects with intelligent risk scoring
- 🤖 **AI-Powered Insights** - Advanced AI engine providing intelligent predictions and recommendations
- 📊 **Interactive Dashboard** - Modern web interface with drill-down capabilities and real-time updates
- 🔌 **JIRA Integration** - Seamless integration with Atlassian JIRA for live data fetching
- 🎯 **Goal Tracking** - Set and track bug reduction goals with predictive analytics
- 📈 **Trend Analysis** - Historical trends and predictive modeling for proactive bug management
- 🏢 **Multi-Project Support** - Analyze multiple projects with company-wide insights
- ⚠️ **Smart Alerts** - Intelligent risk alerts and notification system
- 📱 **Progressive Web App** - Offline capabilities and mobile-responsive design

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- JIRA Account with API access
- pip (Python package manager)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/QAPournima/RiskAnalysis-AI-ML.git
   cd RiskAnalysis-AI-ML/ml-bug-prediction
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv_local
   source venv_local/bin/activate  # On Windows: venv_local\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements/requirements_webapp.txt
   ```

4. **Run the dashboard:**
   ```bash
   python run.py
   ```

5. **Open your browser:** http://localhost:5001

## 🔧 How to Use

### 🔐 Initial Setup

#### 1. JIRA Configuration
1. **Navigate to Settings**: Click the ⚙️ Settings icon in the top navigation
2. **JIRA Configuration Section**:
   - **JIRA URL**: Enter your Atlassian JIRA URL (e.g., `https://yourcompany.atlassian.net`)
   - **Email**: Your JIRA account email address
   - **API Token**: Generate a new token at [Atlassian API Tokens](https://id.atlassian.com/manage-profile/security/api-tokens)
   - **Environment**: Select your environment (Production/Staging/Development)
3. **Test Connection**: Click "Test JIRA Connection" to verify your settings
4. **Save Configuration**: Click "Save JIRA Settings"

#### 2. Project Setup
**Option A: Auto-Discovery (Recommended)**
1. In Settings → **Project Management**
2. Click **"Discover Projects"** button
3. System will automatically find all accessible JIRA projects
4. Review discovered projects and enable the ones you want to analyze
5. Click **"Save Projects"**

**Option B: Manual Setup**
1. In Settings → **Project Management**
2. Click **"Add Project"** button
3. Fill in project details:
   - **Project Name**: Display name (e.g., "Android App")
   - **JIRA Key**: JIRA project key (e.g., "AND", "IOS")
   - **Description**: Optional project description
4. **Enable for Analysis**: Toggle to include in dashboard
5. Click **"Add Project"**

### 📊 Using the Dashboard

#### Main Dashboard Overview
- **Project Selector**: Choose specific project or "ALL Projects" for combined analysis
- **Time Filter**: Set date range for analysis (Last 30 days, 90 days, 6 months, Custom)
- **Real-time Metrics**: Live bug counts, risk scores, and trend indicators

#### Analyzing Projects

**1. Single Project Analysis**
```
1. Select project from dropdown
2. Choose time period (default: last 6 months)
3. Click "Analyze Project" button
4. View results in multiple tabs:
   - 📊 Overview: Component breakdown and risk scores
   - 💡 AI Insights: Intelligent analysis and recommendations
   - 📈 Trends: Historical patterns and predictions
   - 🎯 Goals: Set and track improvement targets
```

**2. Multi-Project Analysis**
```
1. Select "ALL Projects" from dropdown
2. Set unified time period
3. Click "Analyze All Projects"
4. Review:
   - Combined risk assessment
   - Cross-project component analysis
   - Company-wide trends
   - Resource allocation insights
```

#### Understanding the Analysis

**Risk Scoring System**
- 🟢 **Low Risk (0-30)**: Stable components, minimal issues
- 🟡 **Medium Risk (31-60)**: Moderate attention needed
- 🟠 **High Risk (61-80)**: Requires immediate attention
- 🔴 **Critical Risk (81-100)**: Emergency action required

**AI Insights Interpretation**
- **Health Score**: Overall project stability (0-100)
- **Business Impact**: Low/Medium/High based on critical components
- **Predictive Alerts**: AI forecasts of potential issues
- **Recommendations**: Actionable improvement suggestions

### 🎯 Goal Management

#### Setting Up Goals
1. **Navigate to Goals Tab** in any project analysis
2. **Create New Goal**:
   - **Goal Type**: Bug Reduction, Component Stability, Quality Improvement
   - **Target**: Specific metric to achieve (e.g., "Reduce bugs by 30%")
   - **Timeline**: Target completion date
   - **Priority**: High/Medium/Low
3. **Track Progress**: System automatically monitors goal progress
4. **Get Predictions**: AI provides completion likelihood and timeline estimates

#### Goal Types Available
- **Bug Reduction**: Decrease total bug count by percentage
- **Component Stability**: Improve specific component health scores
- **Quality Improvement**: Enhance overall project quality metrics
- **Trend Reversal**: Change negative trends to positive

### 📈 Advanced Features

#### Trend Analysis
- **Historical Patterns**: View 6-12 months of historical data
- **Seasonal Trends**: Identify patterns by day/week/month
- **Predictive Modeling**: AI forecasts future trends
- **Anomaly Detection**: Automatic identification of unusual patterns

#### Smart Filtering
```
Available Filters:
- Date Range: Custom start/end dates
- Issue Types: Bugs, Support Tickets, Tasks
- Components: Filter by specific components
- Environment: Production, Staging, Development
- Priority: Critical, High, Medium, Low
- Status: Open, In Progress, Resolved, Closed
```

#### Export & Reporting
1. **Export Data**: Click "Export" to download CSV/Excel reports
2. **Generate Reports**: Create executive summaries and detailed analyses
3. **Share Insights**: Direct links to specific analysis results
4. **Schedule Reports**: Set up automated report generation

### 🚨 Alert System

#### Setting Up Alerts
1. **Navigate to Settings** → **Alert Configuration**
2. **Configure Thresholds**:
   - **Risk Score Alerts**: Trigger when components exceed risk thresholds
   - **Volume Alerts**: Alert on sudden bug volume increases
   - **Trend Alerts**: Notify on negative trend changes
   - **Goal Alerts**: Updates on goal progress and deadlines

#### Alert Delivery Options
- **Dashboard Notifications**: Real-time alerts in the interface
- **Email Notifications**: Send alerts to specified email addresses
- **Webhook Integration**: Connect to Slack, Teams, or other tools

### 🔍 Troubleshooting Common Issues

#### JIRA Connection Problems
```
Issue: "JIRA connection failed"
Solutions:
1. Verify JIRA URL format: https://yourcompany.atlassian.net
2. Check API token is valid and not expired
3. Ensure account has read access to projects
4. Test with "Test JIRA Connection" button
```

#### No Data Found
```
Issue: "No data found for project"
Solutions:
1. Verify project key is correct (case-sensitive)
2. Check date range - expand to include more data
3. Ensure account has access to project issues
4. Verify project exists and has issues in the specified time period
```

#### Performance Issues
```
Issue: Dashboard loading slowly
Solutions:
1. Reduce date range for analysis
2. Analyze fewer projects simultaneously
3. Clear browser cache and refresh
4. Check internet connection stability
```

### 📱 Mobile Usage

#### Mobile Dashboard Features
- **Responsive Design**: Optimized for tablets and smartphones
- **Touch Navigation**: Swipe and tap interactions
- **Offline Mode**: View cached data without internet
- **Push Notifications**: Receive alerts on mobile devices

#### Installing as Mobile App
1. **Open dashboard** in mobile browser
2. **Browser menu** → "Add to Home Screen"
3. **Install prompt** → Click "Install"
4. **Launch** from home screen like native app

### 🔄 Regular Maintenance

#### Best Practices
```
Daily:
- Check dashboard for new alerts
- Review goal progress updates
- Monitor high-risk components

Weekly:
- Analyze trend changes
- Update project configurations
- Review AI recommendations

Monthly:
- Assess goal achievements
- Update alert thresholds
- Generate executive reports
- Review project health scores
```

#### Data Management
- **Cache Management**: System automatically refreshes data every 5 minutes
- **Manual Refresh**: Use "Refresh Data" button for immediate updates
- **Data Retention**: Historical data stored for up to 12 months
- **Backup Settings**: Export configuration for backup/migration

### 🎓 Training & Support

#### Learning Resources
- **User Guide**: Comprehensive tutorial available in Help section
- **Video Tutorials**: Step-by-step demonstration videos
- **Use Cases**: Real-world scenarios and examples
- **Best Practices**: Industry-standard approaches

#### Getting Help
- **In-App Help**: Click ❓ Help icon for context-sensitive assistance
- **Documentation**: Complete guides in the Help section
- **GitHub Issues**: Report bugs and request features
- **Email Support**: Contact zapaitool@gmail.com & qapournima@gmail.com

## 🔧 Development

### Running from Source

```bash
# Install development dependencies
pip install -r requirements/requirements.txt

# Run in development mode
python run.py
```

### Jupyter Notebooks

The `notebooks/` directory contains analysis notebooks:

```python
from notebook_helper import load_jira_config, get_project_list

# Load configuration from dashboard settings
jira_config = load_jira_config()
projects = get_project_list()
```

### Package Installation

Install as a Python package:

```bash
pip install -e .
```

## 🤖 AI Features

### Intelligent Insights
- **Health Scoring**: AI-powered project health assessment
- **Risk Prediction**: Predictive analytics for component failures
- **Trend Forecasting**: Future bug trend predictions
- **Anomaly Detection**: Unusual pattern identification

### AI-Enhanced Analytics
- **Smart Component Analysis**: Intelligent component risk ranking
- **Predictive Alerts**: Proactive risk notifications
- **Executive Summaries**: AI-generated business impact reports
- **Recommendation Engine**: Actionable improvement suggestions

## 📊 Dashboard Features

### Main Dashboard
- **Project Overview**: Multi-project health dashboard
- **Risk Analytics**: Interactive risk assessment charts
- **Real-time Updates**: Live data refresh capabilities
- **Drill-down Analysis**: Detailed component-level insights

### Advanced Features
- **Goal Tracking**: Set and monitor bug reduction targets
- **Trend Analysis**: Historical and predictive trend visualization
- **Alert Management**: Configurable risk alert system
- **Settings Management**: Comprehensive configuration interface

## 🔌 JIRA Integration

### Supported Features
- **Real-time Data**: Live JIRA data fetching
- **Project Discovery**: Automatic project detection
- **Custom JQL**: Advanced query support
- **Multi-Environment**: Support for different JIRA environments

### API Compatibility
- JIRA Cloud ✅
- JIRA Server ✅
- JIRA Data Center ✅

## 📱 Progressive Web App

- **Offline Support**: Works without internet connection
- **Mobile Responsive**: Optimized for all devices
- **Install Prompt**: Add to home screen capability
- **Push Notifications**: Real-time alert delivery

## 🛠️ Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # Ensure virtual environment is activated
   source venv_local/bin/activate
   pip install -r requirements/requirements_webapp.txt
   ```

2. **JIRA Connection Issues**
   - Verify API token is valid
   - Check JIRA URL format: `https://yourcompany.atlassian.net`
   - Ensure account has project access

3. **Template Not Found**
   - Ensure you're running from the correct directory
   - Check that templates/ directory exists

### Debug Mode

Enable debug output:
```bash
export FLASK_DEBUG=1
python run.py
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Comproprietary commercial your changes (`git comproprietary commercial -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License
Zap⚡ will be offered under a proprietary commercial license. While we believe in transparency and developer empowerment, our core platform will be protected as commercial intellectual property to support long-term sustainability and innovation.

We may release selected SDKs, API clients, or integration plugins as open-source tools to encourage developer adoption and third-party integrations. However, the main platform, AI engine, and dashboard components will remain under commercial licensing.

This approach ensures we can continue to offer enterprise-grade features, strong security, and dedicated support while maintaining control over our product roadmap.

## 🙏 Acknowledgments

- **JIRA API** for seamless integration
- **Flask** for the web framework
- **Pandas & NumPy** for data analysis
- **Chart.js** for interactive visualizations
- **Bootstrap** for responsive UI

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/QAPournima/RiskAnalysis-AI-ML/issues)
- **Documentation**: [Project Wiki](https://github.com/QAPournima/RiskAnalysis-AI-ML/wiki)
- **Email**: zapaitool@gmail.com & qapournima@gmail.com 
- 
---

**Made with ❤️ for better software quality by Zap⚡️ Team** 
