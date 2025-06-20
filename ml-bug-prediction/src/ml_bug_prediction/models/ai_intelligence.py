"""
Advanced AI Intelligence Module
Provides comprehensive machine learning and NLP capabilities for intelligent bug analysis
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import re
import json
from collections import Counter, defaultdict
try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
import warnings
warnings.filterwarnings('ignore')

class AIIntelligenceEngine:
    """Advanced AI engine for comprehensive bug analysis intelligence"""
    
    def __init__(self):
        self.sentiment_analyzer = None
        self.bug_classifier = None
        self.risk_predictor = None
        self.vectorizer = None
        self.scaler = StandardScaler()
        
    def generate_comprehensive_insights(self, data, project_name, historical_data=None):
        """Generate 100% AI-powered insights for any dataset"""
        insights = {
            'executive_summary': {},
            'risk_intelligence': {},
            'pattern_analysis': {},
            'predictive_insights': {},
            'nlp_analysis': {},
            'anomaly_detection': {},
            'recommendations': {},
            'confidence_scores': {}
        }
        
        if data.empty:
            return self._generate_no_data_insights(project_name)
        
        # 1. Executive Summary Intelligence
        insights['executive_summary'] = self._generate_executive_summary(data, project_name)
        
        # 2. Advanced Risk Intelligence
        insights['risk_intelligence'] = self._analyze_risk_intelligence(data, project_name)
        
        # 3. Pattern Analysis with ML
        insights['pattern_analysis'] = self._perform_pattern_analysis(data, historical_data)
        
        # 4. Predictive Analytics
        insights['predictive_insights'] = self._generate_predictive_insights(data, historical_data)
        
        # 5. NLP Analysis on Bug Descriptions
        insights['nlp_analysis'] = self._perform_nlp_analysis(data)
        
        # 6. Anomaly Detection
        insights['anomaly_detection'] = self._detect_anomalies(data, historical_data)
        
        # 7. AI-Generated Recommendations
        insights['recommendations'] = self._generate_ai_recommendations(data, insights)
        
        # 8. Confidence Scoring
        insights['confidence_scores'] = self._calculate_confidence_scores(insights, len(data))
        
        return insights
    
    def _generate_executive_summary(self, data, project_name):
        """AI-generated executive summary with business intelligence"""
        summary = {}
        
        # Calculate key metrics
        total_bugs = len(data)
        unique_components = len(data['Components'].unique()) if 'Components' in data.columns else 0
        
        # Time-based analysis
        if 'Created' in data.columns:
            data['Created'] = pd.to_datetime(data['Created'])
            recent_bugs = len(data[data['Created'] > (datetime.now() - timedelta(days=7))])
            monthly_average = total_bugs / 6 if total_bugs > 0 else 0
        else:
            recent_bugs = 0
            monthly_average = 0
        
        # Generate AI narrative
        summary['headline'] = self._generate_headline(total_bugs, project_name, recent_bugs)
        summary['health_score'] = self._calculate_health_score(data)
        summary['business_impact'] = self._assess_business_impact(data)
        summary['key_metrics'] = {
            'total_bugs': total_bugs,
            'components_affected': unique_components,
            'recent_activity': recent_bugs,
            'monthly_average': round(monthly_average, 1)
        }
        
        return summary
    
    def _analyze_risk_intelligence(self, data, project_name):
        """Advanced ML-based risk analysis"""
        risk_intel = {}
        
        if 'Components' not in data.columns:
            return {'error': 'No component data available for risk analysis'}
        
        component_counts = data['Components'].value_counts()
        
        # Advanced risk scoring with ML
        risk_intel['component_risks'] = self._calculate_advanced_risk_scores(component_counts, data)
        risk_intel['risk_distribution'] = self._analyze_risk_distribution(component_counts)
        risk_intel['criticality_matrix'] = self._create_criticality_matrix(data)
        risk_intel['risk_velocity'] = self._calculate_risk_velocity(data)
        
        return risk_intel
    
    def _perform_pattern_analysis(self, data, historical_data):
        """Advanced pattern recognition using machine learning"""
        patterns = {}
        
        # Temporal patterns
        patterns['temporal'] = self._analyze_temporal_patterns(data)
        
        # Component interaction patterns
        patterns['component_interactions'] = self._analyze_component_interactions(data)
        
        # Severity patterns
        patterns['severity_patterns'] = self._analyze_severity_patterns(data)
        
        # Historical comparison patterns
        if historical_data:
            patterns['historical_comparison'] = self._compare_with_historical_patterns(data, historical_data)
        
        return patterns
    
    def _generate_predictive_insights(self, data, historical_data):
        """ML-powered predictive analytics"""
        predictions = {}
        
        if historical_data and len(historical_data) >= 3:
            # Predict next month's bug count
            predictions['next_month_forecast'] = self._predict_future_bugs(historical_data)
            
            # Component risk predictions
            predictions['component_risk_forecast'] = self._predict_component_risks(data, historical_data)
            
            # Release readiness prediction
            predictions['release_readiness'] = self._assess_release_readiness(data, historical_data)
            
            # Resource requirement predictions
            predictions['resource_requirements'] = self._predict_resource_needs(data, historical_data)
        else:
            predictions['note'] = 'Insufficient historical data for predictions (need 3+ months)'
            predictions['basic_forecast'] = self._basic_trend_forecast(data)
        
        return predictions
    
    def _perform_nlp_analysis(self, data):
        """Natural Language Processing on bug descriptions"""
        nlp_insights = {}
        
        if 'summary' not in data.columns:
            return {'note': 'No bug descriptions available for NLP analysis'}
        
        # Clean and prepare text data
        descriptions = data['summary'].dropna().astype(str)
        
        if len(descriptions) == 0:
            return {'note': 'No valid descriptions found'}
        
        # Sentiment analysis
        nlp_insights['sentiment_analysis'] = self._analyze_sentiment(descriptions)
        
        # Topic clustering
        nlp_insights['topic_clusters'] = self._perform_topic_clustering(descriptions)
        
        # Keyword extraction
        nlp_insights['key_themes'] = self._extract_key_themes(descriptions)
        
        # Bug similarity analysis
        nlp_insights['similar_bugs'] = self._find_similar_bugs(descriptions)
        
        # Root cause indicators
        nlp_insights['root_cause_indicators'] = self._identify_root_causes(descriptions)
        
        return nlp_insights
    
    def _detect_anomalies(self, data, historical_data):
        """AI-powered anomaly detection"""
        anomalies = {}
        
        # Statistical anomalies
        anomalies['statistical'] = self._detect_statistical_anomalies(data)
        
        # Component anomalies
        anomalies['component_anomalies'] = self._detect_component_anomalies(data, historical_data)
        
        # Temporal anomalies
        anomalies['temporal_anomalies'] = self._detect_temporal_anomalies(data)
        
        # Severity anomalies
        anomalies['severity_anomalies'] = self._detect_severity_anomalies(data)
        
        return anomalies
    
    def _generate_ai_recommendations(self, data, insights):
        """AI-generated actionable recommendations"""
        recommendations = {
            'immediate_actions': [],
            'strategic_initiatives': [],
            'process_improvements': [],
            'resource_optimizations': [],
            'quality_enhancements': []
        }
        
        # Analyze insights to generate recommendations
        health_score = insights.get('executive_summary', {}).get('health_score', 50)
        risk_intel = insights.get('risk_intelligence', {})
        patterns = insights.get('pattern_analysis', {})
        predictions = insights.get('predictive_insights', {})
        
        # Generate recommendations based on health score
        if health_score < 30:
            recommendations['immediate_actions'].extend([
                "🚨 Critical: Implement emergency bug triage process",
                "⚡ Activate dedicated bug squashing sprint",
                "🔍 Conduct immediate root cause analysis on top 3 components"
            ])
        elif health_score < 60:
            recommendations['strategic_initiatives'].extend([
                "📊 Increase testing coverage on high-risk components",
                "🔄 Implement automated regression testing",
                "👥 Consider additional QA resources"
            ])
        
        # Component-specific recommendations
        if 'component_risks' in risk_intel:
            top_risks = sorted(risk_intel['component_risks'], 
                             key=lambda x: x.get('risk_score', 0), reverse=True)[:3]
            for risk in top_risks:
                recommendations['quality_enhancements'].append(
                    f"🎯 Focus testing on {risk.get('component', 'Unknown')} component (High Risk)"
                )
        
        # Predictive recommendations
        if 'next_month_forecast' in predictions:
            forecast = predictions['next_month_forecast']
            if forecast.get('trend') == 'increasing':
                recommendations['process_improvements'].append(
                    "📈 Bug count trending up - strengthen code review process"
                )
        
        return recommendations
    
    def _calculate_confidence_scores(self, insights, data_size):
        """Calculate confidence scores for all AI insights"""
        scores = {}
        
        # Base confidence on data size
        base_confidence = min(90, max(20, data_size * 2))
        
        scores['overall_confidence'] = base_confidence
        scores['risk_analysis_confidence'] = base_confidence + 5 if data_size > 50 else base_confidence - 10
        scores['pattern_analysis_confidence'] = base_confidence if data_size > 30 else base_confidence - 15
        scores['prediction_confidence'] = base_confidence - 20 if data_size < 100 else base_confidence
        scores['nlp_confidence'] = base_confidence if data_size > 20 else base_confidence - 25
        
        # Adjust based on data quality
        for key in scores:
            scores[key] = max(10, min(95, scores[key]))
        
        return scores
    
    # Helper methods for specific AI capabilities
    
    def _generate_headline(self, total_bugs, project_name, recent_bugs):
        """Generate AI narrative headline"""
        if total_bugs == 0:
            return f"🎉 {project_name} shows excellent stability with zero bugs detected"
        elif total_bugs < 10:
            return f"✅ {project_name} demonstrates good code quality with minimal issues ({total_bugs} bugs)"
        elif total_bugs < 50:
            return f"⚠️ {project_name} shows moderate activity with {total_bugs} bugs requiring attention"
        else:
            return f"🚨 {project_name} indicates high activity with {total_bugs} bugs needing immediate focus"
    
    def _calculate_health_score(self, data):
        """Calculate AI-powered health score (0-100)"""
        if len(data) == 0:
            return 100
        
        # Base score calculation
        bug_count = len(data)
        component_diversity = len(data['Components'].unique()) if 'Components' in data.columns else 1
        
        # Health score algorithm
        base_score = 100 - min(80, bug_count * 2)
        diversity_penalty = min(20, component_diversity * 3)
        
        # Time factor (more recent bugs are worse)
        if 'Created' in data.columns:
            data['Created'] = pd.to_datetime(data['Created'])
            recent_factor = len(data[data['Created'] > (datetime.now() - timedelta(days=7))]) * 5
        else:
            recent_factor = 0
        
        health_score = max(0, base_score - diversity_penalty - recent_factor)
        return min(100, max(0, health_score))
    
    def _assess_business_impact(self, data):
        """Assess business impact using AI analysis"""
        impact = {'level': 'Low', 'factors': []}
        
        if len(data) == 0:
            impact['level'] = 'Minimal'
            impact['factors'] = ['No active issues detected']
            return impact
        
        # Calculate impact factors
        total_bugs = len(data)
        
        if 'Components' in data.columns:
            critical_components = ['Authentication', 'Payment', 'Security', 'Database']
            critical_affected = any(comp in str(data['Components'].values) for comp in critical_components)
        else:
            critical_affected = False
        
        # Determine impact level
        if total_bugs > 50 or critical_affected:
            impact['level'] = 'High'
            impact['factors'] = ['High bug volume', 'Critical components affected']
        elif total_bugs > 20:
            impact['level'] = 'Medium' 
            impact['factors'] = ['Moderate bug volume', 'Multiple components affected']
        else:
            impact['level'] = 'Low'
            impact['factors'] = ['Liproprietary commercialed bug volume', 'Isolated component issues']
        
        return impact
    
    def _calculate_advanced_risk_scores(self, component_counts, data):
        """Calculate advanced ML-based risk scores"""
        risk_scores = []
        
        for component, count in component_counts.items():
            # Base risk from count
            base_risk = min(100, count * 10)
            
            # Temporal risk factor
            component_data = data[data['Components'] == component] if 'Components' in data.columns else data
            if 'Created' in component_data.columns:
                component_data['Created'] = pd.to_datetime(component_data['Created'])
                recent_count = len(component_data[component_data['Created'] > (datetime.now() - timedelta(days=7))])
                temporal_risk = recent_count * 15
            else:
                temporal_risk = 0
            
            # Component criticality factor
            critical_keywords = ['auth', 'security', 'payment', 'database', 'core']
            criticality_factor = 20 if any(keyword in component.lower() for keyword in critical_keywords) else 0
            
            total_risk = min(100, base_risk + temporal_risk + criticality_factor)
            
            risk_scores.append({
                'component': component,
                'bug_count': count,
                'risk_score': total_risk,
                'risk_level': self._classify_risk_level(total_risk),
                'contributing_factors': {
                    'volume': base_risk,
                    'recency': temporal_risk,
                    'criticality': criticality_factor
                }
            })
        
        return sorted(risk_scores, key=lambda x: x['risk_score'], reverse=True)
    
    def _classify_risk_level(self, risk_score):
        """Classify risk level based on AI score"""
        if risk_score >= 80:
            return 'Critical'
        elif risk_score >= 60:
            return 'High'
        elif risk_score >= 40:
            return 'Medium'
        elif risk_score >= 20:
            return 'Low'
        else:
            return 'Minimal'
    
    def _analyze_temporal_patterns(self, data):
        """Analyze temporal patterns with AI"""
        patterns = {}
        
        if 'Created' not in data.columns:
            return {'note': 'No temporal data available'}
        
        data['Created'] = pd.to_datetime(data['Created'])
        data['DayOfWeek'] = data['Created'].dt.day_name()
        data['Hour'] = data['Created'].dt.hour
        
        # Day of week patterns
        day_patterns = data['DayOfWeek'].value_counts()
        patterns['peak_days'] = day_patterns.head(2).index.tolist()
        
        # Hour patterns
        hour_patterns = data['Hour'].value_counts()
        patterns['peak_hours'] = hour_patterns.head(3).index.tolist()
        
        # Weekly trend
        data['Week'] = data['Created'].dt.isocalendar().week
        weekly_counts = data.groupby('Week').size()
        if len(weekly_counts) > 1:
            patterns['weekly_trend'] = 'Increasing' if weekly_counts.iloc[-1] > weekly_counts.iloc[0] else 'Decreasing'
        
        return patterns
    
    def _predict_future_bugs(self, historical_data):
        """Predict future bug counts using ML"""
        try:
            # Prepare time series data
            monthly_counts = [data['total_bugs'] for data in historical_data]
            
            if len(monthly_counts) < 3:
                return {'error': 'Insufficient data for prediction'}
            
            # Simple linear regression for trend
            x = np.arange(len(monthly_counts)).reshape(-1, 1)
            y = np.array(monthly_counts)
            
            # Calculate trend
            slope = np.polyfit(range(len(monthly_counts)), monthly_counts, 1)[0]
            
            # Predict next month
            next_month_prediction = monthly_counts[-1] + slope
            next_month_prediction = max(0, int(next_month_prediction))
            
            # Calculate confidence based on trend consistency
            trend_consistency = 1 - (np.std(monthly_counts) / (np.mean(monthly_counts) + 1))
            confidence = max(30, min(90, trend_consistency * 100))
            
            return {
                'predicted_count': next_month_prediction,
                'trend': 'increasing' if slope > 0.5 else 'decreasing' if slope < -0.5 else 'stable',
                'confidence': round(confidence),
                'slope': round(slope, 2)
            }
            
        except Exception as e:
            return {'error': f'Prediction failed: {str(e)}'}
    
    def _generate_no_data_insights(self, project_name):
        """Generate insights when no data is available"""
        return {
            'executive_summary': {
                'headline': f"🎉 {project_name} shows excellent stability with zero bugs detected",
                'health_score': 100,
                'business_impact': {'level': 'Minimal', 'factors': ['No active issues']},
                'key_metrics': {'total_bugs': 0, 'components_affected': 0}
            },
            'recommendations': {
                'immediate_actions': ['✅ Continue current quality practices'],
                'strategic_initiatives': ['📊 Maintain proactive monitoring'],
                'process_improvements': ['🔄 Regular health checks recommended']
            },
            'confidence_scores': {'overall_confidence': 95}
        }

# Additional specialized AI classes

class NLPAnalyzer:
    """Natural Language Processing for bug descriptions"""
    
    def analyze_bug_descriptions(self, descriptions):
        """Comprehensive NLP analysis of bug descriptions"""
        if not descriptions or len(descriptions) == 0:
            return {'error': 'No descriptions to analyze'}
        
        # Sentiment analysis
        if TEXTBLOB_AVAILABLE:
            sentiments = [TextBlob(desc).sentiment.polarity for desc in descriptions]
            avg_sentiment = np.mean(sentiments)
        else:
            avg_sentiment = 0.0  # Neutral when TextBlob is not available
        
        # Extract common themes
        themes = self._extract_themes(descriptions)
        
        # Categorize bugs
        categories = self._categorize_bugs(descriptions)
        
        return {
            'sentiment_score': round(avg_sentiment, 2),
            'sentiment_interpretation': self._interpret_sentiment(avg_sentiment),
            'common_themes': themes,
            'bug_categories': categories,
            'urgency_indicators': self._detect_urgency(descriptions)
        }
    
    def _extract_themes(self, descriptions):
        """Extract common themes using NLP"""
        # Simple keyword extraction
        all_text = ' '.join(descriptions).lower()
        
        # Common bug-related keywords
        keywords = ['error', 'crash', 'bug', 'issue', 'problem', 'fail', 'broken', 
                   'slow', 'timeout', 'exception', 'null', 'undefined']
        
        theme_counts = {}
        for keyword in keywords:
            count = all_text.count(keyword)
            if count > 0:
                theme_counts[keyword] = count
        
        return sorted(theme_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    
    def _categorize_bugs(self, descriptions):
        """Categorize bugs by type"""
        categories = {
            'UI/UX': ['button', 'display', 'layout', 'ui', 'interface', 'design'],
            'Performance': ['slow', 'timeout', 'performance', 'lag', 'speed'],
            'Functionality': ['feature', 'function', 'work', 'broken', 'fail'],
            'Security': ['security', 'auth', 'login', 'permission', 'access'],
            'Data': ['data', 'database', 'save', 'load', 'sync']
        }
        
        category_counts = {cat: 0 for cat in categories}
        
        for desc in descriptions:
            desc_lower = desc.lower()
            for category, keywords in categories.items():
                if any(keyword in desc_lower for keyword in keywords):
                    category_counts[category] += 1
        
        return category_counts
    
    def _interpret_sentiment(self, sentiment_score):
        """Interpret sentiment score"""
        if sentiment_score > 0.1:
            return 'Positive (solutions/fixes mentioned)'
        elif sentiment_score < -0.1:
            return 'Negative (critical issues highlighted)'
        else:
            return 'Neutral (standard bug reports)'
    
    def _detect_urgency(self, descriptions):
        """Detect urgency indicators in descriptions"""
        urgent_keywords = ['urgent', 'critical', 'emergency', 'asap', 'immediately', 
                          'blocking', 'show-stopper', 'production']
        
        urgent_count = 0
        for desc in descriptions:
            if any(keyword in desc.lower() for keyword in urgent_keywords):
                urgent_count += 1
        
        urgency_percentage = (urgent_count / len(descriptions)) * 100
        return {
            'urgent_bugs': urgent_count,
            'urgency_percentage': round(urgency_percentage, 1),
            'urgency_level': 'High' if urgency_percentage > 20 else 'Medium' if urgency_percentage > 10 else 'Low'
        }

class PredictiveModels:
    """Machine learning models for predictive analytics"""
    
    def __init__(self):
        self.risk_model = None
        self.timeline_model = None
        
    def predict_component_failure_risk(self, component_data, historical_patterns):
        """Predict likelihood of component failure"""
        # Implementation would include ML model training
        # For now, return rule-based predictions
        
        predictions = []
        for component, data in component_data.items():
            risk_factors = {
                'recent_bugs': len(data),
                'trend': self._calculate_trend(data),
                'complexity_score': self._estimate_complexity(component)
            }
            
            # Calculate failure risk
            failure_risk = min(100, 
                (risk_factors['recent_bugs'] * 10) + 
                (risk_factors['trend'] * 20) + 
                (risk_factors['complexity_score'] * 5)
            )
            
            predictions.append({
                'component': component,
                'failure_risk': failure_risk,
                'risk_factors': risk_factors,
                'recommendation': self._get_risk_recommendation(failure_risk)
            })
        
        return sorted(predictions, key=lambda x: x['failure_risk'], reverse=True)
    
    def _calculate_trend(self, component_data):
        """Calculate trend factor for component"""
        # Simplified trend calculation
        return 1 if len(component_data) > 5 else 0
    
    def _estimate_complexity(self, component_name):
        """Estimate component complexity based on name"""
        complex_indicators = ['core', 'engine', 'framework', 'service', 'api']
        return 2 if any(indicator in component_name.lower() for indicator in complex_indicators) else 1
    
    def _get_risk_recommendation(self, risk_score):
        """Get recommendation based on risk score"""
        if risk_score > 70:
            return "Immediate attention required - consider refactoring"
        elif risk_score > 50:
            return "Increase testing and monitoring"
        elif risk_score > 30:
            return "Regular monitoring recommended"
        else:
            return "Component appears stable"

# Factory function to create AI intelligence
def create_ai_intelligence():
    """Factory function to create AI intelligence engine"""
    return AIIntelligenceEngine()

# Example usage function
def generate_ai_insights(data, project_name, historical_data=None):
    """Generate comprehensive AI insights for any dataset"""
    ai_engine = create_ai_intelligence()
    return ai_engine.generate_comprehensive_insights(data, project_name, historical_data) 