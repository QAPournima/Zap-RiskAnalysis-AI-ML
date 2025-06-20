"""
ML Models and Analysis Components
=================================

This package contains machine learning models, AI engines, and analysis
components for bug risk prediction and trend analysis.

Modules:
- ai_intelligence: Core AI engine for intelligent insights
- trend_analysis: Time series analysis and trend prediction
- component_risk_table: Risk assessment and component analysis
- data_preprocessing: Data cleaning and feature engineering
- model_training: ML model training and evaluation
"""

from .ai_intelligence import AIIntelligenceEngine
from .trend_analysis import TrendAnalyzer
from .component_risk_table import component_risk_table

__all__ = [
    'AIIntelligenceEngine',
    'TrendAnalyzer', 
    'component_risk_table'
] 